#!/usr/bin/env python3
"""
Voice Recognition Service for DingTalk
Handles voice message processing and speech-to-text conversion using DingTalk's official API
"""

import asyncio
import logging
import os
import tempfile
import requests
import base64
from typing import Optional, Dict, Any
from src.config import (
    DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET
)

logger = logging.getLogger(__name__)

# Constants
TOKEN_EXPIRY_BUFFER = 600  # 10 minutes buffer for token refresh
API_TIMEOUT = 30  # seconds
TOKEN_REQUEST_TIMEOUT = 10  # seconds

class VoiceRecognitionService:
    """
    Service for processing voice messages from DingTalk.
    Uses DingTalk's official speech recognition API.
    """
    
    def __init__(self):
        """
        Initialize voice recognition service with DingTalk credentials.
        """
        self.client_id = DINGTALK_CLIENT_ID
        self.client_secret = DINGTALK_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
        # DingTalk API endpoints
        self.base_url = "https://oapi.dingtalk.com"
        self.speech_api_url = f"{self.base_url}/v1/ai/speech/transcription"
        
        logger.info("VoiceRecognitionService initialized")
    
    async def get_access_token(self) -> Optional[str]:
        """
        Get DingTalk access token for API authentication.
        
        Returns:
            Access token string or None if failed
        """
        try:
            if self.access_token and self.token_expires_at > asyncio.get_event_loop().time():
                return self.access_token
            
            url = f"{self.base_url}/gettoken"
            params = {
                "appkey": self.client_id,
                "appsecret": self.client_secret
            }
            
            response = requests.get(url, params=params, timeout=TOKEN_REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if data.get("errcode") == 0:
                self.access_token = data.get("access_token")
                # Token expires in 2 hours, refresh 10 minutes early
                self.token_expires_at = asyncio.get_event_loop().time() + (7200 - TOKEN_EXPIRY_BUFFER)
                logger.debug("DingTalk access token obtained successfully")
                return self.access_token
            else:
                logger.error(f"Failed to get access token: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    async def convert_speech_to_text(self, audio_data: bytes, audio_format: str = "wav") -> Optional[str]:
        """
        Convert speech to text using DingTalk's official speech recognition API.
        
        Args:
            audio_data: Raw audio data bytes
            audio_format: Audio format (wav, mp3, etc.) or "text" for pre-recognized text
            
        Returns:
            Transcribed text or None if failed
        """
        # Input validation
        if not audio_data:
            logger.error("No audio data provided")
            return None
        
        if not audio_format:
            logger.error("No audio format specified")
            return None
        
        # Handle pre-recognized text from DingTalk
        if audio_format == "text":
            try:
                text = audio_data.decode('utf-8')
                if text and text.strip():  # Ensure text is not empty
                    logger.info(f"Using DingTalk pre-recognized text: {text}")
                    return text.strip()
                else:
                    logger.warning("DingTalk provided empty recognition text")
                    return None
            except Exception as e:
                logger.error(f"Error decoding pre-recognized text: {str(e)}")
                return None
        
        try:
            access_token = await self.get_access_token()
            if not access_token:
                logger.error("No access token available for speech recognition")
                return None
            
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Prepare multipart form data
                files = {
                    "media": (f"audio.{audio_format}", audio_data, f"audio/{audio_format}")
                }
                
                params = {
                    "access_token": access_token
                }
                
                # Make API request to DingTalk speech recognition
                response = requests.post(
                    self.speech_api_url,
                    params=params,
                    files=files,
                    timeout=API_TIMEOUT
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("errcode") == 0:
                    transcribed_text = result.get("result", {}).get("text", "")
                    logger.info(f"Speech recognition successful: {len(transcribed_text)} characters")
                    return transcribed_text
                else:
                    error_code = result.get("errcode", "unknown")
                    error_msg = result.get("errmsg", "unknown error")
                    logger.error(f"Speech recognition failed (code: {error_code}): {error_msg}")
                    return None
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in DingTalk speech recognition: {str(e)}")
            return None
    
    def is_voice_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Check if the message contains voice/audio content.
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            True if message contains voice content, False otherwise
        """
        # Check for DingTalk audio message type
        msgtype = message_data.get("msgtype", "")
        if msgtype == "audio":
            return True
        
        # Check for voice message indicators
        message_type = message_data.get("message_type", "")
        extensions = message_data.get("extensions", {})
        
        # Common voice message indicators
        voice_indicators = [
            "voice", "audio", "speech", "recording", "sound"
        ]
        
        # Check message type
        if any(indicator in message_type.lower() for indicator in voice_indicators):
            return True
        
        # Check extensions for voice content
        if extensions:
            for key, value in extensions.items():
                if any(indicator in str(key).lower() or indicator in str(value).lower() 
                      for indicator in voice_indicators):
                    return True
        
        # Check for audio file attachments
        if "audio" in message_data or "voice" in message_data:
            return True
        
        return False
    
    def extract_audio_data(self, message_data: Dict[str, Any]) -> tuple[Optional[bytes], str]:
        """
        Extract audio data from message.
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            Tuple of (audio_data_bytes, audio_format) or (None, "wav") if not found
        """
        try:
            # Check for DingTalk audio message format
            if message_data.get("msgtype") == "audio":
                content = message_data.get("content", {})
                if isinstance(content, dict):
                    # DingTalk provides recognition text directly
                    recognition_text = content.get("recognition", "")
                    if recognition_text and recognition_text.strip():
                        logger.info(f"DingTalk provided recognition: {recognition_text}")
                        # Return the recognition text as if it were audio data
                        # This will be handled specially in the calling code
                        return recognition_text.strip().encode('utf-8'), "text"
                    else:
                        logger.warning("DingTalk audio message has no recognition text")
                        return None, "text"
            
            # Check for audio content in various locations
            audio_sources = [
                message_data.get("audio"),
                message_data.get("voice"),
                message_data.get("audio_content"),
                message_data.get("voice_content")
            ]
            
            for audio_source in audio_sources:
                if audio_source:
                    # Handle different audio data formats
                    if isinstance(audio_source, dict):
                        # Audio data might be in a nested structure
                        audio_data = audio_source.get("data") or audio_source.get("content")
                        audio_format = audio_source.get("format", "wav")
                        if audio_data:
                            return audio_data, audio_format
                    elif isinstance(audio_source, bytes):
                        # Try to detect format from message metadata
                        audio_format = message_data.get("audio_format", "wav")
                        return audio_source, audio_format
                    elif isinstance(audio_source, str):
                        # Base64 encoded audio data
                        try:
                            audio_format = message_data.get("audio_format", "wav")
                            return base64.b64decode(audio_source), audio_format
                        except:
                            pass
            
            logger.warning("No audio data found in message")
            return None, "wav"
            
        except Exception as e:
            logger.error(f"Error extracting audio data: {str(e)}")
            return None, "wav" 