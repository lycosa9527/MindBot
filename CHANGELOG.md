# MindBot Changelog / MindBot 更新日志

## v0.4.1 (2025-01-30) - Voice Recognition Logic Fixes

### 🐛 Voice Recognition Logic Errors Fixed / 语音识别逻辑错误修复
- **Empty text handling** - Fixed handling of empty recognition text from DingTalk
- **Better validation** - Added validation for empty recognition results
- **Enhanced error handling** - Improved error handling for DingTalk's pre-recognized text
- **Debug logging** - Added comprehensive debug logging for better troubleshooting
- **Text encoding/decoding** - Fixed potential issues with text encoding/decoding

### 🔧 Technical Improvements / 技术改进
- **Enhanced VoiceRecognitionService** - Better input validation and error handling
- **Improved extract_audio_data** - Added empty text detection and validation
- **Updated convert_speech_to_text** - Better error handling for pre-recognized text
- **Enhanced debug logging** - More detailed logging throughout voice processing pipeline

### 📝 Code Quality / 代码质量
- **Better error messages** - More descriptive error messages for troubleshooting
- **Input validation** - Added validation for empty or whitespace-only text
- **Edge case handling** - Improved handling of edge cases in voice recognition

---

## v0.4 (2025-01-30) - Voice Recognition and Major Bug Fixes

### 🎤 Voice Recognition Feature / 语音识别功能

#### Speech-to-Text Integration / 语音转文字集成
- **DingTalk Official API** - Integrated DingTalk's speech recognition service for voice messages
- **Fallback Services** - Added Google Speech Recognition and Sphinx offline recognition as alternatives
- **Multi-format Support** - Supports WAV, MP3, M4A, AAC, OGG audio formats
- **Automatic Detection** - Seamlessly detects and processes voice messages without user intervention
- **Graceful Degradation** - Falls back to alternative services if primary DingTalk API fails

#### Voice Processing Architecture / 语音处理架构
- **VoiceRecognitionService** - New dedicated service for speech-to-text conversion
- **Enhanced Message Handler** - Updated `MindBotChatbotHandler` to support both text and voice messages
- **Unified Content Extraction** - Single method `_extract_message_content()` handles both text and voice
- **Seamless Integration** - No changes required to existing AI agent logic or response handling

#### Technical Implementation / 技术实现
- **Async Processing** - Voice recognition runs asynchronously to maintain performance
- **Memory Management** - Temporary audio file handling with automatic cleanup
- **Error Handling** - Comprehensive error handling for audio processing and API failures
- **Logging Integration** - Detailed logging for voice processing workflow and debugging

### 🐛 Critical Bug Fixes / 关键错误修复

#### DingTalk SDK Duplication Issues / 钉钉 SDK 重复问题
- **Fixed message duplication** - Implemented proper message acknowledgments (`AckMessage.STATUS_OK`, `AckMessage.STATUS_ERROR`) to prevent server-side retries
- **Root cause identified** - DingTalk SDK requires explicit acknowledgments from the `process` method, otherwise messages are retried
- **Enhanced deduplication system** - Added hash-based deduplication with TTL (300s) and thread-safe operations
- **Improved message handling** - Uses `incoming_message.message_id` for deduplication when available, falls back to SHA-256 hash

#### Architecture Refactoring / 架构重构
- **Migrated to official SDK** - Replaced custom `MessageHandler` with `MindBotChatbotHandler` extending `dingtalk_stream.ChatbotHandler`
- **Proper SDK integration** - Implemented `async def process(self, callback)` as the official entry point
- **Removed manual webhook sending** - Replaced custom `send_reply` with `self.reply_text(response, incoming_message)`
- **Corrected topic registration** - Changed from `"/v1.0/im/bot/messages/get"` to `ChatbotMessage.TOPIC`

### 🔧 Technical Improvements / 技术改进

#### Console Logging Optimization / 控制台日志优化
- **Reduced redundant logging** - Moved internal flow logs from `INFO` to `DEBUG` level
- **Consolidated message flow** - Streamlined logging across `dingtalk_client.py`, `main.py`, `agent.py`, and `dify_client.py`
- **Improved visibility** - User messages and responses remain at `INFO` level for clear conversation tracking
- **Professional appearance** - Clean, fast, and neat logging output without emojis

#### Configuration Updates / 配置更新
- **Updated AI model** - Changed Qwen model from `qwen-turbo-latest` to `qwen3-0.6b` for better performance
- **Default settings** - Set `DEBUG_MODE=false` and `LOG_LEVEL=INFO` for production use
- **Enhanced documentation** - Added comprehensive inline comments for all logging levels and their usage

#### Error Handling and Recovery / 错误处理和恢复
- **Enhanced exception management** - Better error handling for network issues, API failures, and invalid messages
- **Improved timeout configuration** - Increased Dify API timeout from 60s to 120s for better reliability
- **Graceful degradation** - Application continues running even when individual components fail

### 📚 Documentation and User Experience / 文档和用户体验

#### Bilingual Documentation / 双语文档
- **Moved README to root** - Relocated from `docs/README.md` to root directory for GitHub homepage visibility
- **Comprehensive bilingual content** - All sections available in both English and Chinese
- **Professional presentation** - Clean, neat, and user-friendly documentation
- **Updated version badges** - All documentation reflects v0.4 and current build date

#### Git Workflow Improvements / Git 工作流改进
- **Cross-platform compatibility** - Added `.gitattributes` for line ending standardization
- **Conflict resolution** - Removed `__pycache__` and `.log` files from version control
- **Better collaboration** - Configured `pull.rebase false` for merge-based workflow

### 🚀 Performance and Reliability / 性能和可靠性

#### Message Processing / 消息处理
- **Thread-safe operations** - Added `threading.Lock` for concurrent message handling
- **Memory management** - Limited recent messages to 100 entries with 300s TTL
- **Efficient deduplication** - SHA-256 hash-based message identification with automatic cleanup

#### Network and API / 网络和 API
- **Increased timeouts** - Extended Dify API timeout for better reliability
- **SSL/TLS improvements** - Enhanced certificate validation and connection handling
- **Better error recovery** - Automatic retry mechanisms and connection pooling

### 🔍 Code Quality and Maintenance / 代码质量和维护

#### Code Review Improvements / 代码审查改进
- **Removed wildcard imports** - Changed `from config import *` to specific imports
- **Enhanced validation** - Added null checks for log records and component names
- **Better error messages** - More descriptive exception handling and user feedback
- **Professional coding standards** - PEP 8 compliance and modern async patterns

#### Development Tools / 开发工具
- **Enhanced diagnostics** - Comprehensive network and API connectivity testing
- **Better debugging** - Improved log level management and component isolation
- **Development workflow** - Added `.cursorignore` for IDE-specific file management

---

## v0.3 (2025-07-30) - Logging and Performance Improvements

### Console Logging Enhancements / 控制台日志增强
- **Level-only coloring** - Only logging levels are colored, not timestamps or component names
- **Professional appearance** - Clean, fast, and neat logging output
- **Performance optimization** - Optimized timestamp handling with fallback mechanisms

### Error Handling / 错误处理
- **Enhanced validation** - Better handling of invalid log records and component names
- **Network improvements** - Fixed timeout configuration for better reliability
- **Code quality** - Improved validation and safety checks throughout the application

---

## v0.2 (2024-01-20) - Stability and Reliability

### Bug Fixes / 错误修复
- **Fixed await expression errors** in DingTalk stream processing
- **Improved error handling** for message processing
- **Enhanced logging** with better color schemes

### Performance / 性能
- **Updated timeout settings** for better reliability
- **Added comprehensive diagnostics** for system health
- **Improved thread management** for WebSocket connections

### Quality Assurance / 质量保证
- **Added message validation** to prevent processing errors
- **Enhanced configuration validation** with better error messages

---

## v0.1 (2024-01-20) - Initial Release

### Core Features / 核心功能
- **Initial release** with basic DingTalk integration
- **Dify API integration** for AI-powered responses
- **WebSocket communication** with DingTalk Stream Mode
- **Basic message processing** and response generation
- **Configuration management** with environment variables
- **Professional logging** system with colored output

---

## 🎯 Summary of v0.4 Improvements

**English**: Version 0.4 represents a major milestone in MindBot's development, focusing on critical bug fixes and architectural improvements. The most significant achievement is resolving the persistent message duplication issues by properly implementing the DingTalk SDK's acknowledgment system. This version also introduces comprehensive logging optimization, enhanced error handling, and professional documentation updates.

**中文**: 版本 0.4 代表了 MindBot 开发的一个重要里程碑，专注于关键错误修复和架构改进。最重要的成就是通过正确实现钉钉 SDK 的确认系统解决了持续的消息重复问题。此版本还引入了全面的日志优化、增强的错误处理和专业的文档更新。

### Key Achievements / 主要成就
1. **Eliminated message duplication** - Fixed root cause of duplicate messages
2. **Improved architecture** - Migrated to official DingTalk SDK patterns
3. **Enhanced user experience** - Cleaner, more professional logging
4. **Better reliability** - Improved error handling and recovery mechanisms
5. **Professional documentation** - Comprehensive bilingual documentation

---

**Maintainer**: MindSpring Team  
**Last Updated**: January 30, 2025  
**Version**: v0.4 