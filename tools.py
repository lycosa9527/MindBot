from langchain.tools import BaseTool
from typing import Optional
import datetime
import logging

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
        return asyncio.run(self.dify_client.chat_completion(query))
    
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
        return f"User ID: {user_id}\nPlatform: DingTalk\nStatus: Active"
    
    async def _arun(self, user_id: str) -> str:
        """Get user information asynchronously"""
        return self._run(user_id)

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform basic mathematical calculations. Input should be a mathematical expression like '2 + 2' or '10 * 5'."
    
    def _run(self, expression: str) -> str:
        """Perform calculation"""
        try:
            # Simple evaluation for basic math operations
            # Note: In production, use a safer evaluation method
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic mathematical operations are allowed"
            
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Perform calculation asynchronously"""
        return self._run(expression) 