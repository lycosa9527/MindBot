import logging
import aiohttp
import asyncio
from typing import Dict, Any
from config import DIFY_API_KEY, DIFY_BASE_URL, QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, DEBUG_MODE

logger = logging.getLogger(__name__)

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

class ConnectionTester:
    def __init__(self):
        self.debug_logger = DebugLogger("ConnectionTester")
    
    async def test_dify_connection(self) -> bool:
        """Test connection to Dify API"""
        try:
            self.debug_logger.log_info("Testing Dify API connection...")
            
            url = f"{DIFY_BASE_URL}/chat-messages"
            headers = {
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": {},
                "query": "test",
                "response_mode": "blocking",
                "user": "test_user"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        self.debug_logger.log_info("Dify API connection successful")
                        return True
                    else:
                        error_text = await response.text()
                        self.debug_logger.log_error(f"Dify API connection failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.debug_logger.log_error(f"Dify API connection error: {str(e)}")
            return False
    
    async def test_qwen_connection(self) -> bool:
        """Test connection to Qwen API"""
        try:
            self.debug_logger.log_info("Testing Qwen API connection...")
            
            # Simple test - try to create a ChatOpenAI instance with Qwen config
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model=QWEN_MODEL,
                temperature=0,
                openai_api_key=QWEN_API_KEY,
                openai_api_base=QWEN_BASE_URL
            )
            
            # Test with a simple message
            response = await llm.ainvoke("Hello")
            
            if response and response.content:
                self.debug_logger.log_info("Qwen API connection successful")
                return True
            else:
                self.debug_logger.log_error("Qwen API connection failed - no response")
                return False
                
        except Exception as e:
            self.debug_logger.log_error(f"Qwen API connection error: {str(e)}")
            return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configuration settings"""
        self.debug_logger.log_info("Validating configuration...")
        
        results = {
            "dify_api_key": bool(DIFY_API_KEY),
            "dify_base_url": bool(DIFY_BASE_URL),
            "qwen_api_key": bool(QWEN_API_KEY),
            "qwen_base_url": bool(QWEN_BASE_URL),
            "qwen_model": bool(QWEN_MODEL),
            "debug_mode": DEBUG_MODE
        }
        
        missing_items = [key for key, value in results.items() if not value]
        if missing_items:
            self.debug_logger.log_error(f"Missing configuration: {missing_items}")
        else:
            self.debug_logger.log_info("Configuration validation passed")
        
        return results

class ToolTester:
    def __init__(self):
        self.debug_logger = DebugLogger("ToolTester")
    
    async def test_dify_tool(self, dify_client) -> bool:
        """Test Dify chat tool"""
        try:
            self.debug_logger.log_info("Testing Dify chat tool...")
            
            from tools import DifyChatTool
            tool = DifyChatTool(dify_client)
            
            result = await tool._arun("Hello, this is a test")
            
            if result and not result.startswith("Error"):
                self.debug_logger.log_info("Dify chat tool test successful")
                return True
            else:
                self.debug_logger.log_error(f"Dify chat tool test failed: {result}")
                return False
                
        except Exception as e:
            self.debug_logger.log_error(f"Dify chat tool test error: {str(e)}")
            return False
    
    async def test_time_tool(self) -> bool:
        """Test get time tool"""
        try:
            self.debug_logger.log_info("Testing get time tool...")
            
            from tools import GetTimeTool
            tool = GetTimeTool()
            
            result = await tool._arun("")
            
            if result and "Current time:" in result:
                self.debug_logger.log_info("Get time tool test successful")
                return True
            else:
                self.debug_logger.log_error(f"Get time tool test failed: {result}")
                return False
                
        except Exception as e:
            self.debug_logger.log_error(f"Get time tool test error: {str(e)}")
            return False
    
    async def test_calculator_tool(self) -> bool:
        """Test calculator tool"""
        try:
            self.debug_logger.log_info("Testing calculator tool...")
            
            from tools import CalculatorTool
            tool = CalculatorTool()
            
            result = await tool._arun("2 + 2")
            
            if result and "Result: 4" in result:
                self.debug_logger.log_info("Calculator tool test successful")
                return True
            else:
                self.debug_logger.log_error(f"Calculator tool test failed: {result}")
                return False
                
        except Exception as e:
            self.debug_logger.log_error(f"Calculator tool test error: {str(e)}")
            return False

class AgentTester:
    def __init__(self):
        self.debug_logger = DebugLogger("AgentTester")
    
    async def test_agent_tool_calling(self, agent) -> bool:
        """Test agent's tool calling capabilities"""
        try:
            self.debug_logger.log_info("Testing agent tool calling...")
            
            test_cases = [
                "What time is it?",
                "Calculate 10 + 5",
                "Hello, how are you?"
            ]
            
            success_count = 0
            for test_case in test_cases:
                try:
                    result = await agent.process_message(test_case)
                    if result and not result.startswith("Error"):
                        success_count += 1
                        self.debug_logger.log_info(f"Test case '{test_case}' passed")
                    else:
                        self.debug_logger.log_error(f"Test case '{test_case}' failed: {result}")
                except Exception as e:
                    self.debug_logger.log_error(f"Test case '{test_case}' error: {str(e)}")
            
            success_rate = success_count / len(test_cases)
            self.debug_logger.log_info(f"Agent tool calling test completed: {success_count}/{len(test_cases)} passed")
            
            return success_rate >= 0.5  # At least 50% success rate
            
        except Exception as e:
            self.debug_logger.log_error(f"Agent tool calling test error: {str(e)}")
            return False

async def run_diagnostics():
    """Run comprehensive diagnostics"""
    logger.info("Starting comprehensive diagnostics...")
    
    # Initialize testers
    connection_tester = ConnectionTester()
    tool_tester = ToolTester()
    agent_tester = AgentTester()
    
    # Test configuration
    config_results = connection_tester.validate_configuration()
    
    # Test connections
    dify_connection = await connection_tester.test_dify_connection()
    qwen_connection = await connection_tester.test_qwen_connection()
    
    # Test tools (if connections are working)
    tool_results = {}
    if dify_connection:
        from dify_client import DifyClient
        dify_client = DifyClient()
        tool_results["dify_tool"] = await tool_tester.test_dify_tool(dify_client)
    
    tool_results["time_tool"] = await tool_tester.test_time_tool()
    tool_results["calculator_tool"] = await tool_tester.test_calculator_tool()
    
    # Test agent (if Qwen connection is working)
    agent_result = False
    if qwen_connection:
        from agent import MindBotAgent
        agent = MindBotAgent()
        agent_result = await agent_tester.test_agent_tool_calling(agent)
    
    # Summary
    logger.info("=== DIAGNOSTICS SUMMARY ===")
    logger.info(f"Configuration: {'PASS' if all(config_results.values()) else 'FAIL'}")
    logger.info(f"Dify Connection: {'PASS' if dify_connection else 'FAIL'}")
    logger.info(f"Qwen Connection: {'PASS' if qwen_connection else 'FAIL'}")
    logger.info(f"Tool Tests: {sum(tool_results.values())}/{len(tool_results)} PASS")
    logger.info(f"Agent Test: {'PASS' if agent_result else 'FAIL'}")
    
    overall_success = (
        all(config_results.values()) and
        dify_connection and
        qwen_connection and
        all(tool_results.values()) and
        agent_result
    )
    
    logger.info(f"Overall Status: {'PASS' if overall_success else 'FAIL'}")
    
    return overall_success 