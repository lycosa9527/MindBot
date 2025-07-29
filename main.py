import asyncio
import signal
import sys
import logging
from config import DEBUG_MODE
from dingtalk_stream import DingTalkStreamClient
from agent import MindBotAgent
from debug import run_diagnostics

logger = logging.getLogger(__name__)

class MindBotStreamApp:
    def __init__(self):
        self.agent = None
        self.dingtalk_client = None
        self.running = False
        
    async def initialize(self):
        """Initialize the application components"""
        try:
            logger.info("Initializing MindBot Stream Application...")
            
            # Initialize agent
            self.agent = MindBotAgent()
            logger.info("Agent initialized successfully")
            
            # Initialize DingTalk stream client
            self.dingtalk_client = DingTalkStreamClient(
                agent_handler=self.handle_message
            )
            logger.info("DingTalk Stream Client initialized successfully")
            
            # Run diagnostics if debug mode is enabled
            if DEBUG_MODE:
                logger.info("Running diagnostics...")
                diagnostics_success = await run_diagnostics()
                if not diagnostics_success:
                    logger.warning("Some diagnostics failed, but continuing...")
            
            # Test agent tool calling
            await self.agent.test_tool_calling()
            
            logger.info("Application initialization completed")
            
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            raise
    
    async def handle_message(self, message: str, context: dict = None) -> str:
        """Handle incoming messages"""
        try:
            logger.info(f"Handling message: {message[:50]}...")
            response = await self.agent.process_message(message, context)
            logger.info(f"Generated response: {response[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the application"""
        try:
            logger.info("Starting MindBot Stream Application...")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize components
            await self.initialize()
            
            # Start the DingTalk stream client
            self.running = True
            logger.info("Starting DingTalk Stream Client...")
            await self.dingtalk_client.start()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error in application: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the application"""
        try:
            logger.info("Stopping MindBot Stream Application...")
            
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
                logger.info("DingTalk Stream Client stopped")
            
            self.running = False
            logger.info("Application stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

async def main():
    """Main entry point"""
    app = MindBotStreamApp()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1) 