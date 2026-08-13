# RedSkill 发布(小红书 AI 技能市场)

RedSkill = 小红书官方 AI Skill 市场。发布包是标准 SKILL.md 格式的 zip bundle(≤10MB),与 Claude/OpenClaw 生态兼容。

## 平台信息(2026-08 实测)

- 后端 API:`edith.xiaohongshu.com`
  - 搜索:`/api/sns/v1/creator/red_skill/search_published_skills?q=<kw>&limit=5&page=1`
  - 下载 bundle:`/api/sns/v1/creator/red_skill/get_skill_bundle?identifier=<id>`(返回 data.zip_url / sha256 / version)
  - 统一信封 `{code, success, msg, data}`
- 发布入口:公开资料无官方 CLI(npm/GitHub 均未找到);在小红书创作者平台(创作中心 → RedSkill/AI 技能专区),需小红书创作者账号
- SKILL.md frontmatter 兼容:`name` / `description` / `allowed-tools`

## ⚠️ 审核适配(核心教训:发布被拒的元凶)

**发布未通过的首因 = 提到其他平台名/竞品品牌**(自家平台市场里出现竞品平台,审核必拒)。打包前必须泛化替换(实测替换 154 处后通过抽查):

| 原词 | 替换 |
|---|---|
| 抖音 | 短视频平台 |
| 微信视频号 / 视频号 | 视频平台 |
| 公众号 / 微信 | 图文平台 |
| GitHub / github | 开源社区 |
| DeepSeek | 大模型 |
| MiMo(-V2.5-TTS-VoiceClone) | 语音(克隆)模型 |
| HyperFrames | 渲染引擎 |

保留:小红书(自家平台)、自家项目名、纯技术工具名(Chrome/ffmpeg/GSAP)。

**发布页填写的名称/简介同样不能出现平台名**;若再被拒,把平台给的拒绝原因要回来,针对性改。

## 打包

```bash
zip -r <name>.zip SKILL.md references scripts -x "*.DS_Store"
shasum -a 256 <name>.zip          # 每次打包生成新 SHA256,记录到上传说明
unzip -p <name>.zip SKILL.md | grep -c "抖音\|微信\|公众号\|GitHub"  # 必须 = 0
```

## 字数限制(用户实测要求)

- **SKILL.md ≤ 10000 字符**(用户明确要求;发布平台有字符上限)
- 实测教训:完整版 14842 字符超限;极限精简版 838 字符信息不足(流程骨感,无法照着跑);**2125 字符的九章结构版是平衡点**(流程总览/配音预算/配音/布局铁律/封面工厂/审核适配/关键坑/验证清单/成本)
- 压缩策略:保留 frontmatter + 流程骨架 + 关键坑 + 验证 + 成本;删展开描述/示例细节;references/scripts 完整携带(细节都在支持文件里)
- 压缩前先做平台名净化(替换表会顺带缩短文本)

## 版本管理

- 上传说明里记录:内容清单、SHA256、替换记录、平台调研结论
- 每次更新重新打包(新 SHA256),注意替换表要**先长词后短词**('微信视频号' 先于 '微信')
