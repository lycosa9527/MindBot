"""
Runtime Adapter
Based on LangBot's RuntimeBot pattern for individual adapter lifecycle management
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .task_manager import TaskManager, TaskContext, TaskScope
from ..logging_config import get_logger

logger = get_logger(__name__)

class RuntimeAdapter:
    """Runtime adapter wrapper with lifecycle management"""
    
    def __init__(
        self,
        adapter_id: str,
        adapter_instance: Any,
        config: Dict[str, Any],
        task_manager: TaskManager,
        logger_name: Optional[str] = None
    ):
        self.adapter_id = adapter_id
        self.adapter_instance = adapter_instance
        self.config = config
        self.task_manager = task_manager
        self.logger = get_logger(logger_name or f"runtime-adapter-{adapter_id}")
        
        # Lifecycle state
        self.is_running = False
        self.is_enabled = config.get("enabled", True)
        self.start_time: Optional[datetime] = None
        self.last_heartbeat: Optional[datetime] = None
        
        # Task management
        self.task_wrapper: Optional[asyncio.Task] = None
        self.task_context = TaskContext()
        
        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}
        
    async def initialize(self):
        """Initialize the adapter"""
        try:
            self.logger.info(f"Initializing adapter {self.adapter_id}")
            
            # Initialize adapter instance
            if hasattr(self.adapter_instance, 'initialize'):
                await self.adapter_instance.initialize()
            
            # Register event handlers
            await self._register_event_handlers()
            
            self.logger.info(f"Adapter {self.adapter_id} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing adapter {self.adapter_id}: {e}")
            raise
    
    async def start(self):
        """Start the adapter"""
        if self.is_running:
            self.logger.warning(f"Adapter {self.adapter_id} already running")
            return
        
        if not self.is_enabled:
            self.logger.info(f"Adapter {self.adapter_id} is disabled, skipping start")
            return
        
        try:
            self.logger.info(f"Starting adapter {self.adapter_id}")
            
            # Create task wrapper with error handling
            self.task_wrapper = self.task_manager.create_task(
                self._run_with_error_handling(),
                kind='platform-adapter',
                name=f'platform-adapter-{self.adapter_id}',
                context=self.task_context,
                scopes=[TaskScope.APPLICATION, TaskScope.PLATFORM]
            )
            
            self.is_running = True
            self.start_time = datetime.now()
            self.last_heartbeat = datetime.now()
            
            self.logger.info(f"Adapter {self.adapter_id} started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting adapter {self.adapter_id}: {e}")
            raise
    
    async def stop(self):
        """Stop the adapter"""
        if not self.is_running:
            self.logger.warning(f"Adapter {self.adapter_id} not running")
            return
        
        try:
            self.logger.info(f"Stopping adapter {self.adapter_id}")
            
            # Cancel task
            if self.task_wrapper:
                self.task_manager.cancel_task(self.task_wrapper)
                self.task_wrapper = None
            
            # Cleanup adapter
            if hasattr(self.adapter_instance, 'cleanup'):
                await self.adapter_instance.cleanup()
            
            self.is_running = False
            self.logger.info(f"Adapter {self.adapter_id} stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping adapter {self.adapter_id}: {e}")
            raise
    
    async def restart(self):
        """Restart the adapter"""
        self.logger.info(f"Restarting adapter {self.adapter_id}")
        await self.stop()
        await asyncio.sleep(1)  # Brief pause
        await self.start()
    
    async def _run_with_error_handling(self):
        """Run adapter with comprehensive error handling"""
        try:
            self.task_context.set_current_action('Running...')
            
            # Start adapter
            if hasattr(self.adapter_instance, 'start'):
                await self.adapter_instance.start()
            
            # Run adapter
            if hasattr(self.adapter_instance, 'run'):
                await self.adapter_instance.run()
            else:
                # Keep running until cancelled
                while True:
                    await asyncio.sleep(1)
                    self.last_heartbeat = datetime.now()
                    
        except asyncio.CancelledError:
            self.task_context.set_current_action('Cancelled')
            self.logger.info(f"Adapter {self.adapter_id} cancelled")
            raise
        except Exception as e:
            self.task_context.set_current_action('Error')
            self.logger.error(f"Adapter {self.adapter_id} error: {e}")
            raise
        finally:
            self.task_context.set_current_action('Stopped')
            self.is_running = False
    
    async def _register_event_handlers(self):
        """Register event handlers for the adapter"""
        # This would be implemented based on the specific adapter type
        # For now, it's a placeholder
        pass
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type] = handler
    
    def unregister_event_handler(self, event_type: str):
        """Unregister an event handler"""
        if event_type in self.event_handlers:
            del self.event_handlers[event_type]
    
    async def send_message(self, target_type: str, target_id: str, message: Any):
        """Send message through the adapter"""
        if not self.is_running:
            raise RuntimeError(f"Adapter {self.adapter_id} not running")
        
        if hasattr(self.adapter_instance, 'send_message'):
            return await self.adapter_instance.send_message(target_type, target_id, message)
        else:
            raise NotImplementedError(f"Adapter {self.adapter_id} does not support send_message")
    
    async def reply_message(self, message_source: Any, message: Any, quote_origin: bool = False):
        """Reply to a message through the adapter"""
        if not self.is_running:
            raise RuntimeError(f"Adapter {self.adapter_id} not running")
        
        if hasattr(self.adapter_instance, 'reply_message'):
            return await self.adapter_instance.reply_message(message_source, message, quote_origin)
        else:
            raise NotImplementedError(f"Adapter {self.adapter_id} does not support reply_message")
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status information"""
        return {
            "adapter_id": self.adapter_id,
            "is_running": self.is_running,
            "is_enabled": self.is_enabled,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "current_action": self.task_context.current_action,
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def enable(self):
        """Enable the adapter"""
        self.is_enabled = True
        self.logger.info(f"Adapter {self.adapter_id} enabled")
    
    def disable(self):
        """Disable the adapter"""
        self.is_enabled = False
        self.logger.info(f"Adapter {self.adapter_id} disabled")
    
    async def health_check(self) -> bool:
        """Perform health check on the adapter"""
        try:
            if not self.is_running:
                return False
            
            # Check if task is still running
            if self.task_wrapper and self.task_wrapper.is_done():
                return False
            
            # Check last heartbeat
            if self.last_heartbeat:
                time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
                if time_since_heartbeat > 300:  # 5 minutes
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed for adapter {self.adapter_id}: {e}")
            return False
