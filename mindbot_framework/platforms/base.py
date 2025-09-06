"""
Platform Adapter Base Class
Defines the interface for all platform integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages that can be processed"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"

@dataclass
class Message:
    """Standard message format for all platforms"""
    id: str
    platform: str
    user_id: str
    user_name: str
    content: str
    message_type: MessageType
    timestamp: float
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]

@dataclass
class Response:
    """Standard response format for all platforms"""
    message_id: str
    platform: str
    content: str
    message_type: MessageType
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class PlatformAdapter(ABC):
    """
    Base class for all platform adapters
    Defines the interface that all platform integrations must implement
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_running = False
        self.message_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.logger = logging.getLogger(f"platform.{name}")
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the platform adapter
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """
        Start the platform adapter
        Begin listening for messages and processing
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the platform adapter
        Clean up resources and stop processing
        """
        pass
    
    @abstractmethod
    async def send_message(self, response: Response) -> bool:
        """
        Send a message to the platform
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def process_incoming_message(self, raw_message: Dict[str, Any]) -> Optional[Message]:
        """
        Process an incoming message from the platform
        Convert platform-specific format to standard Message format
        Returns None if message should be ignored
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the platform adapter is healthy
        Returns True if healthy, False otherwise
        """
        pass
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """
        Get information about the platform
        Returns platform-specific information
        """
        return {
            "name": self.name,
            "is_running": self.is_running,
            "config": self.config
        }
    
    async def validate_config(self) -> bool:
        """
        Validate the platform configuration
        Returns True if valid, False otherwise
        """
        required_fields = self.get_required_config_fields()
        for field in required_fields:
            if field not in self.config:
                self.logger.error(f"Missing required config field: {field}")
                return False
        return True
    
    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """
        Get list of required configuration fields
        Returns list of field names that must be present in config
        """
        pass
    
    async def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors in the platform adapter
        Log error and potentially take recovery actions
        """
        self.logger.error(f"Error in {self.name} adapter: {error}")
        if context:
            self.logger.error(f"Context: {context}")
        
        # Override in subclasses for specific error handling
        pass
    
    async def get_message_queue(self) -> asyncio.Queue:
        """
        Get the message queue for this adapter
        Returns the queue where incoming messages are placed
        """
        return self.message_queue
    
    async def get_response_queue(self) -> asyncio.Queue:
        """
        Get the response queue for this adapter
        Returns the queue where outgoing responses are placed
        """
        return self.response_queue
    
    async def start_message_processing(self) -> None:
        """
        Start processing messages from the message queue
        This is a default implementation that can be overridden
        """
        self.logger.info(f"Starting message processing for {self.name}")
        
        while self.is_running:
            try:
                # Wait for a message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # Process the message
                await self._process_message(message)
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                await self.handle_error(e, "message processing")
    
    async def _process_message(self, message: Message) -> None:
        """
        Process a single message
        This is a default implementation that can be overridden
        """
        try:
            self.logger.info(f"Processing message from {message.user_name}: {message.content[:100]}...")
            
            # Create a response (this would normally go through the LLM)
            response = Response(
                message_id=message.id,
                platform=message.platform,
                content=f"Echo: {message.content}",
                message_type=MessageType.TEXT,
                metadata={},
                success=True
            )
            
            # Send the response
            await self.send_message(response)
            
        except Exception as e:
            await self.handle_error(e, f"processing message {message.id}")
    
    def __str__(self) -> str:
        return f"PlatformAdapter(name={self.name}, running={self.is_running})"
    
    def __repr__(self) -> str:
        return f"PlatformAdapter(name='{self.name}', config={self.config})"
