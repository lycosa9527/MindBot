#!/usr/bin/env python3
"""
MindBot Framework Usage Example
Demonstrates how to use the new MindBot framework
"""

import asyncio
import logging
from mindbot_framework.core.application import MindBotApplication
from mindbot_framework.platforms.base import PlatformAdapter, Message, MessageType, Response
from mindbot_framework.core.event_bus import EventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExamplePlatformAdapter(PlatformAdapter):
    """
    Example platform adapter implementation
    """
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.message_count = 0
    
    def get_required_config_fields(self):
        return ["api_key", "webhook_url"]
    
    async def initialize(self) -> bool:
        """Initialize the platform adapter"""
        logger.info(f"Initializing {self.name} adapter...")
        
        # Validate configuration
        if not await self.validate_config():
            return False
        
        # Simulate initialization
        await asyncio.sleep(0.1)
        
        logger.info(f"{self.name} adapter initialized successfully")
        return True
    
    async def start(self) -> None:
        """Start the platform adapter"""
        logger.info(f"Starting {self.name} adapter...")
        self.is_running = True
        
        # Start message processing
        asyncio.create_task(self.start_message_processing())
        
        logger.info(f"{self.name} adapter started")
    
    async def stop(self) -> None:
        """Stop the platform adapter"""
        logger.info(f"Stopping {self.name} adapter...")
        self.is_running = False
        logger.info(f"{self.name} adapter stopped")
    
    async def send_message(self, response: Response) -> bool:
        """Send a message to the platform"""
        logger.info(f"Sending message to {self.name}: {response.content}")
        
        # Simulate sending message
        await asyncio.sleep(0.1)
        
        logger.info(f"Message sent successfully to {self.name}")
        return True
    
    async def process_incoming_message(self, raw_message: dict) -> Message:
        """Process an incoming message from the platform"""
        self.message_count += 1
        
        # Create a standard message from raw data
        message = Message(
            id=f"msg_{self.message_count}",
            platform=self.name,
            user_id=raw_message.get("user_id", "unknown"),
            user_name=raw_message.get("user_name", "Unknown User"),
            content=raw_message.get("content", ""),
            message_type=MessageType.TEXT,
            timestamp=raw_message.get("timestamp", 0),
            metadata=raw_message.get("metadata", {}),
            raw_data=raw_message
        )
        
        logger.info(f"Processed incoming message from {self.name}: {message.content}")
        return message
    
    async def health_check(self) -> bool:
        """Check if the platform adapter is healthy"""
        return self.is_running

async def main():
    """Main function demonstrating MindBot framework usage"""
    
    # Configuration
    config = {
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "platforms": {
            "example": {
                "api_key": "example_api_key",
                "webhook_url": "https://example.com/webhook"
            }
        }
    }
    
    # Create MindBot application
    app = MindBotApplication(config)
    
    # Create and register platform adapter
    example_adapter = ExamplePlatformAdapter("example", config["platforms"]["example"])
    app.register_platform_adapter(example_adapter)
    
    # Start the application
    logger.info("Starting MindBot application...")
    success = await app.start()
    
    if not success:
        logger.error("Failed to start MindBot application")
        return
    
    logger.info("MindBot application started successfully!")
    
    # Simulate some activity
    try:
        # Simulate receiving a message
        raw_message = {
            "user_id": "user123",
            "user_name": "Test User",
            "content": "Hello, MindBot!",
            "timestamp": 1234567890,
            "metadata": {}
        }
        
        # Process the message
        message = await example_adapter.process_incoming_message(raw_message)
        
        # Create a response
        response = Response(
            message_id=message.id,
            platform=message.platform,
            content=f"Hello {message.user_name}! I received your message: {message.content}",
            message_type=MessageType.TEXT,
            metadata={},
            success=True
        )
        
        # Send the response
        await example_adapter.send_message(response)
        
        # Get application status
        status = await app.get_status()
        logger.info(f"Application status: {status}")
        
        # Get health check
        health = await app.health_check()
        logger.info(f"Health check: {health}")
        
        # Keep running for a bit
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        # Shutdown the application
        logger.info("Shutting down MindBot application...")
        await app.shutdown()
        logger.info("MindBot application shutdown completed")

if __name__ == "__main__":
    asyncio.run(main())
