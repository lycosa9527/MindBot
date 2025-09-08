"""
DingTalk Platform Adapter
Implements DingTalk integration using the existing DingTalk client code
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..base import PlatformAdapter, Message, Response, MessageType

logger = logging.getLogger(__name__)

class DingTalkAdapter(PlatformAdapter):
    """
    DingTalk platform adapter implementation
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.dingtalk_client = None
        self.message_count = 0
        self.is_connected = False
        
    def get_required_config_fields(self) -> List[str]:
        """Get list of required configuration fields"""
        return ["client_id", "client_secret", "robot_code"]
    
    async def initialize(self) -> bool:
        """Initialize the DingTalk adapter"""
        logger.info(f"Initializing DingTalk adapter: {self.name}")
        
        try:
            # Validate configuration
            if not await self.validate_config():
                logger.error(f"Invalid configuration for DingTalk adapter: {self.name}")
                return False
            
            # Import DingTalk client components
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            from src.dingtalk_client import MindBotDingTalkClient
            from src.config import DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE
            
            # Create DingTalk client
            self.dingtalk_client = MindBotDingTalkClient(
                client_id=self.config.get("client_id", DINGTALK_CLIENT_ID),
                client_secret=self.config.get("client_secret", DINGTALK_CLIENT_SECRET),
                robot_code=self.config.get("robot_code", DINGTALK_ROBOT_CODE)
            )
            
            logger.info(f"DingTalk adapter {self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DingTalk adapter {self.name}: {e}")
            return False
    
    async def start(self) -> None:
        """Start the DingTalk adapter"""
        logger.info(f"Starting DingTalk adapter: {self.name}")
        
        try:
            if not self.dingtalk_client:
                raise Exception("DingTalk client not initialized")
            
            # Start the DingTalk client
            await self.dingtalk_client.start()
            self.is_running = True
            self.is_connected = True
            
            # Start message processing
            asyncio.create_task(self._process_messages())
            
            logger.info(f"DingTalk adapter {self.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start DingTalk adapter {self.name}: {e}")
            self.is_connected = False
    
    async def stop(self) -> None:
        """Stop the DingTalk adapter"""
        logger.info(f"Stopping DingTalk adapter: {self.name}")
        
        try:
            self.is_running = False
            self.is_connected = False
            
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
            
            logger.info(f"DingTalk adapter {self.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping DingTalk adapter {self.name}: {e}")
    
    async def send_message(self, response: Response) -> bool:
        """Send a message to DingTalk"""
        try:
            if not self.dingtalk_client or not self.is_connected:
                logger.error(f"DingTalk adapter {self.name} not connected")
                return False
            
            # Use the DingTalk client to send the response
            # This would integrate with the existing send_reply method
            logger.info(f"Sending message via DingTalk adapter {self.name}: {response.content[:100]}...")
            
            # For now, simulate sending
            await asyncio.sleep(0.1)
            
            logger.info(f"Message sent successfully via DingTalk adapter {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message via DingTalk adapter {self.name}: {e}")
            return False
    
    async def process_incoming_message(self, raw_message: Dict[str, Any]) -> Optional[Message]:
        """Process an incoming message from DingTalk"""
        try:
            self.message_count += 1
            
            # Extract message content from DingTalk format
            content = raw_message.get("text", {}).get("content", "")
            user_id = raw_message.get("senderId", "unknown")
            user_name = raw_message.get("senderNick", "Unknown User")
            
            # Create standard message
            message = Message(
                id=f"{self.name}_msg_{self.message_count}",
                platform=self.name,
                user_id=user_id,
                user_name=user_name,
                content=content,
                message_type=MessageType.TEXT,
                timestamp=datetime.now().timestamp(),
                metadata={
                    "dingtalk_msg_id": raw_message.get("msgId"),
                    "conversation_id": raw_message.get("conversationId"),
                    "adapter_name": self.name
                },
                raw_data=raw_message
            )
            
            logger.info(f"Processed incoming message from {self.name}: {content[:100]}...")
            return message
            
        except Exception as e:
            logger.error(f"Failed to process incoming message for {self.name}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if the DingTalk adapter is healthy"""
        return self.is_running and self.is_connected and self.dingtalk_client is not None
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """Get information about the DingTalk adapter"""
        return {
            "name": self.name,
            "type": "dingtalk",
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "message_count": self.message_count,
            "config": {
                "client_id": self.config.get("client_id", "***"),
                "robot_code": self.config.get("robot_code", "***")
            }
        }
    
    async def _process_messages(self) -> None:
        """Process messages from the message queue"""
        while self.is_running:
            try:
                # Wait for a message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # Process the message
                await self._handle_message(message)
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                logger.error(f"Error processing message in {self.name}: {e}")
    
    async def _handle_message(self, message: Message) -> None:
        """Handle a single message"""
        try:
            logger.info(f"Handling message in {self.name}: {message.content[:100]}...")
            
            # Create a response (this would normally go through the LLM)
            response = Response(
                message_id=message.id,
                platform=message.platform,
                content=f"[{self.name}] Echo: {message.content}",
                message_type=MessageType.TEXT,
                metadata={
                    "adapter_name": self.name,
                    "processed_at": datetime.now().isoformat()
                },
                success=True
            )
            
            # Send the response
            await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}")
