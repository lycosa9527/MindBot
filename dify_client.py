import aiohttp
import logging
from typing import Dict, Any, Optional
from config import DIFY_API_KEY, DIFY_BASE_URL, VERSION

logger = logging.getLogger(__name__)

class DifyClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or DIFY_API_KEY
        self.base_url = base_url or DIFY_BASE_URL
        self.debug_logger = DebugLogger("DifyClient")
        
    async def chat_completion(self, query: str, user_id: str = None) -> str:
        """
        Send a chat completion request to Dify API
        Returns the response text directly
        """
        if not query or not query.strip():
            return "Error: Empty query provided"
            
        try:
            self.debug_logger.log_info(f"Sending request to Dify API: {query[:50]}...")
            
            # Ensure proper URL construction
            url = f"{self.base_url.rstrip('/')}/chat-messages"
            
            payload = {
                "inputs": {},
                "query": query.strip(),
                "response_mode": "blocking",
                "user": user_id or "default_user"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"MindBot/{VERSION}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data.get("answer", "")
                        if not answer:
                            answer = data.get("message", "No response from Dify API")
                        self.debug_logger.log_info(f"Dify API response: {answer[:100]}...")
                        return answer
                    else:
                        error_text = await response.text()
                        self.debug_logger.log_error(f"Dify API error: {response.status} - {error_text}")
                        return f"Error: Unable to get response from Dify API (Status: {response.status})"
                        
        except aiohttp.ClientTimeout:
            self.debug_logger.log_error("Dify API request timed out")
            return "Error: Request to Dify API timed out"
        except aiohttp.ClientError as e:
            self.debug_logger.log_error(f"Dify API connection error: {str(e)}")
            return f"Error: Connection to Dify API failed - {str(e)}"
        except Exception as e:
            self.debug_logger.log_error(f"Exception in chat_completion: {str(e)}")
            return f"Error: {str(e)}"

class DebugLogger:
    def __init__(self, context: str):
        self.context = context
        self.logger = logging.getLogger(f"{context}")
    
    def log_info(self, message: str):
        self.logger.info(f"[{self.context}] {message}")
    
    def log_error(self, message: str):
        self.logger.error(f"[{self.context}] {message}")
    
    def log_debug(self, message: str):
        self.logger.debug(f"[{self.context}] {message}") 