from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import BaseTool
from typing import List, Dict, Any
import logging
from config import OPENAI_API_KEY
from dify_client import DifyClient
from tools import DifyChatTool, GetTimeTool, GetUserInfoTool, CalculatorTool

logger = logging.getLogger(__name__)

class MindBotAgent:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or OPENAI_API_KEY
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize Dify client
        self.dify_client = DifyClient()
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("MindBotAgent initialized successfully")
    
    def _create_tools(self) -> List[BaseTool]:
        """Create and return list of available tools"""
        tools = [
            DifyChatTool(self.dify_client),
            GetTimeTool(),
            GetUserInfoTool(),
            CalculatorTool()
        ]
        logger.info(f"Created {len(tools)} tools for agent")
        return tools
    
    def _create_agent(self):
        """Create the LangChain agent with tools"""
        system_prompt = """You are MindBot, a helpful AI assistant integrated with DingTalk. 
        You have access to the following tools:
        - dify_chat: Use this to chat with Dify API for knowledge and workflow responses
        - get_time: Get current date and time
        - get_user_info: Get information about the current user
        - calculator: Perform basic mathematical calculations
        
        When a user asks a question, you should:
        1. First try to use the dify_chat tool to get a response from Dify API
        2. If the user asks for time, use get_time tool
        3. If the user asks for calculations, use calculator tool
        4. If the user asks about themselves, use get_user_info tool
        
        Always be helpful and provide clear, concise responses."""
        
        prompt = [SystemMessage(content=system_prompt)]
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        logger.info("Agent created with OpenAI functions")
        return agent
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message using the agent"""
        try:
            # Enhance message with context
            user_id = context.get("user_id", "unknown") if context else "unknown"
            enhanced_message = f"User {user_id}: {message}"
            
            logger.info(f"Processing message: {message[:50]}...")
            
            # Use agent to process the message
            result = await self.agent.ainvoke({
                "input": enhanced_message
            })
            
            response = result.get("output", "")
            logger.info(f"Agent response: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in agent processing: {str(e)}")
            # Fallback to direct Dify chat
            try:
                fallback_response = await self.dify_client.chat_completion(message)
                logger.info("Used fallback Dify response")
                return fallback_response
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    async def test_tool_calling(self):
        """Test the agent's tool calling capabilities"""
        logger.info("Testing agent tool calling...")
        
        test_cases = [
            "What time is it?",
            "Calculate 15 * 7",
            "Tell me about user 12345",
            "Hello, how are you?"
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"Testing: {test_case}")
                result = await self.process_message(test_case)
                logger.info(f"Test result: {result[:100]}...")
            except Exception as e:
                logger.error(f"Test failed for '{test_case}': {str(e)}")
        
        logger.info("Tool calling test completed") 