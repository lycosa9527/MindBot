#!/usr/bin/env python3
"""
Debug Logger Module
Simple debug logging utility for MindBot
"""

from typing import Any, Dict
from .logging_config import get_logger

class DebugLogger:
    """Simple debug logger for development and troubleshooting"""
    
    def __init__(self, name: str):
        self.logger = get_logger(f"debug.{name}")
        self.name = name
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"[{self.name}] {message}", extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(f"[{self.name}] {message}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(f"[{self.name}] {message}", extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(f"[{self.name}] {message}", extra=kwargs)
    
    def log_data(self, data: Any, label: str = "data"):
        """Log structured data for debugging"""
        self.debug(f"{label}: {data}")
    
    def log_dict(self, data: Dict[str, Any], label: str = "dict"):
        """Log dictionary data for debugging"""
        for key, value in data.items():
            self.debug(f"{label}.{key}: {value}")