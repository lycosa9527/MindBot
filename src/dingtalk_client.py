#!/usr/bin/env python3
"""
DingTalk Stream Client - WebSocket Integration
Handles real-time message reception and sending via DingTalk Stream Mode
"""

import asyncio
import json
from .logging_config import get_logger
import threading
import hashlib
import time
import uuid
import requests
from typing import Callable, Optional, Dict, Any
from dingtalk_stream import DingTalkStreamClient, Credential, ChatbotHandler, ChatbotMessage, AckMessage, AICardReplier
from dingtalk_stream.frames import CallbackMessage as CallbackFrame

# Note: AI Card functionality is handled by dingtalk-stream.AICardReplier

# Note: DingTalk credentials are now passed via constructor parameters
# Streaming configuration constants (can be moved to config later)
ENABLE_STREAMING = True
STREAMING_MIN_CHUNK_SIZE = 20
STREAMING_UPDATE_DELAY = 0.05
STREAMING_MAX_RETRIES = 3
STREAMING_RETRY_DELAY = 1.0
ENABLE_FLUID_STREAMING = True
FLUID_STREAMING_MIN_CHUNK = 10
FLUID_STREAMING_DELAY = 0.02
from src.debug import DebugLogger
from src.voice_recognition import VoiceRecognitionService
from src.agent import MindBotAgent

logger = get_logger("DingTalk")

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
                "appkey": self.client_id,
                "appsecret": self.client_secret
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Failed to get access token: {response.status_code}")
                return None
                    
            data = response.json()
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
    
    # Note: Streaming updates are handled by dingtalk-stream.AICardReplier
    
    # Note: Card creation is handled by dingtalk-stream.AICardReplier
        
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
            card_template_id = self.card_template_id
            
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
            
            # Use smart message routing based on Dify response type
            if ENABLE_STREAMING:
                # For streaming mode, always use AI Cards for real-time experience
                full_response = await self._process_streaming_response(text_content, context, incoming_message)
            else:
                # For blocking mode, use smart routing for static responses
                logger.debug(f"Sending to Dify (blocking): {text_content}")
                response = await self.agent_handler(text_content, context)
                logger.debug(f"Dify response: {response}")
                
                # Smart routing based on response content (static responses only)
                await self._smart_reply_static(response, incoming_message)
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
                
                # Use smart routing for the complete response
                await self._smart_reply_static(full_response, incoming_message)
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
        Extract content from message, handling all supported message types.
        
        Supported message types:
        - Text messages: Direct text content
        - Voice messages: Audio that gets transcribed to text
        - Image messages: Processed and sent to Dify for analysis
        - Video messages: Processed and sent to Dify for analysis
        - File messages: Processed and sent to Dify for analysis
        - Rich text messages: Processed and sent to Dify for analysis
        - Card messages: Processed and sent to Dify for analysis
        
        Args:
            incoming_message: ChatbotMessage object from DingTalk
            
        Returns:
            Text content from message or processed multimedia content
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
            
            # Handle other message types and send to Dify
            if "image" in message_data:
                logger.info("Image message received - processing with Dify")
                return await self._process_image_message(incoming_message)
            elif "file" in message_data:
                logger.info("File message received - processing with Dify")
                return await self._process_file_message(incoming_message)
            elif "card" in message_data:
                logger.info("Card message received - processing with Dify")
                return await self._process_card_message(incoming_message)
            elif "video" in message_data:
                logger.info("Video message received - processing with Dify")
                return await self._process_video_message(incoming_message)
            elif "rich_text" in message_data:
                logger.info("Rich text message received - processing with Dify")
                return await self._process_richtext_message(incoming_message)
            
            # This is normal - DingTalk sends various message types
            logger.debug("No processable content found in message (normal for system messages)")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting message content: {str(e)}")
            return None
    
    async def _process_image_message(self, incoming_message: ChatbotMessage) -> str:
        """
        Process image messages and send to Dify.
        
        Args:
            incoming_message: ChatbotMessage object containing image data
            
        Returns:
            Text description of the image from Dify
        """
        try:
            # Get image list from message
            images = incoming_message.get_image_list()
            if not images:
                logger.warning("No images found in image message")
                return "I received an image but couldn't process it."
            
            # Process each image
            image_descriptions = []
            for i, image in enumerate(images):
                try:
                    # Get image download URL
                    image_url = self.get_image_download_url(image)
                    if not image_url:
                        logger.warning(f"Could not get download URL for image {i}")
                        continue
                    
                    # Send image to Dify for analysis
                    logger.info(f"Processing image {i+1}/{len(images)}: {image_url}")
                    
                    # Create context for Dify
                    context = {
                        "user_id": incoming_message.sender_staff_id,
                        "conversation_id": incoming_message.conversation_id,
                        "message_type": "image",
                        "image_url": image_url,
                        "session_webhook": incoming_message.session_webhook
                    }
                    
                    # Send to Dify with image context
                    response = await self.agent_handler(f"Please analyze this image: {image_url}", context)
                    image_descriptions.append(f"Image {i+1}: {response}")
                    
                except Exception as e:
                    logger.error(f"Error processing image {i}: {e}")
                    image_descriptions.append(f"Image {i+1}: Error processing image")
            
            if image_descriptions:
                return "\n\n".join(image_descriptions)
            else:
                return "I received an image but couldn't process it."
                
        except Exception as e:
            logger.error(f"Error processing image message: {e}")
            return "I received an image but encountered an error processing it."
    
    async def _process_file_message(self, incoming_message: ChatbotMessage) -> str:
        """
        Process file messages and send to Dify.
        
        Args:
            incoming_message: ChatbotMessage object containing file data
            
        Returns:
            Text description of the file from Dify
        """
        try:
            # Get file information from message
            message_data = incoming_message.to_dict()
            file_data = message_data.get("file", {})
            
            if not file_data:
                logger.warning("No file data found in file message")
                return "I received a file but couldn't process it."
            
            # Extract file information
            file_name = file_data.get("file_name", "unknown")
            file_size = file_data.get("file_size", 0)
            file_type = file_data.get("file_type", "unknown")
            
            logger.info(f"Processing file: {file_name} ({file_type}, {file_size} bytes)")
            
            # Create context for Dify
            context = {
                "user_id": incoming_message.sender_staff_id,
                "conversation_id": incoming_message.conversation_id,
                "message_type": "file",
                "file_name": file_name,
                "file_size": file_size,
                "file_type": file_type,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Send file information to Dify
            response = await self.agent_handler(f"Please analyze this file: {file_name} (Type: {file_type}, Size: {file_size} bytes)", context)
            return f"File Analysis: {response}"
            
        except Exception as e:
            logger.error(f"Error processing file message: {e}")
            return "I received a file but encountered an error processing it."
    
    async def _process_video_message(self, incoming_message: ChatbotMessage) -> str:
        """
        Process video messages and send to Dify.
        
        Args:
            incoming_message: ChatbotMessage object containing video data
            
        Returns:
            Text description of the video from Dify
        """
        try:
            # Get video information from message
            message_data = incoming_message.to_dict()
            video_data = message_data.get("video", {})
            
            if not video_data:
                logger.warning("No video data found in video message")
                return "I received a video but couldn't process it."
            
            # Extract video information
            video_name = video_data.get("video_name", "unknown")
            video_size = video_data.get("video_size", 0)
            video_duration = video_data.get("video_duration", 0)
            
            logger.info(f"Processing video: {video_name} (Duration: {video_duration}s, Size: {video_size} bytes)")
            
            # Create context for Dify
            context = {
                "user_id": incoming_message.sender_staff_id,
                "conversation_id": incoming_message.conversation_id,
                "message_type": "video",
                "video_name": video_name,
                "video_size": video_size,
                "video_duration": video_duration,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Send video information to Dify
            response = await self.agent_handler(f"Please analyze this video: {video_name} (Duration: {video_duration}s, Size: {video_size} bytes)", context)
            return f"Video Analysis: {response}"
            
        except Exception as e:
            logger.error(f"Error processing video message: {e}")
            return "I received a video but encountered an error processing it."
    
    async def _process_richtext_message(self, incoming_message: ChatbotMessage) -> str:
        """
        Process rich text messages and send to Dify.
        
        Args:
            incoming_message: ChatbotMessage object containing rich text data
            
        Returns:
            Processed rich text content from Dify
        """
        try:
            # Get rich text content from message
            rich_text_content = incoming_message.rich_text_content
            if not rich_text_content:
                logger.warning("No rich text content found in rich text message")
                return "I received rich text but couldn't process it."
            
            logger.info(f"Processing rich text message: {len(rich_text_content)} characters")
            
            # Create context for Dify
            context = {
                "user_id": incoming_message.sender_staff_id,
                "conversation_id": incoming_message.conversation_id,
                "message_type": "rich_text",
                "rich_text_content": rich_text_content,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Send rich text to Dify
            response = await self.agent_handler(f"Please process this rich text content: {rich_text_content}", context)
            return f"Rich Text Analysis: {response}"
            
        except Exception as e:
            logger.error(f"Error processing rich text message: {e}")
            return "I received rich text but encountered an error processing it."
    
    async def _process_card_message(self, incoming_message: ChatbotMessage) -> str:
        """
        Process card messages and send to Dify.
        
        Args:
            incoming_message: ChatbotMessage object containing card data
            
        Returns:
            Processed card content from Dify
        """
        try:
            # Get card information from message
            message_data = incoming_message.to_dict()
            card_data = message_data.get("card", {})
            
            if not card_data:
                logger.warning("No card data found in card message")
                return "I received a card but couldn't process it."
            
            # Extract card information
            card_title = card_data.get("card_title", "unknown")
            card_content = card_data.get("card_content", "")
            
            logger.info(f"Processing card message: {card_title}")
            
            # Create context for Dify
            context = {
                "user_id": incoming_message.sender_staff_id,
                "conversation_id": incoming_message.conversation_id,
                "message_type": "card",
                "card_title": card_title,
                "card_content": card_content,
                "session_webhook": incoming_message.session_webhook
            }
            
            # Send card information to Dify
            response = await self.agent_handler(f"Please process this card: {card_title} - {card_content}", context)
            return f"Card Analysis: {response}"
            
        except Exception as e:
            logger.error(f"Error processing card message: {e}")
            return "I received a card but encountered an error processing it."
    
    async def _smart_reply_static(self, response: str, incoming_message: ChatbotMessage) -> None:
        """
        Smart message routing for static responses (when streaming is disabled).
        
        Detects:
        - Markdown with images → reply_markdown()
        - Interactive content → reply_markdown_button()
        - Complex formatting → reply_markdown_card()
        - Simple markdown → reply_markdown()
        - Plain text → reply_text()
        
        Args:
            response: Dify response content
            incoming_message: ChatbotMessage object for reply
        """
        try:
            # Detect response type and choose appropriate reply method
            response_type = self._detect_response_type(response)
            logger.info(f"Detected response type: {response_type}")
            
            if response_type == "markdown_with_images":
                # Markdown with images - use reply_markdown()
                logger.debug("Using reply_markdown() for markdown with images")
                self.reply_markdown(response, incoming_message)
                
            elif response_type == "interactive_markdown":
                # Interactive markdown with buttons - use reply_markdown_button()
                logger.debug("Using reply_markdown_button() for interactive content")
                self.reply_markdown_button(response, incoming_message)
                
            elif response_type == "complex_markdown":
                # Complex markdown formatting - use reply_markdown_card()
                logger.debug("Using reply_markdown_card() for complex formatting")
                self.reply_markdown_card(response, incoming_message)
                
            elif response_type == "simple_markdown":
                # Simple markdown - use reply_markdown()
                logger.debug("Using reply_markdown() for simple markdown")
                self.reply_markdown(response, incoming_message)
                
            else:
                # Plain text or unknown - use reply_text()
                logger.debug("Using reply_text() for plain text")
                self.reply_text(response, incoming_message)
                
        except Exception as e:
            logger.error(f"Error in smart reply routing: {e}")
            # Fallback to simple text reply
            self.reply_text(response, incoming_message)
    
    def _detect_response_type(self, response: str) -> str:
        """
        Detect the type of Dify response to choose appropriate reply method.
        
        Args:
            response: Dify response content
            
        Returns:
            Response type: "markdown_with_images", "interactive_markdown", 
                          "complex_markdown", "simple_markdown", "plain_text"
        """
        try:
            # Check for markdown with images (![]() syntax)
            if "![" in response and "](" in response and ")" in response:
                logger.debug("Detected markdown with images")
                return "markdown_with_images"
            
            # Check for interactive content (buttons, links)
            if "[" in response and "](" in response and ")" in response:
                # Check if it's interactive (multiple links or button-like syntax)
                link_count = response.count("](")
                if link_count > 1 or "button" in response.lower() or "click" in response.lower():
                    logger.debug("Detected interactive markdown")
                    return "interactive_markdown"
                else:
                    logger.debug("Detected simple markdown")
                    return "simple_markdown"
            
            # Check for complex markdown formatting
            markdown_elements = ["#", "##", "###", "**", "*", "`", "```", ">", "-", "1."]
            markdown_count = sum(1 for element in markdown_elements if element in response)
            
            if markdown_count >= 3:
                logger.debug("Detected complex markdown formatting")
                return "complex_markdown"
            elif markdown_count >= 1:
                logger.debug("Detected simple markdown")
                return "simple_markdown"
            
            # Check for streaming text patterns
            if len(response) > 200 or "\n" in response or "..." in response:
                logger.debug("Detected stream text response")
                return "stream_text"
            
            # Default to plain text
            logger.debug("Detected plain text")
            return "plain_text"
            
        except Exception as e:
            logger.error(f"Error detecting response type: {e}")
            return "plain_text"
    
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
    
    def __init__(self, agent_handler: Callable, agent_instance=None, 
                 client_id: str = None, client_secret: str = None, 
                 robot_code: str = None, robot_name: str = None, 
                 card_template_id: str = None):
        """
        Initialize DingTalk client with agent handler and credentials.
        
        Args:
            agent_handler: Function to call with processed messages
            agent_instance: Optional agent instance for direct streaming access
            client_id: DingTalk client ID
            client_secret: DingTalk client secret
            robot_code: DingTalk robot code
            robot_name: DingTalk robot name
            card_template_id: DingTalk AI card template ID
        """
        self.agent_handler = agent_handler  # AI agent callback
        self.agent_instance = agent_instance  # Agent instance for streaming
        self.client = None  # DingTalk WebSocket client
        self.client_thread = None  # Thread for client connection
        self.running = False  # Client running state
        self.debug_logger = DebugLogger("DingTalkClient")
        
        # Store DingTalk credentials
        self.client_id = client_id
        self.client_secret = client_secret
        self.robot_code = robot_code
        self.robot_name = robot_name
        self.card_template_id = card_template_id
        
        # Validate required configuration
        if not self.client_id:
            raise ValueError("client_id is not set")
        if not self.client_secret:
            raise ValueError("client_secret is not set")
        if not self.robot_code:
            raise ValueError("robot_code is not set")
        
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
                client_id=self.client_id,
                client_secret=self.client_secret
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
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # Test client creation
            test_client = DingTalkStreamClient(credential)
            
            logger.info("DingTalk API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"DingTalk API connection test failed: {str(e)}")
            return False 