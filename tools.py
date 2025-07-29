from langchain.tools import BaseTool
from typing import Optional
import datetime
import logging
import re
import ast

logger = logging.getLogger(__name__)

class DifyChatTool(BaseTool):
    name = "dify_chat"
    description = "Use this tool to chat with Dify API. Input should be a string containing the user's message."
    
    def __init__(self, dify_client):
        super().__init__()
        self.dify_client = dify_client
    
    def _run(self, query: str) -> str:
        """Run the tool synchronously"""
        import asyncio
        try:
            # Check if there's already a running event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, we can't use asyncio.run()
                # This is a fallback for sync contexts only
                return "Error: This tool should be used in async context"
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                return asyncio.run(self.dify_client.chat_completion(query))
        except Exception as e:
            return f"Error running Dify chat tool: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Run the tool asynchronously"""
        return await self.dify_client.chat_completion(query)

class GetTimeTool(BaseTool):
    name = "get_time"
    description = "Get the current date and time. No input required."
    
    def _run(self, query: str = "") -> str:
        """Get current time"""
        now = datetime.datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    async def _arun(self, query: str = "") -> str:
        """Get current time asynchronously"""
        return self._run(query)

class GetUserInfoTool(BaseTool):
    name = "get_user_info"
    description = "Get information about the current user. Input should be the user ID."
    
    def _run(self, user_id: str) -> str:
        """Get user information"""
        if not user_id or user_id.strip() == "":
            user_id = "unknown"
        return f"User ID: {user_id}\nPlatform: DingTalk\nStatus: Active"
    
    async def _arun(self, user_id: str) -> str:
        """Get user information asynchronously"""
        return self._run(user_id)

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform basic mathematical calculations. Input should be a mathematical expression like '2 + 2' or '10 * 5'."
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expressions"""
        # Remove all whitespace
        expression = expression.replace(' ', '')
        
        # Only allow digits, operators, and parentheses
        allowed_chars = set('0123456789+-*/.()')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Only basic mathematical operations are allowed")
        
        # Additional safety checks
        if len(expression) > 100:  # Prevent very long expressions
            raise ValueError("Expression too long")
        
        # Check for balanced parentheses
        if expression.count('(') != expression.count(')'):
            raise ValueError("Unbalanced parentheses")
        
        # Use ast.literal_eval for safer evaluation
        try:
            # Parse the expression
            tree = ast.parse(expression, mode='eval')
            
            # Check that it only contains allowed operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    raise ValueError("Function calls not allowed")
                elif isinstance(node, ast.Name):
                    raise ValueError("Variable names not allowed")
            
            # Evaluate using a restricted environment
            code = compile(tree, '<string>', 'eval')
            result = eval(code, {"__builtins__": {}}, {})
            
            if not isinstance(result, (int, float)):
                raise ValueError("Result must be a number")
                
            return float(result)
            
        except (ValueError, SyntaxError, ZeroDivisionError) as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def _run(self, expression: str) -> str:
        """Perform calculation"""
        try:
            if not expression or not expression.strip():
                return "Error: No expression provided"
            
            result = self._safe_eval(expression.strip())
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Perform calculation asynchronously"""
        return self._run(expression) 