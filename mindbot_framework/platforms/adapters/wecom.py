"""
WeCom Platform Adapter
Implements WeCom (WeChat Work) integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..base import PlatformAdapter, Message, Response, MessageType

logger = logging.getLogger(__name__)

class WeComAdapter(PlatformAdapter):
    """
    WeCom (WeChat Work) platform adapter implementation
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.wecom_client = None
        self.message_count = 0
        self.is_connected = False
        
    def get_required_config_fields(self) -> List[str]:
        """Get list of required configuration fields"""
        return ["corp_id", "corp_secret", "agent_id"]
    
    async def initialize(self) -> bool:
        """Initialize the WeCom adapter"""
        logger.info(f"Initializing WeCom adapter: {self.name}")
        
        try:
            # Validate configuration
            if not await self.validate_config():
                logger.error(f"Invalid configuration for WeCom adapter: {self.name}")
                return False
            
            # TODO: Import WeCom client components when implemented
            # from ...src.wecom_client import MindBotWeComClient
            # from ...src.config import WECOM_CORP_ID, WECOM_CORP_SECRET, WECOM_AGENT_ID
            
            # For now, simulate WeCom client
            self.wecom_client = {"type": "wecom", "initialized": True}
            
            logger.info(f"WeCom adapter {self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WeCom adapter {self.name}: {e}")
            return False
    
    async def start(self) -> None:
        """Start the WeCom adapter"""
        logger.info(f"Starting WeCom adapter: {self.name}")
        
        try:
            if not self.wecom_client:
                raise Exception("WeCom client not initialized")
            
            # TODO: Start the WeCom client
            # await self.wecom_client.start()
            self.is_running = True
            self.is_connected = True
            
            # Start message processing
            asyncio.create_task(self._process_messages())
            
            logger.info(f"WeCom adapter {self.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start WeCom adapter {self.name}: {e}")
            self.is_connected = False
    
    async def stop(self) -> None:
        """Stop the WeCom adapter"""
        logger.info(f"Stopping WeCom adapter: {self.name}")
        
        try:
            self.is_running = False
            self.is_connected = False
            
            if self.wecom_client:
                # TODO: Stop the WeCom client
                # await self.wecom_client.stop()
                pass
            
            logger.info(f"WeCom adapter {self.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping WeCom adapter {self.name}: {e}")
    
    async def send_message(self, response: Response) -> bool:
        """Send a message to WeCom"""
        try:
            if not self.wecom_client or not self.is_connected:
                logger.error(f"WeCom adapter {self.name} not connected")
                return False
            
            # TODO: Use the WeCom client to send the response
            logger.info(f"Sending message via WeCom adapter {self.name}: {response.content[:100]}...")
            
            # For now, simulate sending
            await asyncio.sleep(0.1)
            
            logger.info(f"Message sent successfully via WeCom adapter {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message via WeCom adapter {self.name}: {e}")
            return False
    
    async def process_incoming_message(self, raw_message: Dict[str, Any]) -> Optional[Message]:
        """Process an incoming message from WeCom"""
        try:
            self.message_count += 1
            
            # Extract message content from WeCom format
            content = raw_message.get("Content", "")
            user_id = raw_message.get("FromUserName", "unknown")
            user_name = raw_message.get("FromUserName", "Unknown User")
            
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
                    "wecom_msg_id": raw_message.get("MsgId"),
                    "wecom_msg_type": raw_message.get("MsgType"),
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
        """Check if the WeCom adapter is healthy"""
        return self.is_running and self.is_connected and self.wecom_client is not None
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """Get information about the WeCom adapter"""
        return {
            "name": self.name,
            "type": "wecom",
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "message_count": self.message_count,
            "config": {
                "corp_id": self.config.get("corp_id", "***"),
                "agent_id": self.config.get("agent_id", "***")
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
