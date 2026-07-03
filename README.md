# Codex 重置次数查询 Skill

这是一个 Codex Skill，用于使用本机 Codex 凭证查询 ChatGPT/Codex 的 rate-limit reset credits，并以中文表格展示可用重置次数、状态、发放时间和到期时间。

## 功能

- 读取本机 `~/.codex/auth.json` 中的 `tokens.access_token`。
- 请求 `https://chatgpt.com/backend-api/wham/rate-limit-reset-credits`。
- 只输出允许展示的汇总信息，不输出 token、cookie、Authorization header 或完整唯一 ID。
- 将接口中的 UTC 时间转换为本机本地时区。
- 使用中文 Markdown 表格输出，不展示标题列。
- 当接口返回 HTTP 401 时，提示凭证失效或 Authorization header 无效/缺失。

## 安装

### 方式一：直接 clone 到 Codex skills 目录

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/zhuimengFIRE/rate-limit-reset-credits.git ~/.codex/skills/rate-limit-reset-credits
```

如果已经安装过，更新即可：

```bash
cd ~/.codex/skills/rate-limit-reset-credits
git pull
```

### 方式二：先 clone，再运行安装脚本

```bash
git clone https://github.com/zhuimengFIRE/rate-limit-reset-credits.git
cd rate-limit-reset-credits
bash install.sh
```

安装脚本会复制当前仓库内容到：

```text
~/.codex/skills/rate-limit-reset-credits
```

## 使用

在 Codex 中直接说：

```text
重置次数查询
```

也可以使用类似表达：

```text
查询重置次数
重置次数到期时间
查一下 reset credits
rate-limit reset credits
```

Skill 会运行：

```bash
python3 scripts/check_rate_limit_reset_credits.py
```

也可以手动运行：

```bash
cd ~/.codex/skills/rate-limit-reset-credits
python3 scripts/check_rate_limit_reset_credits.py
```

## 输出示例

```text
可用重置次数：3

重置次数明细：

| 序号 | 状态 | 发放时间 | 到期时间 |
| --- | --- | --- | --- |
| 1 | 可用 | 2026-06-18 08:33:20 CST+0800 | 2026-07-18 08:33:20 CST+0800 |
| 2 | 可用 | 2026-06-27 07:40:34 CST+0800 | 2026-07-27 07:40:34 CST+0800 |
| 3 | 可用 | 2026-07-02 03:53:07 CST+0800 | 2026-08-01 03:53:07 CST+0800 |
```

## 安全说明

此 Skill 必须遵守以下限制：

- 不打印 `access_token`、`refresh_token`、cookie 或 `Authorization` header。
- 不打印原始 `~/.codex/auth.json` 内容。
- 不打印原始接口响应。
- 只展示：
  - 可用重置次数 `available_count`
  - 每条 credit 的状态 `status`
  - 发放时间 `granted_at`
  - 到期时间 `expires_at`

## 前置条件

- 已在本机登录 Codex，并存在 `~/.codex/auth.json`。
- `~/.codex/auth.json` 中包含有效的 `tokens.access_token`。
- 本机可访问 `https://chatgpt.com`。
- Python 3.10 或更高版本。

## 仓库结构

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── check_rate_limit_reset_credits.py
├── install.sh
└── .gitignore
```

## 401 错误

如果输出 HTTP 401，通常表示：

- 本机 Codex 凭证已失效；或
- 请求没有携带有效的 `Authorization` header。

重新登录 Codex 后再运行查询。