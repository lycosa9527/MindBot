# MindBot v0.4 - Intelligent DingTalk Chatbot / 智能钉钉聊天机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.4-orange.svg)](https://github.com/lycosa9527/MindBot/releases)
[![WakaTime](https://wakatime.com/badge/user/60ba0518-3829-457f-ae10-3eff184d5f69/project/707446f2-b1e2-4f2d-8f57-53d016ce3302.svg)](https://wakatime.com/@60ba0518-3829-457f-ae10-3eff184d5f69/projects/707446f2-b1e2-4f2d-8f57-53d016ce3302)

---

## 🎯 Overview / 概述

**English**: MindBot is an intelligent DingTalk chatbot powered by Dify API, designed to provide educational assistance and teaching support. The application uses DingTalk's Stream Mode for real-time message processing and integrates with Dify's knowledge base for intelligent responses.

**中文**: MindBot 是一个基于 Dify API 的智能钉钉聊天机器人，专为教育辅助和教学支持而设计。应用程序使用钉钉的 Stream Mode 进行实时消息处理，并集成 Dify 知识库以提供智能回复。

**Version / 版本**: v0.4  
**Build Date / 构建日期**: 2025-01-30

---

## ✨ Features / 功能特性

### Core Features / 核心功能
- 🚀 **Real-time Message Processing / 实时消息处理**: Instant response to DingTalk messages
- 🤖 **AI-Powered Responses / AI 驱动回复**: Integration with Dify knowledge base
- 📱 **Multi-Platform Support / 多平台支持**: Works with DingTalk mobile and desktop
- 🔒 **Professional Logging / 专业日志**: Clean, colored console output
- 🛡️ **Health Monitoring / 健康监控**: Comprehensive system diagnostics
- 🔄 **Error Recovery / 错误恢复**: Automatic error handling and recovery

### Technical Features / 技术特性
- ⚡ **Async/Await Architecture / 异步架构**: Modern Python async programming
- 🌐 **WebSocket Communication / WebSocket 通信**: Real-time bidirectional messaging
- 🔗 **HTTP API Integration / HTTP API 集成**: RESTful API calls to Dify
- 🔐 **SSL/TLS Security / SSL/TLS 安全**: Secure connections with certificate validation
- 🧵 **Thread Management / 线程管理**: Proper resource management and cleanup
- ⚙️ **Configuration Management / 配置管理**: Environment-based configuration

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置要求
- Python 3.8+ / Python 3.8 或更高版本
- DingTalk Developer Account / 钉钉开发者账户
- Dify API Access / Dify API 访问权限

### Installation / 安装

**1. Clone Repository / 克隆仓库**
```bash
git clone https://github.com/lycosa9527/MindBot.git
cd MindBot
```

**2. Install Dependencies / 安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

**3. Configure Environment / 配置环境**
   ```bash
# Copy environment template
   cp config/env_example.txt .env

# Edit with your credentials
nano .env
```

**4. Run Application / 运行应用程序**
```bash
python run.py
```

---

## ⚙️ Configuration / 配置

### Environment Variables / 环境变量

| Variable / 变量 | Description / 描述 | Required / 必需 | Example / 示例 |
|-----------------|-------------------|-----------------|----------------|
| `DINGTALK_CLIENT_ID` | DingTalk App Client ID / 钉钉应用客户端 ID | Yes / 是 | `dingr6bg0cj9ylmlpuqz` |
| `DINGTALK_CLIENT_SECRET` | DingTalk App Client Secret / 钉钉应用客户端密钥 | Yes / 是 | `h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD` |
| `DINGTALK_ROBOT_CODE` | DingTalk Robot Code / 钉钉机器人编码 | Yes / 是 | `dingr6bg0cj9ylmlpuqz` |
| `DIFY_API_KEY` | Dify API Key / Dify API 密钥 | Yes / 是 | `app-4DGFRXExxcP0xZ5Og3AXfT2N` |
| `DIFY_BASE_URL` | Dify API Base URL / Dify API 基础 URL | Yes / 是 | `http://dify.mindspringedu.com/v1` |
| `QWEN_MODEL` | Qwen Model Name / Qwen 模型名称 | No / 否 | `qwen3-0.6b` |
| `DEBUG_MODE` | Enable Debug Mode / 启用调试模式 | No / 否 | `false` |
| `LOG_LEVEL` | Logging Level / 日志级别 | No / 否 | `INFO` |

### Getting Credentials / 获取凭据

#### DingTalk Setup / 钉钉设置
**English**: Follow the detailed guide in [WIKI.md](docs/WIKI.md#dingtalk-authentication--钉钉认证)

**中文**: 请参考 [WIKI.md](docs/WIKI.md#dingtalk-authentication--钉钉认证) 中的详细指南

#### Dify Setup / Dify 设置
**English**: 
1. Go to [Dify Cloud](https://cloud.dify.ai/) or your self-hosted instance
2. Create a new application
3. Get API Key and Base URL

**中文**：
1. 访问 [Dify Cloud](https://cloud.dify.ai/) 或您的自托管实例
2. 创建新应用
3. 获取 API 密钥和基础 URL

---

## 🎮 Usage / 使用方法

### How to Use / 如何使用

**English**:
1. Add the MindBot robot to your DingTalk group
2. Send messages to the robot
3. The robot will respond with AI-powered educational assistance
4. Supported message types: text messages

**中文**：
1. 将 MindBot 机器人添加到您的钉钉群组
2. 向机器人发送消息
3. 机器人将以 AI 驱动的教育辅助回复
4. 支持的消息类型：文本消息

### Example Message Flow / 示例消息流程

```
User: "你好" / User: "Hello"
↓
DingTalk → MindBot → Dify API
↓
Dify: "你好！我是MindMate，是你的虚拟教研伙伴..." / Dify: "Hello! I'm MindMate, your virtual teaching partner..."
↓
MindBot → DingTalk → User
```

---

## 📁 Project Structure / 项目结构

```
mindbot_poc/
├── src/                    # Main application code / 主应用程序代码
│   ├── main.py            # Application entry point / 应用程序入口点
│   ├── dingtalk_client.py # DingTalk WebSocket client / 钉钉 WebSocket 客户端
│   ├── agent.py           # AI agent logic / AI 代理逻辑
│   ├── dify_client.py     # Dify API integration / Dify API 集成
│   ├── config.py          # Configuration management / 配置管理
│   ├── debug.py           # Logging and diagnostics / 日志和诊断
│   ├── tools.py           # Utility tools / 实用工具
│   └── banner.py          # Application banner / 应用程序横幅
├── config/                 # Configuration files / 配置文件
│   └── env_example.txt    # Environment variables template / 环境变量模板
├── docs/                   # Documentation / 文档
│   └── WIKI.md            # Comprehensive wiki / 详细维基
├── requirements.txt        # Python dependencies / Python 依赖项
├── run.py                 # Application launcher / 应用程序启动器
└── .env                   # Environment variables (user-created) / 环境变量（用户创建）
```

---

## 🔧 Development / 开发

### Key Components / 核心组件

#### `MindBotStreamApp`
**English**: Main application orchestrator that manages application lifecycle, component initialization, message routing, and error handling.

**中文**: 管理应用程序生命周期、组件初始化、消息路由和错误处理的主应用程序编排器。

#### `MindBotDingTalkClient`
**English**: DingTalk integration that handles WebSocket connection management, message reception and parsing, response sending via webhooks, and connection health monitoring.

**中文**: 处理 WebSocket 连接管理、消息接收和解析、通过 webhook 发送响应以及连接健康监控的钉钉集成。

#### `MindBotAgent`
**English**: AI agent that processes user message analysis, Dify API integration, response generation, and context management.

**中文**: 处理用户消息分析、Dify API 集成、响应生成和上下文管理的 AI 代理。

#### `DifyClient`
**English**: Dify API client that manages HTTP requests to Dify, authentication and headers, response parsing, and error handling.

**中文**: 管理对 Dify 的 HTTP 请求、认证和头部、响应解析和错误处理的 Dify API 客户端。

---

## 🛠️ Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. Connection Errors / 连接错误
```
[ERROR] DingTalk authentication failed: 401 Unauthorized
```
**English**: Check your DingTalk credentials in `.env`

**中文**: 检查 `.env` 中的钉钉凭据

#### 2. Dify API Errors / Dify API 错误
```
[ERROR] Dify API returned status 401: Unauthorized
```
**English**: Verify your Dify API key and base URL

**中文**: 验证您的 Dify API 密钥和基础 URL

#### 3. Network Connectivity / 网络连接
```
[ERROR] Connection to api.dingtalk.com failed
```
**English**: Check your internet connection and firewall settings

**中文**: 检查您的互联网连接和防火墙设置

### Diagnostic Commands / 诊断命令

**English**: Run system diagnostics:
**中文**: 运行系统诊断：

   ```bash
   python run.py
   ```

**English**: Check configuration:
**中文**: 检查配置：

```bash
python -c "from src.config import *; print('Config loaded successfully')"
```

---

## 📚 Documentation / 文档

- **[WIKI.md](docs/WIKI.md)**: Comprehensive bilingual documentation with detailed setup instructions
- **DingTalk Authentication**: Step-by-step guide for getting DingTalk credentials
- **Configuration Guide**: Detailed environment variable setup
- **Troubleshooting**: Common issues and solutions

---

## 🤝 Contributing / 贡献

**English**:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**中文**：
1. Fork 仓库
2. 创建功能分支
3. 进行您的更改
4. 如适用，添加测试
5. 提交拉取请求

---

## 📄 License / 许可证

**English**: This project is licensed under the MIT License - see the LICENSE file for details.

**中文**: 本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

---

## 🙏 Acknowledgments / 致谢

- **DingTalk Open Platform** for Stream Mode API / **钉钉开放平台** 提供流模式 API
- **Dify** for AI knowledge base integration / **Dify** 提供 AI 知识库集成
- **Python Community** for excellent async libraries / **Python 社区** 提供优秀的异步库
- **MindSpring Team** for development support / **MindSpring 团队** 提供开发支持

---

**Last Updated / 最后更新**: July 30, 2025 / 2025年7月30日  
**Version / 版本**: v0.3  
**Maintainer / 维护者**: MindSpring Team / MindSpring 团队 