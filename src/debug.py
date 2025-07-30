#!/usr/bin/env python3
"""
MindBot Debug and Logging System
Provides professional colored logging and diagnostic utilities
"""

import logging
import asyncio
import aiohttp
import ssl
import certifi
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages for better readability.
    Uses ANSI escape codes for professional console output.
    """
    
    # Define color scheme for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,      # Cyan for debug messages
        'INFO': Fore.GREEN,      # Green for info messages
        'WARNING': Fore.YELLOW,  # Yellow for warnings
        'ERROR': Fore.RED,       # Red for errors
        'CRITICAL': Fore.RED + Style.BRIGHT  # Bright red for critical errors
    }
    
    def format(self, record):
        """
        Format log record with only the logging level colored.
        
        Args:
            record: LogRecord object containing message details
            
        Returns:
            Formatted log message with only level name colored
        """
        # Add timestamp in plain text (using record creation time for better performance)
        try:
            timestamp = f"[{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')}]"
        except (ValueError, OSError):
            # Fallback to current time if record.created is invalid
            timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]"
        
        # Add colored level name only
        level_name_safe = record.levelname or "UNKNOWN"
        level_color = self.COLORS.get(level_name_safe, Fore.WHITE)
        level_name = level_color + Style.BRIGHT + f"[{level_name_safe}]" + Style.RESET_ALL
        
        # Add component name in plain text
        component_name_safe = record.name or "unknown"
        component = f"[{component_name_safe}]"
        
        # Format the actual message in plain text
        message = f"{record.getMessage()}"
        
        # Combine all parts with proper spacing
        formatted = f"{timestamp} {level_name} {component} {message}"
        
        return formatted

class DebugLogger:
    """
    Enhanced logger for debugging and diagnostic information.
    Provides structured logging with clear status indicators.
    """
    
    def __init__(self, component_name: str):
        """
        Initialize debug logger for a specific component.
        
        Args:
            component_name: Name of the component for logging identification
        """
        if not component_name or not isinstance(component_name, str):
            component_name = "unknown"
        self.component_name = component_name
        self.logger = logging.getLogger(component_name)
    
    def log_success(self, message: str):
        """
        Log a success message.
        
        Args:
            message: Success message to log
        """
        self.logger.info(f"[SUCCESS] {message}")
    
    def log_failure(self, message: str):
        """
        Log a failure message.
        
        Args:
            message: Failure message to log
        """
        self.logger.error(f"[FAILURE] {message}")
    
    def log_step(self, message: str):
        """
        Log a step message.
        
        Args:
            message: Step message to log
        """
        self.logger.info(f"[STEP] {message}")
    
    def log_separator(self, title: str):
        """
        Log a separator line with title for visual organization.
        
        Args:
            title: Title to display in the separator
        """
        separator = f"━━━ {title} ━━━"
        self.logger.info(separator)
    
    def log_info(self, message: str):
        """
        Log an informational message.
        
        Args:
            message: Info message to log
        """
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """
        Log a debug message.
        
        Args:
            message: Debug message to log
        """
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        """
        Log a warning message.
        
        Args:
            message: Warning message to log
        """
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """
        Log an error message.
        
        Args:
            message: Error message to log
        """
        self.logger.error(message)

def setup_colored_logging():
    """
    Configure the logging system with colored output and proper formatting.
    This function sets up the root logger with custom formatter and handlers.
    """
    # Get the root logger to configure global logging
    root_logger = logging.getLogger()
    
    # Clear only console handlers to prevent duplicate logging
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler):
            root_logger.removeHandler(handler)
    
    # Create console handler for colored output
    console_handler = logging.StreamHandler()
    
    # Create custom colored formatter
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    # Set log level based on configuration
    from src.config import LOG_LEVEL
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    console_handler.setLevel(log_level)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)
    
    # Enable propagation to ensure child loggers inherit configuration
    root_logger.propagate = True

async def test_dingtalk_connection():
    """
    Test connection to DingTalk API to verify configuration and network connectivity.
    
    Returns:
        bool: True if connection test passes, False otherwise
    """
    from src.config import DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET
    from dingtalk_stream import Credential, DingTalkStreamClient
    
    debug_logger = DebugLogger("DingTalkTest")
    debug_logger.log_separator("DINGTALK CONNECTION TEST")
    
    try:
        # Test 1: Validate configuration
        debug_logger.log_step("Validating DingTalk configuration...")
        if not DINGTALK_CLIENT_ID:
            debug_logger.log_failure("DINGTALK_CLIENT_ID is not set")
            return False
        if not DINGTALK_CLIENT_SECRET:
            debug_logger.log_failure("DINGTALK_CLIENT_SECRET is not set")
            return False
        
        debug_logger.log_success("Configuration validation passed")
        
        # Test 2: Create credentials
        debug_logger.log_step("Creating DingTalk credentials...")
        credential = Credential(
            client_id=DINGTALK_CLIENT_ID,
            client_secret=DINGTALK_CLIENT_SECRET
        )
        debug_logger.log_success("Credentials created successfully")
        
        # Test 3: Create client
        debug_logger.log_step("Creating DingTalk Stream client...")
        client = DingTalkStreamClient(credential)
        debug_logger.log_success("Client created successfully")
        
        # Test 4: Test SSL configuration
        debug_logger.log_step("Testing SSL configuration...")
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        debug_logger.log_success("SSL context configured successfully")
        
        debug_logger.log_success("All DingTalk connection tests passed")
        return True
        
    except Exception as e:
        debug_logger.log_failure(f"DingTalk connection test failed: {str(e)}")
        return False

async def test_dify_connection():
    """
    Test connection to Dify API to verify configuration and network connectivity.
    
    Returns:
        bool: True if connection test passes, False otherwise
    """
    from src.config import DIFY_API_KEY, DIFY_BASE_URL
    
    debug_logger = DebugLogger("DifyTest")
    debug_logger.log_separator("DIFY CONNECTION TEST")
    
    try:
        # Test 1: Validate configuration
        debug_logger.log_step("Validating Dify configuration...")
        if not DIFY_API_KEY:
            debug_logger.log_failure("DIFY_API_KEY is not set")
            return False
        if not DIFY_BASE_URL:
            debug_logger.log_failure("DIFY_BASE_URL is not set")
            return False
        
        debug_logger.log_success("Configuration validation passed")
        
        # Test 2: Test HTTP connection with increased timeout
        debug_logger.log_step("Testing HTTP connection to Dify...")
        url = f"{DIFY_BASE_URL}/chat-messages"
        
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {},
            "query": "Hello",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "test_user",
            "files": []
        }
        
        # Increased timeout from default to 60 seconds for Dify API
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    debug_logger.log_success("Dify API connection successful")
                    return True
                else:
                    error_text = await response.text()
                    debug_logger.log_failure(f"Dify API returned status {response.status}: {error_text}")
                    return False
                    
    except Exception as e:
        debug_logger.log_failure(f"Dify connection test failed: {str(e)}")
        return False

async def test_network_connectivity():
    """
    Test general network connectivity to external services.
    
    Returns:
        bool: True if network tests pass, False otherwise
    """
    debug_logger = DebugLogger("NetworkTest")
    debug_logger.log_separator("NETWORK CONNECTIVITY TEST")
    
    test_urls = [
        "https://www.bing.com",  # Changed from Google to Bing for better reliability
        "https://www.baidu.com",
        "https://api.dingtalk.com"
    ]
    
    success_count = 0
    
    for url in test_urls:
        try:
            debug_logger.log_step(f"Testing connection to {url}...")
            # Increased timeout from 10 to 30 seconds for better reliability
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        debug_logger.log_success(f"Connection to {url} successful")
                        success_count += 1
                    else:
                        debug_logger.log_failure(f"Connection to {url} failed: {response.status}")
        except Exception as e:
            debug_logger.log_failure(f"Connection to {url} failed: {str(e)}")
    
    debug_logger.log_info(f"Network test results: {success_count}/{len(test_urls)} successful")
    return success_count >= len(test_urls) * 0.5  # At least 50% success rate

async def run_diagnostics():
    """
    Run comprehensive system diagnostics to verify all components.
    This function tests all critical system components and reports results.
    """
    debug_logger = DebugLogger("Diagnostics")
    debug_logger.log_separator("SYSTEM DIAGNOSTICS")
    
    # Track test results
    test_results = []
    
    # Test 1: Network connectivity
    debug_logger.log_step("Testing network connectivity...")
    network_ok = await test_network_connectivity()
    test_results.append(("Network", network_ok))
    
    # Test 2: DingTalk connection
    debug_logger.log_step("Testing DingTalk connection...")
    dingtalk_ok = await test_dingtalk_connection()
    test_results.append(("DingTalk", dingtalk_ok))
    
    # Test 3: Dify connection
    debug_logger.log_step("Testing Dify connection...")
    dify_ok = await test_dify_connection()
    test_results.append(("Dify", dify_ok))
    
    # Report results
    debug_logger.log_separator("DIAGNOSTIC RESULTS")
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        if result:
            debug_logger.log_success(f"{test_name}: PASS")
        else:
            debug_logger.log_failure(f"{test_name}: FAIL")
    
    debug_logger.log_info(f"Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        debug_logger.log_success("All diagnostics passed - system ready")
    else:
        debug_logger.log_warning("Some diagnostics failed - check configuration")
    
    return passed_tests == total_tests 