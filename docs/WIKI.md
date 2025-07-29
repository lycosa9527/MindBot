# MindBot Wiki

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.2-orange.svg)](https://github.com/lycosa9527/MindBot/releases)
[![WakaTime](https://wakatime.com/badge/user/60ba0518-3829-457f-ae10-3eff184d5f69/project/707446f2-b1e2-4f2d-8f57-53d016ce3302.svg)](https://wakatime.com/@60ba0518-3829-457f-ae10-3eff184d5f69/projects/707446f2-b1e2-4f2d-8f57-53d016ce3302)
[![DingTalk](https://img.shields.io/badge/DingTalk-Stream%20Mode-red.svg)](https://open.dingtalk.com/)
[![Dify](https://img.shields.io/badge/Dify-API%20Integration-purple.svg)](https://dify.ai/)
[![LangChain](https://img.shields.io/badge/LangChain-Tools-yellow.svg)](https://langchain.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-3.8+-lightblue.svg)](https://docs.aiohttp.org/)
[![python-dotenv](https://img.shields.io/badge/python--dotenv-1.0+-green.svg)](https://github.com/theskumar/python-dotenv)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/lycosa9527/MindBot)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Changelog](#changelog)

## 🎯 Overview

MindBot is an intelligent DingTalk chatbot powered by Dify API, designed to provide educational assistance and teaching support. The application uses DingTalk's Stream Mode for real-time message processing and integrates with Dify's knowledge base for intelligent responses.

### Key Components

- **DingTalk Stream Integration**: Real-time WebSocket communication
- **Dify API Integration**: AI-powered knowledge base responses
- **Professional Logging**: Colored console output with structured logging
- **Comprehensive Diagnostics**: Network and API connectivity testing
- **Error Handling**: Robust error management and graceful degradation

## ✨ Features

### Core Features
- ✅ **Real-time Message Processing**: Instant response to DingTalk messages
- ✅ **AI-Powered Responses**: Integration with Dify knowledge base
- ✅ **Multi-Platform Support**: Works with DingTalk mobile and desktop
- ✅ **Professional Logging**: Clean, colored console output
- ✅ **Health Monitoring**: Comprehensive system diagnostics
- ✅ **Error Recovery**: Automatic error handling and recovery

### Technical Features
- ✅ **Async/Await Architecture**: Modern Python async programming
- ✅ **WebSocket Communication**: Real-time bidirectional messaging
- ✅ **HTTP API Integration**: RESTful API calls to Dify
- ✅ **SSL/TLS Security**: Secure connections with certificate validation
- ✅ **Thread Management**: Proper resource management and cleanup
- ✅ **Configuration Management**: Environment-based configuration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DingTalk      │    │   MindBot       │    │   Dify API      │
│   Stream Mode   │◄──►│   Application   │◄──►│   Knowledge     │
│   WebSocket     │    │   (Python)      │    │   Base          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Structure

```
mindbot_poc/
├── src/                    # Main application code
│   ├── main.py            # Application entry point
│   ├── dingtalk_client.py # DingTalk WebSocket client
│   ├── agent.py           # AI agent logic
│   ├── dify_client.py     # Dify API integration
│   ├── config.py          # Configuration management
│   ├── debug.py           # Logging and diagnostics
│   ├── tools.py           # Utility tools
│   └── banner.py          # Application banner
├── config/                 # Configuration files
│   └── env_example.txt    # Environment variables template
├── docs/                   # Documentation
│   ├── README.md          # Project documentation
│   └── WIKI.md            # This wiki file
├── requirements.txt        # Python dependencies
├── run.py                 # Application launcher
└── .env                   # Environment variables (user-created)
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- DingTalk Developer Account
- Dify API Access
- Network connectivity to DingTalk and Dify APIs

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mindbot_poc
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

1. Copy the example environment file:
   ```bash
   cp config/env_example.txt .env
   ```

2. Edit `.env` with your actual credentials:
   ```env
   # DingTalk Configuration
   DINGTALK_CLIENT_ID=your_actual_client_id
   DINGTALK_CLIENT_SECRET=your_actual_client_secret
   DINGTALK_ROBOT_CODE=your_actual_robot_code
   DINGTALK_ROBOT_NAME=MindBot_v0.2

   # Dify Configuration
   DIFY_API_KEY=your_actual_dify_api_key
   DIFY_BASE_URL=https://your-dify-instance.com/v1

   # Qwen Configuration (Optional)
   QWEN_API_KEY=your_actual_qwen_api_key
   QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_MODEL=qwen-turbo-latest
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DINGTALK_CLIENT_ID` | DingTalk App Client ID | Yes | `dingr6bg0cj9ylmlpuqz` |
| `DINGTALK_CLIENT_SECRET` | DingTalk App Client Secret | Yes | `h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD` |
| `DINGTALK_ROBOT_CODE` | DingTalk Robot Code | Yes | `dingr6bg0cj9ylmlpuqz` |
| `DINGTALK_ROBOT_NAME` | Bot Display Name | No | `MindBot_v0.2` |
| `DIFY_API_KEY` | Dify API Key | Yes | `app-4DGFRXExxcP0xZ5Og3AXfT2N` |
| `DIFY_BASE_URL` | Dify API Base URL | Yes | `http://dify.mindspringedu.com/v1` |
| `QWEN_API_KEY` | Qwen API Key | No | `sk-xxx` |
| `QWEN_BASE_URL` | Qwen API Base URL | No | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `QWEN_MODEL` | Qwen Model Name | No | `qwen-turbo-latest` |
| `DEBUG_MODE` | Enable Debug Mode | No | `true` |
| `LOG_LEVEL` | Logging Level | No | `DEBUG` |

### Getting Credentials

#### DingTalk Setup
1. Go to [DingTalk Open Platform](https://open.dingtalk.com/)
2. Create a new application
3. Configure robot settings
4. Get Client ID and Client Secret

#### Dify Setup
1. Go to [Dify Cloud](https://cloud.dify.ai/) or your self-hosted instance
2. Create a new application
3. Get API Key and Base URL

## 🎮 Usage

### Starting the Application

```bash
python run.py
```

### Application Flow

1. **Initialization**: System diagnostics and component setup
2. **Connection**: Establish WebSocket connection to DingTalk
3. **Message Reception**: Receive messages from DingTalk users
4. **Processing**: Send messages to Dify API for AI processing
5. **Response**: Send AI-generated responses back to users
6. **Monitoring**: Continuous health monitoring and error handling

### Example Message Flow

```
User: "你好"
↓
DingTalk → MindBot → Dify API
↓
Dify: "你好！我是MindMate，是你的虚拟教研伙伴..."
↓
MindBot → DingTalk → User
```

## 📚 API Documentation

### DingTalk Stream Mode

The application uses DingTalk's Stream Mode for real-time communication:

- **WebSocket Endpoint**: `wss://wss-open-connection.dingtalk.com:443/connect`
- **Message Format**: JSON with text content and metadata
- **Response Method**: Session webhook HTTP POST

### Dify API Integration

- **Endpoint**: `{DIFY_BASE_URL}/chat-messages`
- **Method**: POST
- **Authentication**: Bearer token
- **Response Format**: JSON with AI-generated text

### Message Processing Pipeline

1. **Reception**: WebSocket message from DingTalk
2. **Parsing**: Extract text content and metadata
3. **Context**: Build user context and conversation ID
4. **AI Processing**: Send to Dify API with context
5. **Response**: Format and send back via webhook

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Errors
```
[ERROR] DingTalk authentication failed: 401 Unauthorized
```
**Solution**: Check your DingTalk credentials in `.env`

#### 2. Dify API Errors
```
[ERROR] Dify API returned status 401: Unauthorized
```
**Solution**: Verify your Dify API key and base URL

#### 3. Network Connectivity
```
[ERROR] Connection to api.dingtalk.com failed
```
**Solution**: Check your internet connection and firewall settings

#### 4. Message Processing Errors
```
[ERROR] object NoneType can't be used in 'await' expression
```
**Solution**: This has been fixed in v0.2. Update to latest version.

### Diagnostic Commands

Run system diagnostics:
```bash
python run.py
```

Check configuration:
```bash
python -c "from src.config import *; print('Config loaded successfully')"
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General application information
- **WARNING**: Warning messages
- **ERROR**: Error messages

## 🛠️ Development

### Project Structure

```
src/
├── main.py              # Application entry point and orchestration
├── dingtalk_client.py   # DingTalk WebSocket client and message handling
├── agent.py             # AI agent logic and message processing
├── dify_client.py       # Dify API client and integration
├── config.py            # Configuration management and validation
├── debug.py             # Logging setup and diagnostic utilities
├── tools.py             # Utility tools and helper functions
└── banner.py            # Application banner and startup display
```

### Key Classes

#### `MindBotStreamApp`
Main application orchestrator that manages:
- Application lifecycle
- Component initialization
- Message routing
- Error handling

#### `MindBotDingTalkClient`
DingTalk integration that handles:
- WebSocket connection management
- Message reception and parsing
- Response sending via webhooks
- Connection health monitoring

#### `MindBotAgent`
AI agent that processes:
- User message analysis
- Dify API integration
- Response generation
- Context management

#### `DifyClient`
Dify API client that manages:
- HTTP requests to Dify
- Authentication and headers
- Response parsing
- Error handling

### Development Setup

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

### Testing

The application includes comprehensive diagnostics:
- Network connectivity tests
- API authentication tests
- Component health checks
- Error simulation and recovery

### Code Style

- **Python**: PEP 8 compliance
- **Async/Await**: Modern async programming patterns
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging with colors
- **Documentation**: Comprehensive docstrings and comments

## 📝 Changelog

### v0.2 (2024-01-20)
- ✅ **Fixed await expression errors** in DingTalk stream processing
- ✅ **Improved error handling** for message processing
- ✅ **Enhanced logging** with better color schemes
- ✅ **Updated timeout settings** for better reliability
- ✅ **Added comprehensive diagnostics** for system health
- ✅ **Improved thread management** for WebSocket connections
- ✅ **Added message validation** to prevent processing errors
- ✅ **Enhanced configuration validation** with better error messages

### v0.1 (2024-01-20)
- ✅ **Initial release** with basic DingTalk integration
- ✅ **Dify API integration** for AI-powered responses
- ✅ **WebSocket communication** with DingTalk Stream Mode
- ✅ **Basic message processing** and response generation
- ✅ **Configuration management** with environment variables
- ✅ **Professional logging** system with colored output

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DingTalk Open Platform** for Stream Mode API
- **Dify** for AI knowledge base integration
- **Python Community** for excellent async libraries
- **MindSpring Team** for development support

---

**Last Updated**: January 20, 2024  
**Version**: v0.2  
**Maintainer**: MindSpring Team 