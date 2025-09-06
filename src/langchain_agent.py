#!/usr/bin/env python3
"""
MindBot LangChain Agent - Enhanced Agent Integration
Provides seamless LangChain agent integration with zero compatibility issues
"""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tool_manager import LangChainToolManager
from src.tools import create_tools
import logging

logger = logging.getLogger(__name__)

class MindBotLangChainAgent:
    """
    Enhanced LangChain agent integration for MindBot
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tool_manager = LangChainToolManager()
        self.llm = self._create_llm()
        self.agent_executor = None
        self._setup_tools()
    
    def _create_llm(self):
        """Create LLM based on configuration"""
        provider = self.config.get('provider', 'openai')
        
        try:
            if provider == 'openai':
                return ChatOpenAI(
                    model=self.config.get('model', 'gpt-4'),
                    temperature=self.config.get('temperature', 0.7),
                    api_key=self.config.get('api_key')
                )
            elif provider == 'anthropic':
                return ChatAnthropic(
                    model=self.config.get('model', 'claude-3-sonnet'),
                    temperature=self.config.get('temperature', 0.7),
                    api_key=self.config.get('api_key')
                )
            elif provider == 'google':
                return ChatGoogleGenerativeAI(
                    model=self.config.get('model', 'gemini-pro'),
                    temperature=self.config.get('temperature', 0.7),
                    api_key=self.config.get('api_key')
                )
            else:
                logger.warning(f"Unsupported provider: {provider}, falling back to OpenAI")
                return ChatOpenAI(
                    model=self.config.get('model', 'gpt-4'),
                    temperature=self.config.get('temperature', 0.7),
                    api_key=self.config.get('api_key')
                )
        except Exception as e:
            logger.error(f"Error creating LLM: {e}")
            raise
    
    def _setup_tools(self):
        """Setup tools and create agent"""
        try:
            # Load existing tools
            existing_tools = create_tools()
            
            # Register existing tools
            for tool in existing_tools:
                self.tool_manager.register_tool(tool)
            
            # Load additional tools if configured
            if self.config.get('load_custom_tools', False):
                self._load_custom_tools()
            
            # Create LangChain tools
            langchain_tools = self.tool_manager.create_langchain_tools()
            
            if not langchain_tools:
                logger.warning("No tools available for agent")
                return
            
            # Create agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.config.get('system_prompt', 'You are MindBot, an intelligent assistant.')),
                ("user", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            agent = create_tool_calling_agent(self.llm, langchain_tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=langchain_tools,
                verbose=self.config.get('verbose', False),
                max_iterations=self.config.get('max_iterations', 10),
                handle_parsing_errors=True
            )
            
            logger.info(f"LangChain agent initialized with {len(langchain_tools)} tools")
            
        except Exception as e:
            logger.error(f"Error setting up tools: {e}")
            raise
    
    def _load_custom_tools(self):
        """Load custom tools from various sources"""
        # This can be extended to load tools from plugins, directories, etc.
        logger.info("Loading custom tools...")
        # Placeholder for custom tool loading
        pass
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message through LangChain agent"""
        try:
            if not self.agent_executor:
                return "Agent not properly initialized"
            
            result = await self.agent_executor.ainvoke({
                "input": message,
                "context": context or {}
            })
            return result.get('output', 'No response generated')
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Error processing message: {str(e)}"
    
    def add_tool(self, tool):
        """Add a new tool to the agent"""
        try:
            self.tool_manager.register_tool(tool)
            # Recreate agent with new tools
            self._setup_tools()
            logger.info(f"Added tool: {tool.name}")
        except Exception as e:
            logger.error(f"Error adding tool: {e}")
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        return self.tool_manager.get_tool_info(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return self.tool_manager.list_tools()
    
    def validate_tools(self) -> Dict[str, Any]:
        """Validate all tools for compatibility"""
        return self.tool_manager.validate_all_tools()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and configuration"""
        return {
            'provider': self.config.get('provider'),
            'model': self.config.get('model'),
            'tools_count': len(self.tool_manager.list_tools()),
            'agent_initialized': self.agent_executor is not None,
            'tools_validation': self.validate_tools()
        }
