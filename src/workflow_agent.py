#!/usr/bin/env python3
"""
MindBot Multi-Dify Workflow Agent
Handles multiple Dify workflows based on different task types
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from src.dify_client import DifyClient

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task types for workflow routing"""
    GENERAL_CHAT = "general_chat"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENT_PROCESSING = "document_processing"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE_WRITING = "creative_writing"
    RESEARCH = "research"
    CUSTOM = "custom"

@dataclass
class WorkflowConfig:
    """Configuration for a Dify workflow"""
    name: str
    dify_endpoint: str
    dify_api_key: str
    task_patterns: List[str]
    priority: int
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3

class WorkflowRouter:
    """
    Routes tasks to appropriate Dify workflows based on content analysis
    """
    
    def __init__(self):
        self.workflows: Dict[TaskType, WorkflowConfig] = {}
        self.pattern_cache: Dict[TaskType, List[re.Pattern]] = {}
        self._setup_default_workflows()
    
    def _setup_default_workflows(self):
        """Setup default workflow configurations"""
        # This would be loaded from config file in production
        default_workflows = {
            TaskType.GENERAL_CHAT: WorkflowConfig(
                name="general_chat",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",  # Will be set from environment
                task_patterns=[
                    r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b",
                    r"\b(how are you|what's up|how's it going)\b",
                    r"\b(thank you|thanks|appreciate)\b",
                    r"\b(help|assist|support)\b"
                ],
                priority=1
            ),
            TaskType.CODE_ANALYSIS: WorkflowConfig(
                name="code_analysis",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",
                task_patterns=[
                    r"\b(code|programming|function|class|variable)\b",
                    r"\b(debug|error|bug|fix|issue)\b",
                    r"\b(python|javascript|java|c\+\+|sql)\b",
                    r"\b(algorithm|data structure|optimization)\b"
                ],
                priority=2
            ),
            TaskType.DOCUMENT_PROCESSING: WorkflowConfig(
                name="document_processing",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",
                task_patterns=[
                    r"\b(document|file|pdf|text|content)\b",
                    r"\b(analyze|extract|parse|summarize)\b",
                    r"\b(read|process|review|examine)\b"
                ],
                priority=3
            ),
            TaskType.DATA_ANALYSIS: WorkflowConfig(
                name="data_analysis",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",
                task_patterns=[
                    r"\b(data|statistics|analysis|chart|graph)\b",
                    r"\b(calculate|compute|analyze|trend)\b",
                    r"\b(excel|csv|database|query)\b"
                ],
                priority=4
            ),
            TaskType.CREATIVE_WRITING: WorkflowConfig(
                name="creative_writing",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",
                task_patterns=[
                    r"\b(write|create|generate|compose)\b",
                    r"\b(story|article|blog|content|copy)\b",
                    r"\b(creative|imaginative|original)\b"
                ],
                priority=5
            ),
            TaskType.RESEARCH: WorkflowConfig(
                name="research",
                dify_endpoint="https://api.dify.ai/v1/chat-messages",
                dify_api_key="",
                task_patterns=[
                    r"\b(research|find|search|investigate)\b",
                    r"\b(information|facts|details|sources)\b",
                    r"\b(study|learn|understand|explain)\b"
                ],
                priority=6
            )
        }
        
        for task_type, config in default_workflows.items():
            self.register_workflow(task_type, config)
    
    def register_workflow(self, task_type: TaskType, config: WorkflowConfig):
        """Register a new workflow configuration"""
        self.workflows[task_type] = config
        self.pattern_cache[task_type] = [
            re.compile(pattern, re.IGNORECASE) for pattern in config.task_patterns
        ]
        logger.info(f"Registered workflow: {task_type.value}")
    
    def classify_task(self, message: str, context: Dict[str, Any] = None) -> Tuple[TaskType, float]:
        """
        Classify a task based on message content and context
        
        Args:
            message: The user message to classify
            context: Optional context information
            
        Returns:
            Tuple of (TaskType, confidence_score)
        """
        message_lower = message.lower()
        scores = {}
        
        # Calculate scores for each workflow
        for task_type, patterns in self.pattern_cache.items():
            if not self.workflows[task_type].enabled:
                continue
                
            score = 0
            for pattern in patterns:
                matches = pattern.findall(message_lower)
                score += len(matches) * 0.1  # Weight by number of matches
            
            # Boost score based on context
            if context:
                if task_type == TaskType.CODE_ANALYSIS and context.get('previous_task') == 'code':
                    score += 0.3
                elif task_type == TaskType.DOCUMENT_PROCESSING and context.get('has_attachment'):
                    score += 0.4
            
            scores[task_type] = score
        
        # Return the task type with highest score
        if not scores or max(scores.values()) == 0:
            return TaskType.GENERAL_CHAT, 0.1
        
        best_task = max(scores, key=scores.get)
        confidence = min(scores[best_task], 1.0)
        
        logger.debug(f"Task classified as {best_task.value} with confidence {confidence:.2f}")
        return best_task, confidence
    
    def get_workflow_config(self, task_type: TaskType) -> Optional[WorkflowConfig]:
        """Get workflow configuration for a task type"""
        return self.workflows.get(task_type)

class DifyWorkflowManager:
    """
    Manages multiple Dify workflow clients
    """
    
    def __init__(self):
        self.clients: Dict[TaskType, DifyClient] = {}
        self.workflow_configs: Dict[TaskType, WorkflowConfig] = {}
    
    def register_workflow(self, task_type: TaskType, config: WorkflowConfig):
        """Register a workflow with its Dify client"""
        try:
            # Create Dify client for this workflow
            client = DifyClient(
                api_key=config.dify_api_key,
                base_url=config.dify_endpoint
            )
            self.clients[task_type] = client
            self.workflow_configs[task_type] = config
            logger.info(f"Registered Dify client for workflow: {task_type.value}")
        except Exception as e:
            logger.error(f"Failed to register workflow {task_type.value}: {e}")
    
    async def process_message(self, task_type: TaskType, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process message through specific workflow
        
        Args:
            task_type: The workflow to use
            message: The message to process
            context: Optional context information
            
        Returns:
            Response from the workflow
        """
        if task_type not in self.clients:
            raise ValueError(f"No client registered for workflow: {task_type.value}")
        
        client = self.clients[task_type]
        config = self.workflow_configs[task_type]
        
        try:
            # Process with retries
            for attempt in range(config.max_retries):
                try:
                    response = await asyncio.wait_for(
                        client.chat_completion(message, context.get('user_id', 'unknown')),
                        timeout=config.timeout
                    )
                    return response
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout for workflow {task_type.value}, attempt {attempt + 1}")
                    if attempt == config.max_retries - 1:
                        raise
                except Exception as e:
                    logger.warning(f"Error in workflow {task_type.value}, attempt {attempt + 1}: {e}")
                    if attempt == config.max_retries - 1:
                        raise
                    await asyncio.sleep(1)  # Brief delay before retry
            
        except Exception as e:
            logger.error(f"Failed to process message through workflow {task_type.value}: {e}")
            return f"Sorry, I encountered an error processing your request through the {task_type.value} workflow."

class MultiDifyWorkflowAgent:
    """
    Main agent that handles multiple Dify workflows based on task classification
    """
    
    def __init__(self, workflow_configs: Dict[TaskType, WorkflowConfig] = None):
        self.router = WorkflowRouter()
        self.workflow_manager = DifyWorkflowManager()
        self.context_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Register workflows
        if workflow_configs:
            for task_type, config in workflow_configs.items():
                self.router.register_workflow(task_type, config)
                self.workflow_manager.register_workflow(task_type, config)
        else:
            # Use default workflows
            for task_type, config in self.router.workflows.items():
                self.workflow_manager.register_workflow(task_type, config)
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process message through appropriate workflow
        
        Args:
            message: The user message to process
            context: Optional context information
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Classify the task
            task_type, confidence = self.router.classify_task(message, context)
            
            # Get workflow configuration
            workflow_config = self.router.get_workflow_config(task_type)
            if not workflow_config:
                raise ValueError(f"No workflow configuration for task type: {task_type.value}")
            
            # Process through appropriate workflow
            response = await self.workflow_manager.process_message(
                task_type, message, context
            )
            
            # Update context history
            user_id = context.get('user_id', 'unknown') if context else 'unknown'
            if user_id not in self.context_history:
                self.context_history[user_id] = []
            
            self.context_history[user_id].append({
                'task_type': task_type.value,
                'confidence': confidence,
                'workflow': workflow_config.name,
                'message': message,
                'response': response
            })
            
            # Keep only last 10 interactions per user
            if len(self.context_history[user_id]) > 10:
                self.context_history[user_id] = self.context_history[user_id][-10:]
            
            return {
                'response': response,
                'task_type': task_type.value,
                'confidence': confidence,
                'workflow': workflow_config.name,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': f"Sorry, I encountered an error processing your request: {str(e)}",
                'task_type': 'error',
                'confidence': 0.0,
                'workflow': 'error',
                'success': False
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all workflows"""
        status = {}
        for task_type, config in self.workflow_manager.workflow_configs.items():
            status[task_type.value] = {
                'enabled': config.enabled,
                'priority': config.priority,
                'timeout': config.timeout,
                'max_retries': config.max_retries,
                'client_registered': task_type in self.workflow_manager.clients
            }
        return status
    
    def get_user_context(self, user_id: str) -> List[Dict[str, Any]]:
        """Get context history for a user"""
        return self.context_history.get(user_id, [])
    
    def add_custom_workflow(self, task_type: TaskType, config: WorkflowConfig):
        """Add a custom workflow"""
        self.router.register_workflow(task_type, config)
        self.workflow_manager.register_workflow(task_type, config)
        logger.info(f"Added custom workflow: {task_type.value}")
