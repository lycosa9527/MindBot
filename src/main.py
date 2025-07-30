#!/usr/bin/env python3
"""
MindBot - DingTalk Stream Mode Chatbot
Main application entry point for the MindBot chatbot system
"""

import asyncio
import signal
import sys
import traceback
import logging
from datetime import datetime
import uuid

# Import local modules
from config import VERSION, BUILD_DATE
from debug import setup_colored_logging, run_diagnostics
from dingtalk_client import MindBotDingTalkClient
from agent import MindBotAgent
from banner import display_banner

# Version information imported from config

# Setup professional colored logging for the entire application
setup_colored_logging()

# Get logger for this module
logger = logging.getLogger(__name__)

class MindBotStreamApp:
    """
    Main application class that orchestrates the MindBot chatbot system.
    Handles initialization, message processing, and graceful shutdown.
    """
    
    def __init__(self):
        """Initialize the application with default state"""
        self.agent = None  # AI agent for processing messages
        self.dingtalk_client = None  # DingTalk WebSocket client
        self.running = False  # Application running state flag
        self.instance_id = str(uuid.uuid4())[:8]  # Unique instance ID for logging
        
    async def initialize(self):
        """
        Initialize all application components including agent, client, and diagnostics.
        This method sets up the core functionality before starting the application.
        """
        try:
            # Display application banner first for user identification
            display_banner()
            
            logger.info("Initializing MindBot Stream Application")
            logger.info(f"Version: {VERSION} ({BUILD_DATE})")
            logger.info(f"Instance: {self.instance_id}")
            
            # Initialize AI agent for message processing
            logger.info("Initializing AI Agent...")
            self.agent = MindBotAgent()
            logger.info("Agent initialized successfully")
            
            # Initialize DingTalk stream client for WebSocket communication
            logger.info("Initializing DingTalk Stream Client...")
            self.dingtalk_client = MindBotDingTalkClient(
                agent_handler=self.handle_message  # Pass message handler to client
            )
            logger.info("DingTalk client initialized successfully")
            
            # Run comprehensive system diagnostics to verify all components
            logger.info("Running system diagnostics...")
            await run_diagnostics()
            logger.info("Diagnostics completed")
            
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise  # Re-raise to prevent application startup with errors
    
    async def handle_message(self, message_text: str, context: dict) -> str:
        """
        Handle incoming messages from DingTalk and process them through the AI agent.
        
        Args:
            message_text: The user's message content
            context: Additional context information (user_id, conversation_id, etc.)
            
        Returns:
            The AI-generated response to send back to the user
        """
        try:
            # Validate message content to prevent processing empty messages
            if not message_text or not message_text.strip():
                logger.warning("Received empty message")
                return "I'm sorry, I didn't receive any message. Please try again."
            
            # Validate context parameter to prevent crashes from invalid types
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                logger.warning(f"Invalid context type: {type(context)}")
                context = {}
            
            # Process message through AI agent for intelligent response generation
            response = await self.agent.process_message(message_text, context)
            
            # Validate agent response to ensure quality output
            if not response or not response.strip():
                logger.warning("Agent returned empty response")
                return "I'm sorry, I couldn't generate a response. Please try again."
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    async def start(self):
        """
        Start the application and begin listening for messages.
        This is the main application loop that keeps the system running.
        """
        try:
            logger.info("Starting MindBot Stream Application...")
            
            # Initialize all components before starting
            await self.initialize()
            
            # Start DingTalk client to begin listening for messages
            logger.info("Starting DingTalk Stream Client...")
            await self.dingtalk_client.start()
            
            logger.info("Application started successfully")
            logger.info("Waiting for messages...")
            self.running = True
            
            # Main application loop - keep running until stopped
            while self.running:
                await asyncio.sleep(1)  # Prevent CPU spinning
                
        except Exception as e:
            logger.error(f"Error in application: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Ensure we stop gracefully even if an error occurs during runtime
            try:
                await self.stop()
            except Exception as stop_error:
                logger.error(f"Error during emergency stop: {stop_error}")
            raise  # Re-raise to indicate application failure
    
    async def stop(self):
        """
        Stop the application gracefully, closing all connections and resources.
        This ensures clean shutdown without resource leaks.
        """
        try:
            logger.info("Stopping MindBot Stream Application...")
            self.running = False  # Signal main loop to stop
            
            # Stop DingTalk client and close WebSocket connection
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
            
            logger.info("Application stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping application: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

def signal_handler(signum, frame):
    """
    Handle system shutdown signals (SIGINT, SIGTERM) for graceful termination.
    
    Args:
        signum: The signal number received
        frame: The current stack frame
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)  # Clean exit

async def main():
    """
    Main application entry point that sets up signal handlers and starts the application.
    This function orchestrates the entire application lifecycle.
    """
    # Register signal handlers for graceful shutdown on Ctrl+C or system signals
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # System termination
    
    # Create and start the main application instance
    app = MindBotStreamApp()
    
    try:
        await app.start()  # Start the application and begin message processing
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        # Ensure application is always stopped properly, even on errors
        await app.stop()

if __name__ == "__main__":
    # Run the main application using asyncio event loop
    asyncio.run(main()) 