#!/usr/bin/env python3
"""
MindBot Agent Module
AI agent wrapper for Dify integration
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .logging_config import get_logger

logger = get_logger("AI-Agent")

class MindBotAgent:
    """AI agent wrapper for Dify integration"""
    
    def __init__(self, dify_api_key: str = None, dify_base_url: str = None):
        self.dify_api_key = dify_api_key
        self.dify_base_url = dify_base_url or "https://api.dify.ai/v1"
        self.logger = get_logger("AI-Agent")
        
        # Initialize Dify client if credentials are provided
        self.dify_client = None
        if self.dify_api_key and self.dify_base_url:
            try:
                self.dify_client = self._create_dify_client()
                self.logger.info("Dify client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Dify client: {e}")
                self.dify_client = None
    
    def _create_dify_client(self):
        """Create Dify client instance"""
        # For Phase 1 POC, return a mock client
        # In production, this would be the actual Dify client
        return MockDifyClient(self.dify_api_key, self.dify_base_url)
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process message through AI agent
        
        Args:
            message: User message
            context: Message context
            
        Returns:
            AI response
        """
        try:
            self.logger.info(f"Processing message: {message[:100]}...")
            
            if self.dify_client:
                # Use Dify client for AI processing
                response = await self.dify_client.chat_completion(message, context.get("user_id", "unknown"))
                self.logger.info(f"AI response generated: {len(response)} characters")
                return response
            else:
                # Fallback to simple response
                return self._generate_fallback_response(message, context)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error processing your message."
    
    async def process_message_streaming(self, message: str, context: Dict[str, Any], callback: Callable[[str], None]) -> str:
        """
        Process message with streaming response
        
        Args:
            message: User message
            context: Message context
            callback: Callback function for streaming chunks
            
        Returns:
            Complete AI response
        """
        try:
            self.logger.info(f"Processing message with streaming: {message[:100]}...")
            
            if self.dify_client:
                # Use Dify client for streaming AI processing
                response = await self.dify_client.chat_completion_streaming_with_callback(
                    message, 
                    context.get("user_id", "unknown"), 
                    callback
                )
                self.logger.info(f"Streaming AI response completed: {len(response)} characters")
                return response
            else:
                # Fallback to simple response
                response = self._generate_fallback_response(message, context)
                # Simulate streaming by calling callback with chunks
                await self._simulate_streaming(response, callback)
                return response
                
        except Exception as e:
            self.logger.error(f"Error processing streaming message: {e}")
            return "I'm sorry, I encountered an error processing your message."
    
    def _generate_fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate fallback response when Dify is not available"""
        user_id = context.get("user_id", "unknown")
        platform = context.get("platform", "unknown")
        
        # Simple response logic for POC
        if "hello" in message.lower() or "hi" in message.lower():
            return f"Hello! I'm MindBot running on {platform}. How can I help you today?"
        elif "status" in message.lower():
            return f"MindBot is running on {platform} for user {user_id}. All systems operational!"
        elif "help" in message.lower():
            return f"""
**MindBot Help - {platform}**

Available commands:
- `hello` - Greeting
- `status` - Check bot status  
- `help` - Show this help
- Send any message for AI response

*Note: This is a Phase 1 proof of concept. Full AI integration coming soon!*
            """
        else:
            return f"Echo from {platform}: {message}\n\n*This is a Phase 1 POC response. Full AI integration will be available soon!*"
    
    async def _simulate_streaming(self, response: str, callback: Callable[[str], None]):
        """Simulate streaming response by calling callback with chunks"""
        try:
            # Split response into chunks
            chunk_size = 20
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                await callback(chunk)
                await asyncio.sleep(0.1)  # Small delay to simulate streaming
        except Exception as e:
            self.logger.error(f"Error in simulated streaming: {e}")

class MockDifyClient:
    """Mock Dify client for Phase 1 POC"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = get_logger("AI-Agent.MockDifyClient")
    
    async def chat_completion(self, message: str, user_id: str) -> str:
        """Mock chat completion"""
        self.logger.info(f"Mock Dify chat completion for user {user_id}")
        
        # Generate a more sophisticated mock response
        responses = [
            f"Thank you for your message: '{message}'. I'm processing this through our AI system.",
            f"I understand you're asking about: '{message}'. Let me provide you with a comprehensive response.",
            f"Great question! Regarding '{message}', here's what I can tell you: This is a Phase 1 proof of concept, so I'm providing a mock response. In the full implementation, this would be processed by Dify AI.",
            f"Your message '{message}' has been received. I'm currently running in POC mode, so this is a simulated AI response.",
        ]
        
        import random
        return random.choice(responses)
    
    async def chat_completion_streaming_with_callback(self, message: str, user_id: str, callback: Callable[[str], None]) -> str:
        """Mock streaming chat completion"""
        self.logger.info(f"Mock Dify streaming chat completion for user {user_id}")
        
        # Generate streaming response
        base_response = f"Thank you for your message: '{message}'. I'm processing this through our AI system and will provide a detailed response."
        
        # Stream the response
        words = base_response.split()
        accumulated = ""
        
        for word in words:
            accumulated += word + " "
            await callback(word + " ")
            await asyncio.sleep(0.1)  # Simulate streaming delay
        
        return accumulated.strip()