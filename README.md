# MindBot - Multi-Platform LLM Bot Framework

[![Version](https://img.shields.io/badge/version-v0.5.0-blue.svg)](https://github.com/lycosa9527/MindBot)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active%20development-brightgreen.svg)](https://github.com/lycosa9527/MindBot)

A high-concurrency, event-driven multi-platform LLM bot framework with modern web dashboard and comprehensive platform integrations.

## 🚀 Features

### Core Framework
- **Event-driven Architecture** - High-concurrency, loosely coupled components
- **Stage-based Initialization** - LifecycleManager with health monitoring
- **Platform Adapter System** - Extensible platform integrations
- **Message Processing Pipeline** - Async processing with error handling and retry logic
- **Modern Web Dashboard** - Professional AstrBot-style interface
- **Unified Startup** - Single command deployment

### Platform Support
- **DingTalk** - Full WebSocket integration with voice recognition
- **WeCom** - Enterprise messaging platform (planned)
- **WeCom Customer Service** - Customer service integration (planned)

### AI Integration
- **Dify API** - Advanced AI workflows and knowledge base
- **OpenAI** - GPT models with function calling
- **LangChain** - Tool integration and agent capabilities
- **Multiple LLM Providers** - Load balancing and failover

### Advanced Features
- **Voice Recognition** - Speech-to-text for voice messages
- **Real-time Streaming** - Progressive response delivery
- **Health Monitoring** - Component status and performance metrics
- **Error Recovery** - Automatic retry and fallback mechanisms
- **Hot Reload** - Dynamic component updates (planned)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Quick Start
```bash
# Clone the repository
git clone https://github.com/lycosa9527/MindBot.git
cd MindBot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/env_example.txt .env
# Edit .env with your credentials

# Start MindBot
python start_mindbot.py
```

### Environment Configuration
```bash
# Required Environment Variables
DINGTALK_CLIENT_ID=your_dingtalk_client_id
DINGTALK_CLIENT_SECRET=your_dingtalk_client_secret
DINGTALK_ROBOT_CODE=your_robot_code
DIFY_API_KEY=your_dify_api_key
DIFY_BASE_URL=https://your-dify-instance.com/v1

# Optional Configuration
DEBUG_MODE=false
LOG_LEVEL=INFO
QWEN_MODEL=qwen3-0.6b
```

## 🎮 Usage

### Basic Usage
```python
from mindbot_framework import MindBotApplication

# Create application
config = {
    "logging": {"level": "INFO"},
    "platforms": {
        "dingtalk": {
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "robot_code": "your_robot_code"
        }
    }
}

app = MindBotApplication(config)

# Register platform adapters
app.register_platform_adapter(dingtalk_adapter)

# Start application
await app.start()
```

### Web Dashboard
Access the modern web dashboard at `http://localhost:9529`:
- **Real-time Monitoring** - Bot status and performance metrics
- **Message Testing** - Send test messages to verify functionality
- **Configuration Management** - View and update settings
- **Logs Viewer** - Real-time log streaming
- **Health Checks** - Component status monitoring

### Command Line
```bash
# Start with web dashboard
python start_mindbot.py

# Run example usage
python example_usage.py

# Check framework health
python -c "from mindbot_framework import MindBotApplication; print('Framework loaded successfully')"
```

## 🏗️ Architecture

### Core Components
```
mindbot_framework/
├── core/
│   ├── application.py      # MindBotApplication orchestrator
│   ├── lifecycle.py        # LifecycleManager with stages
│   ├── event_bus.py        # Event routing and processing
│   └── message_processor.py # Async message pipeline
└── platforms/
    └── base.py             # PlatformAdapter interface
```

### Message Flow
```
Platform Message → PlatformAdapter → EventBus → MessageProcessor → LLM → Response → Platform
```

### Lifecycle Stages
1. **Setup Logging** - Initialize logging system
2. **Load Configuration** - Load and validate config
3. **Initialize Database** - Setup data storage
4. **Start Platform Adapters** - Initialize platform connections
5. **Start Event Processing** - Begin message processing

## 📚 Documentation

- **[Implementation Plan](docs/MINDBOT_IMPLEMENTATION_PLAN.md)** - Detailed development roadmap
- **[Comprehensive Framework](docs/MINDBOT_COMPREHENSIVE_FRAMEWORK.md)** - Technical architecture
- **[Wiki](docs/WIKI.md)** - Setup guides and troubleshooting
- **[Changelog](CHANGELOG.md)** - Version history and updates

## 🔧 Development

### Project Structure
```
mindbot_poc/
├── mindbot_framework/      # Core framework
├── src/                    # Existing DingTalk bot code
├── templates/              # Web dashboard templates
├── docs/                   # Documentation
├── start_mindbot.py       # Unified startup script
├── example_usage.py       # Framework usage example
└── requirements.txt       # Dependencies
```

### Adding New Platforms
```python
from mindbot_framework.platforms.base import PlatformAdapter

class MyPlatformAdapter(PlatformAdapter):
    async def initialize(self) -> bool:
        # Platform-specific initialization
        pass
    
    async def start(self) -> None:
        # Start platform connection
        pass
    
    async def send_message(self, response: Response) -> bool:
        # Send message to platform
        pass
```

### Running Tests
```bash
# Run example usage
python example_usage.py

# Test framework components
python -c "from mindbot_framework.core import *; print('All components loaded')"
```

## 🚀 Deployment

### Docker (Planned)
```bash
# Build and run with Docker
docker build -t mindbot .
docker run -p 9529:9529 mindbot
```

### Production
```bash
# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:9529 app:app
```

## 📊 Status

### Phase 1: Foundation & MVP ✅ **COMPLETED**
- [x] Core framework architecture
- [x] Lifecycle management system
- [x] Platform adapter interface
- [x] Event bus architecture
- [x] Message processing pipeline
- [x] Web dashboard

### Phase 2: Core Features 🎯 **IN PROGRESS**
- [ ] Complete platform integrations
- [ ] Vector database & RAG
- [ ] LLM provider system
- [ ] LangChain integration

### Phase 3: Advanced Features 📋 **PLANNED**
- [ ] Plugin system
- [ ] Workflow capabilities
- [ ] Alert & monitoring
- [ ] Hot-reload features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DingTalk Open Platform** for Stream Mode API
- **Dify** for AI knowledge base integration
- **LangChain** for LLM tool integration
- **AstrBot** for dashboard design inspiration
- **Python Community** for excellent async libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/lycosa9527/MindBot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/lycosa9527/MindBot/discussions)
- **Documentation**: [Wiki](docs/WIKI.md)

---

**Maintainer**: MindSpring Team  
**Last Updated**: September 7, 2025  
**Version**: v0.5.0  
**Status**: Active Development
