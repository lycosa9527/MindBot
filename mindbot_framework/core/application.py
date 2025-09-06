"""
MindBot Application
Main orchestrator for the MindBot framework
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional
from datetime import datetime

from .lifecycle import LifecycleManager, LifecycleStage
from .event_bus import EventBus, EventType
from .message_processor import MessageProcessor
from ..platforms.base import PlatformAdapter

logger = logging.getLogger(__name__)

class MindBotApplication:
    """
    Main MindBot application orchestrator
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lifecycle_manager = LifecycleManager()
        self.event_bus = EventBus()
        self.message_processor = MessageProcessor(self.event_bus)
        self.platform_adapters: Dict[str, PlatformAdapter] = {}
        self.is_running = False
        
        # Setup logging
        self._setup_logging()
        
        # Register components with lifecycle manager
        self._register_components()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_format = self.config.get('logging', {}).get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('mindbot.log')
            ]
        )
        
        logger.info("Logging configured")
    
    def _register_components(self):
        """Register components with the lifecycle manager"""
        # Register event bus
        self.lifecycle_manager.register_component(
            "event_bus", 
            self.event_bus, 
            LifecycleStage.SETUP_LOGGING
        )
        
        # Register message processor
        self.lifecycle_manager.register_component(
            "message_processor", 
            self.message_processor, 
            LifecycleStage.START_EVENT_PROCESSING
        )
        
        # Register stage handlers
        self.lifecycle_manager.register_stage_handler(
            LifecycleStage.SETUP_LOGGING,
            self._setup_logging_stage
        )
        
        self.lifecycle_manager.register_stage_handler(
            LifecycleStage.LOAD_CONFIGURATION,
            self._load_configuration_stage
        )
        
        self.lifecycle_manager.register_stage_handler(
            LifecycleStage.START_PLATFORM_ADAPTERS,
            self._start_platform_adapters_stage
        )
        
        self.lifecycle_manager.register_stage_handler(
            LifecycleStage.START_EVENT_PROCESSING,
            self._start_event_processing_stage
        )
        
        # Register shutdown handlers
        self.lifecycle_manager.register_shutdown_handler(self._shutdown_handler)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _setup_logging_stage(self):
        """Setup logging stage handler"""
        logger.info("Setting up logging...")
        # Logging is already configured in __init__
        logger.info("Logging setup completed")
    
    async def _load_configuration_stage(self):
        """Load configuration stage handler"""
        logger.info("Loading configuration...")
        # Configuration is already loaded in __init__
        logger.info("Configuration loaded")
    
    async def _start_platform_adapters_stage(self):
        """Start platform adapters stage handler"""
        logger.info("Starting platform adapters...")
        
        # This is where platform adapters would be started
        # For now, we'll just log that we're ready
        logger.info("Platform adapters ready")
    
    async def _start_event_processing_stage(self):
        """Start event processing stage handler"""
        logger.info("Starting event processing...")
        
        # Start event bus
        await self.event_bus.start()
        
        # Start message processor
        await self.message_processor.start()
        
        logger.info("Event processing started")
    
    async def _shutdown_handler(self):
        """Shutdown handler"""
        logger.info("Shutting down MindBot application...")
        
        # Stop message processor
        await self.message_processor.stop()
        
        # Stop event bus
        await self.event_bus.stop()
        
        # Stop platform adapters
        for adapter in self.platform_adapters.values():
            await adapter.stop()
        
        logger.info("MindBot application shutdown completed")
    
    async def start(self) -> bool:
        """
        Start the MindBot application
        Returns True if successful, False otherwise
        """
        try:
            logger.info("Starting MindBot application...")
            
            # Initialize all components
            success = await self.lifecycle_manager.initialize()
            if not success:
                logger.error("Failed to initialize MindBot application")
                return False
            
            self.is_running = True
            logger.info("MindBot application started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MindBot application: {e}")
            return False
    
    async def stop(self) -> None:
        """
        Stop the MindBot application
        """
        if not self.is_running:
            logger.warning("MindBot application is not running")
            return
        
        self.is_running = False
        await self.lifecycle_manager.shutdown()
        logger.info("MindBot application stopped")
    
    async def shutdown(self) -> None:
        """
        Shutdown the MindBot application
        """
        await self.stop()
    
    def register_platform_adapter(self, adapter: PlatformAdapter) -> None:
        """
        Register a platform adapter
        """
        self.platform_adapters[adapter.name] = adapter
        self.lifecycle_manager.register_component(
            adapter.name,
            adapter,
            LifecycleStage.START_PLATFORM_ADAPTERS
        )
        logger.info(f"Registered platform adapter: {adapter.name}")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get application status
        """
        return {
            "is_running": self.is_running,
            "start_time": datetime.now().isoformat(),
            "lifecycle": self.lifecycle_manager.get_status(),
            "event_bus": await self.event_bus.get_stats(),
            "message_processor": await self.message_processor.get_stats(),
            "platform_adapters": {
                name: await adapter.get_platform_info()
                for name, adapter in self.platform_adapters.items()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check
        """
        health_status = {
            "overall": "healthy",
            "components": {}
        }
        
        # Check lifecycle manager
        lifecycle_health = self.lifecycle_manager.get_health_status()
        health_status["components"]["lifecycle"] = lifecycle_health
        
        # Check event bus
        event_bus_health = await self.event_bus.health_check()
        health_status["components"]["event_bus"] = "healthy" if event_bus_health else "unhealthy"
        
        # Check message processor
        message_processor_health = await self.message_processor.health_check()
        health_status["components"]["message_processor"] = "healthy" if message_processor_health else "unhealthy"
        
        # Check platform adapters
        for name, adapter in self.platform_adapters.items():
            adapter_health = await adapter.health_check()
            health_status["components"][f"platform_{name}"] = "healthy" if adapter_health else "unhealthy"
        
        # Determine overall health
        if any(status != "healthy" for status in health_status["components"].values()):
            health_status["overall"] = "unhealthy"
        
        return health_status
    
    async def run(self) -> None:
        """
        Run the MindBot application
        """
        try:
            # Start the application
            success = await self.start()
            if not success:
                logger.error("Failed to start MindBot application")
                return
            
            # Keep running until stopped
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error in MindBot application: {e}")
        finally:
            await self.shutdown()
    
    def __str__(self) -> str:
        return f"MindBotApplication(running={self.is_running})"
    
    def __repr__(self) -> str:
        return f"MindBotApplication(config={self.config})"
