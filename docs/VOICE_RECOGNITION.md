# Voice Recognition Implementation

## Overview

This implementation adds voice recognition capabilities to the MindBot DingTalk client, allowing it to process voice messages and convert them to text before sending to the AI agent.

## Prerequisites

### System Requirements

**No Additional Dependencies Required**
The voice recognition service uses only DingTalk's official API and standard Python libraries. No FFmpeg or additional audio processing tools are needed.

**No Installation Required**
The voice recognition service works out of the box with your existing DingTalk credentials.

## Features

### ✅ Implemented Features

1. **DingTalk Official Speech Recognition API**
   - Uses DingTalk's official speech-to-text API
   - Supports multiple audio formats (WAV, MP3, etc.)
   - Automatic access token management
   - No additional dependencies required

3. **Voice Message Detection**
   - Automatically detects voice/audio messages
   - Extracts audio data from various message formats
   - Supports base64 encoded audio data

4. **Seamless Integration**
   - Works with existing text message processing
   - No changes required to AI agent logic
   - Maintains all existing functionality

## Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   DingTalk      │    │   Voice Recognition │    │   AI Agent      │
│   Message       │───▶│   Service           │───▶│   (Dify)        │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Text Response │
                       └─────────────────┘
```

## Implementation Details

### Voice Recognition Service (`src/voice_recognition.py`)

The `VoiceRecognitionService` class provides:

- **DingTalk API Integration**: Uses official DingTalk speech recognition
- **Fallback Services**: Multiple speech recognition options
- **Audio Processing**: Handles various audio formats
- **Message Detection**: Identifies voice messages automatically

### Enhanced DingTalk Client (`src/dingtalk_client.py`)

The `MindBotChatbotHandler` class now includes:

- **Voice Message Processing**: Detects and processes voice messages
- **Content Extraction**: Unified method for text and voice content
- **Seamless Integration**: No changes to existing text processing

## Configuration

### Environment Variables

Add these to your `.env` file for voice recognition:

```env
# DingTalk Voice Recognition (same as existing credentials)
DINGTALK_CLIENT_ID=your_client_id
DINGTALK_CLIENT_SECRET=your_client_secret
```

### Dependencies

The voice recognition service uses only standard dependencies:

```txt
# Core dependencies (already included)
requests>=2.31.0
```

## Usage

### Automatic Voice Processing

Voice messages are automatically processed when received:

1. **Message Detection**: System detects voice message
2. **Audio Extraction**: Extracts audio data from message
3. **Speech Recognition**: Converts speech to text
4. **AI Processing**: Sends transcribed text to AI agent
5. **Response**: AI response sent back to user

### Message Flow

```
User sends voice message
    ↓
DingTalk Stream receives message
    ↓
VoiceRecognitionService detects voice content
    ↓
Audio data extracted from message
    ↓
Speech-to-text conversion (DingTalk API → Fallback)
    ↓
Transcribed text sent to AI agent
    ↓
AI response sent back to user
```

## Supported Audio Formats

- **WAV** (recommended)
- **MP3**
- **M4A**
- **AAC**
- **OGG**

## Error Handling

### Error Handling

1. **DingTalk API Failure**: Logs error and continues processing
2. **Network Issues**: Automatic retry with exponential backoff
3. **Invalid Audio**: Graceful error handling with user feedback

### Logging

Comprehensive logging for debugging:

```python
logger.info("Processing voice message")
logger.info(f"Voice message transcribed: {text}")
logger.warning("Failed to transcribe voice message")
logger.error("Error in DingTalk speech recognition: {str(e)}")
```

## Testing

### Manual Testing

1. **Send voice message** in DingTalk
2. **Check logs** for voice processing messages
3. **Verify transcription** accuracy
4. **Test AI response** quality

### Test Scenarios

- ✅ Voice message with clear speech
- ✅ Voice message with background noise
- ✅ Very short voice messages
- ✅ Long voice messages
- ✅ Different languages (Chinese/English)
- ✅ Network connectivity issues

## Performance Considerations

### Processing Time

- **DingTalk API**: ~2-5 seconds
- **Network Latency**: Depends on connection speed
- **Audio Processing**: Minimal local processing

### Resource Usage

- **Memory**: Minimal temporary file storage
- **CPU**: Minimal local processing
- **Network**: API calls to DingTalk speech recognition

## Troubleshooting

### Common Issues

1. **"No audio data found"**
   - Check message format
   - Verify audio extraction logic

2. **"Access token not available"**
   - Verify DingTalk credentials
   - Check network connectivity

3. **"Failed to transcribe voice message"**
   - Check DingTalk API status
   - Verify audio quality and format
   - Check network connectivity

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger('voice_recognition').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Real-time Voice Recognition**
   - Stream processing for live voice
   - Lower latency processing

2. **Multi-language Support**
   - Automatic language detection
   - Language-specific models

3. **Voice Response**
   - Text-to-speech for responses
   - Voice message replies

4. **Advanced Audio Processing**
   - Noise reduction
   - Audio enhancement
   - Format optimization

## Security Considerations

### Data Privacy

- Audio data processed temporarily
- No permanent storage of voice data
- Secure API communication

### Access Control

- DingTalk API authentication
- Token-based access
- Secure credential management

## API Reference

### VoiceRecognitionService

```python
class VoiceRecognitionService:
    async def convert_speech_to_text(audio_data: bytes, audio_format: str = "wav") -> Optional[str]
    def is_voice_message(message_data: Dict[str, Any]) -> bool
    def extract_audio_data(message_data: Dict[str, Any]) -> tuple[Optional[bytes], str]
```

### Enhanced ChatbotHandler

```python
class MindBotChatbotHandler(ChatbotHandler):
    async def _extract_message_content(incoming_message: ChatbotMessage) -> Optional[str]
```

## Contributing

When contributing to voice recognition features:

1. **Test with real voice messages**
2. **Verify fallback mechanisms**
3. **Check error handling**
4. **Update documentation**
5. **Add comprehensive logging**

## Support

For issues with voice recognition:

1. Check the logs for error messages
2. Verify DingTalk credentials
3. Test with different audio formats
4. Check network connectivity
5. Review API documentation 