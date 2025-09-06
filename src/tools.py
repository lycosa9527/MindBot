#!/usr/bin/env python3
"""
MindBot Tools - AI Agent Capabilities
Provides various tools for the AI agent including Dify chat, time, user info, and calculator
"""

import asyncio
import logging
import re
import json
import ast
from datetime import datetime
from typing import Dict, Any, List
from langchain.tools import BaseTool
from src.config import CALCULATOR_EXPRESSION_LIMIT

logger = logging.getLogger(__name__)

class DifyChatTool(BaseTool):
    """
    Tool for communicating with Dify API for knowledge-based responses.
    This tool enables the AI agent to access external knowledge bases.
    """
    
    name: str = "dify_chat"
    description: str = "Send a message to Dify API for intelligent responses"
    
    def __init__(self, dify_client):
        """
        Initialize the Dify chat tool with client.
        
        Args:
            dify_client: DifyClient instance for API communication
        """
        super().__init__()
        self.dify_client = dify_client
    
    def _run(self, message: str) -> str:
        """
        Synchronously send a message to Dify API.
        
        Args:
            message: The message to send to Dify
            
        Returns:
            The response from Dify API
        """
        import asyncio
        return asyncio.run(self._arun(message))
    
    async def _arun(self, message: str) -> str:
        """
        Asynchronously send a message to Dify API.
        
        Args:
            message: The message to send to Dify
            
        Returns:
            The response from Dify API
        """
        try:
            # Validate input message
            if not message or not message.strip():
                return "Error: Empty message provided"
            
            # Send message to Dify API
            response = await self.dify_client.chat_completion(message.strip(), "tool_user")
            
            # Validate response
            if not response or response.startswith("Error:"):
                return f"Error: Failed to get response from Dify API - {response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Dify chat tool: {str(e)}")
            return f"Error: {str(e)}"

class GetTimeTool(BaseTool):
    """
    Tool for getting current time and date information.
    Provides time-related information to users.
    """
    
    name: str = "get_time"
    description: str = "Get the current time and date"
    
    def _run(self, query: str = "") -> str:
        """
        Get current time and date information synchronously.
        
        Args:
            query: Optional query string (not used for time tool)
            
        Returns:
            Formatted time and date information
        """
        import asyncio
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str = "") -> str:
        """
        Get current time and date information.
        
        Args:
            query: Optional query string (not used for time tool)
            
        Returns:
            Formatted time and date information
        """
        try:
            # Get current datetime
            now = datetime.now()
            
            # Format time and date information
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%Y-%m-%d")
            day_str = now.strftime("%A")
            
            # Create comprehensive time response
            response = f"Current time: {time_str}\n"
            response += f"Current date: {date_str}\n"
            response += f"Day of week: {day_str}\n"
            response += f"Timezone: {now.astimezone().tzinfo}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in get time tool: {str(e)}")
            return f"Error: {str(e)}"

class GetUserInfoTool(BaseTool):
    """
    Tool for retrieving user information from context.
    Provides user-specific information when available.
    """
    
    name: str = "get_user_info"
    description: str = "Get information about the current user"
    
    def __init__(self):
        """Initialize the user info tool"""
        super().__init__()
        # Note: user_context will be set via set_user_context method
    
    def set_user_context(self, context: Dict[str, Any]) -> None:
        """
        Set user context information for the tool.
        
        Args:
            context: Dictionary containing user information
        """
        # Store context in a way that doesn't conflict with Pydantic
        object.__setattr__(self, 'user_context', context or {})
    
    def _run(self, query: str = "") -> str:
        """
        Get user information from context synchronously.
        
        Args:
            query: Optional query string (not used for user info tool)
            
        Returns:
            User information or error message
        """
        import asyncio
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str = "") -> str:
        """
        Get user information from context.
        
        Args:
            query: Optional query string (not used for user info tool)
            
        Returns:
            User information or error message
        """
        try:
            user_context = getattr(self, 'user_context', {})
            if not user_context:
                return "No user information available"
            
            # Extract user information
            user_id = user_context.get("user_id", "Unknown")
            conversation_id = user_context.get("conversation_id", "Unknown")
            
            # Build response
            response = f"User ID: {user_id}\n"
            response += f"Conversation ID: {conversation_id}\n"
            
            # Add any additional context information
            for key, value in user_context.items():
                if key not in ["user_id", "conversation_id"]:
                    response += f"{key}: {value}\n"
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error in get user info tool: {str(e)}")
            return f"Error: {str(e)}"

class CalculatorTool(BaseTool):
    """
    Tool for performing mathematical calculations.
    Safely evaluates mathematical expressions with security limits.
    """
    
    name: str = "calculator"
    description: str = "Perform mathematical calculations"
    
    def __init__(self):
        """Initialize the calculator tool with security limits"""
        super().__init__()
        self.max_expression_length = CALCULATOR_EXPRESSION_LIMIT  # Security limit
    
    def _is_safe_expression(self, expression: str) -> bool:
        """
        Check if a mathematical expression is safe to evaluate.
        
        Args:
            expression: The mathematical expression to check
            
        Returns:
            True if expression is safe, False otherwise
        """
        # Check expression length
        if len(expression) > self.max_expression_length:
            return False
        
        # Remove whitespace for validation
        clean_expr = expression.replace(" ", "")
        
        # Only allow safe mathematical characters
        safe_chars = set("0123456789+-*/.()")
        if not all(c in safe_chars for c in clean_expr):
            return False
        
        # Check for balanced parentheses
        if clean_expr.count("(") != clean_expr.count(")"):
            return False
        
        # Prevent division by zero patterns
        if "/0" in clean_expr or "/0.0" in clean_expr:
            return False
        
        return True
    
    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression using ast.literal_eval.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The numerical result
            
        Raises:
            ValueError: If expression is invalid or unsafe
        """
        try:
            # Parse the expression using ast
            tree = ast.parse(expression, mode='eval')
            
            # Check that it only contains allowed operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    raise ValueError("Function calls not allowed")
                elif isinstance(node, ast.Name):
                    raise ValueError("Variable names not allowed")
                elif isinstance(node, ast.Attribute):
                    raise ValueError("Attribute access not allowed")
            
            # Evaluate using a restricted environment
            code = compile(tree, '<string>', 'eval')
            result = eval(code, {"__builtins__": {}}, {})
            
            if not isinstance(result, (int, float)):
                raise ValueError("Result must be a number")
                
            return float(result)
            
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _run(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression synchronously.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The calculation result or error message
        """
        import asyncio
        return asyncio.run(self._arun(expression))
    
    async def _arun(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The calculation result or error message
        """
        try:
            # Validate input
            if not expression or not expression.strip():
                return "Error: No expression provided"
            
            # Clean the expression
            clean_expr = expression.strip()
            
            # Check if expression is safe
            if not self._is_safe_expression(clean_expr):
                return f"Error: Expression is not safe or too long (max {self.max_expression_length} characters)"
            
            # Evaluate the expression using safe method
            result = self._safe_eval(clean_expr)
            
            # Format the result
            return f"Result: {result}"
                
        except ZeroDivisionError:
            return "Error: Division by zero"
        except SyntaxError:
            return "Error: Invalid mathematical expression"
        except Exception as e:
            logger.error(f"Error in calculator tool: {str(e)}")
            return f"Error: {str(e)}"

def create_tools(dify_client=None) -> List[BaseTool]:
    """
    Create a list of available tools for the AI agent.
    
    Args:
        dify_client: Optional DifyClient instance for Dify chat tool
        
    Returns:
        List of tool instances
    """
    tools = []
    
    # Add Dify chat tool if client is provided
    if dify_client:
        tools.append(DifyChatTool(dify_client))
    
    # Add utility tools
    tools.append(GetTimeTool())
    tools.append(GetUserInfoTool())
    tools.append(CalculatorTool())
    
    logger.info(f"Created {len(tools)} tools for AI agent")
    return tools 