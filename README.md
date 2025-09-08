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

# Configure system settings (optional)
cp env.example .env
# Edit .env with your system configuration

# Start MindBot
python run.py

# Access web dashboard at http://localhost:9529
# Configure platform adapters via web interface
```

### Configuration Approach

MindBot uses a **hybrid configuration system**:

- **System Configuration**: Environment variables (`config/.env` file)
  - Web dashboard settings (host, port, SSL)
  - Security settings (rate limiting, CORS)
  - Performance settings (concurrency, timeouts)
  - Monitoring settings (logging, health checks)

- **Platform Configuration**: Web interface
  - DingTalk adapters (Client ID, Secret, Robot Code)
  - WeCom adapters (Corp ID, Secret, Agent ID)
  - Dify API key and settings
  - All AI provider configurations
  - Adapter-specific configurations

### System Configuration (`config/.env`)
```bash
# Web Dashboard
WEB_DASHBOARD_HOST=0.0.0.0
WEB_DASHBOARD_PORT=9529
EXTERNAL_IP=your_server_ip
EXTERNAL_DOMAIN=your_domain.com

# Security
RATE_LIMITING_ENABLED=true
CORS_ORIGINS=http://localhost:9529,https://your_domain.com

# Performance
MAX_CONCURRENT_MESSAGES=50
MESSAGE_TIMEOUT=30.0

# Monitoring
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=30
```

### Platform Configuration (Web Interface)
1. Start MindBot: `python run.py`
2. Open web dashboard: `http://localhost:9529`
3. Add adapters via "Add Adapter" button
4. Configure Dify API key via "Edit Dify API Key"

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
- **Logs Viewer** - Real-time log streaming and management
- **Health Checks** - Component status monitoring

### Command Line
```bash
# Start with web dashboard
python run.py

# Manage logs
python tools/manage_logs.py list          # List all log files
python tools/manage_logs.py stats         # Show log statistics
python tools/manage_logs.py tail          # Show recent log entries
python tools/manage_logs.py clean --days 30  # Clean old logs
python tools/manage_logs.py compress      # Compress log files

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

- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Complete configuration setup guide
- **[Web Dashboard Guide](WEB_DASHBOARD_README.md)** - Web interface usage and features
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
├── tools/                  # Utility scripts
│   └── manage_logs.py     # Log management tool
├── logs/                   # Log files directory
├── config/                 # Configuration files
│   ├── mindbot_config.json # Main configuration
│   ├── env_example.txt     # Environment template
│   └── .env               # Environment variables (create from template)
├── docs/                   # Documentation
├── run.py                 # Main startup script
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
