"""
Message Processing Pipeline
Handles async message processing with error handling and retry logic
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import traceback

from ..platforms.base import Message, Response, MessageType

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Stages in the message processing pipeline"""
    RECEIVED = "received"
    VALIDATED = "validated"
    CLASSIFIED = "classified"
    PROCESSED = "processed"
    RESPONDED = "responded"
    FAILED = "failed"

@dataclass
class ProcessingContext:
    """Context for message processing"""
    message: Message
    stage: ProcessingStage
    start_time: datetime
    attempts: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class MessageProcessor:
    """
    Handles message processing with pipeline stages and error handling
    """
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.processing_queue = asyncio.Queue()
        self.is_running = False
        self.logger = logging.getLogger("message_processor")
        
        # Processing stages
        self.stages: Dict[ProcessingStage, List[Callable]] = {
            ProcessingStage.RECEIVED: [],
            ProcessingStage.VALIDATED: [],
            ProcessingStage.CLASSIFIED: [],
            ProcessingStage.PROCESSED: [],
            ProcessingStage.RESPONDED: [],
            ProcessingStage.FAILED: []
        }
        
        # Error handlers
        self.error_handlers: List[Callable] = []
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    async def start(self) -> None:
        """Start the message processor"""
        self.is_running = True
        self.logger.info("Starting message processor...")
        
        # Start processing loop
        asyncio.create_task(self._process_messages())
        
        self.logger.info("Message processor started")
    
    async def stop(self) -> None:
        """Stop the message processor"""
        self.is_running = False
        self.logger.info("Message processor stopped")
    
    async def process_message(self, message: Message) -> Optional[Response]:
        """
        Process a message through the pipeline
        Returns the response if successful, None otherwise
        """
        context = ProcessingContext(
            message=message,
            stage=ProcessingStage.RECEIVED,
            start_time=datetime.now()
        )
        
        try:
            # Add to processing queue
            await self.processing_queue.put(context)
            self.logger.info(f"Queued message {message.id} for processing")
            
            # Wait for processing to complete
            return await self._wait_for_completion(context)
            
        except Exception as e:
            self.logger.error(f"Failed to process message {message.id}: {e}")
            await self._handle_error(context, e)
            return None
    
    async def _wait_for_completion(self, context: ProcessingContext) -> Optional[Response]:
        """
        Wait for message processing to complete
        """
        # This is a simplified implementation
        # In a real system, you'd use a more sophisticated completion tracking
        await asyncio.sleep(0.1)  # Simulate processing time
        return None
    
    async def _process_messages(self) -> None:
        """
        Main message processing loop
        """
        while self.is_running:
            try:
                # Wait for a message with timeout
                context = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=1.0
                )
                
                # Process the message
                await self._process_single_message(context)
                
            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
    
    async def _process_single_message(self, context: ProcessingContext) -> None:
        """
        Process a single message through all stages
        """
        try:
            self.logger.info(f"Processing message {context.message.id} through pipeline")
            
            # Execute each stage
            for stage in ProcessingStage:
                if stage == ProcessingStage.FAILED:
                    continue  # Skip failed stage
                
                context.stage = stage
                success = await self._execute_stage(context, stage)
                
                if not success:
                    context.stage = ProcessingStage.FAILED
                    await self._handle_error(context, Exception(f"Stage {stage.value} failed"))
                    return
            
            # Processing completed successfully
            self.logger.info(f"Message {context.message.id} processed successfully")
            
        except Exception as e:
            context.stage = ProcessingStage.FAILED
            await self._handle_error(context, e)
    
    async def _execute_stage(self, context: ProcessingContext, stage: ProcessingStage) -> bool:
        """
        Execute a specific processing stage
        """
        try:
            self.logger.debug(f"Executing stage {stage.value} for message {context.message.id}")
            
            # Execute stage handlers
            handlers = self.stages.get(stage, [])
            for handler in handlers:
                await self._call_handler_safely(handler, context)
            
            # Execute stage-specific logic
            if stage == ProcessingStage.RECEIVED:
                return await self._handle_received(context)
            elif stage == ProcessingStage.VALIDATED:
                return await self._handle_validated(context)
            elif stage == ProcessingStage.CLASSIFIED:
                return await self._handle_classified(context)
            elif stage == ProcessingStage.PROCESSED:
                return await self._handle_processed(context)
            elif stage == ProcessingStage.RESPONDED:
                return await self._handle_responded(context)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Stage {stage.value} failed for message {context.message.id}: {e}")
            return False
    
    async def _handle_received(self, context: ProcessingContext) -> bool:
        """Handle message received stage"""
        self.logger.debug(f"Message {context.message.id} received")
        return True
    
    async def _handle_validated(self, context: ProcessingContext) -> bool:
        """Handle message validation stage"""
        message = context.message
        
        # Basic validation
        if not message.content or not message.user_id:
            self.logger.warning(f"Invalid message {message.id}: missing content or user_id")
            return False
        
        self.logger.debug(f"Message {message.id} validated")
        return True
    
    async def _handle_classified(self, context: ProcessingContext) -> bool:
        """Handle message classification stage"""
        message = context.message
        
        # Simple classification based on content
        if message.content.startswith("/"):
            context.metadata["type"] = "command"
        elif "?" in message.content:
            context.metadata["type"] = "question"
        else:
            context.metadata["type"] = "conversation"
        
        self.logger.debug(f"Message {message.id} classified as {context.metadata['type']}")
        return True
    
    async def _handle_processed(self, context: ProcessingContext) -> bool:
        """Handle message processing stage"""
        message = context.message
        
        # This is where the LLM would be called
        # For now, we'll just create a simple response
        response_content = f"Processed: {message.content}"
        
        context.metadata["response"] = Response(
            message_id=message.id,
            platform=message.platform,
            content=response_content,
            message_type=MessageType.TEXT,
            metadata={},
            success=True
        )
        
        self.logger.debug(f"Message {message.id} processed")
        return True
    
    async def _handle_responded(self, context: ProcessingContext) -> bool:
        """Handle response stage"""
        response = context.metadata.get("response")
        if response:
            self.logger.debug(f"Response created for message {context.message.id}")
            return True
        
        return False
    
    async def _call_handler_safely(self, handler: Callable, context: ProcessingContext) -> None:
        """
        Call a handler safely, catching any exceptions
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(context)
            else:
                handler(context)
        except Exception as e:
            self.logger.error(f"Handler {handler.__name__} failed: {e}")
    
    async def _handle_error(self, context: ProcessingContext, error: Exception) -> None:
        """
        Handle processing errors
        """
        context.attempts += 1
        
        self.logger.error(f"Error processing message {context.message.id}: {error}")
        self.logger.error(traceback.format_exc())
        
        # Call error handlers
        for handler in self.error_handlers:
            try:
                await self._call_handler_safely(handler, context, error)
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
        
        # Retry if we haven't exceeded max attempts
        if context.attempts < context.max_attempts:
            self.logger.info(f"Retrying message {context.message.id} (attempt {context.attempts + 1})")
            await asyncio.sleep(self.retry_delay * context.attempts)
            await self.processing_queue.put(context)
        else:
            self.logger.error(f"Message {context.message.id} failed after {context.attempts} attempts")
    
    def register_stage_handler(self, stage: ProcessingStage, handler: Callable) -> None:
        """Register a handler for a specific stage"""
        self.stages[stage].append(handler)
        self.logger.info(f"Registered handler for stage {stage.value}")
    
    def register_error_handler(self, handler: Callable) -> None:
        """Register an error handler"""
        self.error_handlers.append(handler)
        self.logger.info("Registered error handler")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get message processor statistics"""
        return {
            "is_running": self.is_running,
            "queue_size": self.processing_queue.qsize(),
            "stages": {
                stage.value: len(handlers)
                for stage, handlers in self.stages.items()
            },
            "error_handlers": len(self.error_handlers)
        }
    
    async def health_check(self) -> bool:
        """Check if the message processor is healthy"""
        return self.is_running and not self.processing_queue.full()
