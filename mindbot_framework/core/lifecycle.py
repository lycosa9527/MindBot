"""
MindBot Lifecycle Manager
Handles stage-based initialization and graceful shutdown
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)

class LifecycleStage(Enum):
    """Lifecycle stages in order of execution"""
    SETUP_LOGGING = "setup_logging"
    LOAD_CONFIGURATION = "load_configuration"
    INITIALIZE_DATABASE = "initialize_database"
    START_PLATFORM_ADAPTERS = "start_platform_adapters"
    START_EVENT_PROCESSING = "start_event_processing"
    READY = "ready"

@dataclass
class ComponentStatus:
    """Status of a lifecycle component"""
    name: str
    stage: LifecycleStage
    status: str  # "pending", "running", "completed", "failed"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None

class LifecycleManager:
    """
    Manages the lifecycle of MindBot components with stage-based initialization
    """
    
    def __init__(self):
        self.components: Dict[str, Any] = {}
        self.component_status: Dict[str, ComponentStatus] = {}
        self.stage_handlers: Dict[LifecycleStage, List[Callable]] = {}
        self.shutdown_handlers: List[Callable] = []
        self.is_initialized = False
        self.is_shutting_down = False
        
        # Setup stage handlers
        self._setup_stage_handlers()
    
    def _setup_stage_handlers(self):
        """Setup default stage handlers"""
        self.stage_handlers = {
            LifecycleStage.SETUP_LOGGING: [],
            LifecycleStage.LOAD_CONFIGURATION: [],
            LifecycleStage.INITIALIZE_DATABASE: [],
            LifecycleStage.START_PLATFORM_ADAPTERS: [],
            LifecycleStage.START_EVENT_PROCESSING: [],
            LifecycleStage.READY: []
        }
    
    def register_component(self, name: str, component: Any, stage: LifecycleStage):
        """Register a component for lifecycle management"""
        self.components[name] = component
        self.component_status[name] = ComponentStatus(
            name=name,
            stage=stage,
            status="pending"
        )
        logger.info(f"Registered component '{name}' for stage {stage.value}")
    
    def register_stage_handler(self, stage: LifecycleStage, handler: Callable):
        """Register a handler for a specific stage"""
        if stage not in self.stage_handlers:
            self.stage_handlers[stage] = []
        self.stage_handlers[stage].append(handler)
        logger.debug(f"Registered handler for stage {stage.value}")
    
    def register_shutdown_handler(self, handler: Callable):
        """Register a handler for shutdown"""
        self.shutdown_handlers.append(handler)
        logger.debug("Registered shutdown handler")
    
    async def initialize(self) -> bool:
        """
        Initialize all components in stage order
        Returns True if successful, False otherwise
        """
        if self.is_initialized:
            logger.warning("LifecycleManager already initialized")
            return True
        
        logger.info("Starting MindBot lifecycle initialization...")
        
        try:
            # Execute stages in order
            for stage in LifecycleStage:
                if stage == LifecycleStage.READY:
                    continue  # Skip READY stage, it's just a marker
                
                logger.info(f"Executing stage: {stage.value}")
                success = await self._execute_stage(stage)
                
                if not success:
                    logger.error(f"Stage {stage.value} failed, stopping initialization")
                    await self.shutdown()
                    return False
            
            # Mark as ready
            self.is_initialized = True
            logger.info("MindBot lifecycle initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Lifecycle initialization failed: {e}")
            logger.error(traceback.format_exc())
            await self.shutdown()
            return False
    
    async def _execute_stage(self, stage: LifecycleStage) -> bool:
        """Execute a specific lifecycle stage"""
        stage_start_time = datetime.now()
        logger.info(f"Executing stage: {stage.value}")
        
        try:
            # Execute stage handlers
            if stage in self.stage_handlers:
                for handler in self.stage_handlers[stage]:
                    await handler()
            
            # Initialize components for this stage
            stage_components = [
                name for name, status in self.component_status.items()
                if status.stage == stage and status.status == "pending"
            ]
            
            for component_name in stage_components:
                success = await self._initialize_component(component_name)
                if not success:
                    return False
            
            stage_duration = (datetime.now() - stage_start_time).total_seconds()
            logger.info(f"Stage {stage.value} completed in {stage_duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Stage {stage.value} failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def _initialize_component(self, component_name: str) -> bool:
        """Initialize a specific component"""
        component = self.components[component_name]
        status = self.component_status[component_name]
        
        logger.info(f"Initializing component: {component_name}")
        status.status = "running"
        status.start_time = datetime.now()
        
        try:
            # Try to call initialize method if it exists
            if hasattr(component, 'initialize'):
                await component.initialize()
            elif hasattr(component, 'start'):
                await component.start()
            
            status.status = "completed"
            status.end_time = datetime.now()
            duration = (status.end_time - status.start_time).total_seconds()
            logger.info(f"Component {component_name} initialized in {duration:.2f}s")
            return True
            
        except Exception as e:
            status.status = "failed"
            status.end_time = datetime.now()
            status.error = str(e)
            logger.error(f"Component {component_name} failed to initialize: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        if self.is_shutting_down:
            logger.warning("Shutdown already in progress")
            return
        
        self.is_shutting_down = True
        logger.info("Starting MindBot shutdown...")
        
        try:
            # Execute shutdown handlers
            for handler in self.shutdown_handlers:
                try:
                    await handler()
                except Exception as e:
                    logger.error(f"Shutdown handler failed: {e}")
            
            # Shutdown components in reverse order
            for component_name in reversed(list(self.components.keys())):
                await self._shutdown_component(component_name)
            
            logger.info("MindBot shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            logger.error(traceback.format_exc())
    
    async def _shutdown_component(self, component_name: str):
        """Shutdown a specific component"""
        component = self.components[component_name]
        status = self.component_status[component_name]
        
        logger.info(f"Shutting down component: {component_name}")
        
        try:
            # Try to call shutdown method if it exists
            if hasattr(component, 'shutdown'):
                await component.shutdown()
            elif hasattr(component, 'stop'):
                await component.stop()
            
            status.status = "completed"
            logger.info(f"Component {component_name} shut down successfully")
            
        except Exception as e:
            logger.error(f"Component {component_name} failed to shutdown: {e}")
            logger.error(traceback.format_exc())
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all components"""
        return {
            "is_initialized": self.is_initialized,
            "is_shutting_down": self.is_shutting_down,
            "components": {
                name: {
                    "stage": status.stage.value,
                    "status": status.status,
                    "start_time": status.start_time.isoformat() if status.start_time else None,
                    "end_time": status.end_time.isoformat() if status.end_time else None,
                    "error": status.error
                }
                for name, status in self.component_status.items()
            }
        }
    
    def get_health_status(self) -> str:
        """Get overall health status"""
        if self.is_shutting_down:
            return "shutting_down"
        elif not self.is_initialized:
            return "initializing"
        
        # Check if any components failed
        failed_components = [
            name for name, status in self.component_status.items()
            if status.status == "failed"
        ]
        
        if failed_components:
            return "unhealthy"
        
        # Check if all components are completed
        all_completed = all(
            status.status == "completed"
            for status in self.component_status.values()
        )
        
        return "healthy" if all_completed else "initializing"
