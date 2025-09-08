"""
Enhanced Multi-Platform Manager
Based on LangBot's superior architecture patterns
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .discovery import ComponentDiscovery, AdapterRegistry
from .runtime import RuntimeAdapter, TaskManager, TaskScope
from .logging_config import get_logger

logger = get_logger("PlatformManager")

class EnhancedMultiPlatformManager:
    """Enhanced multi-platform manager with LangBot-inspired architecture"""
    
    def __init__(self, agent_handler: Callable[[str, Dict[str, Any]], str]):
        self.agent_handler = agent_handler
        self.task_manager = TaskManager()
        self.discovery = ComponentDiscovery()
        self.registry = AdapterRegistry(self.discovery)
        
        # Runtime adapters
        self.runtime_adapters: Dict[str, RuntimeAdapter] = {}
        
        # Statistics
        self.stats = {
            "total_adapters": 0,
            "running_adapters": 0,
            "messages_processed": 0,
            "messages_failed": 0,
            "start_time": datetime.now()
        }
        
        # Health monitoring
        self.health_check_interval = 30
        self.health_check_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the enhanced manager"""
        logger.info("Initializing Enhanced Multi-Platform Manager...")
        
        # Discover available adapters
        await self.discovery.discover_adapters()
        available_adapters = self.discovery.get_available_adapters()
        logger.info(f"Discovered {len(available_adapters)} adapters: {available_adapters}")
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Enhanced Multi-Platform Manager initialized")
    
    async def add_adapter(
        self, 
        adapter_id: str, 
        adapter_name: str, 
        config: Dict[str, Any]
    ) -> bool:
        """Add a new adapter"""
        try:
            logger.info(f"Adding adapter {adapter_id} ({adapter_name})")
            
            # For Phase 1 POC, create adapters directly without discovery system
            if adapter_name == "dingtalk":
                adapter_instance = await self._create_dingtalk_adapter(adapter_id, config)
            elif adapter_name == "wecom":
                adapter_instance = await self._create_wecom_adapter(adapter_id, config)
            else:
                logger.error(f"Unknown adapter type: {adapter_name}")
                return False
            
            if not adapter_instance:
                logger.error(f"Failed to create adapter instance for {adapter_id}")
                return False
            
            # Set agent handler for the adapter
            if hasattr(adapter_instance, 'set_agent_handler'):
                adapter_instance.set_agent_handler(self.agent_handler)
            
            runtime_adapter = RuntimeAdapter(
                adapter_id=adapter_id,
                adapter_instance=adapter_instance,
                config=config,
                task_manager=self.task_manager,
                logger_name=f"runtime-adapter-{adapter_id}"
            )
            
            # Initialize runtime adapter
            await runtime_adapter.initialize()
            
            # Store runtime adapter
            self.runtime_adapters[adapter_id] = runtime_adapter
            
            # Update statistics
            self.stats["total_adapters"] += 1
            
            logger.info(f"Added adapter {adapter_id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding adapter {adapter_id}: {e}")
            return False
    
    async def start_adapter(self, adapter_id: str) -> bool:
        """Start an adapter"""
        if adapter_id not in self.runtime_adapters:
            logger.error(f"Runtime adapter {adapter_id} not found")
            return False
        
        try:
            runtime_adapter = self.runtime_adapters[adapter_id]
            success = await runtime_adapter.start()
            
            if success:
                self.stats["running_adapters"] += 1
                logger.info(f"Started adapter {adapter_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting adapter {adapter_id}: {e}")
            return False
    
    async def stop_adapter(self, adapter_id: str) -> bool:
        """Stop an adapter"""
        if adapter_id not in self.runtime_adapters:
            logger.error(f"Runtime adapter {adapter_id} not found")
            return False
        
        try:
            runtime_adapter = self.runtime_adapters[adapter_id]
            success = await runtime_adapter.stop()
            
            if success:
                self.stats["running_adapters"] = max(0, self.stats["running_adapters"] - 1)
                logger.info(f"Stopped adapter {adapter_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error stopping adapter {adapter_id}: {e}")
            return False
    
    async def restart_adapter(self, adapter_id: str) -> bool:
        """Restart an adapter"""
        if adapter_id not in self.runtime_adapters:
            logger.error(f"Runtime adapter {adapter_id} not found")
            return False
        
        try:
            runtime_adapter = self.runtime_adapters[adapter_id]
            await runtime_adapter.restart()
            logger.info(f"Restarted adapter {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restarting adapter {adapter_id}: {e}")
            return False
    
    async def remove_adapter(self, adapter_id: str) -> bool:
        """Remove an adapter"""
        if adapter_id not in self.runtime_adapters:
            logger.error(f"Runtime adapter {adapter_id} not found")
            return False
        
        try:
            # Stop adapter first
            await self.stop_adapter(adapter_id)
            
            # Remove from registry
            await self.registry.remove_adapter(adapter_id)
            
            # Remove runtime adapter
            del self.runtime_adapters[adapter_id]
            
            # Update statistics
            self.stats["total_adapters"] = max(0, self.stats["total_adapters"] - 1)
            
            logger.info(f"Removed adapter {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing adapter {adapter_id}: {e}")
            return False
    
    async def start_all_adapters(self):
        """Start all adapters"""
        logger.info("Starting all adapters...")
        
        for adapter_id in self.runtime_adapters:
            await self.start_adapter(adapter_id)
        
        logger.info(f"Started {self.stats['running_adapters']} adapters")
    
    async def stop_all_adapters(self):
        """Stop all adapters"""
        logger.info("Stopping all adapters...")
        
        for adapter_id in list(self.runtime_adapters.keys()):
            await self.stop_adapter(adapter_id)
        
        logger.info("All adapters stopped")
    
    async def reload_adapter(self, adapter_id: str, new_config: Dict[str, Any]) -> bool:
        """Reload adapter with new configuration"""
        try:
            logger.info(f"Reloading adapter {adapter_id}")
            
            # Stop current adapter
            await self.stop_adapter(adapter_id)
            
            # Update configuration
            if adapter_id in self.runtime_adapters:
                self.runtime_adapters[adapter_id].config = new_config
            
            # Restart adapter
            await self.start_adapter(adapter_id)
            
            logger.info(f"Reloaded adapter {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading adapter {adapter_id}: {e}")
            return False
    
    def get_adapter_status(self, adapter_id: str) -> Dict[str, Any]:
        """Get adapter status"""
        if adapter_id not in self.runtime_adapters:
            return {"error": f"Adapter {adapter_id} not found"}
        
        runtime_adapter = self.runtime_adapters[adapter_id]
        return runtime_adapter.get_status()
    
    def get_all_adapter_status(self) -> Dict[str, Any]:
        """Get status of all adapters"""
        status = {
            "total_adapters": self.stats["total_adapters"],
            "running_adapters": self.stats["running_adapters"],
            "adapters": {}
        }
        
        for adapter_id, runtime_adapter in self.runtime_adapters.items():
            status["adapters"][adapter_id] = runtime_adapter.get_status()
        
        return status
    
    def get_adapter_stats(self) -> Dict[str, Any]:
        """Get adapter statistics (alias for get_all_adapter_status)"""
        return self.get_all_adapter_status()
    
    def get_available_adapters(self) -> List[str]:
        """Get list of available adapter types"""
        return self.discovery.get_available_adapters()
    
    def get_adapter_manifest(self, adapter_name: str) -> Optional[Dict[str, Any]]:
        """Get adapter manifest"""
        manifest = self.discovery.get_manifest(adapter_name)
        if manifest:
            return manifest.dict()
        return None
    
    async def _health_check_loop(self):
        """Health check loop for all adapters"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for adapter_id, runtime_adapter in self.runtime_adapters.items():
                    try:
                        is_healthy = await runtime_adapter.health_check()
                        if not is_healthy:
                            logger.warning(f"Adapter {adapter_id} health check failed, attempting restart...")
                            await self.restart_adapter(adapter_id)
                    except Exception as e:
                        logger.error(f"Health check error for adapter {adapter_id}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def shutdown(self):
        """Shutdown the enhanced manager"""
        logger.info("Shutting down Enhanced Multi-Platform Manager...")
        
        # Cancel health check
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Stop all adapters
        await self.stop_all_adapters()
        
        # Shutdown task manager
        await self.task_manager.shutdown()
        
        logger.info("Enhanced Multi-Platform Manager shutdown complete")
    
    async def _create_dingtalk_adapter(self, adapter_id: str, config: Dict[str, Any]):
        """Create DingTalk adapter instance"""
        try:
            from .dingtalk_client import MindBotDingTalkClient
            from .agent import MindBotAgent
            
            # Create agent instance
            agent = MindBotAgent(
                dify_api_key=config.get("dify_api_key"),
                dify_base_url=config.get("dify_base_url", "https://api.dify.ai/v1")
            )
            
            # Create DingTalk client with credentials from config
            dingtalk_client = MindBotDingTalkClient(
                agent_handler=agent.process_message,
                agent_instance=agent,
                client_id=config.get("client_id"),
                client_secret=config.get("client_secret"),
                robot_code=config.get("robot_code"),
                robot_name=config.get("robot_name"),
                card_template_id=config.get("card_template_id")
            )
            
            return dingtalk_client
            
        except Exception as e:
            logger.error(f"Error creating DingTalk adapter {adapter_id}: {e}")
            return None
    
    async def _create_wecom_adapter(self, adapter_id: str, config: Dict[str, Any]):
        """Create WeCom adapter instance"""
        try:
            from .wecom_direct_client import WeComDirectClient
            from .agent import MindBotAgent
            
            # Create agent instance
            agent = MindBotAgent(
                dify_api_key=config.get("dify_api_key"),
                dify_base_url=config.get("dify_base_url", "https://api.dify.ai/v1")
            )
            
            # Create WeCom client with credentials from config
            wecom_client = WeComDirectClient(
                agent_handler=agent.process_message,
                agent_instance=agent,
                corp_id=config.get("corp_id"),
                corp_secret=config.get("corp_secret"),
                agent_id=config.get("agent_id"),
                agent_name=config.get("agent_name")
            )
            
            return wecom_client
            
        except Exception as e:
            logger.error(f"Error creating WeCom adapter {adapter_id}: {e}")
            return None
