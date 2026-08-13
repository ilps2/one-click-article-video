#!/usr/bin/env python3
"""公众号文章抓取:输入 mp.weixin.qq.com 链接,输出标题/摘要/纯文本正文。
用法:
  python3 fetch_wechat_article.py <url> [-o out.html] [--text out.txt]
"""
import argparse
import html
import re
import subprocess
import sys
import urllib.request

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")


def fetch(url: str) -> str:
    """优先 curl(可带 -x 代理),回退 urllib。"""
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "30", "-A", UA, url],
            capture_output=True, timeout=40)
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", errors="ignore")
    except Exception:
        pass
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse(raw: str):
    title = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
    title = html.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else ""
    ts = re.search(r'var ct = "(\d+)"', raw)
    import datetime
    pub = datetime.datetime.fromtimestamp(int(ts.group(1))).strftime("%Y-%m-%d %H:%M") if ts else ""
    desc = re.search(r'<meta property="og:description" content="(.*?)"', raw)
    desc = html.unescape(desc.group(1)) if desc else ""
    body = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', raw, re.S)
    if not body:  # 兜底:取到第一个 </div> 前
        body = re.search(r'<div[^>]*id="js_content"[^>]*>(.*)', raw, re.S)
    text = ""
    if body:
        b = body.group(1)
        b = re.sub(r"<br\s*/?>", "\n", b)
        b = re.sub(r"</p>", "\n", b)
        b = re.sub(r"</section>", "\n", b)
        b = re.sub(r"<[^>]+>", "", b)
        text = html.unescape(b)
        text = "\n".join(l.strip() for l in text.split("\n") if l.strip())
    return title, pub, desc, text


def main():
    ap = argparse.ArgumentParser(description="抓取公众号文章")
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default="/tmp/wx_article.html", help="保存原始 HTML")
    ap.add_argument("--text", help="保存纯文本正文到该文件")
    args = ap.parse_args()

    raw = fetch(args.url)
    if not raw:
        print("抓取失败:空响应(可能被风控,请让用户粘贴全文)", file=sys.stderr)
        sys.exit(1)
    title, pub, desc, text = parse(raw)
    # 明确失败判定:无标题且无正文 = 验证页/链接失效,而不是"成功但内容为空"
    if not title and not text:
        print("抓取失败:未解析到 js_content(疑似微信验证页或链接失效)。"
              "可尝试:① PC UA 重试 ② headless 浏览器 ③ 让用户粘贴全文", file=sys.stderr)
        sys.exit(1)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(raw)
    print(f"标题: {title}")
    print(f"发布时间: {pub}")
    print(f"摘要: {desc[:120]}")
    print(f"正文: {len(text)} 字符")
    if args.text:
        with open(args.text, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{text}")
        print(f"正文已存: {args.text}")
    else:
        print("\n" + text[:800])


if __name__ == "__main__":
    main()
