# Platform Adapters

This directory contains all platform-specific adapter implementations for the MindBot framework.

## 📁 Structure

```
adapters/
├── __init__.py          # Adapter exports
├── README.md            # This file
├── dingtalk.py          # DingTalk adapter implementation
├── wecom.py             # WeCom (WeChat Work) adapter implementation
└── slack.py             # Slack adapter implementation
```

## 🚀 Available Adapters

### **DingTalk Adapter** (`dingtalk.py`)
- **Platform**: DingTalk (钉钉)
- **Status**: ✅ Fully implemented
- **Features**: 
  - Real DingTalk client integration
  - Message processing and sending
  - Health monitoring
  - Multiple instance support

### **WeCom Adapter** (`wecom.py`)
- **Platform**: WeCom (企业微信)
- **Status**: 🔄 Skeleton implementation
- **Features**:
  - Basic structure ready
  - TODO: WeCom client integration
  - Message processing framework

### **Slack Adapter** (`slack.py`)
- **Platform**: Slack
- **Status**: 🔄 Skeleton implementation
- **Features**:
  - Basic structure ready
  - TODO: Slack client integration
  - Message processing framework

## 📋 Usage

### **Import Adapters**
```python
from mindbot_framework.platforms.adapters import DingTalkAdapter, WeComAdapter, SlackAdapter
```

### **Create Adapter Instance**
```python
# DingTalk adapter
dingtalk_adapter = DingTalkAdapter("dingtalk_prod", {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret", 
    "robot_code": "your_robot_code"
})

# WeCom adapter
wecom_adapter = WeComAdapter("wecom_prod", {
    "corp_id": "your_corp_id",
    "corp_secret": "your_corp_secret",
    "agent_id": "your_agent_id"
})

# Slack adapter
slack_adapter = SlackAdapter("slack_prod", {
    "bot_token": "your_bot_token",
    "signing_secret": "your_signing_secret",
    "app_token": "your_app_token"
})
```

### **Register with Application**
```python
from mindbot_framework import MindBotApplication

app = MindBotApplication(config)

# Register adapters
app.register_platform_adapter(dingtalk_adapter)
app.register_platform_adapter(wecom_adapter)
app.register_platform_adapter(slack_adapter)

# Start application
await app.start()
```

## 🔧 Configuration

### **DingTalk Configuration**
```python
dingtalk_config = {
    "client_id": "dingr6bg0cj9ylmlpuqz",
    "client_secret": "h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD",
    "robot_code": "dingr6bg0cj9ylmlpuqz"
}
```

### **WeCom Configuration**
```python
wecom_config = {
    "corp_id": "ww1234567890abcdef",
    "corp_secret": "wecom_secret_key_12345",
    "agent_id": "1000001"
}
```

### **Slack Configuration**
```python
slack_config = {
    "bot_token": "xoxb-your-bot-token-here",
    "signing_secret": "your-signing-secret-here",
    "app_token": "xapp-your-app-token-here"
}
```

## 🏗️ Adding New Adapters

### **1. Create Adapter File**
Create a new file `your_platform.py` in this directory.

### **2. Implement Base Class**
```python
from ..base import PlatformAdapter, Message, Response, MessageType

class YourPlatformAdapter(PlatformAdapter):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        # Your initialization code
    
    def get_required_config_fields(self) -> List[str]:
        return ["required_field1", "required_field2"]
    
    async def initialize(self) -> bool:
        # Your initialization logic
        pass
    
    async def start(self) -> None:
        # Your start logic
        pass
    
    async def stop(self) -> None:
        # Your stop logic
        pass
    
    async def send_message(self, response: Response) -> bool:
        # Your send message logic
        pass
    
    async def process_incoming_message(self, raw_message: Dict[str, Any]) -> Optional[Message]:
        # Your message processing logic
        pass
    
    async def health_check(self) -> bool:
        # Your health check logic
        pass
    
    async def get_platform_info(self) -> Dict[str, Any]:
        # Your platform info logic
        pass
```

### **3. Update Exports**
Add your adapter to `__init__.py`:
```python
from .your_platform import YourPlatformAdapter

__all__ = [
    "DingTalkAdapter",
    "WeComAdapter", 
    "SlackAdapter",
    "YourPlatformAdapter",  # Add this
]
```

### **4. Update Main Platforms**
Add to `mindbot_framework/platforms/__init__.py`:
```python
from .adapters import DingTalkAdapter, WeComAdapter, SlackAdapter, YourPlatformAdapter

__all__ = [
    "PlatformAdapter",
    "Message", 
    "Response",
    "MessageType",
    "DingTalkAdapter",
    "WeComAdapter",
    "SlackAdapter",
    "YourPlatformAdapter",  # Add this
]
```

## 🧪 Testing

### **Run Examples**
```bash
# Multiple DingTalk adapters
python multiple_dingtalk_example.py

# Multiple platform types
python multi_platform_types_example.py

# Advanced multi-platform manager
python multi_platform_manager.py
```

### **Test Individual Adapter**
```python
# Test adapter initialization
adapter = DingTalkAdapter("test", config)
success = await adapter.initialize()
assert success == True

# Test message processing
message = await adapter.process_incoming_message(raw_message)
assert message is not None

# Test health check
health = await adapter.health_check()
assert health == True
```

## 📊 Status Overview

| Adapter | Status | Implementation | Testing | Documentation |
|---------|--------|----------------|---------|---------------|
| DingTalk | ✅ Complete | 100% | ✅ Tested | ✅ Complete |
| WeCom | 🔄 Skeleton | 30% | ❌ Pending | ✅ Basic |
| Slack | 🔄 Skeleton | 30% | ❌ Pending | ✅ Basic |

## 🎯 Next Steps

1. **Complete WeCom Implementation** - Add real WeCom client integration
2. **Complete Slack Implementation** - Add real Slack client integration
3. **Add More Platforms** - Telegram, Discord, Microsoft Teams, etc.
4. **Enhanced Testing** - Unit tests for each adapter
5. **Performance Optimization** - Connection pooling, async optimization

---

**Ready to scale across multiple platforms!** 🚀
