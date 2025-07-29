import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Version Information
VERSION = "v0.1"
BUILD_DATE = "2024-01-20"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mindbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# DingTalk Stream Mode Configuration
DINGTALK_CLIENT_ID = os.getenv("DINGTALK_CLIENT_ID", "dingr6bg0cj9ylmlpuqz")
DINGTALK_CLIENT_SECRET = os.getenv("DINGTALK_CLIENT_SECRET", "h2uRQXw2osb5-VhAzCd_fhwXWwTKiitF8pBIb0JuXENwkxnjksYoHtMDqnGwVQmD")
DINGTALK_ROBOT_CODE = os.getenv("DINGTALK_ROBOT_CODE", "dingr6bg0cj9ylmlpuqz")

# Dify Configuration
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-4DGFRXExxcP0xZ5Og3AXfT2N")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "http://dify.mindspringedu.com/v1")
DIFY_WORKSPACE_ID = os.getenv("DIFY_WORKSPACE_ID")

# Qwen Configuration (replacing OpenAI)
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "sk-c688d7977e6547019b7532ab69c818b2")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo-latest")

# OpenAI Configuration (kept for backward compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug Configuration
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

logger.info(f"MindBot {VERSION} ({BUILD_DATE}) - Configuration loaded successfully")
logger.debug(f"DingTalk Client ID: {DINGTALK_CLIENT_ID}")
logger.debug(f"Dify API Key: {'***' if DIFY_API_KEY else 'NOT SET'}")
logger.debug(f"Dify Base URL: {DIFY_BASE_URL}")
logger.debug(f"Qwen API Key: {'***' if QWEN_API_KEY else 'NOT SET'}")
logger.debug(f"Qwen Base URL: {QWEN_BASE_URL}")
logger.debug(f"Qwen Model: {QWEN_MODEL}")
logger.debug(f"OpenAI API Key: {'***' if OPENAI_API_KEY else 'NOT SET'}") 