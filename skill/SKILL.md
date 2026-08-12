---
name: one-click-article-video
description: >
  一键把公众号文章(链接或原文)变成三平台视频 + 四规格封面:抖音/微信 9:16 视频、
  小红书 3:4 视频、抖音 9:16 封面、小红书 3:4 封面、微信 1:1 封面、公众号头图横条 2.35:1。
  纯代码生成:LLM 写 HTML/CSS/JS → HyperFrames 逐帧渲染 mp4,封面 headless Chrome 导出 PNG,
  全程一个 DeepSeek 级别的模型即可,单篇成本约 5 分钱,成品可编辑可批量。
  设计采用「钩子文字 × 意象化模板」封面工厂方法论。触发词:公众号文章转视频、
  一键文章视频、文章视频化、文章做视频、抖音/小红书/微信封面、封面工厂、钩子封面、图文转视频。
---

# 文章 → 视频 + 封面 工厂

纯代码生成视频与封面:不依赖任何视频生成模型,LLM 写 HTML/CSS/JS → HyperFrames 逐帧渲染 mp4;封面是单文件 HTML,headless Chrome 截图导出 PNG。全程确定性、可编辑、可批量。

**定位话术(对外卖点,用户已确认)**:一个 LLM(DeepSeek 级别)全包「视频+封面+文案」;单篇成本 ≈¥0.05;精确中文排版(扩散模型的汉字乱码进不来的市场);成品交付 HTML 源文件可编辑。主打「一键」,不主打模型名(v4-flash 有保质期,模型名只做信任背书与成本锚点)。

## 输入 / 输出

| 输入 | 公众号链接(`mp.weixin.qq.com/s/...`)或文章原文文本 |
|---|---|
| 输出 1 | 视频 9:16 = 1080×1920(**抖音 + 微信视频号通用**) |
| 输出 2 | 视频 3:4 = 1080×1440(小红书) |
| 输出 3 | 封面 9:16 = 1080×1920(抖音封面) |
| 输出 4 | 封面 3:4 = 1080×1440(小红书封面) |
| 输出 5 | 封面 1:1 = 1080×1080(微信视频号封面) |
| 输出 6 | 封面横条 = 900×383(公众号头图,2.35:1) |
| 输出 7 | 三平台发布文案(抖音标题/正文/话题、小红书标题/正文/话题、微信标题/导语) |
| 归档 | `~/Downloads/Agent/Hermes/<YYYY-MM-DD>/<文章主题>/`(用户硬性要求) |

## 流程

### 1. 获取文章

- 链接:运行 `python3 scripts/fetch_wechat_article.py <url> -o /tmp/wx_article.html`,输出标题/摘要/纯文本正文(自动处理 iPhone UA 与 `js_content` 解析)
- 原文文本:直接使用,跳过本步
- 抓取失败(微信 verify 验证页:HTTP 200 但 ~17KB、无 `js_content`):依次尝试 ① PC UA + Referer 再 curl ② headless 浏览器访问 ③ 仍被拦(10w+ 热文常见)→ **降级重建工作流**:用 gzh-explosive-content-detector 按标题关键词/同题词搜,从 JSON 的 `summary` 字段提取故事线(爆款数据源的摘要常含完整叙事),再搜同题文章交叉验证细节——信息足够即可开做,不必硬等全文,也不要反复磨验证页
- 关键词技巧:组合词查不到时拆词搜(实测:「张雪峰替身」0 条 → 「替身」33 条 + 「考研」152 条交叉命中)

### 2. 内容提炼(LLM 完成)

从文章提取:
- **标题钩子**(封面/视频开头用,可再加工)
- **核心论点 3-5 条**(视频主体)
- **金句 1-2 句**(结尾)
- 结构/数据/步骤(可视觉化的元素)
- 生成视频幕结构,推荐 6 幕;三种已验证模板(产品/方法型、情感叙事型、观点/财富型)见 `references/design-systems.md`

**⚠️ 配音优先的时长预算(必须先定文案,再定幕时长)**:
- 每幕先写**配音文案**(念白,非画面文字),按中文语速 **3.5 字/秒(保守)+ 每幕 1.5s 余量** 算幕时长:`幕时长 = 文案字数/3.5 + 1.5`
- 示例:120 字配音 → 34.3s + 余量 → 视频应设计 38-40s,35s 太紧(实测 120 字/33.4s 无余量,画面结尾 1.6s 无配音)
- 画面文字(标题/金句)的停留时间 ≥ 配音念到该处的时间;关键句先出现、配音后到
- 文案与画面文字不必逐字一致:画面可以精简,念白可以补充

### 3. 设计系统(从文章主题推导)

- **已验证设计系统见 `references/design-systems.md`**(宋瓷天青风 / 深夜烟火风 / 财富琥珀金风,含 6 幕模板与封面钩子案例),同类文章直接套用配色/字体/意象;新文章类型做出新系统后回填该文件
- 色板:从文章主题提取 4-5 色(主色/底色/文字色/点缀色),低饱和意象风
- 字体:标题宋体(`Songti SC`)或黑体(`PingFang SC`),等宽(`Menlo`)用于代码/提示词
- 意象化配图原则(封面工厂核心,详见 `references/cover-factory.md`):
  - 用色块、器物剪影、圆点阵、网格、开片纹理等**意象化元素**,不画人脸/产品等精度敏感对象(观众不会拿去和照片比,避开 diffusion 的雷区也避开 SVG 的短板)
  - 钩子文字是主角:SVG/HTML 文字精确、任意字号、可编辑——这是扩散模型(汉字乱码)进不来的市场
- 模板化:钩子文案 × 意象模板 = 组合产出,单张成本极低

### 3.5 信息流字号规范(用户纠正:文字太小,参考抖音/小红书/微信热门)

竖屏信息流视频"3 秒定生死"——标题必须缩略图+前 3 秒看清。主流热门视频标准(1080×1920):

| 元素 | 字号 | 说明 |
|---|---|---|
| 主标题/金句 | **100-140px** | 占屏宽 65-90%,单行 ≤10-12 字 |
| 正文行 | **56-72px** | 每行 ≤12-14 字 |
| 小字/标签/说明 | ≥40px | 低于 40px 手机上看不清 |
| 内容占比 | **75-85%** | 留白仅 15-25%,不要大留白(宋瓷封面风≠视频信息流) |
| 顶部留白 | ≤100px | 信息流不空顶 |

反面教训:54px 正文 + 50% 留白的视频被用户指出"文字太小、像 PPT"。文案/字幕同理放大;封面 hook 与主标题同级。

### 4. 视频 composition(HyperFrames)

```bash
mkdir -p ~/Downloads/Agent/Hermes && cd ~/Downloads/Agent/Hermes
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <name> --example blank --resolution portrait --non-interactive
```

- 竖屏项目(root 1080×1920),**每个平台比例一个 composition 文件**:`index.html`(9:16,抖音+微信通用)+ `compositions/redbook-34.html`(3:4 小红书,1080×1440)
- **3:4 生成规则(宽度保持 + 高度压缩,禁止等比 ×0.75)**:3:4 与 9:16 宽度相同(1080),等比缩小会让内容变小、观感像裁切。正确做法:字号/卡片宽度/水平间距**保持**,垂直尺寸压缩(margin/padding 上下 ×0.72,height>100px 的元素 ×0.78),大图形(印章/器物)额外缩到 ~85%,长标题字号微调避免换行。直接运行 `python3 scripts/scale-to-34.py index.html -o compositions/redbook-34.html --shrink "#seal,0.85" --font-shrink "#s1-title-1,0.85"`。生成后必须抽帧验证:垂直居中(内容中心 ≈ 屏中 720)、顶底无裁切、字号与 9:16 一致
- 布局铁律:内容**纵向排列**(圆点+文字横排一行、向下箭头串联步骤);每幕内容包一个 wrap(`.scene > div` 必须 `display:flex; flex-direction:column; align-items:center; width:100%`,否则窄子元素靠左)
- **单行元素自适应缩字**(防"一行多一个字"难看换行):所有设计为单行的标题/文案元素加 `class="nowrap"`(`white-space:nowrap`)。**两个关键坑**:① inline 元素没有容器宽度概念,fit 前先 `display:inline-block`;② **不要用 scrollWidth 测量**(渲染器与本地浏览器字体度量不同,测量结果漂移,同一页面本地 102px、渲染器 62px)——用**字符计算法**:中文全宽字宽=字号,半宽字符(数字/字母/空格/标点)≈0.55×字号,`w = 全宽字数×fs + 半宽字数×fs×0.55`,超宽则 `fs = 容器宽/(全宽+半宽×0.55)×0.99`。**检查每个单行元素都真的有 nowrap class**(漏加=完全不参与 fit,常见坑:s1-title-2/s1-sub 因原始 HTML 无 class 而漏网)。fitLines 参考实现:
  ```js
  function fitLines() {
    document.querySelectorAll('.nowrap').forEach(function (el) {
      if (getComputedStyle(el).display === 'inline') el.style.display = 'inline-block';
      var maxW = el.parentElement ? el.parentElement.clientWidth - 4 : 0;
      var fs = parseFloat(getComputedStyle(el).fontSize);
      var text = el.textContent;
      var full = (text.match(/[\u4e00-\u9fff\u3000-\u303f]/g) || []).length;
      var half = text.length - full;
      var w = full * fs + half * fs * 0.55;
      if (maxW > 0 && w > maxW) {
        el.style.fontSize = Math.floor(maxW / (full + half * 0.55) * 0.99) + 'px';
      }
    });
  }
  fitLines();
  ```
- 动画:单个 `gsap.timeline({paused:true})` 注册到 `window.__timelines["main"]`;**连续修改同一属性(如换肤轮播的 backgroundColor)必须用 `fromTo` 显式起止色**,否则 tween 起始值在创建时被捕获,播放会闪回初始值
- 场景切换:clip 内 wrap 做 opacity fade,在 clip 边界加 `tl.set(wrap, {opacity:0}, <boundary>)` hard kill(不满足会报 `gsap_exit_missing_hard_kill`)
- 字体:`@font-face { font-family:"PingFang SC"; src:local("PingFang SC"); }` 等声明,否则渲染器 fallback 字体
- 规则:clip 必须 root 直接子元素;不 tween display/visibility;不用 `<br>`(短标题刻意断行除外);根 `data-duration` 编译期锁定(脚本改无效);不 tween clip 元素本身
- 细节参考:hyperframes / hyperframes-core / hyperframes-animation / hyperframes-cli skills

### 5. 封面 HTML(单文件)

- 复制 `references/cover-template.html` 为模板,替换钩子文字、意象元素、配色
- 平台规格:抖音 1080×1920(9:16)、小红书 1080×1440(3:4)、微信视频号 1080×1080(1:1);同一设计系统三份竖版排版
- **公众号封面(横条 900×383)的左 1:1 裁剪机制**:微信转发卡片图 = 封面横条**左侧 383×383 区域直接裁剪**(无独立设置)。因此横条设计必须:左侧 1:1 区内放**完整主题**(印章+主标题,独立表达),补充卖点(数字/副文案)放右侧裁剪区外;设计后用 `ffmpeg crop=766:766:0:0`(2x)验证 1:1 区内主题完整、裁剪边界无半截元素
- 导出 PNG(headless Chrome 2x,无需点 html2canvas 按钮):
  ```bash
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  "$CHROME" --headless=new --disable-gpu --screenshot=cover.png \
    --window-size=<W>,<H> --force-device-scale-factor=2 --hide-scrollbars "file://$PWD/cover.html"
  ```
- 设计参考 `references/cover-factory.md` 的钩子类型 × 模板矩阵

### 6. 渲染与验证(先测后交)

```bash
npm run check                                   # 必须 0 errors
npx hyperframes render -c <file> --quality high --output <name>.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 <name>.mp4
```

帧验证(**ffmpeg 抽帧必须加 `-vframes 1`**,否则输出的是该时间点之后所有帧的平均,颜色/内容判断全错):
```bash
ffmpeg -v error -ss <t> -i <name>.mp4 -vframes 1 -vf "crop=...,scale=..." -f rawvideo -pix_fmt rgb24 - | python3 统计主题色像素占比
```
验证要点:每幕内容存在、动画在位(对比两个时间点像素差异)、换肤/变色轮播各主题稳定期色值、封面卡水平居中(x 中心 ≈ 画布宽/2)。

### 7. 归档与交付

```bash
DEST="$HOME/Downloads/Agent/Hermes/$(date +%Y-%m-%d)/<文章主题>"
mkdir -p "$DEST" && cp *.mp4 *.png "$DEST/" && open "$DEST"
```

交付时给出:文件清单(尺寸/时长)、幕结构表、验证结果、**成本报表**(见成本模型)。

### 8. 三平台发布文案(LLM,与视频同一模型)

- 输入:内容要点 + 视频幕结构 → 输出 JSON:`{douyin:{标题,正文,话题}, redbook:{标题,正文,话题}, wechat:{标题,导语}}`
- 要求:抖音标题 <30 字带钩子;小红书标题带 emoji + 关键词(搜索流量);微信标题沿用公众号原风格
- 量级:≈1k in + 0.8k out,可并入提炼/交付同一轮,不增加独立成本

### 9. 发布前合规检查(平台审核适配,强制)

**所有产出——视频画面文字、封面文字、发布文案——发布前必须过一遍审核适配**,敏感词/竞品名一律用符号、缩写或同音字替代,否则轻则限流、重则封号。

**通用敏感词替换表**:

| 原词 | 替换 | 说明 |
|---|---|---|
| 微信 / 加微信 | 微❤信 / VX / 戳主页 | 引流词,抖音/小红书重灾区 |
| QQ / 公众号(引流语境) | Q 号 / 公号(仅正文提及可用) | 站外导流 |
| 竞品品牌名 | 首字母缩写(如某 H 牌)、「某品牌」、「那家」、同音字 | 竞品比较/提及 |
| 最 / 第一 / 绝对 / 顶级 | 去掉或改「目前见过」「之一」 | 极限词(广告法) |
| 稳赚 / 必赚 / 保本 | 「仅供参考」「案例不代表收益」 | 金融承诺 |
| 根治 / 治愈 / 100% 有效 | 弱化为「改善」「体验」 | 医疗功效 |
| 免费领取 / 私信我 | 评论区见 / 主页有 | 引流诱导 |

**平台侧重**:
- **抖音**:审核最严——金融/医疗/教育类需资质,极限词、竞品词、引流词都会触发;文案里别出现"加微信",用"戳主页"
- **小红书**:重引流词(微信/QQ/链接)与竞品比较;话题标签本身也要审(别带竞品话题)
- **微信/公众号**:广告法极限词、诱导分享("转发领取")、外链管控
- 封面/视频画面文字与文案同等对待(画面文字一样被 OCR 审核)

**第三方账号名(易漏,用户明确纠正过)**:
- 素材(视频 CTA、封面 brand、S1 来源标注)**不得出现第三方公众号名**——把别家爆款文章做成素材时,「关注「XX号」」= 免费帮别人拉粉,是业务损失
- 正确做法:来源标注统一「Nw+ 热文 · 一键成片」;CTA 用中性引导(「评论区聊聊」「点赞收藏」「爆款热文一键成片」)或**自己的品牌**(自己的文章才允许:「后台回复「关键词」」)

**执行**:每单交付前,对 `发布文案.md` + 封面钩子 + 视频关键帧文字做一次扫描,列出替换记录并在交付说明中标注「已过审核适配」。

### 10. 投放(微信侧优先)

微信视频号是官方流量倾斜方向,且公众号↔视频号双向打通。交付时附 `references/publishing-sop.md`(投放 SOP:绑定公众号 → 视频挂文章链接 → 文章插视频号视频 → 冷启动节奏 → 数据验证,按钮级操作)。投放优先级:微信视频号 > 小红书(图文+视频组合)> 抖音(纯算法竞争)。

### 11. 配音(声音克隆,可选但推荐)

用 MiMo-V2.5-TTS-VoiceClone(小米,限时免费)克隆**用户本人声音**配音,与流水线同构(OpenAI 兼容):

```bash
# 前置:语音样本 ~/.hermes/voice-samples/user.mp3(10-60s 自然说话,mp3/wav ≤10MB)
# 调用(chat/completions):
#   model: mimo-v2.5-tts-voiceclone
#   user 消息:风格指令(自然语言,如「沉稳温润,像讲老朋友的故事,语速适中」)
#   assistant 消息:配音文案(从幕结构生成,见 §2 时长预算)
#   audio.voice: "data:audio/mpeg;base64,<录音base64>"
#   audio.format: mp3
#   BASE_URL: https://api.xiaomimimo.com/v1(Key 从 platform.xiaomimimo.com 控制台获取)
# 合成:
ffmpeg -i 视频.mp4 -i 配音.mp3 -filter_complex "[1:a]adelay=800|800[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 128k -shortest 输出-配音版.mp4
```

**要点**:
- **时长预算先行**(§2):配音文案确定后,核对每幕时长 ≥ 该段文案字数/3.5 + 1.5s,不足则加长对应幕或删文案——画面要等声音,不能声音追画面
- 风格指令按文章类型调:文化类「沉稳温润」、情感类「娓娓道来」、观点类「笃定有力」
- 验证:合成后抽听 2-3 处(开头/金句/结尾),确认音画同步、无吞字;配音总时长 < 视频时长(留 ≥1.5s)
- Python 调用注意:系统 Python SSL 证书常坏(CERTIFICATE_VERIFY_FAILED),用 curl 或 `--noproxy '*'` 直连

**实测案例(抖音站外引导弱化)**:抖音正文里的「已开源 GitHub:one-click-article-video」虽无链接(仅搜索引导),仍建议改为「已开源,仓库名评论区见」——抖音对站外平台引导整体偏严,把仓库名放评论区传递(评论区是用户生成内容,审核尺度不同)。小红书对 GitHub 提及宽松(程序员内容常见),可保留原文。

### 11. 配音(可选,用户声音克隆)

给视频配用户本人的声音:幕结构 → 旁白文案(每幕 1-2 句)→ **小米 MiMo-V2.5-TTS-VoiceClone** 克隆配音 → ffmpeg 合成。MiMo TTS 三模型**限时免费**、中文原生、支持自然语言导演指令(情绪/语速/重音/气声)。端点/调用示例/样本要求见 `references/mimo-tts.md`(2026-08 实测可用)。风格指令按设计系统调:宋瓷=温润克制、烟火=深夜叙事、琥珀金=笃定。

## 成本模型(DeepSeek 价:in ¥1/百万,out ¥2/百万,缓存 ¥0.02/百万)

| 环节 | 输入 tokens | 输出 tokens |
|---|---|---|
| 内容提炼 | ~3.5k | ~0.8k |
| 9:16 视频 HTML(13KB 级) | ~2k | ~9k |
| 3 个封面 HTML | ~1k | ~5.5k |
| 三平台文案 | ~1k | ~0.8k |
| 迭代修复(平均 1-2 次) | ~1k | ~1k |
| **合计** | **~8.5k** | **~17.1k** |

**≈ ¥0.043/篇(全套 2 视频+4 封面+文案)**,渲染本地免费;第 2 篇起指令/模板命中缓存,批量 100 篇 ≈ ¥4。对外话术:「一篇文章变 3 平台视频+封面+文案,成本 5 分钱」。

## 开源分发(用户已走通:ilps2/one-click-article-video)

仓库 = `README.md`(按钮级步骤、macOS/Windows 分开、含验证步骤——用户对大众 README 的硬性要求)+ `skill/` 完整目录(skill 可被其他 Hermes/Claude Code 直接导入)。案例成品传 **GitHub Release** 当证据(3 案例 × 2 视频 + 封面,共 ~17MB)。完整命令与坑(API 建仓库、Release 资产上传、SSH 推送、PTY 交互卡死)见 `references/github-publish.md`。

## 动效参考:逆向分析别人的短视频

拿到参考视频(mp4)时,用 ffmpeg 抽帧 + 帧差异定位运动区域 + ASCII 渲染看布局,还原其动效设计,再套进本 skill 的动效升级库。方法见 `references/design-systems.md` 的「动效逆向分析」。

## Pitfalls(踩过的坑)

1. **ffmpeg 采样 bug**:`-ss <t> -i f.mp4` 不加 `-vframes 1` 会输出 t 之后**所有帧**,统计的是平均值——曾因此误判"换肤动画丢失",实际视频是好的。另:缩略图(如 `scale=108:192`)会双线性淡化小字笔画,亮像素统计可能 0% 误判"内容缺失"——验证在**原分辨率**做,或辅以抽帧 PNG 文件大小对比(有内容 ≈ 180KB+,空/纯色 ≈ 10KB)
1b. **抽帧验证必须避开动画进行中的时间点**:入场动画(如列表 stagger 从 26.2s 开始)期间元素还是 opacity 0,此时抽帧会误判"内容被裁切/缺失"。验证选**动画完成后的时间点**(如 stagger 结束后 +0.5s),或用行分布检测确认内容边界没触到画布边缘(顶/底裁切 = 内容行到达 y<20 或 y>H-20)
1c. **浅色卡片检测盲区**:卡片 `#FAF9F5` 与月牙白底 `#F6F4EF` 色差 <30,按"非底色"行检测会漏掉卡片区域,误判"内容偏上"。验证内容分布时给浅色元素单独阈值,或直接抽 PNG 目视确认
1d. **2x PNG 像素检测必须先取真实尺寸**:headless Chrome 导出的是 2x(如横条 900×383 → PNG 1800×766),若代码按逻辑尺寸(900×383)读 raw 像素,索引错乱,行检测结果全是错的(曾把正常布局误判成"内容偏下")。检测 PNG 前先 `sips -g pixelWidth -g pixelHeight` 或 ffprobe 拿真实宽高
2. **GSAP 连续同属性 tween**:起始值在页面加载时捕获。`to()` 连写两个 backgroundColor tween,第二个会从初始色渐变(闪回)。必须 `fromTo(prevColor, nextColor)`
3. **hard kill**:clip 内 wrap 的 exit fade 必须在 clip 边界 `tl.set(..., 边界时间)` 补硬切,否则 lint 报 `gsap_exit_missing_hard_kill`
4. **wrap 居中(水平+垂直)**:`.scene > div` 必须 `display:flex; flex-direction:column; align-items:center; width:100%`,否则窄子元素靠左。**垂直居中必须再加 `flex:1`**(否则 wrap 高度=内容高度,`justify-content:center` 无效,内容堆在顶部、下半屏空白——竖屏视频最常见的"内容偏上"问题)
5. **竖屏堆叠**:竖屏(9:16/3:4)里多卡片/多节点必须上下堆叠(`flex-direction:column` + 全宽横条),不要横排;横排只在 16:9 横屏里用
6. **字体**:中文必须 `@font-face src:local()` 声明(Songti SC / PingFang SC / Menlo),否则渲染器替换字体;`snapshot` 报 "Fonts FAILED" 是探测限制,不影响 local() 字体渲染
6. **公众号抓取**:需要移动端 UA;解析 `<div id="js_content">`;被风控就让用户贴原文
7. **HyperFrames 项目**:`HYPERFRAMES_SKIP_SKILLS=1` 跳过 GitHub skills 检查(网络慢);`render --quality high` 是交付标准,draft 仅迭代;不同比例 = 不同 composition 文件(尺寸编译期锁定)
8. **对比度**:check 的 contrast 采样会落在颜色过渡帧上导致假警告,静态状态达标即可;浅底深字/深底浅字是换肤类动画的刚需。**图形内白字(印章/圆卡)必须用深色渐变底**:浅天青 `#7FA8B5` 上白字只有 ~2.1:1 不达标,用深青 `#2E5563` 系渐变(#3D6472→#2E5563→#264A54)白字才 3:1(宋瓷印章/「瓷」圆卡/消息气泡均如此)
9. **演示类轮播要覆盖全部选项(含初始态)**:换肤/主题轮播别跳过"初始主题"(如初始就是月白,仍要单独演示一次)——用户会注意到"为什么跳过那个",6 个釉色就要演示 6 次
10. **程序化生成多比例**:`width="N"` 属性正则误伤 `data-width`(root 被缩成 1080),用负向后行断言;且**3:4 必须"宽度保持+高度压缩"而非等比缩放**,否则内容变小观感像裁切——用 `scripts/scale-to-34.py`,见 §4
11. **抽帧验证的采样时间**:动画未完成时抽帧会误判"内容缺失/裁切"——验证必须取**动画完成后的时间点**(每幕入场动画结束后 0.5s+),如 S5 列表 26.2s 入场、28.5s 才是完成态;误在 26.0s 抽帧会看到"列表被裁"的假象
11. **不编造时间线/过程(用户纠正过)**:文案与视频里的迭代叙事必须真实——写过"3 天迭代"被用户否掉("为什么要成三天实际上不是的")。写真实过程:如"16s demo → 10w+ 文章完整成片 → 封面工厂 → 动效升级 → 多平台",不编天数;标签用"第一步/第二步"而非"第 1 天/第 2 天"
12. **本地浏览器正常 ≠ 渲染器正常(CDP 诊断)**:页面在本地 Chrome 打开正常、HyperFrames 渲染输出异常(字号/布局不同)时,别猜——用 headless Chrome CDP 读取实际 computed 值对比:`Chrome --headless=new --remote-debugging-port=9333 <file>` 后台起,node 连 CDP 执行 `Runtime.evaluate` 读 `getComputedStyle(el).fontSize`/`scrollWidth`/`clientWidth`/`parentElement.clientWidth`(脚本: `scripts/fit-diag.mjs`,输出所有 .nowrap 元素的实测值)。实测案例:同一页面本地 fit 后 102px、渲染器实际 ~62px——scrollWidth 字体度量在渲染环境漂移,所以 fit 必须用与字体无关的字符计算法(见 §4)

## 验证清单

- [ ] 文章内容提取完整(钩子/论点/金句/结构)
- [ ] `npm run check` 0 errors
- [ ] 各比例视频渲染成功,ffprobe 尺寸正确
- [ ] 每幕抽帧验证(动画完成后时间点!内容存在 + 动画差异 >0 + 换肤各主题色值)
- [ ] 封面 PNG 尺寸正确(抖音 2160×3840 / 小红书 2160×2880 / 微信 2160×2160,均 2x)
- [ ] **发布前合规扫描:文案+封面+画面文字过一遍敏感词替换表,标注替换记录**
- [ ] **无第三方账号名**(视频 CTA/封面 brand/来源标注均不出现别家公众号名,统一「Nw+ 热文 · 一键成片」)
- [ ] 全部产物归档到 `~/Downloads/Agent/Hermes/<日期>/<主题>/`
- [ ] 交付附成本报表(输入/输出 tokens × 单价 ≈¥0.05)
