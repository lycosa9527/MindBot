import asyncio
import signal
import sys
import logging
from config import DEBUG_MODE, VERSION, BUILD_DATE
from dingtalk_client import MindBotDingTalkClient
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
            logger.info(f"Initializing MindBot {VERSION} ({BUILD_DATE}) Stream Application...")
            
            # Initialize agent
            self.agent = MindBotAgent()
            logger.info("Agent initialized successfully")
            
            # Initialize DingTalk stream client
            self.dingtalk_client = MindBotDingTalkClient(
                agent_handler=self.handle_message
            )
            logger.info("DingTalk Stream Client initialized successfully")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            logger.info("Application initialization completed")
            
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
            raise
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            # Create a task to stop the application
            asyncio.create_task(self.stop())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def handle_message(self, message: str, context: dict = None) -> str:
        """Handle incoming messages using the agent"""
        try:
            # Validate input
            if not message or not message.strip():
                return "I'm sorry, I didn't receive any message. Please try again."
            
            logger.info(f"Handling message: {message[:50]}...")
            
            # Process with agent
            response = await self.agent.process_message(message, context)
            
            logger.info(f"Generated response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return "I'm sorry, I encountered an error processing your message. Please try again."
    
    async def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        logger.info("Running diagnostics...")
        
        try:
            # Test agent tool calling
            agent_success = await self.agent.test_tool_calling()
            
            logger.info("=== DIAGNOSTICS SUMMARY ===")
            logger.info(f"Agent Tool Calling: {'PASS' if agent_success else 'FAIL'}")
            
            return agent_success
            
        except Exception as e:
            logger.error(f"Diagnostics failed: {str(e)}")
            return False
    
    async def start(self):
        """Start the application"""
        try:
            logger.info(f"Starting MindBot {VERSION} Stream Application...")
            
            # Initialize components
            await self.initialize()
            
            # Run diagnostics
            diagnostics_ok = await self.run_diagnostics()
            
            if not diagnostics_ok:
                logger.warning("Some diagnostics failed, but continuing...")
            
            # Start DingTalk stream client
            logger.info("Starting DingTalk Stream Client...")
            await self.dingtalk_client.start()
            
        except Exception as e:
            logger.error(f"Error in application: {str(e)}")
            await self.stop()
            sys.exit(1)
    
    async def stop(self):
        """Stop the application"""
        try:
            logger.info("Stopping MindBot Stream Application...")
            self.running = False
            
            if self.dingtalk_client:
                await self.dingtalk_client.stop()
                logger.info("DingTalk Stream Client stopped")
            
            logger.info("Application stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping application: {str(e)}")

async def main():
    """Main entry point"""
    app = MindBotStreamApp()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1) 