#!/usr/bin/env python3
"""
MindBot Configuration Module
Handles environment variables, API keys, and application settings
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file automatically
load_dotenv()

# Version Information for the application
VERSION = "v0.4"
BUILD_DATE = "2025-01-30"

# DingTalk Stream Mode Configuration
# These are required for DingTalk WebSocket connection and message processing
DINGTALK_CLIENT_ID = os.getenv("DINGTALK_CLIENT_ID")
DINGTALK_CLIENT_SECRET = os.getenv("DINGTALK_CLIENT_SECRET")
DINGTALK_ROBOT_CODE = os.getenv("DINGTALK_ROBOT_CODE")
DINGTALK_ROBOT_NAME = os.getenv("DINGTALK_ROBOT_NAME", "MindBot_poc")

# Dify Configuration for AI knowledge base integration
# These connect to the Dify API for intelligent responses
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL")
DIFY_WORKSPACE_ID = os.getenv("DIFY_WORKSPACE_ID")

# Qwen Configuration (replacing OpenAI) for LLM processing
# These connect to Alibaba's Qwen model for AI responses
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3-0.6b")

# OpenAI Configuration (kept for backward compatibility)
# This allows switching to OpenAI if needed in the future
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug Configuration for development and troubleshooting
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Logging Levels Used in Application / 应用程序中使用的日志级别
# 
# The application uses 5 standard Python logging levels:
# 应用程序使用 5 个标准 Python 日志级别：
#
# 1. DEBUG (10) - Detailed diagnostic information for developers
#    - Internal message flow tracking
#    - API request/response details
#    - Method entry/exit points
#    - Configuration details (masked sensitive data)
#    - Network connectivity details
#    - Memory usage and performance metrics
#
# 2. INFO (20) - General operational information for users
#    - User messages received (what users actually sent)
#    - AI responses sent to users
#    - Application startup/shutdown events
#    - Component initialization status
#    - Duplicate message detection
#    - Error responses sent to users
#    - Connection status and health checks
#
# 3. WARNING (30) - Warning messages for potential issues
#    - Empty or invalid messages received
#    - API responses that need attention
#    - Configuration issues (non-critical)
#    - Performance degradation warnings
#    - Message truncation due to length limits
#
# 4. ERROR (40) - Error messages for actual problems
#    - API call failures
#    - Network connectivity issues
#    - Configuration errors (missing required variables)
#    - Message processing failures
#    - WebSocket connection problems
#    - JSON parsing errors
#
# 5. CRITICAL (50) - Critical errors that may cause application failure
#    - System-level failures
#    - Resource exhaustion
#    - Security violations
#    - Unrecoverable errors
#
# Default LOG_LEVEL is "INFO" for production use
# Set to "DEBUG" for detailed troubleshooting
# Set to "WARNING" to reduce console output
#
# Log Level Usage Statistics / 日志级别使用统计
# 
# Current application log level distribution:
# 当前应用程序日志级别分布：
#
# DEBUG: ~45 instances - Internal flow, API details, method calls
# INFO:  ~35 instances - User messages, responses, status updates
# WARNING: ~8 instances - Non-critical issues, empty messages
# ERROR:  ~25 instances - Failures, exceptions, connectivity issues
# CRITICAL: ~0 instances - Not currently used (reserved for system failures)
#
# Total: ~113 logging statements across all modules
# 总计：所有模块中约 113 个日志语句

# Application Constants for limits and validation
# These prevent resource exhaustion and ensure security
DINGTALK_MESSAGE_LIMIT = 5000  # Maximum message length for DingTalk
CALCULATOR_EXPRESSION_LIMIT = 100  # Maximum expression length for calculator tool

# Get logger for this module for configuration logging
logger = logging.getLogger(__name__)

# Validate required environment variables to prevent runtime errors
# This ensures all necessary API keys and URLs are provided
required_vars = {
    "DINGTALK_CLIENT_ID": DINGTALK_CLIENT_ID,
    "DINGTALK_CLIENT_SECRET": DINGTALK_CLIENT_SECRET,
    "DINGTALK_ROBOT_CODE": DINGTALK_ROBOT_CODE,
    "DIFY_API_KEY": DIFY_API_KEY,
    "DIFY_BASE_URL": DIFY_BASE_URL,
    "QWEN_API_KEY": QWEN_API_KEY,
    "QWEN_BASE_URL": QWEN_BASE_URL
}

# Check for missing required variables and provide clear error messages
missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    logger.error(f"Missing required environment variables: {missing_vars}")
    logger.error("Please set these variables in your .env file")
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# Log successful configuration loading with masked sensitive data
logger.info(f"MindBot {VERSION} ({BUILD_DATE}) - Configuration loaded successfully")
logger.debug(f"DingTalk Client ID: {DINGTALK_CLIENT_ID}")
logger.debug(f"DingTalk Robot Code: {DINGTALK_ROBOT_CODE}")
logger.debug(f"DingTalk Robot Name: {DINGTALK_ROBOT_NAME}")
logger.debug(f"Dify API Key: {'***' if DIFY_API_KEY else 'NOT SET'}")
logger.debug(f"Dify Base URL: {DIFY_BASE_URL}")
logger.debug(f"Qwen API Key: {'***' if QWEN_API_KEY else 'NOT SET'}")
logger.debug(f"Qwen Base URL: {QWEN_BASE_URL}")
logger.debug(f"Qwen Model: {QWEN_MODEL}")
logger.debug(f"OpenAI API Key: {'***' if OPENAI_API_KEY else 'NOT SET'}") 