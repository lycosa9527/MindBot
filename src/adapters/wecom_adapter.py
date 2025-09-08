"""
WeCom Adapter Implementation
Integrates with existing WeCom client for the enhanced multi-platform system
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Import our direct WeCom client (no webhooks)
from src.wecom_direct_client import WeComDirectClient

logger = logging.getLogger(__name__)

class WeComAdapter:
    """WeCom adapter for the enhanced multi-platform system"""
    
    def __init__(self, adapter_id: str, config: Dict[str, Any]):
        self.adapter_id = adapter_id
        self.config = config
        
        # Extract configuration
        self.corp_id = config.get("corp_id", "")
        self.corp_secret = config.get("corp_secret", "")
        self.agent_id = config.get("agent_id", "")
        # Remove webhook configuration - use direct API instead
        
        # WeCom client
        self.wecom_client: Optional[WeComDirectClient] = None
        
        # State
        self.is_initialized = False
        self.is_running = False
        self.agent_handler: Optional[Callable] = None
        
        # Statistics
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "errors": 0,
            "start_time": None
        }
    
    async def initialize(self):
        """Initialize the WeCom adapter"""
        try:
            logger.info(f"Initializing WeCom adapter {self.adapter_id}")
            
            # Validate configuration
            if not self.corp_id or not self.corp_secret or not self.agent_id:
                raise ValueError("Missing required WeCom configuration")
            
            # Create WeCom direct client
            self.wecom_client = WeComDirectClient(
                corp_id=self.corp_id,
                corp_secret=self.corp_secret,
                agent_id=self.agent_id
            )
            
            self.is_initialized = True
            logger.info(f"WeCom adapter {self.adapter_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WeCom adapter {self.adapter_id}: {e}")
            raise
    
    async def start(self):
        """Start the WeCom adapter"""
        if not self.is_initialized:
            raise RuntimeError("Adapter not initialized")
        
        if self.is_running:
            logger.warning(f"WeCom adapter {self.adapter_id} already running")
            return
        
        try:
            logger.info(f"Starting WeCom adapter {self.adapter_id}")
            
            # Start the WeCom client
            await self.wecom_client.start()
            
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            
            logger.info(f"WeCom adapter {self.adapter_id} started successfully")
            
        except Exception as e:
            logger.error(f"Error starting WeCom adapter {self.adapter_id}: {e}")
            raise
    
    async def run(self):
        """Run the WeCom adapter (main message loop)"""
        if not self.is_running:
            raise RuntimeError("Adapter not started")
        
        try:
            # WeCom direct client doesn't need a message loop
            # It's used for sending messages only
            # This method is called by the RuntimeAdapter task wrapper
            while self.is_running:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info(f"WeCom adapter {self.adapter_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in WeCom adapter {self.adapter_id} run loop: {e}")
            self.stats["errors"] += 1
            raise
    
    async def stop(self):
        """Stop the WeCom adapter"""
        if not self.is_running:
            logger.warning(f"WeCom adapter {self.adapter_id} not running")
            return
        
        try:
            logger.info(f"Stopping WeCom adapter {self.adapter_id}")
            
            # Stop the WeCom client
            if self.wecom_client:
                await self.wecom_client.stop()
            
            self.is_running = False
            logger.info(f"WeCom adapter {self.adapter_id} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping WeCom adapter {self.adapter_id}: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.wecom_client:
                await self.wecom_client.stop()
            
            self.is_running = False
            self.is_initialized = False
            
            logger.info(f"WeCom adapter {self.adapter_id} cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up WeCom adapter {self.adapter_id}: {e}")
    
    def set_agent_handler(self, agent_handler: Callable[[str, Dict[str, Any]], str]):
        """Set the agent handler for processing messages"""
        self.agent_handler = agent_handler
    
    async def _handle_message(self, message: str, context: Dict[str, Any]) -> str:
        """Handle incoming messages from WeCom"""
        try:
            self.stats["messages_received"] += 1
            
            # Add adapter context
            context.update({
                "adapter_id": self.adapter_id,
                "platform": "wecom",
                "timestamp": datetime.now().isoformat()
            })
            
            # Process with agent handler
            if self.agent_handler:
                response = await self.agent_handler(message, context)
                self.stats["messages_sent"] += 1
                return response
            else:
                logger.warning(f"No agent handler set for WeCom adapter {self.adapter_id}")
                return "No agent handler available"
                
        except Exception as e:
            logger.error(f"Error handling message in WeCom adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            return f"Error processing message: {str(e)}"
    
    async def send_message(self, target_type: str, target_id: str, message: Any):
        """Send message through WeCom"""
        if not self.is_running:
            raise RuntimeError(f"WeCom adapter {self.adapter_id} not running")
        
        try:
            # Use the direct WeCom client to send messages
            if self.wecom_client:
                success = await self.wecom_client.send_text_message(target_id, str(message))
                if success:
                    self.stats["messages_sent"] += 1
                    logger.info(f"Message sent via WeCom adapter {self.adapter_id} to {target_id}")
                else:
                    logger.error(f"Failed to send message via WeCom adapter {self.adapter_id}")
                    self.stats["errors"] += 1
            else:
                raise RuntimeError("WeCom client not initialized")
                
        except Exception as e:
            logger.error(f"Error sending message via WeCom adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            raise
    
    async def reply_message(self, message_source: Any, message: Any, quote_origin: bool = False):
        """Reply to a message through WeCom"""
        if not self.is_running:
            raise RuntimeError(f"WeCom adapter {self.adapter_id} not running")
        
        try:
            # Use the direct WeCom client to reply to messages
            if self.wecom_client:
                # Extract user ID from message source
                user_id = getattr(message_source, 'user_id', None) if message_source else None
                if not user_id:
                    logger.error("No user ID found in message source")
                    return
                
                success = await self.wecom_client.send_text_message(user_id, str(message))
                if success:
                    self.stats["messages_sent"] += 1
                    logger.info(f"Reply sent via WeCom adapter {self.adapter_id} to {user_id}")
                else:
                    logger.error(f"Failed to send reply via WeCom adapter {self.adapter_id}")
                    self.stats["errors"] += 1
            else:
                raise RuntimeError("WeCom client not initialized")
                
        except Exception as e:
            logger.error(f"Error replying to message via WeCom adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "adapter_id": self.adapter_id,
            "platform": "wecom",
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "stats": self.stats.copy(),
            "config": {
                "corp_id": self.corp_id,
                "agent_id": self.agent_id,
                "connection_type": "direct_api"
            }
        }
    
    def get_capabilities(self) -> list:
        """Get adapter capabilities"""
        return [
            "text_messages",
            "image_messages",
            "file_messages", 
            "markdown_messages",
            "direct_api_connection"
        ]
