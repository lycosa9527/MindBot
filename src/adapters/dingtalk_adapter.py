"""
DingTalk Adapter Implementation
Integrates with existing DingTalk client for the enhanced multi-platform system
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Import our existing DingTalk client
from src.dingtalk_client import DingTalkStreamClient, MindBotChatbotHandler
from src.config import DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE

logger = logging.getLogger(__name__)

class DingTalkAdapter:
    """DingTalk adapter for the enhanced multi-platform system"""
    
    def __init__(self, adapter_id: str, config: Dict[str, Any]):
        self.adapter_id = adapter_id
        self.config = config
        
        # Extract configuration
        self.client_id = config.get("client_id", DINGTALK_CLIENT_ID)
        self.client_secret = config.get("client_secret", DINGTALK_CLIENT_SECRET)
        self.robot_code = config.get("robot_code", DINGTALK_ROBOT_CODE)
        self.card_template_id = config.get("card_template_id", "")
        self.enable_streaming = config.get("enable_streaming", True)
        
        # DingTalk client
        self.dingtalk_client: Optional[DingTalkStreamClient] = None
        self.chatbot_handler: Optional[MindBotChatbotHandler] = None
        
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
        """Initialize the DingTalk adapter"""
        try:
            logger.info(f"Initializing DingTalk adapter {self.adapter_id}")
            
            # Validate configuration
            if not self.client_id or not self.client_secret or not self.robot_code:
                raise ValueError("Missing required DingTalk configuration")
            
            # Create DingTalk client
            self.dingtalk_client = DingTalkStreamClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                robot_code=self.robot_code
            )
            
            # Create chatbot handler
            self.chatbot_handler = MindBotChatbotHandler(
                agent_handler=self._handle_message,
                dingtalk_client=self.dingtalk_client
            )
            
            # Set up the client with the handler
            self.dingtalk_client.set_chatbot_handler(self.chatbot_handler)
            
            self.is_initialized = True
            logger.info(f"DingTalk adapter {self.adapter_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DingTalk adapter {self.adapter_id}: {e}")
            raise
    
    async def start(self):
        """Start the DingTalk adapter"""
        if not self.is_initialized:
            raise RuntimeError("Adapter not initialized")
        
        if self.is_running:
            logger.warning(f"DingTalk adapter {self.adapter_id} already running")
            return
        
        try:
            logger.info(f"Starting DingTalk adapter {self.adapter_id}")
            
            # Start the DingTalk client
            await self.dingtalk_client.start()
            
            self.is_running = True
            self.stats["start_time"] = datetime.now()
            
            logger.info(f"DingTalk adapter {self.adapter_id} started successfully")
            
        except Exception as e:
            logger.error(f"Error starting DingTalk adapter {self.adapter_id}: {e}")
            raise
    
    async def run(self):
        """Run the DingTalk adapter (main message loop)"""
        if not self.is_running:
            raise RuntimeError("Adapter not started")
        
        try:
            # The DingTalk client handles the main message loop
            # This method is called by the RuntimeAdapter task wrapper
            while self.is_running:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info(f"DingTalk adapter {self.adapter_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in DingTalk adapter {self.adapter_id} run loop: {e}")
            self.stats["errors"] += 1
            raise
    
    async def stop(self):
        """Stop the DingTalk adapter"""
        if not self.is_running:
            logger.warning(f"DingTalk adapter {self.adapter_id} not running")
            return
        
        try:
            logger.info(f"Stopping DingTalk adapter {self.adapter_id}")
            
            # Stop the DingTalk client
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
            
            self.is_running = False
            logger.info(f"DingTalk adapter {self.adapter_id} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping DingTalk adapter {self.adapter_id}: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
            
            self.is_running = False
            self.is_initialized = False
            
            logger.info(f"DingTalk adapter {self.adapter_id} cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up DingTalk adapter {self.adapter_id}: {e}")
    
    def set_agent_handler(self, agent_handler: Callable[[str, Dict[str, Any]], str]):
        """Set the agent handler for processing messages"""
        self.agent_handler = agent_handler
    
    async def _handle_message(self, message: str, context: Dict[str, Any]) -> str:
        """Handle incoming messages from DingTalk"""
        try:
            self.stats["messages_received"] += 1
            
            # Add adapter context
            context.update({
                "adapter_id": self.adapter_id,
                "platform": "dingtalk",
                "timestamp": datetime.now().isoformat()
            })
            
            # Process with agent handler
            if self.agent_handler:
                response = await self.agent_handler(message, context)
                self.stats["messages_sent"] += 1
                return response
            else:
                logger.warning(f"No agent handler set for DingTalk adapter {self.adapter_id}")
                return "No agent handler available"
                
        except Exception as e:
            logger.error(f"Error handling message in DingTalk adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            return f"Error processing message: {str(e)}"
    
    async def send_message(self, target_type: str, target_id: str, message: Any):
        """Send message through DingTalk"""
        if not self.is_running:
            raise RuntimeError(f"DingTalk adapter {self.adapter_id} not running")
        
        try:
            # Use the existing DingTalk client to send messages
            if self.dingtalk_client:
                # This would use the existing send_message functionality
                # Implementation depends on the specific DingTalk client methods
                logger.info(f"Sending message via DingTalk adapter {self.adapter_id}")
                # TODO: Implement actual message sending
                self.stats["messages_sent"] += 1
            else:
                raise RuntimeError("DingTalk client not initialized")
                
        except Exception as e:
            logger.error(f"Error sending message via DingTalk adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            raise
    
    async def reply_message(self, message_source: Any, message: Any, quote_origin: bool = False):
        """Reply to a message through DingTalk"""
        if not self.is_running:
            raise RuntimeError(f"DingTalk adapter {self.adapter_id} not running")
        
        try:
            # Use the existing DingTalk client to reply to messages
            if self.dingtalk_client:
                # This would use the existing reply functionality
                logger.info(f"Replying to message via DingTalk adapter {self.adapter_id}")
                # TODO: Implement actual message replying
                self.stats["messages_sent"] += 1
            else:
                raise RuntimeError("DingTalk client not initialized")
                
        except Exception as e:
            logger.error(f"Error replying to message via DingTalk adapter {self.adapter_id}: {e}")
            self.stats["errors"] += 1
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            "adapter_id": self.adapter_id,
            "platform": "dingtalk",
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "stats": self.stats.copy(),
            "config": {
                "client_id": self.client_id,
                "robot_code": self.robot_code,
                "enable_streaming": self.enable_streaming
            }
        }
    
    def get_capabilities(self) -> list:
        """Get adapter capabilities"""
        return [
            "text_messages",
            "image_messages", 
            "voice_messages",
            "file_messages",
            "rich_text_messages",
            "ai_cards",
            "streaming_responses"
        ]
