#!/usr/bin/env python3
"""
Centralized Logging Configuration for MindBot
Provides unified logging setup across all modules
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class MindBotLogger:
    """Centralized logging configuration for MindBot"""
    
    _configured = False
    _config = None
    
    @classmethod
    def configure(cls, config: Optional[Dict[str, Any]] = None):
        """Configure logging system"""
        if cls._configured:
            return
            
        # Default configuration
        default_config = {
            "level": "INFO",
            "log_file": "logs/mindbot.log",
            "file_rotation": True,
            "max_file_size": "10MB",
            "backup_count": 5,
            "log_format": "%(asctime)s - %(levelname)s - %(message)s",
            "console_output": True,
            "file_output": True,
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        
        cls._config = default_config
        
        # Create logs directory if it doesn't exist
        log_file = Path(default_config["log_file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, default_config["level"].upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter with custom date format
        formatter = logging.Formatter(
            default_config["log_format"],
            datefmt=default_config["date_format"]
        )
        
        # Console handler
        if default_config["console_output"]:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(getattr(logging, default_config["level"].upper()))
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if default_config["file_output"]:
            if default_config["file_rotation"]:
                # Use RotatingFileHandler for file rotation
                max_bytes = cls._parse_size(default_config["max_file_size"])
                file_handler = logging.handlers.RotatingFileHandler(
                    default_config["log_file"],
                    maxBytes=max_bytes,
                    backupCount=default_config["backup_count"],
                    encoding='utf-8'
                )
            else:
                # Use regular FileHandler
                file_handler = logging.FileHandler(
                    default_config["log_file"],
                    encoding='utf-8'
                )
            
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, default_config["level"].upper()))
            root_logger.addHandler(file_handler)
        
        # Configure specific loggers
        cls._configure_module_loggers()
        
        cls._configured = True
        
        # Log configuration success (only to file, not console)
        logger = logging.getLogger(__name__)
        logger.info("Centralized logging system configured successfully")
        logger.info(f"Log level: {default_config['level']}")
        logger.info(f"Log file: {default_config['log_file']}")
        logger.info(f"File rotation: {default_config['file_rotation']}")
        
        # Reduce console noise by setting this logger to WARNING for console
        console_logger = logging.getLogger(__name__)
        for handler in console_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.WARNING)
    
    @classmethod
    def _configure_module_loggers(cls):
        """Configure specific module loggers with appropriate levels"""
        module_configs = {
            # Core framework modules - use friendly names
            "mindbot_framework": "INFO",
            "src.enhanced_multi_platform_manager": "INFO",
            "src.agent": "INFO",
            "src.dingtalk_client": "INFO",
            "src.wecom_direct_client": "INFO",
            "__main__": "INFO",  # Main application
            
            # External libraries (reduce noise)
            "dingtalk_stream": "WARNING",
            "werkzeug": "WARNING",
            "urllib3": "WARNING",
            "requests": "WARNING",
            "aiohttp": "WARNING",
            "flask": "WARNING",
            
            # Runtime adapters
            "runtime-adapter": "INFO",
            
            # Voice and debug modules
            "src.voice_recognition": "INFO",
            "src.debug": "DEBUG",
            
            # Config modules
            "src.config": "WARNING",
        }
        
        for module, level in module_configs.items():
            logger = logging.getLogger(module)
            logger.setLevel(getattr(logging, level.upper()))
    
    @classmethod
    def _parse_size(cls, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance"""
        if not cls._configured:
            cls.configure()
        return logging.getLogger(name)
    
    @classmethod
    def set_level(cls, level: str):
        """Set logging level for all handlers"""
        if not cls._configured:
            return
            
        log_level = getattr(logging, level.upper())
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(log_level)
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get current logging configuration"""
        return cls._config or {}


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger"""
    return MindBotLogger.get_logger(name)


def configure_logging(config: Optional[Dict[str, Any]] = None):
    """Convenience function to configure logging"""
    MindBotLogger.configure(config)


# Module-level logger
logger = get_logger(__name__)
