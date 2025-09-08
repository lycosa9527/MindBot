"""
Adapter Registry
Manages adapter instances and their lifecycle
"""

import asyncio
import logging
from typing import Dict, List, Optional, Type, Any
from .engine import AdapterManifest, ComponentDiscovery

logger = logging.getLogger(__name__)

class AdapterRegistry:
    """Registry for managing adapter instances"""
    
    def __init__(self, discovery: ComponentDiscovery):
        self.discovery = discovery
        self.adapters: Dict[str, Any] = {}
        self.adapter_tasks: Dict[str, asyncio.Task] = {}
        self.adapter_status: Dict[str, str] = {}
        
    async def register_adapter(self, adapter_id: str, adapter_name: str, config: Dict[str, Any]) -> bool:
        """Register a new adapter instance"""
        try:
            # Validate configuration
            if not self.discovery.validate_config(adapter_name, config):
                logger.error(f"Invalid configuration for adapter {adapter_id}")
                return False
            
            # Load adapter class
            adapter_class = await self.discovery.load_adapter_class(adapter_name)
            if not adapter_class:
                logger.error(f"Failed to load adapter class {adapter_name}")
                return False
            
            # Create adapter instance
            adapter_instance = adapter_class(adapter_id, config)
            
            # Store adapter
            self.adapters[adapter_id] = adapter_instance
            self.adapter_status[adapter_id] = "registered"
            
            logger.info(f"Registered adapter {adapter_id} ({adapter_name})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering adapter {adapter_id}: {e}")
            return False
    
    async def start_adapter(self, adapter_id: str) -> bool:
        """Start an adapter instance"""
        if adapter_id not in self.adapters:
            logger.error(f"Adapter {adapter_id} not found")
            return False
        
        if adapter_id in self.adapter_tasks:
            logger.warning(f"Adapter {adapter_id} already running")
            return True
        
        try:
            adapter_instance = self.adapters[adapter_id]
            
            # Start adapter in task
            task = asyncio.create_task(
                self._run_adapter_with_error_handling(adapter_id, adapter_instance),
                name=f"adapter-{adapter_id}"
            )
            
            self.adapter_tasks[adapter_id] = task
            self.adapter_status[adapter_id] = "running"
            
            logger.info(f"Started adapter {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting adapter {adapter_id}: {e}")
            return False
    
    async def stop_adapter(self, adapter_id: str) -> bool:
        """Stop an adapter instance"""
        if adapter_id not in self.adapters:
            logger.error(f"Adapter {adapter_id} not found")
            return False
        
        try:
            # Cancel task
            if adapter_id in self.adapter_tasks:
                task = self.adapter_tasks[adapter_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.adapter_tasks[adapter_id]
            
            # Cleanup adapter
            adapter_instance = self.adapters[adapter_id]
            if hasattr(adapter_instance, 'cleanup'):
                await adapter_instance.cleanup()
            
            self.adapter_status[adapter_id] = "stopped"
            logger.info(f"Stopped adapter {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping adapter {adapter_id}: {e}")
            return False
    
    async def remove_adapter(self, adapter_id: str) -> bool:
        """Remove an adapter instance"""
        # Stop first
        await self.stop_adapter(adapter_id)
        
        # Remove from registry
        if adapter_id in self.adapters:
            del self.adapters[adapter_id]
        if adapter_id in self.adapter_status:
            del self.adapter_status[adapter_id]
        
        logger.info(f"Removed adapter {adapter_id}")
        return True
    
    async def _run_adapter_with_error_handling(self, adapter_id: str, adapter_instance: Any):
        """Run adapter with comprehensive error handling"""
        try:
            # Start adapter
            if hasattr(adapter_instance, 'start'):
                await adapter_instance.start()
            
            # Run adapter
            if hasattr(adapter_instance, 'run'):
                await adapter_instance.run()
            else:
                # Keep running until cancelled
                while True:
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info(f"Adapter {adapter_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Adapter {adapter_id} error: {e}")
            self.adapter_status[adapter_id] = "error"
        finally:
            # Cleanup
            if hasattr(adapter_instance, 'cleanup'):
                try:
                    await adapter_instance.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up adapter {adapter_id}: {e}")
    
    def get_adapter(self, adapter_id: str) -> Optional[Any]:
        """Get adapter instance by ID"""
        return self.adapters.get(adapter_id)
    
    def get_adapter_status(self, adapter_id: str) -> str:
        """Get adapter status"""
        return self.adapter_status.get(adapter_id, "unknown")
    
    def get_all_adapters(self) -> Dict[str, Any]:
        """Get all adapter instances"""
        return self.adapters.copy()
    
    def get_running_adapters(self) -> List[str]:
        """Get list of running adapter IDs"""
        return [adapter_id for adapter_id, status in self.adapter_status.items() 
                if status == "running"]
    
    async def shutdown_all(self):
        """Shutdown all adapters"""
        for adapter_id in list(self.adapters.keys()):
            await self.stop_adapter(adapter_id)
