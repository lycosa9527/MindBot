"""
Platform Adapters
Collection of platform-specific adapter implementations
"""

from .dingtalk import DingTalkAdapter
from .wecom import WeComAdapter
from .slack import SlackAdapter

__all__ = [
    "DingTalkAdapter",
    "WeComAdapter", 
    "SlackAdapter",
]
