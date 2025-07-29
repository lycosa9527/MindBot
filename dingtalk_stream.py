from dingtalk_stream import AsyncDingTalkStreamClient
import logging
from config import DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE, VERSION

logger = logging.getLogger(__name__)

class DingTalkStreamClient:
    def __init__(self, agent_handler=None):
        self.client = AsyncDingTalkStreamClient(
            client_id=DINGTALK_CLIENT_ID,
            client_secret=DINGTALK_CLIENT_SECRET
        )
        self.agent_handler = agent_handler
        self.debug_logger = DebugLogger("DingTalkStream")
        
        # Register message handler
        self.client.on_chatbot_message = self._handle_message
        
        logger.info(f"DingTalk Stream Client {VERSION} initialized")
    
    async def _handle_message(self, message):
        """Handle incoming DingTalk messages"""
        try:
            if not message or not message.text or not message.text.strip():
                self.debug_logger.log_error("Received empty message")
                return
                
            self.debug_logger.log_info(f"Received message: {message.text[:50]}...")
            
            # Extract user information
            user_id = message.sender_staff_id or message.sender_union_id or "unknown"
            context = {
                "user_id": user_id,
                "conversation_id": message.conversation_id,
                "message_id": message.message_id
            }
            
            # Process message with agent
            if self.agent_handler:
                response = await self.agent_handler(message.text, context)
            else:
                response = "I'm sorry, the agent is not available right now."
            
            # Validate response
            if not response or not response.strip():
                response = "I'm sorry, I couldn't generate a response. Please try again."
            
            # Send reply
            await self.client.reply_message(
                message_id=message.message_id,
                content=response
            )
            
            self.debug_logger.log_info(f"Sent response: {response[:50]}...")
            
        except Exception as e:
            self.debug_logger.log_error(f"Error handling message: {str(e)}")
            # Send error response
            try:
                await self.client.reply_message(
                    message_id=message.message_id,
                    content="I'm sorry, I encountered an error processing your message. Please try again."
                )
            except Exception as reply_error:
                self.debug_logger.log_error(f"Error sending error response: {str(reply_error)}")
    
    async def start(self):
        """Start the DingTalk stream client"""
        try:
            self.debug_logger.log_info(f"Starting DingTalk Stream Client {VERSION}...")
            await self.client.start_forever()
        except Exception as e:
            self.debug_logger.log_error(f"Error starting stream client: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the DingTalk stream client"""
        try:
            self.debug_logger.log_info("Stopping DingTalk Stream Client...")
            await self.client.stop()
        except Exception as e:
            self.debug_logger.log_error(f"Error stopping stream client: {str(e)}")

class DebugLogger:
    def __init__(self, context: str):
        self.context = context
        self.logger = logging.getLogger(f"{context}")
    
    def log_info(self, message: str):
        self.logger.info(f"[{self.context}] {message}")
    
    def log_error(self, message: str):
        self.logger.error(f"[{self.context}] {message}")
    
    def log_debug(self, message: str):
        self.logger.debug(f"[{self.context}] {message}") 