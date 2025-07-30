# MindBot POC v0.3 - DingTalk Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.3-orange.svg)](https://github.com/lycosa9527/MindBot/releases)
[![WakaTime](https://wakatime.com/badge/user/60ba0518-3829-457f-ae10-3eff184d5f69/project/707446f2-b1e2-4f2d-8f57-53d016ce3302.svg)](https://wakatime.com/@60ba0518-3829-457f-ae10-3eff184d5f69/projects/707446f2-b1e2-4f2d-8f57-53d016ce3302)

A proof-of-concept DingTalk chatbot that integrates with Dify API using LangChain agents.

**Version:** v0.3  
**Build Date:** 2025-07-30

📖 **For detailed documentation, see [WIKI.md](WIKI.md)**

## Features

- **DingTalk Stream Mode**: Real-time message processing using DingTalk's stream mode
- **Dify API Integration**: Connects to Dify API for knowledge base and workflow responses
- **LangChain Agent**: Uses proper LangChain tool-calling mechanisms
- **Multiple Tools**: Calculator, time, user info, and Dify chat tools
- **Debug Features**: Comprehensive diagnostics and logging
- **Graceful Shutdown**: Proper signal handling and cleanup
- **Enhanced Security**: Safe mathematical evaluation and input validation
- **Error Handling**: Robust error handling with fallback mechanisms

## Project Structure

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
│   └── WIKI.md            # Comprehensive wiki
├── requirements.txt        # Python dependencies
├── run.py                 # Application launcher
└── .env                   # Environment variables (user-created)
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file based on the example:
   ```bash
   cp config/env_example.txt .env
   ```
   
   Then edit `.env` with your actual API keys:
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
       QWEN_MODEL=qwen3-0.6b
   ```

3. **Configuration**:
   - All credentials must be set via environment variables
   - Debug mode is enabled by default
   - Comprehensive diagnostics run on startup

## Usage

1. **Run the Application**:
   ```bash
   python run.py
   ```

2. **Test the Bot**:
   - Send messages to your DingTalk robot
   - The bot will respond using the Dify API integration
   - Check console output for detailed logs
   - System diagnostics run automatically on startup

## Available Tools

The application includes these utility tools:

- **Dify API Integration**: Direct integration with Dify knowledge base
- **Time Tool**: Get current date and time information
- **User Info Tool**: Get information about the current user
- **Calculator Tool**: Perform basic mathematical calculations (with enhanced security)
- **Comprehensive Diagnostics**: Network and API connectivity testing

## Debug Features

The application includes comprehensive debugging:

- **Network Connectivity Testing**: Tests connections to Bing, Baidu, and DingTalk APIs
- **DingTalk Connection Testing**: Validates DingTalk credentials and SSL configuration
- **Dify API Testing**: Tests Dify API connectivity and authentication
- **Configuration Validation**: Checks all required environment variables
- **Professional Logging**: Colored console output with structured logging
- **Error Recovery**: Automatic error handling and graceful degradation

## Configuration

### Environment Variables
All configuration is done through environment variables in the `.env` file:

- **DingTalk Settings**: Client ID, Client Secret, Robot Code
- **Dify Settings**: API Key, Base URL
- **Qwen Settings**: API Key, Base URL, Model (optional)
- **Debug Settings**: Debug mode, log level

### Getting Credentials
- **DingTalk**: Get credentials from [DingTalk Open Platform](https://open.dingtalk.com/)
- **Dify**: Get credentials from [Dify Cloud](https://cloud.dify.ai/) or your self-hosted instance

### Dify Settings
- API Key: `app-4DGFRXExxcP0xZ5Og3AXfT2N` (default)
- Base URL: `http://dify.mindspringedu.com/v1` (default)

## Security Improvements (v0.1)

- **Safe Calculator**: Replaced `eval()` with secure AST-based evaluation
- **Input Validation**: Added comprehensive input validation
- **Error Handling**: Enhanced error handling with specific error types
- **Timeout Protection**: Added request timeouts to prevent hanging
- **Environment Variables**: Moved hardcoded credentials to environment variables

## Troubleshooting

1. **Check Logs**: Review `mindbot.log` for detailed error information
2. **Run Diagnostics**: The application runs diagnostics on startup if debug mode is enabled
3. **Test Connections**: Use the debug utilities to test API connections
4. **Verify Configuration**: Ensure all required API keys are set

## Development

- **Adding New Tools**: Extend the `tools.py` file with new LangChain tools
- **Modifying Agent**: Update the system prompt in `agent.py`
- **Custom Handlers**: Modify the message handling in `dingtalk_stream.py`

## License

This is a proof-of-concept implementation for educational purposes. 