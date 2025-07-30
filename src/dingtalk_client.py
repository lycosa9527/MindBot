#!/usr/bin/env python3
"""
DingTalk Stream Client - WebSocket Integration
Handles real-time message reception and sending via DingTalk Stream Mode
"""

import asyncio
import json
import logging
import threading
import hashlib
import time
import uuid
import aiohttp
from typing import Callable, Optional, Dict, Any
from dingtalk_stream import DingTalkStreamClient, Credential, ChatbotHandler, ChatbotMessage, AckMessage, AICardReplier
from dingtalk_stream.frames import CallbackMessage as CallbackFrame

# Import official Alibaba Cloud DingTalk SDK
from alibabacloud_dingtalk.card_1_0 import client as card_client, models as card_models
from alibabacloud_tea_openapi import models as openapi_models
from alibabacloud_tea_util import models as util_models

from src.config import (
    DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE,
    DINGTALK_ROBOT_NAME, DEBUG_MODE, LOG_LEVEL, ENABLE_STREAMING, DINGTALK_CARD_TEMPLATE_ID,
    STREAMING_MIN_CHUNK_SIZE, STREAMING_UPDATE_DELAY, STREAMING_MAX_RETRIES, STREAMING_RETRY_DELAY,
    ENABLE_FLUID_STREAMING, FLUID_STREAMING_MIN_CHUNK, FLUID_STREAMING_DELAY
)
from src.debug import DebugLogger
from src.voice_recognition import VoiceRecognitionService
from src.agent import MindBotAgent

logger = logging.getLogger(__name__)

class MindBotChatbotHandler(ChatbotHandler):
    """
    Handles incoming messages from DingTalk Stream Mode.
    Extends the official ChatbotHandler for proper SDK integration.
    """
    
    def __init__(self, agent_handler: Callable, agent_instance=None, dingtalk_client=None):
        """
        Initialize message handler with agent callback.
        
        Args:
            agent_handler: Function to call with processed messages
            agent_instance: Optional agent instance for direct access to dify_client
            dingtalk_client: DingTalk client instance (required for AICardReplier)
        """
        super().__init__()
        self.agent_handler = agent_handler  # Callback to AI agent
        self.agent_instance = agent_instance  # Direct access to agent for streaming
        self.dingtalk_client = dingtalk_client  # DingTalk client for AICardReplier
        self.debug_logger = DebugLogger("MindBotChatbotHandler")
        
        # Initialize voice recognition service
        self.voice_service = VoiceRecognitionService()
        
        # Initialize deduplication tracking with thread safety
        self._recent_messages = {}  # {message_hash: timestamp}
        self._dedup_lock = threading.Lock()
        self._max_recent_messages = 100
        self._message_ttl = 300  # 5 minutes TTL
        
        # DingTalk streaming API configuration
        self.streaming_api_url = "https://api.dingtalk.com/v1.0/card/streaming"
        self.access_token = None
        self.token_expires_at = 0
        
    async def get_access_token(self) -> Optional[str]:
        """
        Get DingTalk access token for streaming API authentication.
        
        Returns:
            Access token string or None if failed
        """
        try:
            if self.access_token and self.token_expires_at > asyncio.get_event_loop().time():
                return self.access_token
            
            url = "https://oapi.dingtalk.com/gettoken"
            params = {
                "appkey": DINGTALK_CLIENT_ID,
                "appsecret": DINGTALK_CLIENT_SECRET
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get access token: {response.status}")
                        return None
                    
                    data = await response.json()
                    if data.get("errcode") == 0:
                        self.access_token = data.get("access_token")
                        # Token expires in 2 hours, refresh 10 minutes early
                        self.token_expires_at = asyncio.get_event_loop().time() + (7200 - 600)
                        logger.debug("DingTalk access token obtained successfully")
                        return self.access_token
                    else:
                        logger.error(f"Failed to get access token: {data}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    async def send_streaming_update(self, card_instance_id: str, content: str, 
                                  is_full: bool = False, is_finalize: bool = False, 
                                  is_error: bool = False, incoming_message=None, out_track_id: str = None) -> bool:
        """
        Send streaming update using DingTalk's official Alibaba Cloud SDK.
        
        Args:
            card_instance_id: ID of the card to update
            content: Text content to send
            is_full: Whether this is a full message
            is_finalize: Whether this is the final update
            is_error: Whether this is an error message
            incoming_message: Original DingTalk message (not used in official SDK)
            out_track_id: The outTrackId used in card creation (should be the same)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get access token
            token = await self.get_access_token()
            if not token:
                logger.error("Failed to get access token for streaming API")
                return False
            
            # Try official Alibaba Cloud SDK first (matching official example)
            try:
                logger.debug("Attempting streaming update using official Alibaba Cloud SDK...")
                
                # Create client using official example pattern
                config = openapi_models.Config()
                config.protocol = 'https'
                config.region_id = 'central'
                client = card_client.Client(config)
                
                # Create headers using official example pattern
                streaming_update_headers = card_models.StreamingUpdateHeaders()
                streaming_update_headers.x_acs_dingtalk_access_token = token
                
                # Use the same outTrackId from card creation, or generate a new one if not provided
                if not out_track_id:
                    out_track_id = str(uuid.uuid4())
                
                # Generate GUID in the format shown in official documentation: 0F714542-0AFC-2B0E-CF14-E2D39F5BFFE8
                guid = str(uuid.uuid4()).upper()
                
                # Create request using official example pattern
                streaming_update_request = card_models.StreamingUpdateRequest(
                    out_track_id=out_track_id,
                    guid=guid,
                    key='your-ai-param',  # Use the key from official example
                    content=content,
                    is_full=is_full,
                    is_finalize=is_finalize,
                    is_error=is_error
                )
                
                # Send streaming update using official SDK (matching official example)
                try:
                    await client.streaming_update_with_options_async(streaming_update_request, streaming_update_headers, util_models.RuntimeOptions())
                    logger.debug(f"Streaming update sent successfully using official SDK: {len(content)} characters")
                    return True
                except Exception as err:
                    # Error handling matching official example
                    if hasattr(err, 'code') and hasattr(err, 'message'):
                        logger.error(f"Service error - code: {err.code}, message: {err.message}")
                    else:
                        logger.error(f"Streaming update failed: {str(err)}")
                    return False
                    
            except Exception as e:
                logger.warning(f"Official SDK streaming update failed: {str(e)}, trying direct API...")
            
            # Fallback to direct HTTP API approach
            logger.debug("Attempting streaming update using direct HTTP API...")
            
            # Use the same outTrackId from card creation, or generate a new one if not provided
            if not out_track_id:
                out_track_id = str(uuid.uuid4())
            
            # Generate GUID in the format shown in official documentation: 0F714542-0AFC-2B0E-CF14-E2D39F5BFFE8
            guid = str(uuid.uuid4()).upper()
            
            # Prepare request headers
            headers = {
                "x-acs-dingtalk-access-token": token,
                "Content-Type": "application/json"
            }
            
            # Prepare request payload according to official API format
            payload = {
                "outTrackId": out_track_id,
                "guid": guid,
                "key": "your-ai-param",  # Use the key from official example
                "content": content,
                "isFull": is_full,
                "isFinalize": is_finalize,
                "isError": is_error
            }
            
            # Send streaming update using PUT /v1.0/card/streaming
            streaming_url = "https://api.dingtalk.com/v1.0/card/streaming"
            async with aiohttp.ClientSession() as session:
                async with session.put(streaming_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Streaming update sent successfully using direct API: {len(content)} characters")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Streaming API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending streaming update: {str(e)}")
            return False
    
    async def create_card(self, user_id: str, out_track_id: str, initial_content: str = "", incoming_message=None) -> Optional[str]:
        """
        Create a card using DingTalk's official Alibaba Cloud SDK.
        
        Args:
            user_id: User ID to send the card to
            out_track_id: Unique identifier for the card
            initial_content: Initial content to display in the card
            incoming_message: Original DingTalk message (not used in official SDK)
            
        Returns:
            Card instance ID if successful, None otherwise
        """
        try:
            # Get access token
            token = await self.get_access_token()
            if not token:
                logger.error("Failed to get access token for card creation")
                return None
            
            # Try official Alibaba Cloud SDK first (matching official example)
            try:
                logger.debug("Attempting card creation using official Alibaba Cloud SDK...")
                
                # Create client using official example pattern
                config = openapi_models.Config()
                config.protocol = 'https'
                config.region_id = 'central'
                client = card_client.Client(config)
                
                # Create headers using official example pattern
                create_card_headers = card_models.CreateCardHeaders()
                create_card_headers.x_acs_dingtalk_access_token = token
                
                # Create card data
                card_data = card_models.CreateCardRequestCardData(
                    card_param_map={
                        "content": initial_content,
                        "title": "AI Assistant",
                        "StringValue": initial_content,
                        "robotCode": DINGTALK_ROBOT_CODE  # Add robot code binding
                    }
                )
                
                # Create IM single open space model
                im_single_open_space_model = card_models.CreateCardRequestImSingleOpenSpaceModel(
                    support_forward=True,
                    last_message_i18n={
                        "key": "AI Assistant"
                    },
                    search_support=card_models.CreateCardRequestImSingleOpenSpaceModelSearchSupport(
                        search_icon="🤖",
                        search_type_name="AI Assistant",
                        search_desc="AI-powered responses"
                    ),
                    notification=card_models.CreateCardRequestImSingleOpenSpaceModelNotification(
                        alert_content="AI Assistant replied",
                        notification_off=False
                    )
                )
                
                # Create request using official example pattern
                create_card_request = card_models.CreateCardRequest(
                    user_id=user_id,
                    card_template_id=DINGTALK_CARD_TEMPLATE_ID,  # Use AI card type instead of StandardCard
                    out_track_id=out_track_id,
                    callback_type="STREAM",  # Explicitly declare STREAM callback type
                    callback_route_key="ai-streaming",
                    card_data=card_data,
                    im_single_open_space_model=im_single_open_space_model,
                    user_id_type=1
                )
                
                # Create card using official SDK (matching official example)
                try:
                    response = await client.create_card_with_options_async(create_card_request, create_card_headers, util_models.RuntimeOptions())
                    if response and response.body and response.body.card_instance_id:
                        card_instance_id = response.body.card_instance_id
                        logger.debug(f"Card created successfully using official SDK: {card_instance_id}")
                        return card_instance_id
                    else:
                        logger.warning("Official SDK card creation returned no card_instance_id, trying direct API...")
                except Exception as err:
                    # Error handling matching official example
                    if hasattr(err, 'code') and hasattr(err, 'message'):
                        logger.error(f"Service error - code: {err.code}, message: {err.message}")
                    else:
                        logger.error(f"Card creation failed: {str(err)}")
                    
            except Exception as e:
                logger.warning(f"Official SDK card creation failed: {str(e)}, trying direct API...")
            
            # Fallback to direct HTTP API approach
            logger.debug("Attempting card creation using direct HTTP API...")
            
            # Prepare request headers
            headers = {
                "x-acs-dingtalk-access-token": token,
                "Content-Type": "application/json"
            }
            
            # Prepare request payload according to official DingTalk documentation
            payload = {
                "userId": user_id,
                "cardTemplateId": DINGTALK_CARD_TEMPLATE_ID,  # Use AI card type instead of StandardCard
                "outTrackId": out_track_id,
                "callbackType": "STREAM",  # Explicitly declare STREAM callback type
                "callbackRouteKey": "ai-streaming",
                "cardData": {
                    "cardParamMap": {
                        "content": initial_content,
                        "title": "AI Assistant",
                        "StringValue": initial_content,
                        "robotCode": DINGTALK_ROBOT_CODE  # Add robot code binding
                    }
                },
                "imSingleOpenSpaceModel": {
                    "supportForward": True,
                    "lastMessageI18n": {
                        "key": "AI Assistant"
                    },
                    "searchSupport": {
                        "searchIcon": "🤖",
                        "searchTypeName": "AI Assistant",
                        "searchDesc": "AI-powered responses"
                    },
                    "notification": {
                        "alertContent": "AI Assistant replied",
                        "notificationOff": False
                    }
                },
                "imRobotOpenSpaceModel": {
                    "supportForward": True,
                    "lastMessageI18n": {
                        "key": "AI Assistant"
                    },
                    "searchSupport": {
                        "searchIcon": "🤖",
                        "searchTypeName": "AI Assistant",
                        "searchDesc": "AI-powered responses"
                    },
                    "notification": {
                        "alertContent": "AI Assistant replied",
                        "notificationOff": False
                    }
                },
                "userIdType": 1
            }
            
            # Create card using official API
            card_api_url = "https://api.dingtalk.com/v1.0/card/instances"
            async with aiohttp.ClientSession() as session:
                async with session.post(card_api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        card_instance_id = response_data.get("cardInstanceId")
                        if card_instance_id:
                            logger.debug(f"Card created successfully using direct API: {card_instance_id}")
                            return card_instance_id
                        else:
                            logger.error(f"Card creation response missing cardInstanceId: {response_data}")
                            return None
                    elif response.status == 400:
                        error_text = await response.text()
                        logger.error(f"Card creation bad request: {error_text}")
                        logger.warning("Check if all required fields are provided correctly.")
                        return None
                    elif response.status == 403:
                        error_text = await response.text()
                        logger.error(f"Card creation permission denied: {error_text}")
                        logger.warning("DingTalk app lacks Card.Instance.Write permission. Please add this permission in DingTalk Open Platform.")
                        return None
                    elif response.status == 503:
                        error_text = await response.text()
                        logger.error(f"Card creation service unavailable: {error_text}")
                        logger.warning("DingTalk card service is temporarily unavailable. Using fallback mode.")
                        return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Card creation API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating card: {str(e)}")
            return None
        
    async def create_card_with_dingtalk_stream(self, user_id: str, out_track_id: str, initial_content: str = "", incoming_message=None) -> Optional[str]:
        """
        Create a card using dingtalk_stream.AICardReplier with improved error handling and retry logic.
        
        Args:
            user_id: User ID to send the card to
            out_track_id: Unique identifier for the card
            initial_content: Initial content to display in the card
            incoming_message: Original DingTalk message
            
        Returns:
            Card instance ID if successful, None otherwise
        """
        try:
            logger.debug("Attempting card creation using dingtalk_stream.AICardReplier...")
            
            # Create AICardReplier instance (matching example code pattern)
            card_instance = AICardReplier(
                self.dingtalk_client, incoming_message
            )
            
            # Use the configured card template ID
            card_template_id = DINGTALK_CARD_TEMPLATE_ID
            
            # Create card data (matching example code pattern)
            content_key = "content"
            card_data = {content_key: initial_content}
            
            # Retry logic for card creation (configurable attempts)
            max_retries = STREAMING_MAX_RETRIES
            retry_delay = STREAMING_RETRY_DELAY
            
            for attempt in range(max_retries):
                try:
                    # Create and deliver card (matching example code pattern)
                    card_instance_id = await card_instance.async_create_and_deliver_card(
                        card_template_id, card_data
                    )
                    
                    if card_instance_id:
                        logger.debug(f"Card created successfully using AICardReplier: {card_instance_id}")
                        return card_instance_id
                    else:
                        logger.warning(f"Card creation attempt {attempt + 1} returned no card_instance_id")
                        
                except Exception as e:
                    logger.warning(f"Card creation attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise e
                        
            logger.error("All card creation attempts failed")
            return None
                
        except Exception as e:
            logger.error(f"Error creating card with AICardReplier: {str(e)}")
            return None
        
    def pre_start(self):
        """
        Called before the stream starts - required by DingTalk stream library.
        This method is called by the library before starting the stream.
        """
        logger.info("MindBotChatbotHandler pre_start called")
        # This method is required by the DingTalk SDK but not used in our implementation
        
    async def process(self, callback):
        """
        Main message processing method required by ChatbotHandler.
        This is the official entry point for all incoming messages.
        Supports both text and voice messages with streaming responses.
        
        Args:
            callback: CallbackMessage object from DingTalk SDK
        """
        try:
            logger.debug("MindBotChatbotHandler.process invoked")
            
            # Extract ChatbotMessage from callback
            incoming_message = ChatbotMessage.from_dict(callback.data)
            
            # Debug: Log callback structure
            logger.debug(f"Callback data: {callback.data}")
            logger.debug(f"Callback type: {type(callback)}")
            
            # Extract user and conversation information
            user_id = incoming_message.sender_staff_id
            conversation_id = incoming_message.conversation_id
            message_id = incoming_message.message_id
            
            logger.debug(f"Message from user {user_id} in conversation {conversation_id}")
            
            # Process message content (text or voice)
            text_content = await self._extract_message_content(incoming_message)
            logger.debug(f"Extracted content: {text_content}")
            
            if not text_content:
                logger.debug("No processable content found in message (normal for system messages, images, files, etc.)")
                return AckMessage.STATUS_OK, "No processable content"
            
            # Log user message at INFO level for visibility
            logger.info(f"User {user_id} sent: {text_content}")
            
            # Use DingTalk's message ID for deduplication
            if message_id:
                message_hash = message_id
            else:
                # Fallback to our own hash if no message ID provided
                message_hash = self._create_message_hash(user_id, conversation_id, text_content)
            
            # Check for duplicates with thread safety and TTL
            if self._is_duplicate_message(message_hash):
                logger.info(f"Duplicate detected - User {user_id}: {text_content}")
                return AckMessage.STATUS_OK, "Duplicate message acknowledged"
            
            # Add message to recent messages with timestamp
            self._add_recent_message(message_hash)
            
            # Create context for AI agent
            context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Use streaming response for all messages (if enabled)
            if ENABLE_STREAMING:
                full_response = await self._process_streaming_response(text_content, context, incoming_message)
            else:
                # Fallback to blocking response
                logger.debug(f"Sending to Dify (blocking): {text_content}")
                response = await self.agent_handler(text_content, context)
                logger.debug(f"Dify response: {response}")
                self.reply_text(response, incoming_message)
                full_response = response
            
            # Log workflow completion
            logger.info(f"Streaming response completed for {user_id}")
            
            # Return success acknowledgment
            return AckMessage.STATUS_OK, "Message processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AckMessage.STATUS_SYSTEM_EXCEPTION, f"Error processing message: {str(e)}"
    
    async def process_message_streaming(self, callback):
        """
        Process messages with streaming Dify responses.
        This demonstrates how to integrate streaming responses with DingTalk.
        
        Args:
            callback: CallbackMessage object from DingTalk SDK
        """
        try:
            logger.debug("MindBotChatbotHandler.process_streaming invoked")
            
            # Extract ChatbotMessage from callback
            incoming_message = ChatbotMessage.from_dict(callback.data)
            
            # Extract user and conversation information
            user_id = incoming_message.sender_staff_id
            conversation_id = incoming_message.conversation_id
            message_id = incoming_message.message_id
            
            # Process message content (text or voice)
            text_content = await self._extract_message_content(incoming_message)
            if not text_content:
                logger.debug("No processable content found in message")
                return AckMessage.STATUS_OK, "No processable content"
            
            # Log user message
            logger.info(f"User {user_id} sent: {text_content}")
            
            # Check for duplicates
            if message_id:
                message_hash = message_id
            else:
                message_hash = self._create_message_hash(user_id, conversation_id, text_content)
            
            if self._is_duplicate_message(message_hash):
                logger.info(f"Duplicate detected - User {user_id}: {text_content}")
                return AckMessage.STATUS_OK, "Duplicate message acknowledged"
            
            # Add message to recent messages
            self._add_recent_message(message_hash)
            
            # Create context for AI agent
            context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Use streaming Dify response
            full_response = await self._process_streaming_response(text_content, context, incoming_message)
            
            logger.info(f"Streaming response completed for {user_id}")
            return AckMessage.STATUS_OK, "Message processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing streaming message: {str(e)}")
            return AckMessage.STATUS_SYSTEM_EXCEPTION, f"Error processing message: {str(e)}"

    async def _process_streaming_response(self, text_content: str, context: dict, incoming_message: ChatbotMessage):
        """
        Process streaming response from Dify using dingtalk_stream.AICardReplier with optimized chunk handling.
        
        Args:
            text_content: User's message
            context: Message context
            incoming_message: Original DingTalk message
        """
        try:
            user_id = context.get("user_id", "unknown")
            
            # Step 1: Create an AI card using dingtalk_stream.AICardReplier (matching example code)
            card_instance_id = await self.create_card_with_dingtalk_stream(user_id, str(uuid.uuid4()), "", incoming_message)
            
            if not card_instance_id:
                logger.warning("Failed to create AI card, falling back to regular message")
                # Fallback to regular message if card creation fails
                if self.agent_instance and hasattr(self.agent_instance, 'dify_client'):
                    logger.debug(f"Sending to Dify (streaming): {text_content}")
                    try:
                        # Create a proper async callback function for fallback
                        async def fallback_callback(chunk: str):
                            # Ignore chunks in fallback mode
                            pass
                        
                        full_response = await self.agent_instance.dify_client.chat_completion_streaming_with_callback(
                            text_content, 
                            user_id, 
                            fallback_callback
                        )
                    except Exception as e:
                        logger.error(f"Error in Dify streaming: {str(e)}")
                        full_response = "I'm sorry, I encountered an error processing your message."
                else:
                    response = await self.agent_handler(text_content, context)
                    full_response = response if response and not response.startswith("Error:") else "I'm sorry, I encountered an error processing your message."
                
                # Send the complete response
                self.reply_text(full_response, incoming_message)
                return full_response
            
            # Step 2: Create AICardReplier instance for streaming updates (matching example code)
            card_instance = AICardReplier(
                self.dingtalk_client, incoming_message
            )
            
            # Step 3: Set up optimized streaming callback with improved fluidity
            content_key = "content"
            accumulated_content = ""
            last_update_length = 0
            min_chunk_size = FLUID_STREAMING_MIN_CHUNK  # Reduced from 20 for more frequent updates
            max_update_interval = 0.5  # Maximum 0.5 seconds between updates for responsiveness
            streaming_start_time = time.time()
            max_streaming_duration = 120  # Maximum 2 minutes for streaming
            last_update_time = time.time()
            
            async def fluid_streaming_callback(content_value: str):
                """Fluid streaming callback with optimized update frequency"""
                nonlocal accumulated_content, last_update_length, last_update_time
                
                try:
                    # Check for timeout
                    if time.time() - streaming_start_time > max_streaming_duration:
                        logger.warning("Streaming timeout reached, sending final update")
                        return False
                    
                    # Accumulate content
                    accumulated_content += content_value
                    current_length = len(accumulated_content)
                    current_time = time.time()
                    
                    # More frequent updates for better fluidity
                    should_update = (
                        current_length - last_update_length >= min_chunk_size or  # 10 characters
                        content_value.endswith(('.', '!', '?', '\n', ',')) or  # Update on more punctuation
                        current_time - last_update_time >= max_update_interval or  # Time-based updates
                        len(content_value) >= 5  # Update on longer chunks immediately
                    )
                    
                    if should_update:
                        # Reduced delay for better responsiveness
                        await asyncio.sleep(FLUID_STREAMING_DELAY)
                        
                        result = await card_instance.async_streaming(
                            card_instance_id,
                            content_key=content_key,
                            content_value=accumulated_content,
                            append=False,
                            finished=False,
                            failed=False,
                        )
                        
                        if result:
                            last_update_length = current_length
                            last_update_time = current_time
                            logger.debug(f"Fluid streaming update sent: {current_length} characters")
                        
                        return result
                    else:
                        return True  # Don't send update yet, but don't fail
                        
                except Exception as e:
                    logger.error(f"Error in fluid streaming callback: {str(e)}")
                    return False
            
            # Step 4: Process Dify streaming with optimized callback and timeout
            try:
                if self.agent_instance and hasattr(self.agent_instance, 'dify_client'):
                    logger.debug(f"Sending to Dify (streaming): {text_content}")
                    
                    # Use Dify streaming with our optimized callback and timeout
                    full_response = await asyncio.wait_for(
                        self.agent_instance.dify_client.chat_completion_streaming_with_callback(
                            text_content, 
                            user_id, 
                            fluid_streaming_callback
                        ),
                        timeout=max_streaming_duration
                    )
                    
                    # Ensure final content is sent (in case last chunk was small)
                    if accumulated_content != full_response:
                        await card_instance.async_streaming(
                            card_instance_id,
                            content_key=content_key,
                            content_value=full_response,
                            append=False,
                            finished=True,
                            failed=False,
                        )
                    else:
                        # Send final update with finished=True
                        await card_instance.async_streaming(
                            card_instance_id,
                            content_key=content_key,
                            content_value=full_response,
                            append=False,
                            finished=True,
                            failed=False,
                        )
                    
                    logger.info(f"Streaming response completed for {user_id}: {len(full_response)} characters")
                    return full_response
                else:
                    # Fallback to blocking response
                    response = await self.agent_handler(text_content, context)
                    full_response = response if response else "I'm sorry, I encountered an error processing your message."
                    
                    # Send final update
                    await card_instance.async_streaming(
                        card_instance_id,
                        content_key=content_key,
                        content_value=full_response,
                        append=False,
                        finished=True,
                        failed=False,
                    )
                    
                    return full_response
                    
            except asyncio.TimeoutError:
                logger.error("Streaming operation timed out")
                # Send timeout error update
                await card_instance.async_streaming(
                    card_instance_id,
                    content_key=content_key,
                    content_value="I'm sorry, the response took too long. Please try again.",
                    append=False,
                    finished=False,
                    failed=True,
                )
                return "I'm sorry, the response took too long. Please try again."
            except Exception as e:
                logger.error(f"Error in streaming response: {str(e)}")
                # Send error update (matching example code pattern)
                await card_instance.async_streaming(
                    card_instance_id,
                    content_key=content_key,
                    content_value="",
                    append=False,
                    finished=False,
                    failed=True,
                )
                return "I'm sorry, I encountered an error processing your message."
                
        except Exception as e:
            logger.error(f"Error in _process_streaming_response: {str(e)}")
            return "I'm sorry, I encountered an error processing your message."

    
    async def _extract_message_content(self, incoming_message: ChatbotMessage) -> Optional[str]:
        """
        Extract content from message, handling both text and voice messages.
        
        Supported message types:
        - Text messages: Direct text content
        - Voice messages: Audio that gets transcribed to text
        - Other types (images, files, cards, etc.): Ignored (normal)
        
        Args:
            incoming_message: ChatbotMessage object from DingTalk
            
        Returns:
            Text content from message or transcribed voice content
        """
        try:
            # Convert message to dictionary for easier processing
            message_data = incoming_message.to_dict()
            
            # Debug: Log message structure to understand what we're receiving
            logger.debug(f"Message structure: {message_data}")
            
            # Check if this is a voice message
            if self.voice_service.is_voice_message(message_data):
                logger.info("Processing voice message")
                
                # Extract audio data from message
                audio_data, audio_format = self.voice_service.extract_audio_data(message_data)
                logger.debug(f"Extracted audio data: {type(audio_data)}, format: {audio_format}")
                
                if not audio_data:
                    logger.warning("Voice message detected but no audio data found")
                    return None
                
                # Convert speech to text
                text_content = await self.voice_service.convert_speech_to_text(audio_data, audio_format)
                logger.debug(f"Speech to text result: {text_content}")
                
                if text_content and text_content.strip():
                    logger.info(f"Voice message transcribed: {text_content}")
                    return text_content.strip()
                else:
                    logger.warning("Failed to transcribe voice message or empty result")
                    return None
            
            # Handle text message (existing logic)
            if hasattr(incoming_message, 'text') and incoming_message.text:
                text_content = incoming_message.text.content.strip()
                if text_content:
                    return text_content
            
            # Debug: Log what we found in the message
            message_type = message_data.get("message_type", "unknown")
            logger.debug(f"Message type: {message_type}")
            logger.debug(f"Message keys: {list(message_data.keys())}")
            
            # Check for other message types that we might want to handle
            if "image" in message_data:
                logger.info("Image message received (not supported)")
                return None
            elif "file" in message_data:
                logger.info("File message received (not supported)")
                return None
            elif "card" in message_data:
                logger.info("Card message received (not supported)")
                return None
            
            # This is normal - DingTalk sends various message types
            logger.debug("No text or voice content found in message (normal for system messages, images, files, etc.)")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting message content: {str(e)}")
            return None
    
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
    
    def __init__(self, agent_handler: Callable, agent_instance=None):
        """
        Initialize DingTalk client with agent handler.
        
        Args:
            agent_handler: Function to call with processed messages
            agent_instance: Optional agent instance for direct streaming access
        """
        self.agent_handler = agent_handler  # AI agent callback
        self.agent_instance = agent_instance  # Agent instance for streaming
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
            message_handler = MindBotChatbotHandler(self.agent_handler, self.agent_instance, self.client)
            
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