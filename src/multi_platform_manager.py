#!/usr/bin/env python3
"""
Multi-Platform Manager for Concurrent DingTalk and WeCom Adapters
Handles multiple platform adapters running simultaneously with proper concurrency management
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import uuid

from mindbot_framework.core.lifecycle import LifecycleManager
from mindbot_framework.core.event_bus import EventBus
from mindbot_framework.core.message_processor import MessageProcessor
from mindbot_framework.platforms.adapters.dingtalk import DingTalkAdapter
from mindbot_framework.platforms.adapters.wecom import WeComAdapter

logger = logging.getLogger(__name__)

class AdapterType(Enum):
    DINGTALK = "dingtalk"
    WECOM = "wecom"
    SLACK = "slack"

@dataclass
class AdapterConfig:
    """Configuration for a platform adapter"""
    adapter_id: str
    adapter_type: AdapterType
    config: Dict[str, Any]
    enabled: bool = True
    max_concurrent_messages: int = 10
    message_timeout: float = 30.0

class MessageRouter:
    """Routes messages between different platform adapters"""
    
    def __init__(self):
        self.routing_rules = {}  # {rule_id: routing_function}
        self.cross_platform_enabled = True
        
    def add_routing_rule(self, rule_id: str, rule_function: Callable):
        """Add a routing rule for cross-platform communication"""
        self.routing_rules[rule_id] = rule_function
        logger.info(f"Added routing rule: {rule_id}")
    
    async def route_message(self, source_adapter_id: str, message: Any, target_adapters: List[str] = None):
        """Route a message to other adapters"""
        if not self.cross_platform_enabled:
            return
            
        for rule_id, rule_function in self.routing_rules.items():
            try:
                await rule_function(source_adapter_id, message, target_adapters)
            except Exception as e:
                logger.error(f"Error in routing rule {rule_id}: {e}")

class AdapterInstance:
    """Wrapper for adapter instances with concurrency management"""
    
    def __init__(self, adapter_id: str, adapter: Any, config: AdapterConfig):
        self.adapter_id = adapter_id
        self.adapter = adapter
        self.config = config
        self.task: Optional[asyncio.Task] = None
        self.message_semaphore = asyncio.Semaphore(config.max_concurrent_messages)
        self.is_running = False
        self.message_queue = asyncio.Queue()
        self.stats = {
            "messages_processed": 0,
            "messages_failed": 0,
            "uptime": 0,
            "last_activity": None
        }
    
    async def start(self):
        """Start the adapter instance"""
        if self.is_running:
            logger.warning(f"Adapter {self.adapter_id} is already running")
            return
            
        try:
            self.task = asyncio.create_task(self._run_adapter())
            self.is_running = True
            logger.info(f"Started adapter {self.adapter_id}")
        except Exception as e:
            logger.error(f"Failed to start adapter {self.adapter_id}: {e}")
            raise
    
    async def stop(self):
        """Stop the adapter instance"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped adapter {self.adapter_id}")
    
    async def _run_adapter(self):
        """Main adapter run loop with concurrency control"""
        try:
            # Start the adapter
            await self.adapter.start()
            
            # Process messages concurrently
            while self.is_running:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=1.0
                    )
                    
                    # Process message with concurrency control
                    async with self.message_semaphore:
                        await self._process_message(message)
                        
                except asyncio.TimeoutError:
                    # No messages, continue loop
                    continue
                except Exception as e:
                    logger.error(f"Error in adapter {self.adapter_id}: {e}")
                    self.stats["messages_failed"] += 1
                    
        except Exception as e:
            logger.error(f"Adapter {self.adapter_id} crashed: {e}")
        finally:
            await self.adapter.stop()
    
    async def _process_message(self, message: Any):
        """Process a single message with error handling"""
        try:
            # Update stats
            self.stats["messages_processed"] += 1
            self.stats["last_activity"] = asyncio.get_event_loop().time()
            
            # Process the message
            await self.adapter.process_message(message)
            
        except Exception as e:
            logger.error(f"Error processing message in {self.adapter_id}: {e}")
            self.stats["messages_failed"] += 1
            raise

class MultiPlatformManager:
    """Manages multiple platform adapters concurrently"""
    
    def __init__(self, agent_handler: Callable):
        self.agent_handler = agent_handler
        self.adapters: Dict[str, AdapterInstance] = {}
        self.lifecycle_manager = LifecycleManager()
        self.event_bus = EventBus()
        self.message_processor = MessageProcessor()
        self.message_router = MessageRouter()
        self.is_running = False
        self.manager_task: Optional[asyncio.Task] = None
        
        # Initialize core components
        asyncio.create_task(self.lifecycle_manager.start())
        asyncio.create_task(self.event_bus.start())
        asyncio.create_task(self.message_processor.start())
    
    async def add_dingtalk_adapter(self, adapter_id: str, config: Dict[str, Any]) -> bool:
        """Add a DingTalk adapter"""
        try:
            # Create adapter configuration
            adapter_config = AdapterConfig(
                adapter_id=adapter_id,
                adapter_type=AdapterType.DINGTALK,
                config=config
            )
            
            # Create DingTalk adapter
            dingtalk_adapter = DingTalkAdapter(
                client_id=config.get("client_id"),
                client_secret=config.get("client_secret"),
                robot_code=config.get("robot_code"),
                agent_handler=self.agent_handler
            )
            
            # Create adapter instance
            adapter_instance = AdapterInstance(adapter_id, dingtalk_adapter, adapter_config)
            
            # Register with lifecycle manager
            await self.lifecycle_manager.register_component(adapter_id, adapter_instance)
            
            # Store adapter
            self.adapters[adapter_id] = adapter_instance
            
            logger.info(f"Added DingTalk adapter: {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add DingTalk adapter {adapter_id}: {e}")
            return False
    
    async def add_wecom_adapter(self, adapter_id: str, config: Dict[str, Any]) -> bool:
        """Add a WeCom adapter"""
        try:
            # Create adapter configuration
            adapter_config = AdapterConfig(
                adapter_id=adapter_id,
                adapter_type=AdapterType.WECOM,
                config=config
            )
            
            # Create WeCom adapter
            wecom_adapter = WeComAdapter(
                corp_id=config.get("corp_id"),
                corp_secret=config.get("corp_secret"),
                agent_id=config.get("agent_id"),
                agent_handler=self.agent_handler
            )
            
            # Create adapter instance
            adapter_instance = AdapterInstance(adapter_id, wecom_adapter, adapter_config)
            
            # Register with lifecycle manager
            await self.lifecycle_manager.register_component(adapter_id, adapter_instance)
            
            # Store adapter
            self.adapters[adapter_id] = adapter_instance
            
            logger.info(f"Added WeCom adapter: {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add WeCom adapter {adapter_id}: {e}")
            return False
    
    async def start_all_adapters(self):
        """Start all registered adapters concurrently"""
        if self.is_running:
            logger.warning("Multi-platform manager is already running")
            return
        
        self.is_running = True
        
        # Start all adapters concurrently
        start_tasks = []
        for adapter_id, adapter_instance in self.adapters.items():
            if adapter_instance.config.enabled:
                start_tasks.append(adapter_instance.start())
        
        if start_tasks:
            await asyncio.gather(*start_tasks, return_exceptions=True)
            logger.info(f"Started {len(start_tasks)} adapters")
        else:
            logger.warning("No adapters to start")
    
    async def stop_all_adapters(self):
        """Stop all adapters"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop all adapters concurrently
        stop_tasks = []
        for adapter_instance in self.adapters.values():
            stop_tasks.append(adapter_instance.stop())
        
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            logger.info("Stopped all adapters")
    
    async def restart_adapter(self, adapter_id: str):
        """Restart a specific adapter"""
        if adapter_id not in self.adapters:
            logger.error(f"Adapter {adapter_id} not found")
            return False
        
        try:
            adapter_instance = self.adapters[adapter_id]
            await adapter_instance.stop()
            await asyncio.sleep(1)  # Brief pause
            await adapter_instance.start()
            logger.info(f"Restarted adapter {adapter_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restart adapter {adapter_id}: {e}")
            return False
    
    def get_adapter_stats(self, adapter_id: str = None) -> Dict[str, Any]:
        """Get statistics for adapters"""
        if adapter_id:
            if adapter_id in self.adapters:
                return {
                    "adapter_id": adapter_id,
                    "stats": self.adapters[adapter_id].stats,
                    "is_running": self.adapters[adapter_id].is_running
                }
            else:
                return {"error": f"Adapter {adapter_id} not found"}
        else:
            return {
                "total_adapters": len(self.adapters),
                "running_adapters": sum(1 for a in self.adapters.values() if a.is_running),
                "adapters": {
                    adapter_id: {
                        "stats": adapter.stats,
                        "is_running": adapter.is_running,
                        "type": adapter.config.adapter_type.value
                    }
                    for adapter_id, adapter in self.adapters.items()
                }
            }
    
    async def send_message_to_adapter(self, adapter_id: str, message: Any):
        """Send a message to a specific adapter"""
        if adapter_id not in self.adapters:
            logger.error(f"Adapter {adapter_id} not found")
            return False
        
        try:
            adapter_instance = self.adapters[adapter_id]
            await adapter_instance.message_queue.put(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to adapter {adapter_id}: {e}")
            return False

# Example usage and configuration
async def create_multi_platform_bot(agent_handler: Callable):
    """Create a multi-platform bot with multiple adapters"""
    
    # Create manager
    manager = MultiPlatformManager(agent_handler)
    
    # Add multiple DingTalk adapters
    await manager.add_dingtalk_adapter("dingtalk_main", {
        "client_id": "your_main_client_id",
        "client_secret": "your_main_client_secret",
        "robot_code": "your_main_robot_code"
    })
    
    await manager.add_dingtalk_adapter("dingtalk_test", {
        "client_id": "your_test_client_id", 
        "client_secret": "your_test_client_secret",
        "robot_code": "your_test_robot_code"
    })
    
    # Add WeCom adapters
    await manager.add_wecom_adapter("wecom_main", {
        "corp_id": "your_corp_id",
        "corp_secret": "your_corp_secret", 
        "agent_id": "your_main_agent_id"
    })
    
    await manager.add_wecom_adapter("wecom_test", {
        "corp_id": "your_corp_id",
        "corp_secret": "your_test_corp_secret",
        "agent_id": "your_test_agent_id"
    })
    
    # Start all adapters
    await manager.start_all_adapters()
    
    return manager

if __name__ == "__main__":
    # Example usage
    async def example_agent_handler(message, context):
        return f"Echo: {message}"
    
    async def main():
        manager = await create_multi_platform_bot(example_agent_handler)
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await manager.stop_all_adapters()
    
    asyncio.run(main())
