<div align="center">

# 🎬 One-Click Article Video

**粘贴你的公众号文章,一键产出三平台视频 + 四规格封面 + 发布文案**

**全程一个 LLM(DeepSeek 级别)搞定,单篇成本约 5 分钱,成品可编辑、可批量**

纯代码生成视频:LLM 写 HTML/CSS/JS 动画 → HyperFrames 逐帧渲染 mp4 → 封面 headless Chrome 导出 PNG。不依赖任何视频生成模型,精确中文排版,绝无"AI 视频汉字乱码"。

</div>

---

## 📦 一篇文章,产出什么

| 输出 | 规格 | 平台 |
|---|---|---|
| 视频 1 | 1080×1920 (9:16), 35s | **抖音 + 微信视频号通用** |
| 视频 2 | 1080×1440 (3:4), 35s | **小红书** |
| 封面 1 | 1080×1920 (9:16) | 抖音封面 |
| 封面 2 | 1080×1440 (3:4) | 小红书封面 |
| 封面 3 | 1080×1080 (1:1) | 微信视频号封面 |
| 封面 4 | 900×383 (2.35:1) | 公众号头图横条 |
| 文案 | 三平台发布文案(标题/正文/话题) | 抖音 / 小红书 / 公众号 |

## 💰 成本

| 项目 | 成本 |
|---|---|
| LLM API(DeepSeek 价:输入 ¥1/百万 token,输出 ¥2/百万) | **≈ ¥0.05/篇**(实测约 8.5k 输入 + 17k 输出) |
| 渲染 | 本地 Chrome + ffmpeg,¥0 |
| **全套合计** | **≈ 5 分钱** |

批量做 100 篇 ≈ ¥5。对比:AI 视频模型 ¥0.5-5/条、剪映会员几十元/月、代做 ¥49/小时。

## 🎯 为什么用代码生成视频

1. **钩子文字是 diffusion 的致命伤,是 HTML/SVG 的绝对主场**——AI 视频模型生成的汉字全是乱码,公众号封面/标题的点击率变量恰恰是文字。这个市场它们根本进不来
2. **精确可编辑**——交付 HTML 源文件,改一个字 10 秒,不是一次性生成
3. **意象化配图**——色块/器物/圆点/纹理,不画人脸产品,不触发精度比较
4. **确定性渲染**——同一输入 → 同一输出,可复现、可批量、可审查

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 | 用途 |
|---|---|---|
| Node.js | 22+ | HyperFrames CLI |
| Google Chrome | 任意较新版本 | 逐帧渲染 + 封面导出 |
| FFmpeg | 任意 | 视频合成 |

**macOS 检查方法**:打开「终端」App,输入以下命令逐条回车:

```bash
node --version      # 应显示 v22 或更高
ffmpeg -version     # 应显示版本信息
ls "/Applications/Google Chrome.app"   # 应显示目录存在
```

**Windows 检查方法**:打开「命令提示符」,输入:

```cmd
node --version
ffmpeg -version
```

如果 `node` 或 `ffmpeg` 提示"不是内部或外部命令",先安装:
- Node.js:到 https://nodejs.org 下载 LTS 版,一路下一步(Windows 安装时勾选 "Add to PATH")
- FFmpeg:macOS 用 `brew install ffmpeg`;Windows 到 https://www.gyan.dev/ffmpeg/builds/ 下载,解压后把 `bin` 目录加入系统 PATH

### 安装

**macOS / Linux**:

```bash
# 1. 克隆本仓库
git clone https://github.com/ilps2/one-click-article-video.git
cd one-click-article-video

# 2. 验证 HyperFrames CLI 可用(首次会自动下载,约 1 分钟)
npx --yes hyperframes@latest --version
# 看到版本号(如 0.7.107)即成功
```

**Windows**:

```bat
git clone https://github.com/ilps2/one-click-article-video.git
cd one-click-article-video
npx --yes hyperframes@latest --version
```

### 给 AI 助手使用(Hermes / Claude Code / Codex 等)

本仓库的 `skill/` 目录是一个完整的 Agent Skill:
- **Hermes**:复制 `skill/` 到 `~/.hermes/skills/media/` 下(或 `hermes skills import`)
- **Claude Code / Codex / 其他**:把 `skill/` 内容合并进对应 skills 目录(如项目的 `.claude/skills/`)
- 然后对助手说:**"把这篇公众号文章做成三平台视频和封面"**(附链接或全文)

助手会按 `skill/SKILL.md` 的流程自动完成:抓文章 → 提炼 → 设计 → 生成视频 → 生成封面 → 验证 → 归档。

**前置 Skill 依赖**(SKILL.md 会引用,建议一并安装,否则助手会卡在这些引用上):

| Skill | 用途 | 说明 |
|---|---|---|
| hyperframes(+ core/animation/cli) | 视频渲染引擎的完整规范 | 核心依赖,详见 `npx hyperframes init` 生成的项目文档 |
| gzh-explosive-content-detector | 文章被微信验证页拦截时的降级抓取 | 可选:没有就走「让作者粘贴全文」 |
| mimo-tts | 视频配音(声音克隆,限时免费) | 可选:跳过配音不影响视频/封面产出 |

> 注意:SKILL.md 中 `~/Downloads/Agent/Hermes/` 归档路径是 Hermes 宿主的默认约定,其他宿主请按自己的归档目录习惯调整。

### 手动使用(不依赖 AI 助手)

```bash
# 1. 抓取公众号文章
python3 skill/scripts/fetch_wechat_article.py "https://mp.weixin.qq.com/s/你的文章链接" --text article.txt
# 看到"标题: xxx"和"正文: N 字符"即成功;被微信验证页拦截就手动复制全文到 article.txt

# 2. 初始化视频项目(竖屏 9:16)
cd ~
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init my-video --example blank --resolution portrait --non-interactive

# 3. 让 LLM 按 skill/SKILL.md 的规范编写 index.html(9:16)与 compositions/redbook-34.html(3:4)

# 4. 验证 + 渲染
cd my-video
npm run check        # 必须 0 errors
npx hyperframes render --quality high --output video-916.mp4
npx hyperframes render -c compositions/redbook-34.html --quality high --output video-34.mp4

# 5. 验证输出(应显示 1080x1920 / 1080x1440)
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video-916.mp4

# 6. 封面:复制 skill/references/cover-template.html 为模板,headless Chrome 导出
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --screenshot=cover.png \
  --window-size=1080,1920 --force-device-scale-factor=2 --hide-scrollbars "file://$PWD/cover.html"
# Windows 用: "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --screenshot=cover.png --window-size=1080,1440 --force-device-scale-factor=2 --hide-scrollbars "file://%CD%/cover.html"
```

> **Windows 提示**:以上命令中 `python3` 写 `python`、`$PWD` 写 `%CD%`、Chrome 路径用 `C:\Program Files\Google\Chrome\Application\chrome.exe`(装在其他位置就到安装目录找),其余一致。路径含空格时用引号包裹。

---

## 🎨 设计系统(内置 3 套已验证模板)

| 风格 | 适用文章类型 | 配色 | 意象 |
|---|---|---|---|
| 宋瓷天青风 | 文化/美学/产品 | 月白底 + 天青 + 黑釉 + 茶褐 | 器物剪影、开片、圆点阵 |
| 深夜烟火风 | 情感/人物叙事 | 月牙白底 + 炭火橙 | 月亮、炭火、烟雾 |
| 财富琥珀金风 | 观点/财富/职场 | 月牙白底 + 琥珀金 | 增长曲线、金币 |

每套含 6 幕视频结构模板 + 封面钩子案例,见 `skill/references/design-systems.md`。

## 📖 已验证案例

| 文章 | 风格 | 数据 |
|---|---|---|
| 《从雨过天青到一张会变色的封面》 | 宋瓷天青风 | 公众号 10w+,完整 2 视频 + 4 封面 |
| 《张雪峰的替身—烧烤摊主替张过人间烟火日子》 | 深夜烟火风 | 公众号 10w+,完整 2 视频 + 4 封面 |
| 《马斯克:如果今天破产,我绝不会去找工作…》 | 财富琥珀金风 | 公众号 10w+,完整 2 视频 + 4 封面 |

**🎬 案例成品视频(真实渲染输出)**:[GitHub Release v0.1.0](https://github.com/ilps2/one-click-article-video/releases/tag/v0.1.0) — 每篇含 9:16 视频(抖音/微信)、3:4 视频(小红书)、抖音封面,直接下载看效果。

## 🛠 常见问题

**Q: 公众号文章抓取失败/遇到验证页?**
A: 微信对 10w+ 热文常有人机验证。处理:① 换 PC UA 重试 ② headless 浏览器访问 ③ 让作者复制全文 ④ 用关键词在爆款数据源搜同题文章,从摘要重建故事线(信息足够即可开做)。

**Q: 为什么不用 AI 视频生成模型?**
A: 汉字乱码、不可编辑、改一个字重生成。代码生成精确、可编辑、批量成本趋近于零。

**Q: 需要什么编程基础?**
A: 零基础可用(AI 助手全自动);想手动调样式需要一点 HTML/CSS。

## 📄 许可

MIT

---

*由 DeepSeek 级别的单个 LLM 驱动的「文章 → 三平台视频 + 封面 + 文案」生产线。*
