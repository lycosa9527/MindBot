"""
Slack Platform Adapter
Implements Slack integration
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..base import PlatformAdapter, Message, Response, MessageType

logger = logging.getLogger(__name__)

class SlackAdapter(PlatformAdapter):
    """
    Slack platform adapter implementation
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.slack_client = None
        self.message_count = 0
        self.is_connected = False
        
    def get_required_config_fields(self) -> List[str]:
        """Get list of required configuration fields"""
        return ["bot_token", "signing_secret", "app_token"]
    
    async def initialize(self) -> bool:
        """Initialize the Slack adapter"""
        logger.info(f"Initializing Slack adapter: {self.name}")
        
        try:
            # Validate configuration
            if not await self.validate_config():
                logger.error(f"Invalid configuration for Slack adapter: {self.name}")
                return False
            
            # TODO: Import Slack client components when implemented
            # from ...src.slack_client import MindBotSlackClient
            # from ...src.config import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, SLACK_APP_TOKEN
            
            # For now, simulate Slack client
            self.slack_client = {"type": "slack", "initialized": True}
            
            logger.info(f"Slack adapter {self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Slack adapter {self.name}: {e}")
            return False
    
    async def start(self) -> None:
        """Start the Slack adapter"""
        logger.info(f"Starting Slack adapter: {self.name}")
        
        try:
            if not self.slack_client:
                raise Exception("Slack client not initialized")
            
            # TODO: Start the Slack client
            # await self.slack_client.start()
            self.is_running = True
            self.is_connected = True
            
            # Start message processing
            asyncio.create_task(self._process_messages())
            
            logger.info(f"Slack adapter {self.name} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Slack adapter {self.name}: {e}")
            self.is_connected = False
    
    async def stop(self) -> None:
        """Stop the Slack adapter"""
        logger.info(f"Stopping Slack adapter: {self.name}")
        
        try:
            self.is_running = False
            self.is_connected = False
            
            if self.slack_client:
                # TODO: Stop the Slack client
                # await self.slack_client.stop()
                pass
            
            logger.info(f"Slack adapter {self.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Slack adapter {self.name}: {e}")
    
    async def send_message(self, response: Response) -> bool:
        """Send a message to Slack"""
        try:
            if not self.slack_client or not self.is_connected:
                logger.error(f"Slack adapter {self.name} not connected")
                return False
            
            # TODO: Use the Slack client to send the response
            logger.info(f"Sending message via Slack adapter {self.name}: {response.content[:100]}...")
            
            # For now, simulate sending
            await asyncio.sleep(0.1)
            
            logger.info(f"Message sent successfully via Slack adapter {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message via Slack adapter {self.name}: {e}")
            return False
    
    async def process_incoming_message(self, raw_message: Dict[str, Any]) -> Optional[Message]:
        """Process an incoming message from Slack"""
        try:
            self.message_count += 1
            
            # Extract message content from Slack format
            content = raw_message.get("text", "")
            user_id = raw_message.get("user", "unknown")
            user_name = raw_message.get("user", "Unknown User")
            channel = raw_message.get("channel", "unknown")
            
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
                    "slack_ts": raw_message.get("ts"),
                    "slack_channel": channel,
                    "slack_thread_ts": raw_message.get("thread_ts"),
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
        """Check if the Slack adapter is healthy"""
        return self.is_running and self.is_connected and self.slack_client is not None
    
    async def get_platform_info(self) -> Dict[str, Any]:
        """Get information about the Slack adapter"""
        return {
            "name": self.name,
            "type": "slack",
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "message_count": self.message_count,
            "config": {
                "bot_token": self.config.get("bot_token", "***"),
                "app_token": self.config.get("app_token", "***")
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
