"""
Task Manager
Based on LangBot's task management system
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from ..logging_config import get_logger

logger = get_logger(__name__)

class TaskScope(Enum):
    """Task lifecycle scopes"""
    APPLICATION = "application"
    PLATFORM = "platform"
    ADAPTER = "adapter"
    SESSION = "session"

class TaskContext:
    """Task execution context"""
    
    def __init__(self):
        self.current_action = "Initializing"
        self.start_time = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def set_current_action(self, action: str):
        """Set current action description"""
        self.current_action = action
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)

class TaskWrapper:
    """Task wrapper with metadata"""
    
    def __init__(
        self,
        task_id: str,
        task: asyncio.Task,
        kind: str,
        name: str,
        context: TaskContext,
        scopes: List[TaskScope]
    ):
        self.task_id = task_id
        self.task = task
        self.kind = kind
        self.name = name
        self.context = context
        self.scopes = scopes
        self.created_at = datetime.now()
    
    @property
    def id(self) -> str:
        return self.task_id
    
    def cancel(self):
        """Cancel the task"""
        self.task.cancel()
    
    def is_done(self) -> bool:
        """Check if task is done"""
        return self.task.done()
    
    def get_result(self):
        """Get task result"""
        return self.task.result()
    
    def get_exception(self):
        """Get task exception"""
        return self.task.exception()

class TaskManager:
    """Task manager for lifecycle control"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskWrapper] = {}
        self.task_counter = 0
    
    def create_task(
        self,
        coro,
        kind: str,
        name: str,
        context: TaskContext,
        scopes: List[TaskScope]
    ) -> TaskWrapper:
        """Create a new task with metadata"""
        task_id = f"{kind}-{self.task_counter}-{uuid.uuid4().hex[:8]}"
        self.task_counter += 1
        
        # Create asyncio task
        task = asyncio.create_task(coro, name=name)
        
        # Create wrapper
        wrapper = TaskWrapper(
            task_id=task_id,
            task=task,
            kind=kind,
            name=name,
            context=context,
            scopes=scopes
        )
        
        # Store task
        self.tasks[task_id] = wrapper
        
        # Add done callback for cleanup
        task.add_done_callback(lambda t: self._cleanup_task(task_id))
        
        logger.info(f"Created task {task_id} ({kind}): {name}")
        return wrapper
    
    def cancel_task(self, task_id: str):
        """Cancel a task by ID"""
        if task_id in self.tasks:
            wrapper = self.tasks[task_id]
            wrapper.cancel()
            logger.info(f"Cancelled task {task_id}")
    
    def cancel_tasks_by_scope(self, scope: TaskScope):
        """Cancel all tasks in a specific scope"""
        cancelled_count = 0
        for task_id, wrapper in self.tasks.items():
            if scope in wrapper.scopes:
                wrapper.cancel()
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} tasks in scope {scope.value}")
    
    def cancel_tasks_by_kind(self, kind: str):
        """Cancel all tasks of a specific kind"""
        cancelled_count = 0
        for task_id, wrapper in self.tasks.items():
            if wrapper.kind == kind:
                wrapper.cancel()
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} tasks of kind {kind}")
    
    def get_task(self, task_id: str) -> Optional[TaskWrapper]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_scope(self, scope: TaskScope) -> List[TaskWrapper]:
        """Get all tasks in a specific scope"""
        return [wrapper for wrapper in self.tasks.values() if scope in wrapper.scopes]
    
    def get_tasks_by_kind(self, kind: str) -> List[TaskWrapper]:
        """Get all tasks of a specific kind"""
        return [wrapper for wrapper in self.tasks.values() if wrapper.kind == kind]
    
    def get_all_tasks(self) -> List[TaskWrapper]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_running_tasks(self) -> List[TaskWrapper]:
        """Get all running tasks"""
        return [wrapper for wrapper in self.tasks.values() if not wrapper.is_done()]
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        total_tasks = len(self.tasks)
        running_tasks = len(self.get_running_tasks())
        
        # Group by kind
        tasks_by_kind = {}
        for wrapper in self.tasks.values():
            kind = wrapper.kind
            if kind not in tasks_by_kind:
                tasks_by_kind[kind] = 0
            tasks_by_kind[kind] += 1
        
        # Group by scope
        tasks_by_scope = {}
        for wrapper in self.tasks.values():
            for scope in wrapper.scopes:
                scope_name = scope.value
                if scope_name not in tasks_by_scope:
                    tasks_by_scope[scope_name] = 0
                tasks_by_scope[scope_name] += 1
        
        return {
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "tasks_by_kind": tasks_by_kind,
            "tasks_by_scope": tasks_by_scope
        }
    
    def _cleanup_task(self, task_id: str):
        """Clean up completed task"""
        if task_id in self.tasks:
            wrapper = self.tasks[task_id]
            logger.info(f"Task {task_id} completed: {wrapper.name}")
            del self.tasks[task_id]
    
    async def shutdown(self):
        """Shutdown all tasks"""
        logger.info("Shutting down task manager...")
        
        # Cancel all tasks
        for task_id, wrapper in self.tasks.items():
            wrapper.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*[wrapper.task for wrapper in self.tasks.values()], 
                               return_exceptions=True)
        
        logger.info("Task manager shutdown complete")
