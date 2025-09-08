#!/usr/bin/env python3
"""
WeCom Direct Client
Direct API integration for WeCom (WeChat Work)
"""

import asyncio
from typing import Callable, Optional, Dict, Any
from .logging_config import get_logger

logger = get_logger("WeCom")

class WeComDirectClient:
    """WeCom direct client for API integration"""
    
    def __init__(self, agent_handler: Callable, agent_instance=None,
                 corp_id: str = None, corp_secret: str = None, 
                 agent_id: str = None, agent_name: str = None):
        """
        Initialize WeCom client with agent handler and credentials.
        
        Args:
            agent_handler: Function to call with processed messages
            agent_instance: Optional agent instance for direct streaming access
            corp_id: WeCom Corp ID
            corp_secret: WeCom Corp Secret
            agent_id: WeCom Agent ID
            agent_name: WeCom Agent Name
        """
        self.agent_handler = agent_handler
        self.agent_instance = agent_instance
        self.logger = get_logger("WeCom")
        self.is_running = False
        
        # Store WeCom credentials
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.agent_name = agent_name
        
        # Validate required configuration
        if not self.corp_id:
            raise ValueError("corp_id is not set")
        if not self.corp_secret:
            raise ValueError("corp_secret is not set")
        if not self.agent_id:
            raise ValueError("agent_id is not set")
        
    async def start(self):
        """Start the WeCom client"""
        try:
            self.logger.info("Starting WeCom Direct Client...")
            self.is_running = True
            self.logger.info("WeCom Direct Client started (POC mode)")
        except Exception as e:
            self.logger.error(f"Error starting WeCom client: {e}")
            raise
    
    async def stop(self):
        """Stop the WeCom client"""
        try:
            self.logger.info("Stopping WeCom Direct Client...")
            self.is_running = False
            self.logger.info("WeCom Direct Client stopped")
        except Exception as e:
            self.logger.error(f"Error stopping WeCom client: {e}")
    
    async def run(self):
        """Run the WeCom client (placeholder for POC)"""
        while self.is_running:
            await asyncio.sleep(1)
    
    def set_agent_handler(self, handler: Callable):
        """Set the agent handler"""
        self.agent_handler = handler