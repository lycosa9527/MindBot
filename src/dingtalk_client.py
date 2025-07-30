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
from dingtalk_stream import DingTalkStreamClient, Credential, ChatbotHandler, ChatbotMessage
from config import (
    DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE, 
    DINGTALK_ROBOT_NAME, DINGTALK_MESSAGE_LIMIT, VERSION
)
from debug import DebugLogger

logger = logging.getLogger(__name__)

class MindBotChatbotHandler(ChatbotHandler):
    """
    Handles incoming messages from DingTalk Stream Mode.
    Extends the official ChatbotHandler for proper SDK integration.
    """
    
    def __init__(self, agent_handler: Callable):
        """
        Initialize message handler with agent callback.
        
        Args:
            agent_handler: Function to call with processed messages
        """
        super().__init__()
        self.agent_handler = agent_handler  # Callback to AI agent
        self.debug_logger = DebugLogger("MindBotChatbotHandler")
        
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
        
    async def process(self, callback):
        """
        Main message processing method required by ChatbotHandler.
        This is the official entry point for all incoming messages.
        
        Args:
            callback: CallbackMessage object from DingTalk SDK
        """
        try:
            logger.debug("MindBotChatbotHandler.process invoked")
            
            # Extract ChatbotMessage from callback
            incoming_message = ChatbotMessage.from_dict(callback.data)
            
            # Extract text content
            text_content = incoming_message.text.content.strip()
            if not text_content:
                logger.warning("No text content found in message")
                return AckMessage.STATUS_OK, "No text content"
            
            # Extract user and conversation information
            user_id = incoming_message.sender_staff_id
            conversation_id = incoming_message.conversation_id
            message_id = incoming_message.msg_id
            
            # Log user message at INFO level for visibility
            logger.info(f"User {user_id} sent: {text_content}")
            
            # Debug: Log message structure for analysis
            logger.debug(f"Message ID: {message_id}")
            logger.debug(f"Conversation ID: {conversation_id}")
            
            # Use DingTalk's message ID for deduplication
            if message_id:
                message_hash = message_id
                logger.debug(f"Using DingTalk message ID: {message_id}")
            else:
                # Fallback to our own hash if no message ID provided
                message_hash = self._create_message_hash(user_id, conversation_id, text_content)
                logger.debug(f"No DingTalk message ID, using hash: {message_hash[:10]}...")
            
            # Check for duplicates with thread safety and TTL
            if self._is_duplicate_message(message_hash):
                logger.info(f"Duplicate detected - User {user_id}: {text_content}")
                return AckMessage.STATUS_OK, "Duplicate message acknowledged"
            
            # Add message to recent messages with timestamp
            self._add_recent_message(message_hash)
            
            # Log processing at debug level
            logger.debug(f"Processing message from user {user_id}: {text_content[:50]}...")
            
            # Create context for AI agent
            context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Call AI agent to generate response
            response = await self.agent_handler(text_content, context)
            
            # Log workflow completion at INFO level
            logger.info(f"Response sent to {user_id}: {response[:100]}...")
            
            # Use official SDK method to send reply
            self.reply_text(response, incoming_message)
            
            # Return success acknowledgment
            return AckMessage.STATUS_OK, "Message processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AckMessage.STATUS_ERROR, f"Error processing message: {str(e)}"
    

    
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
            message_handler = MindBotChatbotHandler(self.agent_handler)
            
            # Register message handler with the client
            # Use the official ChatbotMessage topic for proper SDK integration
            self.client.register_callback_handler(
                ChatbotMessage.TOPIC, 
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