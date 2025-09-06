"""
Event Bus Architecture
Handles message routing and event processing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types of events that can be processed"""
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    PLATFORM_CONNECTED = "platform_connected"
    PLATFORM_DISCONNECTED = "platform_disconnected"
    ERROR_OCCURRED = "error_occurred"
    HEALTH_CHECK = "health_check"
    CUSTOM = "custom"

@dataclass
class Event:
    """Standard event format"""
    id: str
    type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: float
    metadata: Dict[str, Any]

class EventBus:
    """
    Event bus for handling message routing and event processing
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, Set[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.is_running = False
        self.event_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("event_bus")
        
        # Initialize subscribers for each event type
        for event_type in EventType:
            self.subscribers[event_type] = set()
    
    async def start(self) -> None:
        """Start the event bus"""
        self.is_running = True
        self.logger.info("Starting event bus...")
        
        # Start event processing loop
        asyncio.create_task(self._process_events())
        
        self.logger.info("Event bus started")
    
    async def stop(self) -> None:
        """Stop the event bus"""
        self.is_running = False
        self.logger.info("Event bus stopped")
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to the event bus
        """
        try:
            await self.event_queue.put(event)
            self.logger.debug(f"Published event: {event.type.value} from {event.source}")
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
    
    async def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Subscribe to events of a specific type
        """
        self.subscribers[event_type].add(handler)
        self.logger.info(f"Subscribed handler to {event_type.value}")
    
    async def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe from events of a specific type
        """
        self.subscribers[event_type].discard(handler)
        self.logger.info(f"Unsubscribed handler from {event_type.value}")
    
    async def register_handler(self, name: str, handler: Callable) -> None:
        """
        Register a named event handler
        """
        self.event_handlers[name] = handler
        self.logger.info(f"Registered event handler: {name}")
    
    async def unregister_handler(self, name: str) -> None:
        """
        Unregister a named event handler
        """
        if name in self.event_handlers:
            del self.event_handlers[name]
            self.logger.info(f"Unregistered event handler: {name}")
    
    async def _process_events(self) -> None:
        """
        Process events from the event queue
        """
        while self.is_running:
            try:
                # Wait for an event with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=1.0
                )
                
                # Process the event
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                # No event received, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _handle_event(self, event: Event) -> None:
        """
        Handle a single event
        """
        try:
            self.logger.debug(f"Handling event: {event.type.value} from {event.source}")
            
            # Notify subscribers
            await self._notify_subscribers(event)
            
            # Call registered handlers
            await self._call_handlers(event)
            
        except Exception as e:
            self.logger.error(f"Error handling event {event.id}: {e}")
    
    async def _notify_subscribers(self, event: Event) -> None:
        """
        Notify all subscribers of an event
        """
        subscribers = self.subscribers.get(event.type, set())
        
        if not subscribers:
            self.logger.debug(f"No subscribers for event type: {event.type.value}")
            return
        
        # Notify all subscribers concurrently
        tasks = []
        for handler in subscribers:
            task = asyncio.create_task(self._call_handler_safely(handler, event))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_handlers(self, event: Event) -> None:
        """
        Call all registered event handlers
        """
        if not self.event_handlers:
            return
        
        # Call all handlers concurrently
        tasks = []
        for name, handler in self.event_handlers.items():
            task = asyncio.create_task(self._call_handler_safely(handler, event))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_handler_safely(self, handler: Callable, event: Event) -> None:
        """
        Call a handler safely, catching any exceptions
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            self.logger.error(f"Handler {handler.__name__} failed: {e}")
    
    async def create_event(self, event_type: EventType, source: str, data: Dict[str, Any], 
                          metadata: Optional[Dict[str, Any]] = None) -> Event:
        """
        Create a new event
        """
        event_id = f"{event_type.value}_{int(datetime.now().timestamp() * 1000)}"
        
        return Event(
            id=event_id,
            type=event_type,
            source=source,
            data=data,
            timestamp=datetime.now().timestamp(),
            metadata=metadata or {}
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics
        """
        return {
            "is_running": self.is_running,
            "queue_size": self.event_queue.qsize(),
            "subscribers": {
                event_type.value: len(subscribers)
                for event_type, subscribers in self.subscribers.items()
            },
            "handlers": len(self.event_handlers)
        }
    
    async def health_check(self) -> bool:
        """
        Check if the event bus is healthy
        """
        return self.is_running and not self.event_queue.full()
