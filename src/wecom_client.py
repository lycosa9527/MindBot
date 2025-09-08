#!/usr/bin/env python3
"""
WeCom Client Implementation
Handles WeCom (WeChat Work) integration with support for multiple instances
"""

import asyncio
import logging
import requests
import json
import time
from typing import Dict, List, Optional, Any, Callable
import uuid

logger = logging.getLogger(__name__)

class WeComMessage:
    """WeCom message representation"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.msg_type = data.get("MsgType", "")
        self.content = data.get("Content", "")
        self.from_user = data.get("FromUserName", "")
        self.to_user = data.get("ToUserName", "")
        self.msg_id = data.get("MsgId", "")
        self.create_time = data.get("CreateTime", int(time.time()))
    
    def to_dict(self) -> Dict[str, Any]:
        return self.data

class WeComHandler:
    """WeCom message handler"""
    
    def __init__(self, adapter_id: str, agent_handler: Callable, agent_instance=None, wecom_client=None):
        self.adapter_id = adapter_id
        self.agent_handler = agent_handler
        self.agent_instance = agent_instance
        self.wecom_client = wecom_client
        
        # Instance-specific configuration
        self.instance_config = {
            "adapter_id": adapter_id,
            "max_concurrent_messages": 10,
            "message_timeout": 30.0
        }
        
        # Message processing semaphore for concurrency control
        self.message_semaphore = asyncio.Semaphore(self.instance_config["max_concurrent_messages"])
        
        logger.info(f"Initialized WeCom handler for adapter: {adapter_id}")
    
    async def process_message(self, message: WeComMessage):
        """Process incoming WeCom message"""
        async with self.message_semaphore:
            return await self._process_message(message)
    
    async def _process_message(self, message: WeComMessage):
        """Process a single WeCom message"""
        try:
            logger.debug(f"Processing WeCom message in adapter {self.adapter_id}")
            
            # Extract message content
            text_content = await self._extract_message_content(message)
            if not text_content:
                return
            
            # Create context
            context = {
                "adapter_id": self.adapter_id,
                "user_id": message.from_user,
                "msg_id": message.msg_id,
                "platform": "wecom",
                "msg_type": message.msg_type
            }
            
            # Process with agent
            response = await self.agent_handler(text_content, context)
            
            # Send response
            await self._send_response(response, message)
            
        except Exception as e:
            logger.error(f"Error processing WeCom message in adapter {self.adapter_id}: {e}")
    
    async def _extract_message_content(self, message: WeComMessage) -> Optional[str]:
        """Extract content from WeCom message"""
        try:
            if message.msg_type == "text":
                return message.content
            elif message.msg_type == "image":
                return f"[Image message from WeCom adapter {self.adapter_id}]"
            elif message.msg_type == "file":
                return f"[File message from WeCom adapter {self.adapter_id}]"
            elif message.msg_type == "voice":
                return f"[Voice message from WeCom adapter {self.adapter_id}]"
            else:
                return f"[{message.msg_type} message from WeCom adapter {self.adapter_id}]"
                
        except Exception as e:
            logger.error(f"Error extracting WeCom message content in adapter {self.adapter_id}: {e}")
            return None
    
    async def _send_response(self, response: str, message: WeComMessage):
        """Send response back to WeCom"""
        try:
            if self.wecom_client:
                await self.wecom_client.send_text_message(
                    to_user=message.from_user,
                    content=response
                )
        except Exception as e:
            logger.error(f"Error sending WeCom response in adapter {self.adapter_id}: {e}")

class WeComClient:
    """WeCom client for sending messages"""
    
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://qyapi.weixin.qq.com"
    
    async def get_access_token(self) -> Optional[str]:
        """Get WeCom access token"""
        try:
            if self.access_token and self.token_expires_at > time.time():
                return self.access_token
            
            url = f"{self.base_url}/cgi-bin/gettoken"
            params = {
                "corpid": self.corp_id,
                "corpsecret": self.corp_secret
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("errcode") == 0:
                    self.access_token = data.get("access_token")
                    self.token_expires_at = time.time() + data.get("expires_in", 7200) - 600
                    logger.debug("WeCom access token obtained successfully")
                    return self.access_token
                else:
                    logger.error(f"Failed to get WeCom access token: {data}")
                    return None
            else:
                logger.error(f"Failed to get WeCom access token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting WeCom access token: {e}")
            return None
    
    async def send_text_message(self, to_user: str, content: str) -> bool:
        """Send text message to WeCom user"""
        try:
            token = await self.get_access_token()
            if not token:
                return False
            
            url = f"{self.base_url}/cgi-bin/message/send"
            params = {"access_token": token}
            
            payload = {
                "touser": to_user,
                "msgtype": "text",
                "agentid": self.agent_id,
                "text": {
                    "content": content
                }
            }
            
            response = requests.post(url, params=params, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("errcode") == 0:
                    logger.debug(f"Sent WeCom message to {to_user}")
                    return True
                else:
                    logger.error(f"Failed to send WeCom message: {data}")
                    return False
            else:
                logger.error(f"Failed to send WeCom message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WeCom message: {e}")
            return False
    
    async def send_markdown_message(self, to_user: str, content: str) -> bool:
        """Send markdown message to WeCom user"""
        try:
            token = await self.get_access_token()
            if not token:
                return False
            
            url = f"{self.base_url}/cgi-bin/message/send"
            params = {"access_token": token}
            
            payload = {
                "touser": to_user,
                "msgtype": "markdown",
                "agentid": self.agent_id,
                "markdown": {
                    "content": content
                }
            }
            
            response = requests.post(url, params=params, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("errcode") == 0:
                    logger.debug(f"Sent WeCom markdown message to {to_user}")
                    return True
                else:
                    logger.error(f"Failed to send WeCom markdown message: {data}")
                    return False
            else:
                logger.error(f"Failed to send WeCom markdown message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WeCom markdown message: {e}")
            return False

class MultiInstanceWeComClient:
    """WeCom client that supports multiple instances"""
    
    def __init__(self, agent_handler: Callable, agent_instance=None):
        self.agent_handler = agent_handler
        self.agent_instance = agent_instance
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
    
    async def add_instance(self, instance_id: str, config: Dict[str, Any]) -> bool:
        """Add a new WeCom instance"""
        try:
            # Create WeCom client
            client = WeComClient(
                corp_id=config["corp_id"],
                corp_secret=config["corp_secret"],
                agent_id=config["agent_id"]
            )
            
            # Create handler
            handler = WeComHandler(
                adapter_id=instance_id,
                agent_handler=self.agent_handler,
                agent_instance=self.agent_instance,
                wecom_client=client
            )
            
            # Store instance
            self.instances[instance_id] = {
                "client": client,
                "handler": handler,
                "config": config,
                "is_running": False
            }
            
            logger.info(f"Added WeCom instance: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add WeCom instance {instance_id}: {e}")
            return False
    
    async def process_webhook_message(self, instance_id: str, message_data: Dict[str, Any]) -> bool:
        """Process webhook message for a specific instance"""
        if instance_id not in self.instances:
            logger.error(f"WeCom instance {instance_id} not found")
            return False
        
        try:
            instance = self.instances[instance_id]
            handler = instance["handler"]
            
            # Create message object
            message = WeComMessage(message_data)
            
            # Process message
            await handler.process_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Error processing WeCom webhook message for {instance_id}: {e}")
            return False
    
    async def send_message(self, instance_id: str, to_user: str, content: str, msg_type: str = "text") -> bool:
        """Send message through specific WeCom instance"""
        if instance_id not in self.instances:
            logger.error(f"WeCom instance {instance_id} not found")
            return False
        
        try:
            instance = self.instances[instance_id]
            client = instance["client"]
            
            if msg_type == "text":
                return await client.send_text_message(to_user, content)
            elif msg_type == "markdown":
                return await client.send_markdown_message(to_user, content)
            else:
                logger.error(f"Unsupported WeCom message type: {msg_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WeCom message for {instance_id}: {e}")
            return False
    
    def get_instance_stats(self, instance_id: str = None) -> Dict[str, Any]:
        """Get statistics for WeCom instances"""
        if instance_id:
            if instance_id in self.instances:
                instance = self.instances[instance_id]
                return {
                    "instance_id": instance_id,
                    "is_running": instance["is_running"],
                    "config": instance["config"]
                }
            else:
                return {"error": f"WeCom instance {instance_id} not found"}
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
async def create_multi_wecom_bot(agent_handler: Callable):
    """Create a multi-instance WeCom bot"""
    
    # Create multi-instance client
    client = MultiInstanceWeComClient(agent_handler)
    
    # Add multiple WeCom instances
    await client.add_instance("main_wecom", {
        "corp_id": "your_corp_id",
        "corp_secret": "your_main_corp_secret",
        "agent_id": "your_main_agent_id"
    })
    
    await client.add_instance("test_wecom", {
        "corp_id": "your_corp_id", 
        "corp_secret": "your_test_corp_secret",
        "agent_id": "your_test_agent_id"
    })
    
    return client

if __name__ == "__main__":
    # Example usage
    async def example_agent_handler(message, context):
        adapter_id = context.get("adapter_id", "unknown")
        return f"[{adapter_id}] Echo: {message}"
    
    async def main():
        client = await create_multi_wecom_bot(example_agent_handler)
        
        # Simulate webhook message processing
        test_message = {
            "MsgType": "text",
            "Content": "Hello from WeCom",
            "FromUserName": "test_user",
            "ToUserName": "test_agent",
            "MsgId": "123456"
        }
        
        await client.process_webhook_message("main_wecom", test_message)
    
    asyncio.run(main())
