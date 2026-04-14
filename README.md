# cmdmaster-pro / cmdmaster-pro

🎯 **智能运维工具箱** | **Intelligent Operations Toolkit** - 让每个人都能享受 AI 辅助的命令行体验 | Let everyone enjoy AI-assisted command line experience

## ✨ 特性 | Features

- 🤖 **AI 驱动 | AI-Driven**: 支持多种大模型（OpenAI、DeepSeek、火山引擎等） Support for multiple large models (OpenAI, DeepSeek, VolcEngine, etc.)
- 🔧 **命令生成 | Command Generation**: 智能生成 Linux/Unix 命令 Intelligently generate Linux/Unix commands
- 📝 **Git 支持 | Git Support**: 完整的 Git 命令生成 Complete Git command generation
- 🧠 **本地引擎 | Local Engine**: 内置专家知识库，无需网络也可使用 Built-in expert knowledge base, can be used without internet
- 📚 **历史记忆 | History Memory**: 智能补全和历史记录 Smart completion and history
- ⚙️ **灵活配置 | Flexible Configuration**: 支持自定义 AI 模型配置 Support for custom AI model configuration
- 🆓 **完全开源 | Fully Open Source**: 无商业限制，用户自主配置 No commercial restrictions, user-configurable

## 🚀 快速开始 | Quick Start

### 安装 | Installation

```bash
pip install requests
pip install -e .
```

### 配置 AI 模型 | Configure AI Model

```bash
# 配置 OpenAI | Configure OpenAI
cmdmaster-pro --set-ai-url "https://api.openai.com/v1/chat/completions"
cmdmaster-pro --set-ai-token "your-openai-key"
cmdmaster-pro --set-ai-model "gpt-3.5-turbo"

# 查看配置 | View configuration
cmdmaster-pro --ai-config
```

### 使用示例 | Usage Examples

```bash
# Git 命令 | Git commands
cmdmaster-pro "commit提交代码"  # 或 | or: cmdmaster-pro "commit code"
# 输出 | Output: git add . && git commit -m '<提交信息>' | '<commit message>'

# 系统管理 | System management
cmdmaster-pro "查看CPU使用率"  # 或 | or: cmdmaster-pro "check CPU usage"
# 输出 | Output: top -bn1 | grep Cpu

# 复杂任务 | Complex tasks
cmdmaster-pro "创建一个Python爬虫脚本"  # 或 | or: cmdmaster-pro "create a Python web scraper"
# 输出 | Output: AI 生成的复杂命令 | AI-generated complex commands
```

## 📖 详细文档 | Detailed Documentation

### 配置指南 | Configuration Guide

cmdmaster-pro 支持多种大模型 API，你可以通过修改 `ai_config.py` 文件或命令行来配置使用不同的大模型服务。

cmdmaster-pro supports multiple large model APIs. You can configure different large model services by modifying the `ai_config.py` file or using command line.

#### 支持的 AI 服务 | Supported AI Services

| 模型 | Model | URL | 说明 | Description |
|------|-------|-----|------|-------------|
| OpenAI | OpenAI | `https://api.openai.com/v1/chat/completions` | GPT-3.5, GPT-4 等 | GPT-3.5, GPT-4, etc. |
| DeepSeek | DeepSeek | `https://api.deepseek.com/v1/chat/completions` | DeepSeek Chat | DeepSeek Chat |
| 火山引擎 | VolcEngine | `https://ark.cn-beijing.volces.com/api/v3/responses` | Doubao 系列 | Doubao series |
| 自定义 | Custom | 任意兼容 API | 自定义大模型 | Custom large models |

#### 配置方法 | Configuration Methods

##### 方法1: 命令行配置（推荐）| Method 1: Command Line Configuration (Recommended)

```bash
cmdmaster-pro --set-ai-url "your-api-url"
cmdmaster-pro --set-ai-token "your-api-key"
cmdmaster-pro --set-ai-model "your-model-name"
```

##### 方法2: 配置文件 | Method 2: Configuration File

编辑 `ai_config.py` 文件：| Edit the `ai_config.py` file:

```python
AI_URL = "https://api.openai.com/v1/chat/completions"
AI_TOKEN = "your-api-key"
AI_MODEL = "gpt-3.5-turbo"
```

### 常用命令示例 | Common Command Examples

#### Git 操作 | Git Operations
```bash
cmdmaster-pro "commit提交代码"  # 或 | or: "commit code"
cmdmaster-pro "push代码到远程"  # 或 | or: "push code to remote"
cmdmaster-pro "创建新分支"     # 或 | or: "create new branch"
cmdmaster-pro "合并分支"       # 或 | or: "merge branch"
```

#### 系统管理 | System Management
```bash
cmdmaster-pro "查看CPU使用率"  # 或 | or: "check CPU usage"
cmdmaster-pro "查看磁盘空间"  # 或 | or: "check disk space"
cmdmaster-pro "查看端口占用"  # 或 | or: "check port usage"
cmdmaster-pro "查看内存使用"  # 或 | or: "check memory usage"
```

#### 文件操作 | File Operations
```bash
cmdmaster-pro "查找大文件"     # 或 | or: "find large files"
cmdmaster-pro "批量重命名文件" # 或 | or: "batch rename files"
cmdmaster-pro "压缩目录"       # 或 | or: "compress directory"
```

### 功能特点 | Features

#### 双引擎架构 | Dual Engine Architecture
- **本地专家引擎 | Local Expert Engine**: 内置丰富的命令知识库，无需网络即可使用 Built-in rich command knowledge base, can be used without internet
- **云端 AI 引擎 | Cloud AI Engine**: 支持多种大模型，提供更智能的命令生成 Support for multiple large models, providing smarter command generation
- **智能切换 | Smart Switching**: 云端不可用时自动回退到本地引擎 Automatically fallback to local engine when cloud is unavailable

#### 智能补全 | Smart Completion
- **历史记忆 | History Memory**: 自动保存最近 30 条命令 Automatically saves last 30 commands
- **智能推荐 | Smart Recommendations**: 基于历史记录和内置知识库 Based on history and built-in knowledge base
- **实时补全 | Real-time Completion**: 输入时实时显示相关建议 Real-time display of relevant suggestions

#### 安全特性 | Security Features
- **危险命令拦截 | Dangerous Command Interception**: 自动检测和拦截危险操作 Automatically detect and intercept dangerous operations
- **安全提示 | Safety Warnings**: 对谨慎操作提供安全提示 Provide safety warnings for cautious operations
- **用户确认 | User Confirmation**: 对高风险操作要求用户确认 Require user confirmation for high-risk operations

## 🛠️ 高级配置 | Advanced Configuration

### 环境变量配置 | Environment Variable Configuration

对于生产环境，建议使用环境变量存储敏感信息：

For production environments, it's recommended to use environment variables to store sensitive information:

```bash
export CMDMASTER_AI_URL="https://api.openai.com/v1/chat/completions"
export CMDMASTER_AI_TOKEN="your-api-key"
export CMDMASTER_AI_MODEL="gpt-3.5-turbo"
```

### 自定义命令模板 | Custom Command Templates

你可以通过编辑本地引擎来添加自定义命令模板：

You can add custom command templates by editing the local engine:

```python
# 在 cmdmaster/cli.py 中的 command_templates 字典添加 | Add to command_templates dictionary in cmdmaster/cli.py
command_templates = {
    "my-custom-command": "your-custom-shell-command",
    # ... 其他命令 | ... other commands
}
```

## 🔧 故障排除 | Troubleshooting

### 命令无法识别 | Commands Not Recognized
- 尝试更具体的描述 | Try more specific descriptions
- 查看历史记录获取类似命令 | Check history for similar commands
- 使用本地 AI 引擎的建议 | Use suggestions from local AI engine

### AI 服务不可用 | AI Service Unavailable
- 检查网络连接 | Check network connection
- 验证 API Token 是否正确 | Verify API Token is correct
- 系统会自动回退到本地引擎 | System will automatically fallback to local engine

### 安装问题 | Installation Issues
- 确保已安装 requests 依赖 | Ensure requests dependency is installed
- 检查 Python 版本 (需要 Python 3.6+) | Check Python version (requires Python 3.6+)
- 查看详细错误信息 | Check detailed error messages

## 🆓 开源优势 | Open Source Advantages

- ✅ **完全免费 | Completely Free**: 无商业限制 No commercial restrictions
- ✅ **用户自主 | User Controlled**: 自己配置 AI 模型 Configure your own AI models
- ✅ **数据安全 | Data Security**: 无数据收集 No data collection
- ✅ **灵活扩展 | Flexible Extension**: 模块化设计 Modular design
- ✅ **社区支持 | Community Support**: 开放源代码 Open source code

## 📊 项目状态 | Project Status

- **代码质量 | Code Quality**: ✅ Good
- **依赖关系 | Dependencies**: ✅ Resolved
- **安装运行 | Installation**: ✅ Working
- **基础功能 | Basic Functionality**: ✅ Working
- **文档完整 | Documentation**: ✅ Complete
- **测试覆盖 | Testing**: ✅ Passed

**总体状态 | Overall Status**: ✅ PROJECT READY FOR PRODUCTION

## 🤝 贡献 | Contributing

欢迎提交 Issue 和 Pull Request！

Welcome to submit Issues and Pull Requests!

1. Fork 项目 | Fork the project
2. 创建特性分支 | Create feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 | Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 | Push to branch (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request | Open Pull Request

## 📄 许可证 | License

MIT License - 详见 | See details in [LICENSE](LICENSE) 文件 | file

## 🌟 致谢 | Acknowledgments

感谢以下开源项目和技术：

Thanks to the following open source projects and technologies:

- [OpenAI](https://openai.com/) - GPT 模型 | GPT models
- [requests](https://docs.python-requests.org/) - HTTP 库 | HTTP library
- [Python](https://python.org/) - 编程语言 | Programming language

---

**让 AI 成为你的命令行助手 | Let AI be your command line assistant** 🚀

## 📞 联系方式 | Contact

如有问题或建议，请通过以下方式联系我们：

For questions or suggestions, please contact us:

- 提交 Issue | Submit Issue
- 发送邮件 | Send email
- 项目讨论 | Project discussions

---

*此项目完全开源，欢迎使用和贡献 | This project is completely open source, welcome to use and contribute* 🎉