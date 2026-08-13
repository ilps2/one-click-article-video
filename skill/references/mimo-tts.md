# 小米 MiMo TTS 接入(配音环节,2026-08 实测)

视频配音 = 文案(幕结构自动生成)→ TTS 克隆配音 → ffmpeg 合成。MiMo-V2.5-TTS 系列**限时免费**,中文原生,支持声音克隆 + 自然语言导演指令。

## 端点与认证

- BASE_URL: `https://api.xiaomimimo.com/v1`(OpenAI 兼容,chat/completions)
- API Key: `sk-` 前缀,在 https://platform.xiaomimimo.com/#/console/api-keys 创建
- 认证: `Authorization: Bearer <key>`(也支持 `api-key: <key>` 头)
- 注意: `https://mimo.mi.com/api/v1/...` 的 chat 接口要 STS 登录态(401),**只有 api.xiaomimimo.com 是 API Key 认证**;`mimo.mi.com/v1/models` 公开可访问(探测 key 用)

## 三个模型

| Model ID | 用途 |
|---|---|
| `mimo-v2.5-tts` | 预置音色合成(开箱即用) |
| `mimo-v2.5-tts-voicedesign` | 文本描述设计全新音色 |
| `mimo-v2.5-tts-voiceclone` | **音频样本复刻音色**(配音用这个) |

价格页(2026-08-06):TTS 三模型**限时免费**;文本模型 mimo-v2.5 与 DeepSeek 同价(in ¥1/out ¥2 每百万)。

## 调用方式(OpenAI 兼容)

```
messages:
  user       → 风格指令(自然语言,如「沉稳温润,像讲老朋友的故事」;可为空)
  assistant  → 要合成的文本(必填)
audio:
  format     → wav / mp3 / pcm16(默认 wav)
  voice      → voiceclone 专用: "data:audio/mpeg;base64,<录音base64>"
```

样本要求:mp3/wav,base64 后 ≤10MB,几段 10-30 秒自然说话(背景安静、普通话)。

返回:`choices[0].message.audio.data`(base64 音频)+ `audio.transcript`。

## 已验证的最小调用(curl)

```bash
curl -s https://api.xiaomimimo.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MIMO_KEY" \
  -d '{"model":"mimo-v2.5-tts","messages":[
        {"role":"user","content":"沉稳温润"},
        {"role":"assistant","content":"雨过天青云破处,一色千年。"}],
        "audio":{"format":"mp3"}}'
# 实测:HTTP 200,返回 6.24s mp3(base64)
```

voiceclone 版本:`"audio":{"format":"wav","voice":"data:audio/mpeg;base64,<录音>"}`,model 换 `mimo-v2.5-tts-voiceclone`。

## 能力亮点

- 自然语言风格指令:复合情绪(「压抑的愤怒」「带着哽咽的笑意」)、多粒度(段落→句子→词→字级重音/气音)
- 导演模式:user 消息写【角色】【场景】【指导】三维输入,像给演员写剧本
- 文档:https://mimo.mi.com/llms.txt(可 curl,含全部 API 文档路径);TTS 指南 https://mimo.mi.com/static/docs/quick-start/usage-guide/audio/speech-synthesis-v2.5.md

## ⚠️ 语速控制:自然语言指令几乎无效,必须用文本标签(实测坑)

配音语速直接决定音画同步,实测三连(同一文案 113 字,视频 40s):

| 控制方式 | 结果 | 语速 |
|---|---|---|
| user 消息写「语速放慢,大约每秒三个字」 | 22.6s | ~5 字/秒 ❌ 太快 |
| user 消息强化「非常慢,每秒三个字,每句停顿半秒」 | 27.2s | ~4.2 字/秒 ❌ 仍快 |
| assistant 文本加 `(沉稳 语速慢)` 开头 + `[停顿]` 插句间 | **33.6s** | **~3.4 字/秒 ✅ 匹配预算** |

**结论**:语速/停顿必须写进 **assistant 的合成文本**里,用标签控制:
- 整体风格标签放文本开头:`(沉稳 语速慢)`——括号支持半角 `()` / 全角 `（）` / `[]`,多个风格名空格分隔,自定义风格名也支持
- 细粒度音频标签 `[停顿]`/`[深呼吸]` 等插在任意句间位置(文档叫 audio tag:停顿、呼吸、叹气等)
- 标点也能拖节奏:句号/逗号比自然语言指令更可靠

风格标签示例:`(Sighing)…` `(Lazy)…` `(Magnetic)…`;整体基调类:`(Calm)(Deep)…`;实测 `(沉稳 语速慢)` 有效。

## ffmpeg 合成(视频 + 配音)

```bash
ffmpeg -i video.mp4 -i voice.mp3 -c:v copy -c:a aac -shortest out.mp4
```

## 流程集成

1. 从视频幕结构生成旁白文案(每幕 1-2 句,总时长 ≤ 视频时长)
2. voiceclone 配音(风格指令按设计系统:宋瓷=温润克制/烟火=深夜叙事/琥珀金=笃定)
3. ffmpeg 合成 → 交付时附配音版
