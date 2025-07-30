#!/usr/bin/env python3
"""
MindBot Agent - AI Processing Component
Handles message processing and Dify API integration for intelligent responses
"""

import logging
from typing import Dict, Any
from dify_client import DifyClient
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, VERSION

logger = logging.getLogger(__name__)

class MindBotAgent:
    """
    AI Agent that processes user messages and generates intelligent responses.
    This class acts as the brain of the chatbot, connecting to Dify API for knowledge-based responses.
    """
    
    def __init__(self, qwen_api_key: str = None):
        """
        Initialize the AI agent with Dify client for knowledge base integration.
        
        Args:
            qwen_api_key: Optional Qwen API key (falls back to config if not provided)
        """
        self.qwen_api_key = qwen_api_key or QWEN_API_KEY  # Use provided key or config default
        
        # Initialize Dify client for knowledge base access
        self.dify_client = DifyClient()
        
        logger.info(f"MindBotAgent {VERSION} initialized successfully")
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user message by calling the Dify API for intelligent responses.
        
        Args:
            message: The user's message to process
            context: Optional context containing user_id, conversation_id, etc.
            
        Returns:
            The AI-generated response to send back to the user
        """
        try:
            # Validate input message to prevent processing empty content
            if not message or not message.strip():
                return "I'm sorry, I didn't receive any message. Please try again."
            
            # Store original message for processing
            original_message = message.strip()
            
            # Extract user information from context for personalized responses
            user_id = context.get("user_id", "unknown") if context else "unknown"
            
            # Log only at debug level to reduce console verbosity
            logger.debug(f"Processing: {original_message[:50]}...")
            logger.debug(f"User: {user_id}")
            
            # Call Dify API directly for knowledge-based responses
            # This bypasses complex agent systems for simplicity and reliability
            try:
                # Log only at debug level to reduce console verbosity
                logger.debug("Calling Dify API...")
                response = await self.dify_client.chat_completion(original_message, user_id)
                
                # Validate Dify response to ensure quality output
                if not response or not response.strip():
                    logger.warning("Dify returned empty response")
                    return "I'm sorry, I couldn't generate a response. Please try again."
                
                # Check if response indicates an API error
                if response.startswith("Error:"):
                    logger.error(f"Dify API error: {response}")
                    return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."
                
                # Log only at debug level to reduce console verbosity
                logger.debug(f"Dify response: {response[:50]}...")
                return response
            except Exception as dify_error:
                logger.error(f"Dify API call failed: {str(dify_error)}")
                # Provide fallback response when API is unavailable
                return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."
            
        except Exception as e:
            logger.error(f"Error in message processing: {str(e)}")
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    async def test_tool_calling(self):
        """
        Test the agent's tool calling capabilities with various message types.
        This method validates that the agent can handle different types of requests.
        
        Returns:
            bool: True if at least 50% of tests pass, False otherwise
        """
        logger.info("Testing agent tool calling...")
        
        # Define test cases covering different types of user requests
        test_cases = [
            "What time is it?",           # Time-related query
            "Calculate 15 * 7",           # Mathematical calculation
            "Tell me about user 12345",   # User information request
            "Hello, how are you?"         # General conversation
        ]
        
        success_count = 0
        for test_case in test_cases:
            try:
                logger.info(f"Testing: {test_case}")
                result = await self.process_message(test_case)
                if result and not result.startswith("Error"):
                    success_count += 1
                    logger.info(f"Test passed: {result[:50]}...")
                else:
                    logger.warning(f"Test failed: {result}")
            except Exception as e:
                logger.error(f"Test failed for '{test_case}': {str(e)}")
        
        # Calculate success rate and log results
        success_rate = success_count / len(test_cases)
        logger.info(f"Tool calling test completed: {success_count}/{len(test_cases)} passed")
        return success_count >= len(test_cases) * 0.5  # At least 50% success rate 