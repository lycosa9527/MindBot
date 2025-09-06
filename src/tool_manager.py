#!/usr/bin/env python3
"""
MindBot Tool Manager - LangChain Tool Compatibility
Manages LangChain tools with zero compatibility issues
"""

from typing import Dict, List, Type, Any, Optional
from langchain.tools import BaseTool
from langchain.agents import Tool
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)

class LangChainToolManager:
    """
    Manages LangChain tools with zero compatibility issues
    """
    
    def __init__(self):
        self.registered_tools: Dict[str, BaseTool] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(self, tool: BaseTool, dependencies: List[str] = None):
        """Register a LangChain tool with dependency tracking"""
        tool_name = tool.name
        self.registered_tools[tool_name] = tool
        
        # Track dependencies for compatibility checking
        self.tool_metadata[tool_name] = {
            'dependencies': dependencies or [],
            'tool_class': tool.__class__.__name__,
            'is_async': hasattr(tool, '_arun'),
            'is_sync': hasattr(tool, '_run'),
            'description': tool.description
        }
        
        logger.info(f"Registered tool: {tool_name} ({tool.__class__.__name__})")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name"""
        return self.registered_tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.registered_tools.keys())
    
    def check_compatibility(self, tool_name: str) -> Dict[str, Any]:
        """Check tool compatibility and dependencies"""
        if tool_name not in self.tool_metadata:
            return {'compatible': False, 'error': 'Tool not found'}
        
        metadata = self.tool_metadata[tool_name]
        issues = []
        
        # Check if tool has required methods
        tool = self.registered_tools[tool_name]
        if not hasattr(tool, 'name'):
            issues.append('Missing name attribute')
        if not hasattr(tool, 'description'):
            issues.append('Missing description attribute')
        if not (hasattr(tool, '_run') or hasattr(tool, '_arun')):
            issues.append('Missing _run or _arun method')
        
        return {
            'compatible': len(issues) == 0,
            'issues': issues,
            'metadata': metadata
        }
    
    def create_langchain_tools(self) -> List[Tool]:
        """Convert registered tools to LangChain Tool objects"""
        langchain_tools = []
        for name, tool in self.registered_tools.items():
            try:
                langchain_tool = Tool(
                    name=tool.name,
                    description=tool.description,
                    func=tool._run if hasattr(tool, '_run') else None,
                    coroutine=tool._arun if hasattr(tool, '_arun') else None
                )
                langchain_tools.append(langchain_tool)
                logger.debug(f"Created LangChain tool: {tool.name}")
            except Exception as e:
                logger.error(f"Error creating LangChain tool {tool.name}: {e}")
        
        return langchain_tools
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific tool"""
        if tool_name not in self.registered_tools:
            return {'error': 'Tool not found'}
        
        tool = self.registered_tools[tool_name]
        metadata = self.tool_metadata[tool_name]
        
        return {
            'name': tool.name,
            'description': tool.description,
            'class': tool.__class__.__name__,
            'async_support': metadata['is_async'],
            'sync_support': metadata['is_sync'],
            'dependencies': metadata['dependencies'],
            'compatibility': self.check_compatibility(tool_name)
        }
    
    def validate_all_tools(self) -> Dict[str, Any]:
        """Validate all registered tools for compatibility"""
        results = {}
        for tool_name in self.registered_tools.keys():
            results[tool_name] = self.check_compatibility(tool_name)
        
        compatible_count = sum(1 for r in results.values() if r['compatible'])
        total_count = len(results)
        
        return {
            'total_tools': total_count,
            'compatible_tools': compatible_count,
            'incompatible_tools': total_count - compatible_count,
            'results': results
        }
