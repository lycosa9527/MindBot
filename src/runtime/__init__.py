"""
Runtime Adapter Management
Based on LangBot's RuntimeBot pattern
"""

from .runtime_adapter import RuntimeAdapter
from .task_manager import TaskManager, TaskContext, TaskScope

__all__ = [
    "RuntimeAdapter",
    "TaskManager", 
    "TaskContext",
    "TaskScope"
]
