# cmdmaster-pro

智能运维工具箱 — 用自然语言生成 Shell 命令的 CLI 工具。

Intelligent Operations Toolkit — a CLI that turns natural language into shell commands.

[![Tests](https://github.com/MMCISAGOODMAN/cmdmaster-pro/actions/workflows/test.yml/badge.svg)](https://github.com/MMCISAGOODMAN/cmdmaster-pro/actions/workflows/test.yml)

## 特性

- **双引擎**：本地专家引擎 + 云端 AI，自动降级
- **中英双语**：本地引擎支持中文关键词（如「查看CPU使用率」）
- **平台适配**：macOS / Linux 命令自动区分
- **安全机制**：危险命令拦截、风险分级、执行前确认
- **开箱即用**：历史记忆、收藏夹、用户模板、结果缓存
- **脚本友好**：`--json` 输出，便于集成到自动化流程

## 安装

```bash
git clone https://github.com/MMCISAGOODMAN/cmdmaster-pro.git
cd cmdmaster-pro
pip install -e .
```

要求 Python 3.6+，依赖仅 `requests`。

## 快速上手

```bash
# 生成命令
cmdmaster-pro "查看磁盘空间"
cmdmaster-pro "commit提交代码"

# 交互模式
cmdmaster-pro -i

# 生成并执行（需确认）
cmdmaster-pro -x "查看CPU使用率"

# 离线模式（不调用 AI）
cmdmaster-pro -L "push代码到远程"

# JSON 输出（脚本集成）
cmdmaster-pro --json "查看端口占用"

# 解释已有命令
cmdmaster-pro -d "git reset --hard"
```

## 配置 AI

优先级：**环境变量** > `~/.config/cmdmaster-pro/ai_config.py`

```bash
# 命令行配置
cmdmaster-pro --set-ai-url "https://api.openai.com/v1/chat/completions"
cmdmaster-pro --set-ai-token "your-api-key"
cmdmaster-pro --set-ai-model "gpt-3.5-turbo"
cmdmaster-pro --ai-config
```

```bash
# 环境变量（推荐用于生产环境）
export CMDMASTER_AI_URL="https://api.openai.com/v1/chat/completions"
export CMDMASTER_AI_TOKEN="your-api-key"
export CMDMASTER_AI_MODEL="gpt-3.5-turbo"
```

```bash
# 配置文件
mkdir -p ~/.config/cmdmaster-pro
cp examples/ai_config.example.py ~/.config/cmdmaster-pro/ai_config.py
# 编辑 ai_config.py 填入你的 API 信息
```

### 支持的 AI 服务

| 服务 | API URL |
|------|---------|
| OpenAI | `https://api.openai.com/v1/chat/completions` |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` |
| 火山引擎 | `https://ark.cn-beijing.volces.com/api/v3/responses` |
| 自定义 | 任意 OpenAI 兼容 API |

## CLI 参考

| 选项 | 说明 |
|------|------|
| `-i, --interactive` | 交互模式 |
| `-L, --local-only` | 仅使用本地引擎 |
| `-x, --run` | 生成后执行命令 |
| `-c, --copy` | 复制命令到剪贴板 |
| `-d, --decode` | 解释 shell 命令含义 |
| `-e, --explain` | 显示生成说明 |
| `-y, --yes` | 跳过危险操作确认 |
| `-n, --dry-run` | 只生成，不直接执行输入的命令 |
| `--json` | JSON 格式输出 |
| `--no-color` | 禁用终端颜色 |
| `--no-cache` | 跳过结果缓存 |
| `--search QUERY` | 搜索历史 |
| `--suggest [PREFIX]` | 显示智能建议 |
| `--favorite list/add/remove` | 管理收藏夹 |
| `--template list/add/remove` | 管理用户模板 |
| `--export-history FILE` | 导出历史 |
| `--import-history FILE` | 导入历史 |
| `--clear-history` | 清空历史 |
| `--clear-cache` | 清空缓存 |
| `--completion bash/zsh` | 输出 Shell 补全脚本 |
| `--stdin` | 从标准输入读取查询 |
| `-V, --version` | 显示版本 |

### 交互模式内置命令

```
:help              显示帮助
:history           查看历史
:search <text>     搜索历史
:suggest [prefix]  显示建议（!1..!9 快速选择）
:favorite add/list/rm
:template list
:local on|off      切换离线模式
:clear-cache       清除缓存
exit               退出
```

### Shell 补全

```bash
# Bash
eval "$(cmdmaster-pro --completion bash)"

# Zsh
eval "$(cmdmaster-pro --completion zsh)"
```

## 用户模板

将常用关键词映射到固定命令，保存在 `~/.config/cmdmaster-pro/templates.json`。

```bash
# CLI 添加
cmdmaster-pro --template add "deploy prod" "kubectl rollout restart app -n prod"

# 或复制示例文件
cp examples/templates.example.json ~/.config/cmdmaster-pro/templates.json
```

## 数据文件

| 文件 | 用途 |
|------|------|
| `~/.cmdmaster-pro.history` | 查询历史（最近 30 条） |
| `~/.cmdmaster-pro.favorites` | 收藏夹 |
| `~/.config/cmdmaster-pro/ai_config.py` | AI 配置 |
| `~/.config/cmdmaster-pro/templates.json` | 用户模板 |
| `~/.config/cmdmaster-pro/cache.json` | 结果缓存（24 小时 TTL） |

## 项目结构

```
cmdmaster-pro/
├── cmdmaster/           # 核心包
│   ├── cli.py           # CLI 入口
│   ├── engines.py       # 本地引擎
│   ├── api.py           # 云端 AI
│   ├── config.py        # 配置管理
│   ├── safety.py        # 安全检测
│   ├── history.py       # 历史与建议
│   ├── favorites.py     # 收藏夹
│   ├── templates.py     # 用户模板
│   ├── cache.py         # 结果缓存
│   ├── explain.py       # 命令解释
│   └── ...
├── tests/               # 单元测试
├── examples/            # 配置示例
├── pyproject.toml
└── LICENSE
```

## 开发与测试

```bash
pip install -e .
python -m unittest discover -s tests -v
```

CI 在 push/PR 时于 Ubuntu 和 macOS 上运行测试（Python 3.9 / 3.12）。

## 架构

```
用户输入
  ├─ 用户模板匹配
  ├─ 本地专家引擎（关键词规则）
  ├─ 结果缓存
  ├─ 云端 AI（含平台/目录上下文）
  └─ 本地 AI 降级引擎
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 命令不准确 | 使用更具体的描述，或添加用户模板 |
| AI 不可用 | 检查 Token 和网络；自动降级到本地引擎 |
| 无 AI 配置 | 使用 `-L` 离线模式，或配置 API Token |
| 安装失败 | 确认 Python 3.6+，运行 `pip install -e .` |

## 贡献

欢迎提交 Issue 和 Pull Request。

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/my-feature`
3. 提交更改并确保测试通过
4. 发起 Pull Request

## 许可证

[MIT License](LICENSE)
