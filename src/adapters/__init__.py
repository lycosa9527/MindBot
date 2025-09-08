"""
Adapter implementations for the enhanced multi-platform system
"""

from .dingtalk_adapter import DingTalkAdapter
from .wecom_adapter import WeComAdapter

__all__ = [
    "DingTalkAdapter",
    "WeComAdapter"
]
