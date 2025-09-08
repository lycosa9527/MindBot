#!/usr/bin/env python3
"""
Voice Recognition Service
Handles voice message processing for DingTalk integration
"""

from typing import Optional, Tuple, Any, Dict
from .logging_config import get_logger

logger = get_logger(__name__)

class VoiceRecognitionService:
    """Voice recognition service for DingTalk voice messages"""
    
    def __init__(self):
        self.logger = get_logger("VoiceRecognition")
        self.logger.info("Voice recognition service initialized")
    
    def is_voice_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Check if message contains voice data
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            True if message contains voice data, False otherwise
        """
        try:
            # Check for voice message indicators
            if "voice" in message_data:
                return True
            
            # Check for audio content
            if "audio" in message_data:
                return True
            
            # Check for media type indicators
            content_type = message_data.get("content_type", "")
            if "audio" in content_type.lower() or "voice" in content_type.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking voice message: {e}")
            return False
    
    def extract_audio_data(self, message_data: Dict[str, Any]) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Extract audio data from message
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            Tuple of (audio_data, audio_format) or (None, None) if not found
        """
        try:
            # Look for voice data
            if "voice" in message_data:
                voice_data = message_data["voice"]
                if isinstance(voice_data, dict):
                    audio_data = voice_data.get("data")
                    audio_format = voice_data.get("format", "unknown")
                    return audio_data, audio_format
            
            # Look for audio data
            if "audio" in message_data:
                audio_data = message_data["audio"]
                if isinstance(audio_data, dict):
                    data = audio_data.get("data")
                    format_type = audio_data.get("format", "unknown")
                    return data, format_type
            
            self.logger.warning("No audio data found in message")
            return None, None
            
        except Exception as e:
            self.logger.error(f"Error extracting audio data: {e}")
            return None, None
    
    async def convert_speech_to_text(self, audio_data: bytes, audio_format: str) -> Optional[str]:
        """
        Convert speech audio to text
        
        Args:
            audio_data: Raw audio data
            audio_format: Audio format (e.g., 'wav', 'mp3', 'amr')
            
        Returns:
            Transcribed text or None if conversion failed
        """
        try:
            self.logger.info(f"Converting speech to text (format: {audio_format}, size: {len(audio_data)} bytes)")
            
            # For Phase 1 POC, return a placeholder response
            # In production, this would integrate with actual speech recognition service
            if audio_data and len(audio_data) > 0:
                return "Voice message received (speech-to-text not implemented in POC)"
            else:
                self.logger.warning("Empty audio data provided")
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting speech to text: {e}")
            return None
    
    def get_supported_formats(self) -> list:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported audio format strings
        """
        return ["wav", "mp3", "amr", "aac", "ogg"]
    
    def is_format_supported(self, audio_format: str) -> bool:
        """
        Check if audio format is supported
        
        Args:
            audio_format: Audio format to check
            
        Returns:
            True if format is supported, False otherwise
        """
        return audio_format.lower() in self.get_supported_formats()