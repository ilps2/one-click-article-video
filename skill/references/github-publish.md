# GitHub 开源发布流程(实测走通)

把本 skill 开源到 GitHub 的完整流程。前提:SSH key 已配置(`ssh -T git@github.com` 返回 "Hi <user>!"),GitHub API token(ghp_...)或网页建仓二选一。

## 仓库结构

```
<repo>/
├── README.md          # 按钮级详细:环境检查→安装→使用, macOS/Windows 分开, 含验证步骤
└── skill/             # 完整 skill 目录(SKILL.md + references/ + scripts/),可被其他 agent 直接导入
```

README 要点(用户对大众 README 的硬性要求):
- 每个步骤写到按钮级别(输入什么命令/看到什么输出),macOS 和 Windows 分开写
- 必须包含验证步骤(如 `node --version` 应显示 v22+)
- 附案例 Release 链接当证据

## 建仓库 + 推送

```bash
# 1. 本地 git init + commit(用户身份)
git init -b main && git add -A
git -c user.name="<user>" -c user.email="<email>" commit -m "..."

# 2. 建仓库(二选一)
#    a) API(token):curl -x http://127.0.0.1:7897 -H "Authorization: Bearer ghp_xxx" \
#       https://api.github.com/user/repos -d '{"name":"<repo>","public":true}'
#    b) 网页:https://github.com/new 建空仓库(不勾 README/gitignore/license)

# 3. SSH 推送(HTTPS 直连常超时,用 git@ 格式)
git remote add origin git@github.com:<user>/<repo>.git
git push -u origin main
```

## Release 上传案例资产

```bash
# 创建 release,拿 id
curl -x http://127.0.0.1:7897 -H "Authorization: Bearer ghp_xxx" \
  https://api.github.com/repos/<user>/<repo>/releases \
  -d '{"tag_name":"v0.1.0","name":"...","body":"...","draft":false}'
# → JSON 里的 "id"

# 逐个上传资产(name 带 URL 编码,二进制直接 --data-binary)
curl -X POST -H "Authorization: Bearer ghp_xxx" -H "Content-Type: application/octet-stream" \
  "https://uploads.github.com/repos/<user>/<repo>/releases/<ID>/assets?name=<file>" \
  --data-binary @"<file>"
# HTTP 201 = 成功;结束后 GET releases/tags/v0.1.0 验证资产列表
```

## 坑

1. **gh auth login PTY 交互会卡死**(后台 pty 下 submit 不生效)——别用,直接 API 建仓 + SSH 推
2. **GitHub token 有保质期**:记忆里的 token 会过期(实测旧 ghp_ 返回 Bad credentials)——拿到新 token 立即更新记忆
3. 旧 token 建仓库失败时,让用户在网页建空仓库(30 秒)是最快兜底,不用反复试 API
4. 资产名用 ASCII(如 songci-916.mp4),中文名在部分客户端会乱
5. 案例文件 ~17MB(9 个资产)无压力;大文件(>100MB)才需要考虑 Git LFS 或仅放链接
