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
VERSION = "v0.3"
BUILD_DATE = "2025-07-30"

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