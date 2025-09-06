"""
MindBot Framework
A high-concurrency, event-driven multi-platform LLM bot framework
"""

__version__ = "0.1.0"
__author__ = "MindSpring Team"
__email__ = "team@mindspring.ai"

from .core.application import MindBotApplication
from .core.lifecycle import LifecycleManager, LifecycleStage
from .core.event_bus import EventBus, EventType
from .core.message_processor import MessageProcessor, ProcessingStage
from .platforms.base import PlatformAdapter, Message, Response, MessageType

__all__ = [
    "MindBotApplication",
    "LifecycleManager", 
    "LifecycleStage",
    "EventBus",
    "EventType",
    "MessageProcessor",
    "ProcessingStage",
    "PlatformAdapter",
    "Message",
    "Response", 
    "MessageType"
]