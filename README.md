# MindBot POC v0.1 - DingTalk Chatbot

A proof-of-concept DingTalk chatbot that integrates with Dify API using LangChain agents.

**Version:** v0.1  
**Build Date:** 2024-01-20

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
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── dingtalk_stream.py   # DingTalk stream client
├── dify_client.py       # Dify API client
├── agent.py             # LangChain agent implementation
├── tools.py             # LangChain tools
├── debug.py             # Debug utilities and diagnostics
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables example
└── README.md           # This file
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables** (optional):
   Create a `.env` file based on `env_example.txt`:
   ```bash
   cp env_example.txt .env
   ```
   
   Then edit `.env` with your actual API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   DIFY_WORKSPACE_ID=your_dify_workspace_id
   DINGTALK_CLIENT_ID=your_dingtalk_client_id
   DINGTALK_CLIENT_SECRET=your_dingtalk_client_secret
   DINGTALK_ROBOT_CODE=your_dingtalk_robot_code
   DIFY_BASE_URL=your_dify_base_url
   ```

3. **Configuration**:
   - All credentials can now be set via environment variables
   - Dify API URL and key have default values
   - Debug mode is enabled by default

## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Test the Bot**:
   - Send messages to your DingTalk robot
   - The bot will respond using the LangChain agent
   - Check `mindbot.log` for detailed logs

## Available Tools

The LangChain agent has access to these tools:

- **dify_chat**: Chat with Dify API for knowledge and workflow responses
- **get_time**: Get current date and time
- **get_user_info**: Get information about the current user
- **calculator**: Perform basic mathematical calculations (with enhanced security)

## Debug Features

The application includes comprehensive debugging:

- **Connection Testing**: Tests Dify and OpenAI API connections
- **Tool Testing**: Validates all LangChain tools
- **Agent Testing**: Tests agent's tool calling capabilities
- **Configuration Validation**: Checks all required settings
- **Detailed Logging**: All operations are logged to `mindbot.log`

## Configuration

### DingTalk Settings
- Client ID: `dingr6bg0cj9ylmlpuqz` (default)
- Client Secret: `h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD` (default)
- Robot Code: `dingr6bg0cj9ylmlpuqz` (default)

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