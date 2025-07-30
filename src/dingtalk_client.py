#!/usr/bin/env python3
"""
DingTalk Stream Client - WebSocket Integration
Handles real-time message reception and sending via DingTalk Stream Mode
"""

import asyncio
import aiohttp
import json
import logging
import ssl
import certifi
import threading
import hashlib
import time
from typing import Callable, Dict, Any
from dingtalk_stream import DingTalkStreamClient, Credential
from config import (
    DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE, 
    DINGTALK_ROBOT_NAME, DINGTALK_MESSAGE_LIMIT, VERSION
)
from debug import DebugLogger

logger = logging.getLogger(__name__)

class MessageHandler:
    """
    Handles incoming messages from DingTalk Stream Mode.
    This class processes raw WebSocket messages and extracts user content.
    """
    
    def __init__(self, agent_handler: Callable):
        """
        Initialize message handler with agent callback.
        
        Args:
            agent_handler: Function to call with processed messages
        """
        self.agent_handler = agent_handler  # Callback to AI agent
        self.debug_logger = DebugLogger("MessageHandler")
        
        # Initialize deduplication tracking with thread safety
        self._recent_messages = {}  # {message_hash: timestamp}
        self._dedup_lock = threading.Lock()
        self._max_recent_messages = 100
        self._message_ttl = 300  # 5 minutes TTL
        
    def pre_start(self):
        """
        Called before the stream starts - required by DingTalk stream library.
        This method is called by the library before starting the stream.
        """
        logger.info("MessageHandler pre_start called")
        # This method is required by the DingTalk SDK but not used in our implementation
        
    def __call__(self, message):
        """
        Main message processing method called by DingTalk SDK.
        This is the entry point for all incoming messages.
        
        Args:
            message: Raw message object from DingTalk WebSocket
        """
        # Process message directly to avoid duplication
        return self.raw_process(message)
    
    def raw_process(self, message):
        """
        Raw message processing method required by DingTalk SDK.
        This delegates to the main processing method to avoid duplication.
        
        Args:
            message: Raw message object from DingTalk WebSocket
        """
        # Delegate to main processing to avoid calling on_message twice
        try:
            # Extract message data for processing
            if message is None:
                logger.error("Received None message object")
                return None
            
            message_data = getattr(message, 'data', None)
            if message_data is None:
                logger.error("Message object has no data attribute")
                return None
                
            # Log only at debug level to reduce console verbosity
            logger.debug(f"Received message from {message_data.get('senderStaffId', 'unknown')}: {message_data.get('text', {}).get('content', '')[:50]}...")
            
            # Return the coroutine for async processing
            return self.on_message(message_data)
            
        except Exception as e:
            logger.error(f"Error in raw_process: {str(e)}")
            return None
    
    async def on_message(self, message_data: Dict[str, Any]):
        """
        Process incoming message data and generate AI response.
        
        Args:
            message_data: Parsed message data from DingTalk
        """
        try:
            # Extract text content from nested message structure
            # DingTalk messages have structure: data.text.content
            text_content = message_data.get("text", {}).get("content", "")
            
            if not text_content:
                logger.warning("No text content found in message")
                return
            
            # Extract user and conversation information for deduplication
            user_id = message_data.get("senderStaffId", "unknown")
            conversation_id = message_data.get("conversationId", "")
            
            # Create robust message hash for deduplication
            message_hash = self._create_message_hash(user_id, conversation_id, text_content)
            
            # Check for duplicates with thread safety and TTL
            if self._is_duplicate_message(message_hash):
                logger.info(f"Skipping duplicate message: {text_content[:30]}...")
                return
            
            # Add message to recent messages with timestamp
            self._add_recent_message(message_hash)
            
            # Extract session webhook for sending replies
            session_webhook = message_data.get("sessionWebhook", "")
            if not session_webhook:
                logger.error("No session webhook found in message")
                return
            
            # Create context for AI agent
            context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_webhook": session_webhook
            }
            
            # Log only at debug level to reduce console verbosity
            logger.debug(f"Processing message from user {user_id}: {text_content[:50]}...")
            
            # Call AI agent to generate response
            response = await self.agent_handler(text_content, context)
            
            # Send response back to DingTalk via session webhook
            await self.send_reply(session_webhook, response)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Try to send error response if possible
            session_webhook = message_data.get("sessionWebhook", "")
            if session_webhook:
                await self.send_error_response(session_webhook)
    
    def _create_message_hash(self, user_id: str, conversation_id: str, text_content: str) -> str:
        """
        Create a robust hash for message deduplication.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            text_content: Message text content
            
        Returns:
            SHA-256 hash of the message components
        """
        # Create a unique string combining all message components
        message_string = f"{user_id}:{conversation_id}:{text_content}"
        # Generate SHA-256 hash for robust deduplication
        return hashlib.sha256(message_string.encode('utf-8')).hexdigest()
    
    def _is_duplicate_message(self, message_hash: str) -> bool:
        """
        Check if message is a duplicate with thread safety and TTL.
        
        Args:
            message_hash: Hash of the message to check
            
        Returns:
            True if message is a duplicate, False otherwise
        """
        current_time = time.time()
        
        with self._dedup_lock:
            # Check if message exists and is within TTL
            if message_hash in self._recent_messages:
                timestamp = self._recent_messages[message_hash]
                if current_time - timestamp < self._message_ttl:
                    return True
                else:
                    # Remove expired message
                    del self._recent_messages[message_hash]
            
            return False
    
    def _add_recent_message(self, message_hash: str) -> None:
        """
        Add message to recent messages with cleanup.
        
        Args:
            message_hash: Hash of the message to add
        """
        current_time = time.time()
        
        with self._dedup_lock:
            # Add new message
            self._recent_messages[message_hash] = current_time
            
            # Cleanup expired messages
            expired_hashes = [
                hash_key for hash_key, timestamp in self._recent_messages.items()
                if current_time - timestamp > self._message_ttl
            ]
            for hash_key in expired_hashes:
                del self._recent_messages[hash_key]
            
            # If still too many messages, remove oldest
            if len(self._recent_messages) > self._max_recent_messages:
                # Sort by timestamp and keep only the newest
                sorted_messages = sorted(
                    self._recent_messages.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                self._recent_messages = dict(sorted_messages[:self._max_recent_messages // 2])
    
    async def send_reply(self, session_webhook: str, message: str):
        """
        Send reply message to DingTalk via session webhook.
        
        Args:
            session_webhook: Webhook URL for sending replies
            message: Response message to send
        """
        try:
            # Validate message length to prevent API errors
            if len(message) > DINGTALK_MESSAGE_LIMIT:
                message = message[:DINGTALK_MESSAGE_LIMIT] + "..."
                logger.warning(f"Message truncated to {DINGTALK_MESSAGE_LIMIT} characters")
            
            # Prepare payload for DingTalk message API
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            # Set up headers for HTTP request
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Sending reply via webhook: {message[:50]}...")
            
            # Send HTTP POST request to session webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(session_webhook, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.debug("Reply sent successfully")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send reply: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error sending reply: {str(e)}")
    
    async def send_error_response(self, session_webhook: str, error_message: str = "I'm sorry, I encountered an error processing your message."):
        """
        Send error response to user when message processing fails.
        
        Args:
            session_webhook: Webhook URL for sending replies
            error_message: Error message to send to user
        """
        try:
            await self.send_reply(session_webhook, error_message)
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")

class MindBotDingTalkClient:
    """
    DingTalk Stream Mode client for real-time message handling.
    This class manages WebSocket connection and message routing.
    """
    
    def __init__(self, agent_handler: Callable):
        """
        Initialize DingTalk client with agent handler.
        
        Args:
            agent_handler: Function to call with processed messages
        """
        self.agent_handler = agent_handler  # AI agent callback
        self.client = None  # DingTalk WebSocket client
        self.client_thread = None  # Thread for client connection
        self.running = False  # Client running state
        self.debug_logger = DebugLogger("DingTalkClient")
        
        # Validate required configuration
        if not DINGTALK_CLIENT_ID:
            raise ValueError("DINGTALK_CLIENT_ID is not set")
        if not DINGTALK_CLIENT_SECRET:
            raise ValueError("DINGTALK_CLIENT_SECRET is not set")
        if not DINGTALK_ROBOT_CODE:
            raise ValueError("DINGTALK_ROBOT_CODE is not set")
        
        logger.info("MindBotDingTalkClient initialized successfully")
    
    async def start(self):
        """
        Start the DingTalk WebSocket client and begin listening for messages.
        This establishes the real-time connection to DingTalk Stream Mode.
        """
        try:
            logger.info("Starting DingTalk Stream Client...")
            
            # Create credentials for DingTalk API authentication
            credential = Credential(
                client_id=DINGTALK_CLIENT_ID,
                client_secret=DINGTALK_CLIENT_SECRET
            )
            
            # Initialize DingTalk Stream client
            self.client = DingTalkStreamClient(credential)
            
            # Create message handler for processing incoming messages
            message_handler = MessageHandler(self.agent_handler)
            
            # Register message handler with the client
            # This connects to the specific topic for bot messages
            self.client.register_callback_handler(
                "/v1.0/im/bot/messages/get", 
                message_handler
            )
            
            logger.info("DingTalk client configured successfully")
            
            # Start the client in a separate thread to avoid blocking
            self.client_thread = threading.Thread(
                target=self._run_client,
                daemon=True
            )
            self.client_thread.start()
            
            self.running = True
            logger.info("DingTalk Stream Client started successfully")
            
        except Exception as e:
            logger.error(f"Error starting DingTalk client: {str(e)}")
            raise
    
    def _run_client(self):
        """
        Run the DingTalk client in a separate thread.
        This method handles the WebSocket connection and message processing.
        """
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start the client and begin listening for messages
            loop.run_until_complete(self.client.start())
        except Exception as e:
            logger.error(f"Error in DingTalk client thread: {str(e)}")
        finally:
            # Clean up the event loop
            try:
                loop.close()
            except:
                pass
    
    async def stop(self):
        """
        Stop the DingTalk client and close all connections.
        This ensures clean shutdown without resource leaks.
        """
        try:
            logger.info("Stopping DingTalk Stream Client...")
            self.running = False
            
            # Stop the client connection if it exists
            if self.client:
                try:
                    # Try to close the client connection properly
                    if hasattr(self.client, 'close'):
                        await self.client.close()
                    elif hasattr(self.client, 'stop'):
                        await self.client.stop()
                    logger.info("DingTalk client connection closed")
                except Exception as close_error:
                    logger.error(f"Error closing client connection: {close_error}")
            
            # Wait for client thread to finish if it exists
            if self.client_thread and self.client_thread.is_alive():
                self.client_thread.join(timeout=5)
                if self.client_thread.is_alive():
                    logger.warning("Client thread did not stop within timeout")
            
            logger.info("DingTalk Stream Client stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping DingTalk client: {str(e)}")
    
    async def test_connection(self) -> bool:
        """
        Test the connection to DingTalk API to verify configuration.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing DingTalk API connection...")
            
            # Create test credentials
            credential = Credential(
                client_id=DINGTALK_CLIENT_ID,
                client_secret=DINGTALK_CLIENT_SECRET
            )
            
            # Test client creation
            test_client = DingTalkStreamClient(credential)
            
            logger.info("DingTalk API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"DingTalk API connection test failed: {str(e)}")
            return False 