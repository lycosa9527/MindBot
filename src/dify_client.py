#!/usr/bin/env python3
"""
Dify API Client - Knowledge Base Integration
Handles communication with Dify API for intelligent responses
"""

import aiohttp
import json
import logging
from typing import Optional
from config import DIFY_API_KEY, DIFY_BASE_URL
from debug import DebugLogger

logger = logging.getLogger(__name__)

class DifyClient:
    """
    Client for communicating with Dify API to access knowledge base and generate responses.
    This class handles all HTTP requests to Dify and manages API authentication.
    """
    
    def __init__(self):
        """Initialize the Dify client with API configuration"""
        self.api_key = DIFY_API_KEY
        self.base_url = DIFY_BASE_URL
        self.debug_logger = DebugLogger("DifyClient")
        
        # Validate API configuration on initialization
        if not self.api_key:
            raise ValueError("DIFY_API_KEY is not set")
        if not self.base_url:
            raise ValueError("DIFY_BASE_URL is not set")
        
        logger.info("DifyClient initialized successfully")
    
    async def chat_completion(self, message: str, user_id: str = "default") -> str:
        """
        Send a chat completion request to Dify API for intelligent response generation.
        
        Args:
            message: The user's message to process
            user_id: Unique identifier for the user (for conversation tracking)
            
        Returns:
            The AI-generated response from Dify
            
        Raises:
            Exception: If API call fails or returns invalid response
        """
        try:
            # Construct the API endpoint URL for chat completion
            url = f"{self.base_url}/chat-messages"
            
            # Prepare request headers with authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload with message and context
            payload = {
                "inputs": {},
                "query": message,
                "response_mode": "blocking",
                "conversation_id": "",  # Empty for new conversations
                "user": user_id,
                "files": []  # No file attachments for text-only chat
            }
            
            # Make HTTP POST request to Dify API with increased timeout
            timeout = aiohttp.ClientTimeout(total=120, connect=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    # Check if request was successful
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Dify API error {response.status}: {error_text}")
                        return f"Error: Dify API returned status {response.status}"
                    
                    # Parse JSON response from Dify
                    try:
                        response_data = await response.json()
                    except ValueError as json_error:
                        logger.error(f"Failed to parse Dify JSON response: {json_error}")
                        return "Error: Invalid response format from Dify API"
                    
                    # Extract answer from response data
                    answer = response_data.get("answer", "")
                    if not answer:
                        # Try alternative response fields
                        answer = response_data.get("message", "")
                        if not answer:
                            logger.warning("Dify returned empty answer")
                            return "I'm sorry, I couldn't generate a response. Please try again."
                    
                    # Validate answer content
                    if not answer.strip():
                        logger.warning("Dify returned empty or whitespace-only answer")
                        return "I'm sorry, I couldn't generate a response. Please try again."
                    
                    logger.info(f"Dify response: {answer[:50]}...")
                    return answer.strip()
                    
        except aiohttp.ClientError as e:
            # Handle network and HTTP client errors
            logger.error(f"Network error calling Dify API: {str(e)}")
            return "Error: Network error connecting to Dify API"
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"Unexpected error calling Dify API: {str(e)}")
            return "Error: Unexpected error calling Dify API"
    
    async def test_connection(self) -> bool:
        """
        Test the connection to Dify API to verify configuration and network connectivity.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing Dify API connection...")
            
            # Send a simple test message to verify API functionality
            test_response = await self.chat_completion("Hello", "test_user")
            
            # Check if response indicates success
            if test_response and not test_response.startswith("Error:"):
                logger.info("Dify API connection test successful")
                return True
            else:
                logger.error(f"Dify API connection test failed: {test_response}")
                return False
                
        except Exception as e:
            logger.error(f"Dify API connection test failed: {str(e)}")
            return False 