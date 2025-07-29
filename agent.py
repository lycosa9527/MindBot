from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from typing import List, Dict, Any
import logging
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, VERSION
from dify_client import DifyClient
from tools import DifyChatTool, GetTimeTool, GetUserInfoTool, CalculatorTool

logger = logging.getLogger(__name__)

class MindBotAgent:
    def __init__(self, qwen_api_key: str = None):
        self.qwen_api_key = qwen_api_key or QWEN_API_KEY
        self.llm = ChatOpenAI(
            model=QWEN_MODEL,
            temperature=0.7,
            openai_api_key=self.qwen_api_key,
            openai_api_base=QWEN_BASE_URL
        )
        
        # Initialize Dify client
        self.dify_client = DifyClient()
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent executor
        self.agent_executor = self._create_agent()
        
        logger.info(f"MindBotAgent {VERSION} initialized successfully")
    
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
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor with tools"""
        system_prompt = f"""You are MindBot {VERSION}, a helpful AI assistant integrated with DingTalk. 
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
        
        Always be helpful and provide clear, concise responses.
        If you encounter an error, try to provide a helpful fallback response."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        logger.info("Agent executor created with Qwen functions")
        return agent_executor
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message using the agent executor"""
        try:
            # Validate input
            if not message or not message.strip():
                return "I'm sorry, I didn't receive any message. Please try again."
            
            # Enhance message with context
            user_id = context.get("user_id", "unknown") if context else "unknown"
            enhanced_message = f"User {user_id}: {message.strip()}"
            
            logger.info(f"Processing message: {message[:50]}...")
            
            # Use agent executor to process the message
            result = await self.agent_executor.ainvoke({
                "input": enhanced_message
            })
            
            response = result.get("output", "")
            if not response or response.strip() == "":
                response = "I'm sorry, I couldn't generate a response. Please try again."
            
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
        
        logger.info(f"Tool calling test completed: {success_count}/{len(test_cases)} passed")
        return success_count >= len(test_cases) * 0.5  # At least 50% success rate 