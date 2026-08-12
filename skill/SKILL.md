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

## 输入 / 输出

| 输入 | 公众号链接(`mp.weixin.qq.com/s/...`)或文章原文文本 |
|---|---|
| 输出 1 | 视频 9:16 = 1080×1920(**抖音 + 微信视频号通用**) |
| 输出 2 | 视频 3:4 = 1080×1440(小红书) |
| 输出 3 | 封面 9:16 = 1080×1920(抖音封面) |
| 输出 4 | 封面 3:4 = 1080×1440(小红书封面) |
| 输出 5 | 封面 1:1 = 1080×1080(微信视频号封面) |
| 输出 6 | 封面横条 = 900×383(公众号头图,2.35:1) |
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

### 3. 设计系统(从文章主题推导)

- **已验证设计系统见 `references/design-systems.md`**(宋瓷天青风 / 深夜烟火风 / 财富琥珀金风,含 6 幕模板与封面钩子案例),同类文章直接套用配色/字体/意象;新文章类型做出新系统后回填该文件
- 色板:从文章主题提取 4-5 色(主色/底色/文字色/点缀色),低饱和意象风
- 字体:标题宋体(`Songti SC`)或黑体(`PingFang SC`),等宽(`Menlo`)用于代码/提示词
- 意象化配图原则(封面工厂核心,详见 `references/cover-factory.md`):
  - 用色块、器物剪影、圆点阵、网格、开片纹理等**意象化元素**,不画人脸/产品等精度敏感对象(观众不会拿去和照片比,避开 diffusion 的雷区也避开 SVG 的短板)
  - 钩子文字是主角:SVG/HTML 文字精确、任意字号、可编辑——这是扩散模型(汉字乱码)进不来的市场
- 模板化:钩子文案 × 意象模板 = 组合产出,单张成本极低

### 4. 视频 composition(HyperFrames)

```bash
mkdir -p ~/Downloads/Agent/Hermes && cd ~/Downloads/Agent/Hermes
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init <name> --example blank --resolution portrait --non-interactive
```

- 竖屏项目(root 1080×1920),**每个平台比例一个 composition 文件**:`index.html`(9:16,抖音+微信通用)+ `compositions/redbook-34.html`(3:4 小红书,1080×1440)
- 3:4 版可从 9:16 版程序化生成:CSS px 值 ×0.75 + 高度 1920→1440。**转换脚本的正则顺序**:先 CSS `Npx` 缩放(1920→1440 例外),再 SVG `width=/height=` 属性(须 `(?<!data-)` 负向断言排除 `data-width/data-height`),最后替换 viewport/data-width——顺序错了会把 data-width 误缩
- 布局铁律:内容**纵向排列**(圆点+文字横排一行、向下箭头串联步骤);每幕内容包一个 wrap(`.scene > div` 必须 `display:flex; flex-direction:column; align-items:center; width:100%`,否则窄子元素靠左)
- 动画:单个 `gsap.timeline({paused:true})` 注册到 `window.__timelines["main"]`;**连续修改同一属性(如换肤轮播的 backgroundColor)必须用 `fromTo` 显式起止色**,否则 tween 起始值在创建时被捕获,播放会闪回初始值
- 场景切换:clip 内 wrap 做 opacity fade,在 clip 边界加 `tl.set(wrap, {opacity:0}, <boundary>)` hard kill(不满足会报 `gsap_exit_missing_hard_kill`)
- 字体:`@font-face { font-family:"PingFang SC"; src:local("PingFang SC"); }` 等声明,否则渲染器 fallback 字体
- 规则:clip 必须 root 直接子元素;不 tween display/visibility;不用 `<br>`(短标题刻意断行除外);根 `data-duration` 编译期锁定(脚本改无效);不 tween clip 元素本身
- 细节参考:hyperframes / hyperframes-core / hyperframes-animation / hyperframes-cli skills

### 5. 封面 HTML(单文件)

- 复制 `references/cover-template.html` 为模板,替换钩子文字、意象元素、配色
- 平台规格:抖音 1080×1920(9:16)、小红书 1080×1440(3:4)、微信视频号 1080×1080(1:1);同一设计系统三份竖版排版
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

交付时给出:文件清单(尺寸/时长)、幕结构表、验证结果。

## Pitfalls(踩过的坑)

1. **ffmpeg 采样 bug**:`-ss <t> -i f.mp4` 不加 `-vframes 1` 会输出 t 之后**所有帧**,统计的是平均值——曾因此误判"换肤动画丢失",实际视频是好的。另:缩略图(如 `scale=108:192`)会双线性淡化小字笔画,亮像素统计可能 0% 误判"内容缺失"——验证在**原分辨率**做,或辅以抽帧 PNG 文件大小对比(有内容 ≈ 180KB+,空/纯色 ≈ 10KB)
2. **GSAP 连续同属性 tween**:起始值在页面加载时捕获。`to()` 连写两个 backgroundColor tween,第二个会从初始色渐变(闪回)。必须 `fromTo(prevColor, nextColor)`
3. **hard kill**:clip 内 wrap 的 exit fade 必须在 clip 边界 `tl.set(..., 边界时间)` 补硬切,否则 lint 报 `gsap_exit_missing_hard_kill`
4. **wrap 居中(水平+垂直)**:`.scene > div` 必须 `display:flex; flex-direction:column; align-items:center; width:100%`,否则窄子元素靠左。**垂直居中必须再加 `flex:1`**(否则 wrap 高度=内容高度,`justify-content:center` 无效,内容堆在顶部、下半屏空白——竖屏视频最常见的"内容偏上"问题)
5. **竖屏堆叠**:竖屏(9:16/3:4)里多卡片/多节点必须上下堆叠(`flex-direction:column` + 全宽横条),不要横排;横排只在 16:9 横屏里用
6. **字体**:中文必须 `@font-face src:local()` 声明(Songti SC / PingFang SC / Menlo),否则渲染器替换字体;`snapshot` 报 "Fonts FAILED" 是探测限制,不影响 local() 字体渲染
6. **公众号抓取**:需要移动端 UA;解析 `<div id="js_content">`;被风控就让用户贴原文
7. **HyperFrames 项目**:`HYPERFRAMES_SKIP_SKILLS=1` 跳过 GitHub skills 检查(网络慢);`render --quality high` 是交付标准,draft 仅迭代;不同比例 = 不同 composition 文件(尺寸编译期锁定)
8. **对比度**:check 的 contrast 采样会落在颜色过渡帧上导致假警告,静态状态达标即可;浅底深字/深底浅字是换肤类动画的刚需
9. **演示类轮播要覆盖全部选项(含初始态)**:换肤/主题轮播别跳过"初始主题"(如初始就是月白,仍要单独演示一次)——用户会注意到"为什么跳过那个",6 个釉色就要演示 6 次
10. **程序化生成多比例**:`width="N"` 属性正则误伤 `data-width`(root 被缩成 1080),用负向后行断言,见 §4

## 验证清单

- [ ] 文章内容提取完整(钩子/论点/金句/结构)
- [ ] `npm run check` 0 errors
- [ ] 各比例视频渲染成功,ffprobe 尺寸正确
- [ ] 每幕抽帧验证(内容存在 + 动画差异 >0 + 换肤各主题色值)
- [ ] 封面 PNG 尺寸正确(抖音 2160×3840 / 小红书 2160×2880 / 微信 2160×2160,均 2x)
- [ ] 全部产物归档到 `~/Downloads/Agent/Hermes/<日期>/<主题>/`
