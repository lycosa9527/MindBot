#!/usr/bin/env python3
"""
MindBot Agent - AI Processing Component
Handles message processing and Dify API integration for intelligent responses
"""

import logging
from typing import Dict, Any, Optional, List
from src.dify_client import DifyClient
from src.config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, VERSION
from src.langchain_agent import MindBotLangChainAgent

logger = logging.getLogger(__name__)

class MindBotAgent:
    """
    AI Agent that processes user messages and generates intelligent responses.
    This class acts as the brain of the chatbot, connecting to Dify API for knowledge-based responses.
    """
    
    def __init__(self, qwen_api_key: str = None, use_langchain: bool = True, langchain_config: Dict[str, Any] = None):
        """
        Initialize the AI agent with Dify client and optional LangChain integration.
        
        Args:
            qwen_api_key: Optional Qwen API key (falls back to config if not provided)
            use_langchain: Whether to enable LangChain agent integration
            langchain_config: Optional LangChain configuration
        """
        self.qwen_api_key = qwen_api_key or QWEN_API_KEY  # Use provided key or config default
        self.use_langchain = use_langchain
        
        # Initialize Dify client for knowledge base access
        self.dify_client = DifyClient()
        
        # Initialize LangChain agent if enabled
        self.langchain_agent = None
        if use_langchain:
            try:
                config = langchain_config or self._get_default_langchain_config()
                self.langchain_agent = MindBotLangChainAgent(config)
                logger.info("LangChain agent initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LangChain agent: {e}")
                logger.info("Falling back to Dify-only mode")
                self.use_langchain = False
        
        logger.info(f"MindBotAgent {VERSION} initialized successfully")
    
    def _get_default_langchain_config(self) -> Dict[str, Any]:
        """Get default LangChain configuration"""
        return {
            'provider': 'openai',
            'model': 'gpt-4',
            'api_key': self.qwen_api_key,
            'temperature': 0.7,
            'max_iterations': 10,
            'verbose': False,
            'load_custom_tools': True,
            'system_prompt': 'You are MindBot, an intelligent assistant with access to various tools.'
        }
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user message with optional LangChain agent integration.
        
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
            
            # Use LangChain agent if available and enabled
            if self.use_langchain and self.langchain_agent:
                try:
                    logger.debug("Processing message with LangChain agent")
                    response = await self.langchain_agent.process_message(original_message, context)
                    if response and not response.startswith("Error"):
                        return response
                    else:
                        logger.warning("LangChain agent returned error, falling back to Dify")
                except Exception as langchain_error:
                    logger.warning(f"LangChain agent failed: {langchain_error}, falling back to Dify")
            
            # Fallback to Dify-only processing
            return await self._dify_only_processing(original_message, context)
            
        except Exception as e:
            logger.error(f"Error in message processing: {str(e)}")
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    async def _dify_only_processing(self, message: str, context: Dict[str, Any]) -> str:
        """
        Process message using only Dify API (fallback method).
        
        Args:
            message: The user's message to process
            context: Optional context containing user_id, conversation_id, etc.
            
        Returns:
            The AI-generated response from Dify API
        """
        try:
            # Extract user information from context for personalized responses
            user_id = context.get("user_id", "unknown") if context else "unknown"
            
            # Call Dify API directly for knowledge-based responses
            response = await self.dify_client.chat_completion(message, user_id)
            
            # Validate Dify response to ensure quality output
            if not response or not response.strip():
                logger.warning("Dify returned empty response")
                return "I'm sorry, I couldn't generate a response. Please try again."
            
            # Check if response indicates an API error
            if response.startswith("Error:"):
                logger.error(f"Dify API error: {response}")
                return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."
            
            return response
            
        except Exception as dify_error:
            logger.error(f"Dify API call failed: {str(dify_error)}")
            # Provide fallback response when API is unavailable
            return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."
    
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
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent including LangChain integration status.
        
        Returns:
            Dictionary containing agent status information
        """
        status = {
            'version': VERSION,
            'langchain_enabled': self.use_langchain,
            'langchain_agent_initialized': self.langchain_agent is not None,
            'dify_client_initialized': self.dify_client is not None
        }
        
        if self.langchain_agent:
            status['langchain_status'] = self.langchain_agent.get_agent_status()
        
        return status
    
    def add_langchain_tool(self, tool):
        """
        Add a new tool to the LangChain agent.
        
        Args:
            tool: LangChain BaseTool instance to add
        """
        if self.langchain_agent:
            self.langchain_agent.add_tool(tool)
            logger.info(f"Added tool to LangChain agent: {tool.name}")
        else:
            logger.warning("LangChain agent not initialized, cannot add tool")
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools.
        
        Returns:
            List of tool names
        """
        if self.langchain_agent:
            return self.langchain_agent.list_tools()
        return []
    
    def validate_tools(self) -> Dict[str, Any]:
        """
        Validate all tools for compatibility.
        
        Returns:
            Dictionary containing validation results
        """
        if self.langchain_agent:
            return self.langchain_agent.validate_tools()
        return {'error': 'LangChain agent not initialized'} 