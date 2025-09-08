"""
MindBot Platforms Module
Platform adapters for different messaging platforms
"""

from .base import PlatformAdapter, Message, Response, MessageType
from .adapters import DingTalkAdapter, WeComAdapter, SlackAdapter

__all__ = [
    "PlatformAdapter",
    "Message", 
    "Response",
    "MessageType",
    "DingTalkAdapter",
    "WeComAdapter",
    "SlackAdapter",
]
