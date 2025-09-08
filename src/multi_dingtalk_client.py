#!/usr/bin/env python3
"""
Multi-Instance DingTalk Client
Supports multiple DingTalk adapters running concurrently
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
import uuid

from dingtalk_stream import DingTalkStreamClient, Credential, ChatbotHandler, ChatbotMessage, AckMessage, AICardReplier
from dingtalk_stream.frames import CallbackMessage as CallbackFrame

from src.config import (
    DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET, DINGTALK_ROBOT_CODE,
    DINGTALK_ROBOT_NAME, DEBUG_MODE, LOG_LEVEL, ENABLE_STREAMING, DINGTALK_CARD_TEMPLATE_ID,
    STREAMING_MIN_CHUNK_SIZE, STREAMING_UPDATE_DELAY, STREAMING_MAX_RETRIES, STREAMING_RETRY_DELAY,
    ENABLE_FLUID_STREAMING, FLUID_STREAMING_MIN_CHUNK, FLUID_STREAMING_DELAY
)

logger = logging.getLogger(__name__)

class MultiInstanceDingTalkHandler(ChatbotHandler):
    """DingTalk handler that supports multiple instances"""
    
    def __init__(self, adapter_id: str, agent_handler: Callable, agent_instance=None, dingtalk_client=None):
        super().__init__()
        self.adapter_id = adapter_id
        self.agent_handler = agent_handler
        self.agent_instance = agent_instance
        self.dingtalk_client = dingtalk_client
        
        # Instance-specific configuration
        self.instance_config = {
            "adapter_id": adapter_id,
            "max_concurrent_messages": 10,
            "message_timeout": 30.0
        }
        
        # Message processing semaphore for concurrency control
        self.message_semaphore = asyncio.Semaphore(self.instance_config["max_concurrent_messages"])
        
        # Instance-specific message tracking
        self._recent_messages = {}
        self._dedup_lock = threading.Lock()
        self._max_recent_messages = 100
        self._message_ttl = 300  # 5 minutes TTL
        
        logger.info(f"Initialized DingTalk handler for adapter: {adapter_id}")
    
    async def process(self, callback):
        """Process incoming messages with concurrency control"""
        async with self.message_semaphore:
            return await self._process_message(callback)
    
    async def _process_message(self, callback):
        """Process a single message"""
        try:
            logger.debug(f"Processing message in adapter {self.adapter_id}")
            
            # Extract message data
            incoming_message = ChatbotMessage.from_dict(callback.data)
            user_id = incoming_message.sender_staff_id
            conversation_id = incoming_message.conversation_id
            
            # Add adapter context
            context = {
                "adapter_id": self.adapter_id,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "session_webhook": incoming_message.session_webhook,
                "platform": "dingtalk"
            }
            
            # Extract message content
            text_content = await self._extract_message_content(incoming_message)
            if not text_content:
                return AckMessage.STATUS_OK, "No processable content"
            
            # Process with agent
            response = await self.agent_handler(text_content, context)
            
            # Send response using appropriate method
            await self._send_response(response, incoming_message)
            
            return AckMessage.STATUS_OK, "Message processed successfully"
            
        except Exception as e:
            logger.error(f"Error processing message in adapter {self.adapter_id}: {e}")
            return AckMessage.STATUS_SYSTEM_EXCEPTION, f"Error: {str(e)}"
    
    async def _extract_message_content(self, incoming_message: ChatbotMessage) -> Optional[str]:
        """Extract content from message"""
        try:
            # Handle text messages
            if hasattr(incoming_message, 'text') and incoming_message.text:
                return incoming_message.text.content.strip()
            
            # Handle other message types (images, files, etc.)
            message_data = incoming_message.to_dict()
            
            if "image" in message_data:
                return f"[Image message from adapter {self.adapter_id}]"
            elif "file" in message_data:
                return f"[File message from adapter {self.adapter_id}]"
            elif "card" in message_data:
                return f"[Card message from adapter {self.adapter_id}]"
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting message content in adapter {self.adapter_id}: {e}")
            return None
    
    async def _send_response(self, response: str, incoming_message: ChatbotMessage):
        """Send response using appropriate method"""
        try:
            if ENABLE_STREAMING:
                # Use AI Card for streaming
                await self._send_streaming_response(response, incoming_message)
            else:
                # Use smart routing for static responses
                await self._smart_reply_static(response, incoming_message)
        except Exception as e:
            logger.error(f"Error sending response in adapter {self.adapter_id}: {e}")
            # Fallback to simple text
            self.reply_text(response, incoming_message)
    
    async def _send_streaming_response(self, response: str, incoming_message: ChatbotMessage):
        """Send streaming response using AI Card"""
        try:
            # Create AI card
            card_instance = AICardReplier(self.dingtalk_client, incoming_message)
            card_instance_id = await card_instance.async_create_and_deliver_card(
                DINGTALK_CARD_TEMPLATE_ID, 
                {"content": response}
            )
            
            if card_instance_id:
                # Stream the response
                await card_instance.async_streaming(
                    card_instance_id,
                    content_key="content",
                    content_value=response,
                    is_final=True
                )
            else:
                # Fallback to text
                self.reply_text(response, incoming_message)
                
        except Exception as e:
            logger.error(f"Error in streaming response for adapter {self.adapter_id}: {e}")
            self.reply_text(response, incoming_message)
    
    async def _smart_reply_static(self, response: str, incoming_message: ChatbotMessage):
        """Smart routing for static responses"""
        try:
            # Simple routing based on content
            if "![" in response and "](" in response:
                self.reply_markdown(response, incoming_message)
            elif "[" in response and "](" in response:
                self.reply_markdown_button(response, incoming_message)
            else:
                self.reply_text(response, incoming_message)
        except Exception as e:
            logger.error(f"Error in smart reply for adapter {self.adapter_id}: {e}")
            self.reply_text(response, incoming_message)

class MultiInstanceDingTalkClient:
    """DingTalk client that supports multiple instances"""
    
    def __init__(self, agent_handler: Callable, agent_instance=None):
        self.agent_handler = agent_handler
        self.agent_instance = agent_instance
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        
    async def add_instance(self, instance_id: str, config: Dict[str, Any]) -> bool:
        """Add a new DingTalk instance"""
        try:
            # Create credential
            credential = Credential(
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                robot_code=config["robot_code"]
            )
            
            # Create client
            client = DingTalkStreamClient(credential)
            
            # Create handler
            handler = MultiInstanceDingTalkHandler(
                adapter_id=instance_id,
                agent_handler=self.agent_handler,
                agent_instance=self.agent_instance,
                dingtalk_client=client
            )
            
            # Register handler
            client.register_callback_handler(ChatbotMessage.TOPIC, handler)
            
            # Store instance
            self.instances[instance_id] = {
                "client": client,
                "handler": handler,
                "config": config,
                "task": None,
                "is_running": False
            }
            
            logger.info(f"Added DingTalk instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add DingTalk instance {instance_id}: {e}")
            return False
    
    async def start_instance(self, instance_id: str) -> bool:
        """Start a specific instance"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False
        
        try:
            instance = self.instances[instance_id]
            if instance["is_running"]:
                logger.warning(f"Instance {instance_id} is already running")
                return True
            
            # Start the client
            client = instance["client"]
            task = asyncio.create_task(client.start())
            instance["task"] = task
            instance["is_running"] = True
            
            logger.info(f"Started DingTalk instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start instance {instance_id}: {e}")
            return False
    
    async def stop_instance(self, instance_id: str) -> bool:
        """Stop a specific instance"""
        if instance_id not in self.instances:
            logger.error(f"Instance {instance_id} not found")
            return False
        
        try:
            instance = self.instances[instance_id]
            if not instance["is_running"]:
                logger.warning(f"Instance {instance_id} is not running")
                return True
            
            # Stop the client
            if instance["task"]:
                instance["task"].cancel()
                try:
                    await instance["task"]
                except asyncio.CancelledError:
                    pass
            
            instance["is_running"] = False
            instance["task"] = None
            
            logger.info(f"Stopped DingTalk instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop instance {instance_id}: {e}")
            return False
    
    async def start_all_instances(self):
        """Start all instances"""
        start_tasks = []
        for instance_id in self.instances:
            start_tasks.append(self.start_instance(instance_id))
        
        if start_tasks:
            results = await asyncio.gather(*start_tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            logger.info(f"Started {successful}/{len(start_tasks)} DingTalk instances")
    
    async def stop_all_instances(self):
        """Stop all instances"""
        stop_tasks = []
        for instance_id in self.instances:
            stop_tasks.append(self.stop_instance(instance_id))
        
        if stop_tasks:
            results = await asyncio.gather(*stop_tasks, return_exceptions=True)
            successful = sum(1 for r in results if r is True)
            logger.info(f"Stopped {successful}/{len(stop_tasks)} DingTalk instances")
    
    def get_instance_stats(self, instance_id: str = None) -> Dict[str, Any]:
        """Get statistics for instances"""
        if instance_id:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                return {
                    "instance_id": instance_id,
                    "is_running": instance["is_running"],
                    "config": instance["config"]
                }
            else:
                return {"error": f"Instance {instance_id} not found"}
        else:
            return {
                "total_instances": len(self.instances),
                "running_instances": sum(1 for i in self.instances.values() if i["is_running"]),
                "instances": {
                    instance_id: {
                        "is_running": instance["is_running"],
                        "config": instance["config"]
                    }
                    for instance_id, instance in self.instances.items()
                }
            }

# Example usage
async def create_multi_dingtalk_bot(agent_handler: Callable):
    """Create a multi-instance DingTalk bot"""
    
    # Create multi-instance client
    client = MultiInstanceDingTalkClient(agent_handler)
    
    # Add multiple DingTalk instances
    await client.add_instance("main_dingtalk", {
        "client_id": "your_main_client_id",
        "client_secret": "your_main_client_secret", 
        "robot_code": "your_main_robot_code"
    })
    
    await client.add_instance("test_dingtalk", {
        "client_id": "your_test_client_id",
        "client_secret": "your_test_client_secret",
        "robot_code": "your_test_robot_code"
    })
    
    # Start all instances
    await client.start_all_instances()
    
    return client

if __name__ == "__main__":
    # Example usage
    async def example_agent_handler(message, context):
        adapter_id = context.get("adapter_id", "unknown")
        return f"[{adapter_id}] Echo: {message}"
    
    async def main():
        client = await create_multi_dingtalk_bot(example_agent_handler)
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.stop_all_instances()
    
    asyncio.run(main())
