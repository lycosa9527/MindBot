# MindBot Wiki / MindBot 维基

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.4-orange.svg)](https://github.com/lycosa9527/MindBot/releases)
[![WakaTime](https://wakatime.com/badge/user/60ba0518-3829-457f-ae10-3eff184d5f69/project/707446f2-b1e2-4f2d-8f57-53d016ce3302.svg)](https://wakatime.com/@60ba0518-3829-457f-ae10-3eff184d5f69/projects/707446f2-b1e2-4f2d-8f57-53d016ce3302)

## 📋 Table of Contents / 目录

- [Overview / 概述](#overview--概述)
- [Features / 功能特性](#features--功能特性)
- [Architecture / 架构](#architecture--架构)
- [Installation / 安装](#installation--安装)
- [DingTalk Authentication / 钉钉认证](#dingtalk-authentication--钉钉认证)
- [Configuration / 配置](#configuration--配置)
- [Usage / 使用方法](#usage--使用方法)
- [API Documentation / API文档](#api-documentation--api文档)
- [Troubleshooting / 故障排除](#troubleshooting--故障排除)
- [Development / 开发](#development--开发)
- [Changelog / 更新日志](#changelog--更新日志)

---

## 🎯 Overview / 概述

**English**: MindBot is an intelligent DingTalk chatbot powered by Dify API, designed to provide educational assistance and teaching support. The application uses DingTalk's Stream Mode for real-time message processing and integrates with Dify's knowledge base for intelligent responses.

**中文**: MindBot 是一个基于 Dify API 的智能钉钉聊天机器人，专为教育辅助和教学支持而设计。应用程序使用钉钉的 Stream Mode 进行实时消息处理，并集成 Dify 知识库以提供智能回复。

### Key Components / 核心组件

- **DingTalk Stream Integration / 钉钉流模式集成**: Real-time WebSocket communication / 实时 WebSocket 通信
- **Dify API Integration / Dify API 集成**: AI-powered knowledge base responses / AI 驱动的知识库回复
- **Professional Logging / 专业日志**: Colored console output with structured logging / 带颜色的结构化控制台输出
- **Comprehensive Diagnostics / 全面诊断**: Network and API connectivity testing / 网络和 API 连接测试
- **Error Handling / 错误处理**: Robust error management and graceful degradation / 强大的错误管理和优雅降级

---

## ✨ Features / 功能特性

### Core Features / 核心功能
- ✅ **Real-time Message Processing / 实时消息处理**: Instant response to DingTalk messages / 对钉钉消息的即时响应
- ✅ **AI-Powered Responses / AI 驱动回复**: Integration with Dify knowledge base / 集成 Dify 知识库
- ✅ **Multi-Platform Support / 多平台支持**: Works with DingTalk mobile and desktop / 支持钉钉移动端和桌面端
- ✅ **Professional Logging / 专业日志**: Clean, colored console output / 清洁、带颜色的控制台输出
- ✅ **Health Monitoring / 健康监控**: Comprehensive system diagnostics / 全面的系统诊断
- ✅ **Error Recovery / 错误恢复**: Automatic error handling and recovery / 自动错误处理和恢复

### Technical Features / 技术特性
- ✅ **Async/Await Architecture / 异步架构**: Modern Python async programming / 现代 Python 异步编程
- ✅ **WebSocket Communication / WebSocket 通信**: Real-time bidirectional messaging / 实时双向消息传递
- ✅ **HTTP API Integration / HTTP API 集成**: RESTful API calls to Dify / 对 Dify 的 RESTful API 调用
- ✅ **SSL/TLS Security / SSL/TLS 安全**: Secure connections with certificate validation / 带证书验证的安全连接
- ✅ **Thread Management / 线程管理**: Proper resource management and cleanup / 适当的资源管理和清理
- ✅ **Configuration Management / 配置管理**: Environment-based configuration / 基于环境的配置

---

## 🏗️ Architecture / 架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DingTalk      │    │   MindBot       │    │   Dify API      │
│   Stream Mode   │◄──►│   Application   │◄──►│   Knowledge     │
│   WebSocket     │    │   (Python)      │    │   Base          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Structure / 组件结构

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
│   ├── README.md          # Project documentation / 项目文档
│   └── WIKI.md            # This wiki file / 本维基文件
├── requirements.txt        # Python dependencies / Python 依赖项
├── run.py                 # Application launcher / 应用程序启动器
└── .env                   # Environment variables (user-created) / 环境变量（用户创建）
```

---

## 🚀 Installation / 安装

### Prerequisites / 前置要求

- Python 3.8 or higher / Python 3.8 或更高版本
- DingTalk Developer Account / 钉钉开发者账户
- Dify API Access / Dify API 访问权限
- Network connectivity to DingTalk and Dify APIs / 连接到钉钉和 Dify API 的网络

### Step 1: Clone the Repository / 步骤 1：克隆仓库

```bash
git clone <repository-url>
cd mindbot_poc
```

### Step 2: Install Dependencies / 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment / 步骤 3：配置环境

1. Copy the example environment file / 复制示例环境文件:
   ```bash
   cp config/env_example.txt .env
   ```

2. Edit `.env` with your actual credentials / 使用您的实际凭据编辑 `.env`:
   ```env
   # DingTalk Configuration / 钉钉配置
   DINGTALK_CLIENT_ID=your_actual_client_id
   DINGTALK_CLIENT_SECRET=your_actual_client_secret
   DINGTALK_ROBOT_CODE=your_actual_robot_code
   DINGTALK_ROBOT_NAME=MindBot_v0.3

   # Dify Configuration / Dify 配置
   DIFY_API_KEY=your_actual_dify_api_key
   DIFY_BASE_URL=https://your-dify-instance.com/v1

   # Qwen Configuration (Optional) / Qwen 配置（可选）
   QWEN_API_KEY=your_actual_qwen_api_key
   QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_MODEL=qwen3-0.6b

   # Optional Configuration / 可选配置
   DEBUG_MODE=false
   LOG_LEVEL=INFO
   ```

---

## 🔐 DingTalk Authentication / 钉钉认证

### How to Get DingTalk Authentication Information / 如何获取钉钉认证信息

#### Step 1: Create DingTalk Developer Account / 步骤 1：创建钉钉开发者账户

**English**: 
1. Go to [DingTalk Open Platform](https://open.dingtalk.com/)
2. Sign in with your DingTalk account
3. Complete developer verification if required

**中文**：
1. 访问 [钉钉开放平台](https://open.dingtalk.com/)
2. 使用您的钉钉账户登录
3. 如需要，完成开发者验证

#### Step 2: Create Application / 步骤 2：创建应用

**English**:
1. In the DingTalk Open Platform, click "Create Application" / "创建应用"
2. Select "Internal Application" / "企业内部应用"
3. Fill in the application information:
   - Application Name / 应用名称: `MindBot`
   - Application Description / 应用描述: `AI-powered educational assistant`
   - Application Logo / 应用图标: Upload your logo / 上传您的图标

**中文**：
1. 在钉钉开放平台中，点击"创建应用"
2. 选择"企业内部应用"
3. 填写应用信息：
   - 应用名称：`MindBot`
   - 应用描述：`AI 驱动的教育助手`
   - 应用图标：上传您的图标

#### Step 3: Configure Robot Settings / 步骤 3：配置机器人设置

**English**:
1. In your application dashboard, go to "Robot" / "机器人" section
2. Click "Add Robot" / "添加机器人"
3. Configure robot settings:
   - Robot Name / 机器人名称: `MindBot`
   - Robot Avatar / 机器人头像: Upload robot avatar / 上传机器人头像
   - Robot Description / 机器人描述: `AI-powered educational assistant`
   - Robot Keywords / 机器人关键词: `教育`, `教学`, `学习`

**中文**：
1. 在您的应用仪表板中，进入"机器人"部分
2. 点击"添加机器人"
3. 配置机器人设置：
   - 机器人名称：`MindBot`
   - 机器人头像：上传机器人头像
   - 机器人描述：`AI 驱动的教育助手`
   - 机器人关键词：`教育`, `教学`, `学习`

#### Step 4: Get Authentication Credentials / 步骤 4：获取认证凭据

**English**:
1. In your application dashboard, go to "Basic Information" / "基础信息"
2. Copy the following information:
   - **Client ID / 客户端 ID**: `dingr6bg0cj9ylmlpuqz` (example)
   - **Client Secret / 客户端密钥**: `h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD` (example)
3. In the "Robot" section, copy:
   - **Robot Code / 机器人编码**: `dingr6bg0cj9ylmlpuqz` (example)

**中文**：
1. 在您的应用仪表板中，进入"基础信息"
2. 复制以下信息：
   - **客户端 ID**：`dingr6bg0cj9ylmlpuqz`（示例）
   - **客户端密钥**：`h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD`（示例）
3. 在"机器人"部分，复制：
   - **机器人编码**：`dingr6bg0cj9ylmlpuqz`（示例）

#### Step 5: Configure Permissions / 步骤 5：配置权限

**English**:
1. Go to "Permissions" / "权限管理" section
2. Add the following permissions:
   - `im:robot:send` - Send robot messages / 发送机器人消息
   - `im:robot:receive` - Receive robot messages / 接收机器人消息
   - `im:robot:read` - Read robot messages / 读取机器人消息

**中文**：
1. 进入"权限管理"部分
2. 添加以下权限：
   - `im:robot:send` - 发送机器人消息
   - `im:robot:receive` - 接收机器人消息
   - `im:robot:read` - 读取机器人消息

#### Step 6: Publish Application / 步骤 6：发布应用

**English**:
1. Complete all configuration steps
2. Click "Submit for Review" / "提交审核"
3. Wait for approval (usually 1-2 business days)
4. Once approved, the application will be available for use

**中文**：
1. 完成所有配置步骤
2. 点击"提交审核"
3. 等待审核通过（通常 1-2 个工作日）
4. 审核通过后，应用即可使用

---

## ⚙️ Configuration / 配置

### Environment Variables / 环境变量

| Variable / 变量 | Description / 描述 | Required / 必需 | Example / 示例 |
|-----------------|-------------------|-----------------|----------------|
| `DINGTALK_CLIENT_ID` | DingTalk App Client ID / 钉钉应用客户端 ID | Yes / 是 | `dingr6bg0cj9ylmlpuqz` |
| `DINGTALK_CLIENT_SECRET` | DingTalk App Client Secret / 钉钉应用客户端密钥 | Yes / 是 | `h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD` |
| `DINGTALK_ROBOT_CODE` | DingTalk Robot Code / 钉钉机器人编码 | Yes / 是 | `dingr6bg0cj9ylmlpuqz` |
| `DINGTALK_ROBOT_NAME` | Bot Display Name / 机器人显示名称 | No / 否 | `MindBot_v0.3` |
| `DIFY_API_KEY` | Dify API Key / Dify API 密钥 | Yes / 是 | `app-4DGFRXExxcP0xZ5Og3AXfT2N` |
| `DIFY_BASE_URL` | Dify API Base URL / Dify API 基础 URL | Yes / 是 | `http://dify.mindspringedu.com/v1` |
| `QWEN_API_KEY` | Qwen API Key / Qwen API 密钥 | No / 否 | `sk-xxx` |
| `QWEN_BASE_URL` | Qwen API Base URL / Qwen API 基础 URL | No / 否 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `QWEN_MODEL` | Qwen Model Name / Qwen 模型名称 | No / 否 | `qwen3-0.6b` |
| `DEBUG_MODE` | Enable Debug Mode / 启用调试模式 | No / 否 | `false` |
| `LOG_LEVEL` | Logging Level / 日志级别 | No / 否 | `INFO` |

### Getting Credentials / 获取凭据

#### DingTalk Setup / 钉钉设置
**English**: Follow the authentication steps above to get your DingTalk credentials.

**中文**：按照上述认证步骤获取您的钉钉凭据。

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

### Starting the Application / 启动应用程序

```bash
python run.py
```

### Application Flow / 应用程序流程

**English**:
1. **Initialization**: System diagnostics and component setup
2. **Connection**: Establish WebSocket connection to DingTalk
3. **Message Reception**: Receive messages from DingTalk users
4. **Processing**: Send messages to Dify API for AI processing
5. **Response**: Send AI-generated responses back to users
6. **Monitoring**: Continuous health monitoring and error handling

**中文**：
1. **初始化**：系统诊断和组件设置
2. **连接**：建立与钉钉的 WebSocket 连接
3. **消息接收**：接收来自钉钉用户的消息
4. **处理**：将消息发送到 Dify API 进行 AI 处理
5. **回复**：将 AI 生成的回复发送回用户
6. **监控**：持续的健康监控和错误处理

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

### How to Use the Bot / 如何使用机器人

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

---

## 📚 API Documentation / API文档

### DingTalk Stream Mode / 钉钉流模式

**English**: The application uses DingTalk's Stream Mode for real-time communication:

**中文**：应用程序使用钉钉的流模式进行实时通信：

- **WebSocket Endpoint / WebSocket 端点**: `wss://wss-open-connection.dingtalk.com:443/connect`
- **Message Format / 消息格式**: JSON with text content and metadata / 带文本内容和元数据的 JSON
- **Response Method / 响应方法**: Session webhook HTTP POST / 会话 webhook HTTP POST

### Dify API Integration / Dify API 集成

- **Endpoint / 端点**: `{DIFY_BASE_URL}/chat-messages`
- **Method / 方法**: POST
- **Authentication / 认证**: Bearer token
- **Response Format / 响应格式**: JSON with AI-generated text / 带 AI 生成文本的 JSON

### Message Processing Pipeline / 消息处理管道

**English**:
1. **Reception**: WebSocket message from DingTalk
2. **Parsing**: Extract text content and metadata
3. **Context**: Build user context and conversation ID
4. **AI Processing**: Send to Dify API with context
5. **Response**: Format and send back via webhook

**中文**：
1. **接收**：来自钉钉的 WebSocket 消息
2. **解析**：提取文本内容和元数据
3. **上下文**：构建用户上下文和对话 ID
4. **AI 处理**：将上下文发送到 Dify API
5. **响应**：格式化并通过 webhook 发送回

---

## 🔧 Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. Connection Errors / 连接错误
```
[ERROR] DingTalk authentication failed: 401 Unauthorized
```
**English**: Check your DingTalk credentials in `.env`

**中文**：检查 `.env` 中的钉钉凭据

#### 2. Dify API Errors / Dify API 错误
```
[ERROR] Dify API returned status 401: Unauthorized
```
**English**: Verify your Dify API key and base URL

**中文**：验证您的 Dify API 密钥和基础 URL

#### 3. Network Connectivity / 网络连接
```
[ERROR] Connection to api.dingtalk.com failed
```
**English**: Check your internet connection and firewall settings

**中文**：检查您的互联网连接和防火墙设置

#### 4. Message Processing Errors / 消息处理错误
```
[ERROR] object NoneType can't be used in 'await' expression
```
**English**: This has been fixed in v0.3. Update to latest version.

**中文**：这已在 v0.3 中修复。更新到最新版本。

### Diagnostic Commands / 诊断命令

**English**: Run system diagnostics:
**中文**：运行系统诊断：

```bash
python run.py
```

**English**: Check configuration:
**中文**：检查配置：

```bash
python -c "from src.config import *; print('Config loaded successfully')"
```

### Log Levels / 日志级别

- **DEBUG**: Detailed debugging information / 详细的调试信息
- **INFO**: General application information / 一般应用程序信息
- **WARNING**: Warning messages / 警告消息
- **ERROR**: Error messages / 错误消息

---

## 🛠️ Development / 开发

### Project Structure / 项目结构

```
src/
├── main.py              # Application entry point and orchestration / 应用程序入口点和编排
├── dingtalk_client.py   # DingTalk WebSocket client and message handling / 钉钉 WebSocket 客户端和消息处理
├── agent.py             # AI agent logic and message processing / AI 代理逻辑和消息处理
├── dify_client.py       # Dify API client and integration / Dify API 客户端和集成
├── config.py            # Configuration management and validation / 配置管理和验证
├── debug.py             # Logging setup and diagnostic utilities / 日志设置和诊断工具
├── tools.py             # Utility tools and helper functions / 实用工具和辅助函数
└── banner.py            # Application banner and startup display / 应用程序横幅和启动显示
```

### Key Classes / 关键类

#### `MindBotStreamApp`
**English**: Main application orchestrator that manages:
**中文**：管理以下内容的主应用程序编排器：

- Application lifecycle / 应用程序生命周期
- Component initialization / 组件初始化
- Message routing / 消息路由
- Error handling / 错误处理

#### `MindBotDingTalkClient`
**English**: DingTalk integration that handles:
**中文**：处理以下内容的钉钉集成：

- WebSocket connection management / WebSocket 连接管理
- Message reception and parsing / 消息接收和解析
- Response sending via webhooks / 通过 webhook 发送响应
- Connection health monitoring / 连接健康监控

#### `MindBotAgent`
**English**: AI agent that processes:
**中文**：处理以下内容的 AI 代理：

- User message analysis / 用户消息分析
- Dify API integration / Dify API 集成
- Response generation / 响应生成
- Context management / 上下文管理

#### `DifyClient`
**English**: Dify API client that manages:
**中文**：管理以下内容的 Dify API 客户端：

- HTTP requests to Dify / 对 Dify 的 HTTP 请求
- Authentication and headers / 认证和头部
- Response parsing / 响应解析
- Error handling / 错误处理

### Development Setup / 开发设置

**English**:
1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd mindbot_poc
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp config/env_example.txt .env
   # Edit .env with your credentials
   ```

3. **Run Development Mode**:
   ```bash
   python run.py
   ```

**中文**：
1. **克隆和设置**：
   ```bash
   git clone <repository-url>
   cd mindbot_poc
   pip install -r requirements.txt
   ```

2. **配置环境**：
   ```bash
   cp config/env_example.txt .env
   # 使用您的凭据编辑 .env
   ```

3. **运行开发模式**：
   ```bash
   python run.py
   ```

### Testing / 测试

**English**: The application includes comprehensive diagnostics:
**中文**：应用程序包括全面的诊断：

- Network connectivity tests / 网络连接测试
- API authentication tests / API 认证测试
- Component health checks / 组件健康检查
- Error simulation and recovery / 错误模拟和恢复

### Code Style / 代码风格

- **Python**: PEP 8 compliance / PEP 8 合规
- **Async/Await**: Modern async programming patterns / 现代异步编程模式
- **Error Handling**: Comprehensive exception management / 全面的异常管理
- **Logging**: Structured logging with colors / 带颜色的结构化日志
- **Documentation**: Comprehensive docstrings and comments / 全面的文档字符串和注释

---

## 📝 Changelog / 更新日志

### v0.4 (2025-01-30)
- ✅ **Fixed critical DingTalk SDK duplication issues** - Implemented proper message acknowledgments to prevent server-side retries / 修复关键的钉钉 SDK 重复问题 - 实现正确的消息确认以防止服务器端重试
- ✅ **Refactored DingTalk client architecture** - Migrated from custom handler to official `ChatbotHandler` for proper SDK integration / 重构钉钉客户端架构 - 从自定义处理器迁移到官方 `ChatbotHandler` 以实现正确的 SDK 集成
- ✅ **Enhanced message deduplication system** - Added hash-based deduplication with TTL and thread-safe operations / 增强消息去重系统 - 添加基于哈希的去重，支持 TTL 和线程安全操作
- ✅ **Improved console logging consolidation** - Reduced redundant logs and optimized message flow visibility / 改进控制台日志整合 - 减少冗余日志并优化消息流可见性
- ✅ **Updated AI model configuration** - Changed Qwen model from `qwen-turbo-latest` to `qwen3-0.6b` for better performance / 更新 AI 模型配置 - 将 Qwen 模型从 `qwen-turbo-latest` 更改为 `qwen3-0.6b` 以获得更好的性能
- ✅ **Enhanced error handling and recovery** - Better exception management and graceful degradation / 增强错误处理和恢复 - 更好的异常管理和优雅降级
- ✅ **Professional documentation updates** - Bilingual README and comprehensive changelog / 专业文档更新 - 双语 README 和全面的更新日志
- ✅ **Git workflow improvements** - Added `.gitattributes` for cross-platform line ending standardization / Git 工作流改进 - 添加 `.gitattributes` 以实现跨平台行尾标准化

### v0.3 (2025-07-30)
- ✅ **Enhanced console logging** with level-only coloring for professional appearance / 增强控制台日志，仅对级别进行着色以获得专业外观
- ✅ **Fixed critical logic errors** in logging system propagation / 修复日志系统传播中的关键逻辑错误
- ✅ **Improved performance** with optimized timestamp handling / 通过优化的时间戳处理提高性能
- ✅ **Enhanced error handling** for invalid log records and component names / 增强对无效日志记录和组件名称的错误处理
- ✅ **Fixed network timeout configuration** for better reliability / 修复网络超时配置以提高可靠性
- ✅ **Improved code quality** with better validation and safety checks / 通过更好的验证和安全检查提高代码质量
- ✅ **Professional logging output** with clean, fast, and neat appearance / 具有清洁、快速和整洁外观的专业日志输出

### v0.2 (2024-01-20)
- ✅ **Fixed await expression errors** in DingTalk stream processing / 修复钉钉流处理中的 await 表达式错误
- ✅ **Improved error handling** for message processing / 改进消息处理的错误处理
- ✅ **Enhanced logging** with better color schemes / 通过更好的配色方案增强日志
- ✅ **Updated timeout settings** for better reliability / 更新超时设置以提高可靠性
- ✅ **Added comprehensive diagnostics** for system health / 为系统健康添加全面诊断
- ✅ **Improved thread management** for WebSocket connections / 改进 WebSocket 连接的线程管理
- ✅ **Added message validation** to prevent processing errors / 添加消息验证以防止处理错误
- ✅ **Enhanced configuration validation** with better error messages / 通过更好的错误消息增强配置验证

### v0.1 (2024-01-20)
- ✅ **Initial release** with basic DingTalk integration / 具有基本钉钉集成的初始版本
- ✅ **Dify API integration** for AI-powered responses / 用于 AI 驱动响应的 Dify API 集成
- ✅ **WebSocket communication** with DingTalk Stream Mode / 与钉钉流模式的 WebSocket 通信
- ✅ **Basic message processing** and response generation / 基本消息处理和响应生成
- ✅ **Configuration management** with environment variables / 使用环境变量的配置管理
- ✅ **Professional logging** system with colored output / 带颜色输出的专业日志系统

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

**中文**：本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

---

## 🙏 Acknowledgments / 致谢

- **DingTalk Open Platform** for Stream Mode API / **钉钉开放平台** 提供流模式 API
- **Dify** for AI knowledge base integration / **Dify** 提供 AI 知识库集成
- **Python Community** for excellent async libraries / **Python 社区** 提供优秀的异步库
- **MindSpring Team** for development support / **MindSpring 团队** 提供开发支持

---

**Last Updated / 最后更新**: January 30, 2025 / 2025年1月30日  
**Version / 版本**: v0.4  
**Maintainer / 维护者**: MindSpring Team / MindSpring 团队 