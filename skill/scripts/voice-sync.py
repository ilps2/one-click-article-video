#!/usr/bin/env python3
"""分段配音 + 画面跟随(剪映式文音画同步)。

原理:按幕分段生成配音 → 每幕拿到「实测配音时长」→ 画面时长 = 配音 + 1s(画面先出)
→ 时间轴以真实配音为准,不再估算语速。误差从 ±1s 降到 ±0.1s。

用法:
  python3 voice-sync.py script.json --voice ~/.hermes/voice-samples/user.mp3 \
      --style "沉稳笃定,正常语速" --out /tmp/voice/
  script.json: [{"id":"s1","text":"幕1配音文案"}, ...]

输出:
  <out>/<id>.mp3           每幕配音音频
  <out>/durations.json     每幕实测时长
  <out>/timeline.json      画面时间轴(每幕 = 配音 + 1.0s 画面先出)
"""
import argparse
import base64
import json
import subprocess
import sys
import time

API = "https://api.xiaomimimo.com/v1/chat/completions"
LEAD = 1.0  # 画面先出时间(配音延迟量)
HEAD = 0.4  # 第一幕开头留白


def parse_args():
    ap = argparse.ArgumentParser(description="分段配音 + 画面跟随")
    ap.add_argument("script", help="JSON: [{'id','text'},...]")
    ap.add_argument("--voice", default="~/.hermes/voice-samples/user.mp3", help="克隆声音样本")
    ap.add_argument("--key", default=None, help="MiMo API Key(默认环境变量 MIMO_API_KEY)")
    ap.add_argument("--style", default="正常语速,沉稳笃定", help="风格指令(放 user 消息)")
    ap.add_argument("--out", default="/tmp/voice", help="输出目录")
    return ap.parse_args()


def tts(key, voice_b64, style, text, out_path):
    payload = {
        "model": "mimo-v2.5-tts-voiceclone",
        "messages": [
            {"role": "user", "content": style},
            {"role": "assistant", "content": text},
        ],
        "audio": {"format": "mp3", "voice": f"data:audio/mpeg;base64,{voice_b64}"},
    }
    with open(out_path + ".req.json", "w") as f:
        json.dump(payload, f)
    r = subprocess.run([
        "curl", "-s", "--max-time", "240", API,
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {key}",
        "-d", f"@{out_path}.req.json",
    ], capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "choices" not in d:
        raise RuntimeError(f"TTS 失败: {str(d)[:300]}")
    audio = base64.b64decode(d["choices"][0]["message"]["audio"]["data"])
    with open(out_path + ".mp3", "wb") as f:
        f.write(audio)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    args = parse_args()
    key = args.key
    if not key:
        import os
        key = os.environ.get("MIMO_API_KEY")
    if not key:
        sys.exit("需要 --key 或环境变量 MIMO_API_KEY")
    script = json.load(open(args.script, encoding="utf-8"))
    voice_b64 = base64.b64encode(open(args.voice.replace("~", __import__("os").path.expanduser("~")), "rb").read()).decode()
    import os
    os.makedirs(args.out, exist_ok=True)

    durations = {}
    for i, seg in enumerate(script):
        out = f"{args.out}/{seg['id']}"
        print(f"[{i+1}/{len(script)}] {seg['id']}: {seg['text'][:20]}...", flush=True)
        tts(key, voice_b64, args.style, seg["text"], out)
        durations[seg["id"]] = duration(out + ".mp3")
        print(f"    -> {durations[seg['id']]:.2f}s", flush=True)

    json.dump(durations, open(f"{args.out}/durations.json", "w"), ensure_ascii=False, indent=1)

    # 画面时间轴:每幕 = 配音 + LEAD(画面先出);配音延迟 = 该幕画面起点 + LEAD
    timeline = []
    t_cursor = HEAD
    for seg in script:
        d = durations[seg["id"]]
        scene_start = t_cursor
        timeline.append({
            "id": seg["id"],
            "text": seg["text"],
            "voice_dur": round(d, 2),
            "scene_start": round(scene_start, 2),
            "scene_dur": round(d + LEAD, 2),
            "voice_delay": round(scene_start + LEAD, 2),  # 画面先出 LEAD 秒,配音跟上
        })
        t_cursor += d + LEAD
    json.dump(timeline, open(f"{args.out}/timeline.json", "w"), ensure_ascii=False, indent=1)

    total = t_cursor
    print(f"\n✅ 完成: 配音总时长 {sum(durations.values()):.1f}s, 视频建议时长 {total:.1f}s")
    print("时间轴:", json.dumps([(t["id"], t["scene_start"], t["scene_dur"]) for t in timeline], ensure_ascii=False))
    # 合成命令(多段 amix,延迟 = scene_start + LEAD 秒 → 毫秒)
    parts = ";".join(
        f"[{i + 1}:a]adelay={int((t['scene_start'] + LEAD) * 1000)}:all=1[a{i + 1}]"
        for i, t in enumerate(timeline)
    )
    mix = "".join(f"[a{i + 1}]" for i in range(len(timeline)))
    print(f"\n合成命令示例:\n  ffmpeg -i 视频.mp4 " + " ".join(
        f"-i {args.out}/{t['id']}.mp3" for t in timeline) +
        f" -filter_complex \"{parts};{mix}amix=inputs={len(timeline)}:normalize=0[a]\" "
        f"-map 0:v -map \"[a]\" -c:v copy -c:a aac -b:a 128k -shortest 输出-配音版.mp4")


if __name__ == "__main__":
    main()
