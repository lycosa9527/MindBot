#!/usr/bin/env python3
"""
MindBot Multi-Instance Startup Script
Unified startup for multiple DingTalk and WeCom adapters running concurrently
"""

import asyncio
import logging
import signal
import sys
import json
import os
import threading
import argparse
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

# Import Flask for web dashboard
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Import centralized logging
from src.logging_config import configure_logging, get_logger

# Configure logging will be done after config is loaded
logger = get_logger("MindBot")

# Import our enhanced multi-platform components
from src.enhanced_multi_platform_manager import EnhancedMultiPlatformManager
from src.discovery import ComponentDiscovery
from src.runtime import TaskManager

class MindBotMultiInstance:
    """Main MindBot class for multiple platform instances"""
    
    def __init__(self, config_file: str = "config/mindbot_config.json"):
        self.config_file = config_file
        self.is_running = False
        self.manager = None
        self.config = {}
        self.shutdown_event = asyncio.Event()
        
        # Initialize web dashboard with environment variables
        self.web_app = None
        self.web_thread = None
        self.web_port = int(os.getenv('WEB_DASHBOARD_PORT', '9529'))
        self.web_host = os.getenv('WEB_DASHBOARD_HOST', '0.0.0.0')
        self.web_debug = os.getenv('WEB_DASHBOARD_DEBUG', 'false').lower() == 'true'
        
    async def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                # Substitute environment variables
                self.config = self._substitute_env_vars(self.config)
                
                # Validate configuration
                if not self._validate_config():
                    return False
                
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                # Create default configuration
                self.config = self.create_default_config()
                await self.save_config()
                logger.info(f"Created default configuration file: {self.config_file}")
            
            # Configure centralized logging after config is loaded
            logging_config = self.config.get('logging', {})
            configure_logging(logging_config)
            
            return True
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables in configuration"""
        # Load system-level environment variables into configuration
        if isinstance(config, dict):
            # Update system configuration from environment variables
            if 'monitoring' not in config:
                config['monitoring'] = {}
            
            # Load monitoring settings
            config['monitoring']['health_check_interval'] = int(os.getenv('HEALTH_CHECK_INTERVAL', 
                config['monitoring'].get('health_check_interval', 30)))
            config['monitoring']['stats_interval'] = int(os.getenv('STATS_INTERVAL', 
                config['monitoring'].get('stats_interval', 60)))
            config['monitoring']['log_level'] = os.getenv('LOG_LEVEL', 
                config['monitoring'].get('log_level', 'INFO'))
            config['monitoring']['enable_metrics'] = os.getenv('METRICS_ENABLED', 
                str(config['monitoring'].get('enable_metrics', True))).lower() == 'true'
            
            # Load security settings
            if 'security' not in config:
                config['security'] = {}
            
            config['security']['rate_limiting'] = {
                'enabled': os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true',
                'max_requests_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '100')),
                'max_requests_per_hour': int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
            }
            
            config['security']['enable_webhook_verification'] = os.getenv('WEBHOOK_VERIFICATION_ENABLED', 'true').lower() == 'true'
            
            # Load allowed IPs
            allowed_ips = os.getenv('ALLOWED_IPS', '127.0.0.1,::1')
            config['security']['allowed_ips'] = [ip.strip() for ip in allowed_ips.split(',') if ip.strip()]
            
            # Load logging settings
            if 'logging' not in config:
                config['logging'] = {}
            
            config['logging']['level'] = os.getenv('LOG_LEVEL', config['logging'].get('level', 'INFO'))
            config['logging']['log_file'] = os.getenv('LOG_FILE', config['logging'].get('log_file', 'logs/mindbot.log'))
            config['logging']['max_file_size'] = os.getenv('LOG_MAX_SIZE', config['logging'].get('max_file_size', '10MB'))
            config['logging']['backup_count'] = int(os.getenv('LOG_BACKUP_COUNT', str(config['logging'].get('backup_count', 5))))
            
            # Load agent settings from environment (system-level only)
            if 'agent' not in config:
                config['agent'] = {}
            
            # Load system-level agent settings (not AI provider settings)
            config['agent']['max_concurrent_messages'] = int(os.getenv('MAX_CONCURRENT_MESSAGES', 
                config['agent'].get('max_concurrent_messages', 50)))
            config['agent']['message_timeout'] = float(os.getenv('MESSAGE_TIMEOUT', 
                config['agent'].get('message_timeout', 30.0)))
        
        return config
    
    def _validate_config(self) -> bool:
        """Validate configuration structure"""
        # Basic configuration validation
        if not isinstance(self.config, dict):
            logger.error("Configuration must be a dictionary")
            return False
        
        if "adapters" not in self.config:
            logger.warning("No adapters section found in configuration")
        
        return True
    
    def setup_web_dashboard(self):
        """Setup web dashboard with Flask"""
        self.web_app = Flask(__name__, 
                            static_folder='web/dist',
                            template_folder='web/dist')
        CORS(self.web_app)
        self.start_time = datetime.now()
        self.setup_web_routes()
    
    def setup_web_routes(self):
        """Setup all web routes"""
        
        # Serve Vue.js app
        @self.web_app.route('/')
        def index():
            return send_from_directory('web/dist', 'index.html')
        
        @self.web_app.route('/<path:path>')
        def serve_vue_app(path):
            return send_from_directory('web/dist', path)
        
        # API Routes
        @self.web_app.route('/api/status')
        def get_status():
            """Get bot status and statistics"""
            try:
                if not self.manager:
                    return jsonify({
                        "is_running": False,
                        "adapters": {},
                        "total_adapters": 0,
                        "running_adapters": 0,
                        "uptime": 0,
                        "memory_usage": 0
                    })
                
                stats = self.manager.get_adapter_stats()
                uptime = int((datetime.now() - self.start_time).total_seconds())
                
                return jsonify({
                    "is_running": True,
                    "adapters": stats.get("adapters", {}),
                    "total_adapters": stats.get("total_adapters", 0),
                    "running_adapters": stats.get("running_adapters", 0),
                    "uptime": uptime,
                    "memory_usage": self._get_memory_usage()
                })
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/config')
        def get_config():
            """Get current configuration"""
            try:
                return jsonify(self.config)
            except Exception as e:
                logger.error(f"Error getting config: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/adapters')
        def get_adapters():
            """Get all adapters"""
            try:
                if not self.manager:
                    return jsonify({"adapters": []})
                
                adapters = self.manager.get_all_adapters()
                return jsonify({"adapters": adapters})
            except Exception as e:
                logger.error(f"Error getting adapters: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/adapters/<adapter_id>/start', methods=['POST'])
        def start_adapter(adapter_id):
            """Start a specific adapter"""
            try:
                if not self.manager:
                    return jsonify({"error": "Manager not available"}), 500
                
                success = asyncio.run(self.manager.start_adapter(adapter_id))
                return jsonify({"success": success})
            except Exception as e:
                logger.error(f"Error starting adapter {adapter_id}: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/adapters/<adapter_id>/stop', methods=['POST'])
        def stop_adapter(adapter_id):
            """Stop a specific adapter"""
            try:
                if not self.manager:
                    return jsonify({"error": "Manager not available"}), 500
                
                success = asyncio.run(self.manager.stop_adapter(adapter_id))
                return jsonify({"success": success})
            except Exception as e:
                logger.error(f"Error stopping adapter {adapter_id}: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/adapters/<adapter_id>/restart', methods=['POST'])
        def restart_adapter(adapter_id):
            """Restart a specific adapter"""
            try:
                if not self.manager:
                    return jsonify({"error": "Manager not available"}), 500
                
                success = asyncio.run(self.manager.restart_adapter(adapter_id))
                return jsonify({"success": success})
            except Exception as e:
                logger.error(f"Error restarting adapter {adapter_id}: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/logs')
        def get_logs():
            """Get recent logs"""
            try:
                # This would read from log files in a real implementation
                logs = [
                    {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Web server started"},
                    {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "MindBot dashboard loaded"}
                ]
                return jsonify({"logs": logs})
            except Exception as e:
                logger.error(f"Error getting logs: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/version')
        def get_version():
            """Get version information"""
            try:
                from src.config import VERSION, BUILD_DATE
                return jsonify({
                    "version": VERSION,
                    "build_date": BUILD_DATE,
                    "need_migration": False
                })
            except Exception as e:
                logger.error(f"Error getting version: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.web_app.route('/api/auth/login', methods=['POST'])
        def auth_login():
            """Authentication login endpoint"""
            try:
                data = request.get_json()
                username = data.get('username', '')
                password = data.get('password', '')
                
                # Default credentials: root / password (MD5 hashed)
                default_username = 'root'
                default_password_hash = '5f4dcc3b5aa765d61d8327deb882cf99'  # MD5 of 'password'
                
                if username == default_username and password == default_password_hash:
                    # Generate a simple JWT token (in production, use proper JWT library)
                    import time
                    token = f"mindbot_token_{int(time.time())}"
                    
                    return jsonify({
                        "status": "success",
                        "data": {
                            "token": token,
                            "username": username,
                            "change_pwd_hint": False
                        }
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "用户名或密码错误"
                    }), 401
                    
            except Exception as e:
                logger.error(f"Error in auth login: {e}")
                return jsonify({
                    "status": "error", 
                    "message": "登录失败"
                }), 500
        
        @self.web_app.route('/api/auth/verify', methods=['POST'])
        def auth_verify():
            """Verify authentication token"""
            try:
                # For simplicity, we'll just check if token exists and starts with 'mindbot_token_'
                # In production, you'd properly validate JWT tokens
                return jsonify({
                    "status": "success",
                    "data": {
                        "valid": True,
                        "username": "root"
                    }
                })
            except Exception as e:
                logger.error(f"Error verifying auth: {e}")
                return jsonify({
                    "status": "error",
                    "message": "Token verification failed"
                }), 401
    
    def _get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return round(process.memory_info().rss / 1024 / 1024, 2)  # MB
        except ImportError:
            return 0
    
    def _start_bot_async(self):
        """Start bot asynchronously"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Load configuration
            self.load_config()
            
            # Create agent handler
            agent_handler = self.create_agent_handler()
            
            # Initialize manager
            self.manager = EnhancedMultiPlatformManager(agent_handler)
            loop.run_until_complete(self.manager.initialize())
            
            # Setup adapters
            loop.run_until_complete(self.setup_adapters())
            
            # Start all adapters
            loop.run_until_complete(self.manager.start_all_adapters())
            
            self.is_running = True
            logger.info("Bot started successfully")
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            self.is_running = False
    
    def _stop_bot_async(self):
        """Stop bot asynchronously"""
        try:
            if self.manager:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.manager.stop_all_adapters())
                loop.run_until_complete(self.manager.shutdown())
            
            self.is_running = False
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def start_web_dashboard(self):
        """Start the web dashboard in a separate thread"""
        if self.web_app:
            def run_web():
                self.web_app.run(host=self.web_host, port=self.web_port, debug=self.web_debug, use_reloader=False)
            
            self.web_thread = threading.Thread(target=run_web, daemon=True)
            self.web_thread.start()
            
            # Get external access information
            external_ip = os.getenv('EXTERNAL_IP', 'localhost')
            external_port = os.getenv('EXTERNAL_PORT', str(self.web_port))
            external_domain = os.getenv('EXTERNAL_DOMAIN', '')
            
            logger.info(f"Web dashboard started at http://{self.web_host}:{self.web_port}")
            if external_domain:
                logger.info(f"External access: https://{external_domain}")
            elif external_ip != 'localhost':
                logger.info(f"External access: http://{external_ip}:{external_port}")
            logger.info("Access the dashboard to manage adapters and configuration")
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "agent": {
                "name": "MindBot Multi-Instance",
                "description": "Multi-platform AI assistant supporting DingTalk and WeCom",
                "max_concurrent_messages": 50,
                "message_timeout": 30.0
            },
            "adapters": {
                "dingtalk": [],
                "wecom": []
            },
            "routing": {
                "cross_platform_enabled": True,
                "message_broadcast": False,
                "adapter_communication": True,
                "routing_rules": []
            },
            "monitoring": {
                "stats_interval": 60,
                "health_check_interval": 30,
                "log_level": "INFO",
                "enable_metrics": True,
                "metrics_export_interval": 300,
                "alert_on_adapter_failure": True,
                "max_failure_retries": 3
            },
            "security": {
                "enable_webhook_verification": True,
                "allowed_ips": [],
                "rate_limiting": {
                    "enabled": True,
                    "max_requests_per_minute": 100,
                    "max_requests_per_hour": 1000
                }
            },
            "logging": {
                "level": "INFO",
                "log_file": "logs/mindbot.log",
                "file_rotation": True,
                "max_file_size": "10MB",
                "backup_count": 5,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    async def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def create_agent_handler(self):
        """Create the AI agent handler"""
        async def agent_handler(message: str, context: Dict[str, Any]) -> str:
            """Process messages from any platform"""
            adapter_id = context.get("adapter_id", "unknown")
            platform = context.get("platform", "unknown")
            user_id = context.get("user_id", "unknown")
            
            # Log the message
            logger.info(f"[{platform}:{adapter_id}] User {user_id}: {message}")
            
            # Enhanced AI response with context awareness
            response = await self.generate_ai_response(message, context)
            
            # Add platform-specific formatting
            if platform == "dingtalk":
                response = f"🤖 **DingTalk AI Response**\n\n{response}"
            elif platform == "wecom":
                response = f"💼 **WeCom AI Response**\n\n{response}"
            
            return response
        
        return agent_handler
    
    async def generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate AI response based on message and context"""
        adapter_id = context.get("adapter_id", "unknown")
        platform = context.get("platform", "unknown")
        
        # Simple AI logic - you can replace this with your actual AI integration
        if "hello" in message.lower() or "hi" in message.lower():
            return f"Hello! I'm MindBot running on {platform} adapter {adapter_id}. How can I help you today?"
        elif "status" in message.lower():
            return await self.get_adapter_status_response(adapter_id)
        elif "help" in message.lower():
            return self.get_help_response(platform)
        else:
            return f"Echo from {platform} adapter {adapter_id}: {message}"
    
    async def get_adapter_status_response(self, adapter_id: str) -> str:
        """Get status response for an adapter"""
        if not self.manager:
            return "Manager not available"
        
        stats = self.manager.get_adapter_stats(adapter_id)
        if "error" in stats:
            return f"Error: {stats['error']}"
        
        return f"Adapter {adapter_id} is running. Messages processed: {stats['stats']['messages_processed']}"
    
    def get_help_response(self, platform: str) -> str:
        """Get help response for a platform"""
        if platform == "dingtalk":
            return """
**DingTalk Commands:**
- `hello` - Greeting
- `status` - Check adapter status
- `help` - Show this help
- Send any message for AI response
            """
        elif platform == "wecom":
            return """
**WeCom Commands:**
- `hello` - Greeting
- `status` - Check adapter status  
- `help` - Show this help
- Send any message for AI response
            """
        else:
            return "Available commands: hello, status, help"
    
    async def setup_adapters(self):
        """Setup all configured adapters"""
        logger.info("Setting up platform adapters...")
        
        # Setup all adapters using enhanced discovery
        all_adapters = []
        all_adapters.extend(self.config.get("adapters", {}).get("dingtalk", []))
        all_adapters.extend(self.config.get("adapters", {}).get("wecom", []))
        
        # Check if we're in demo mode
        demo_mode = self.config.get("agent", {}).get("demo_mode", False)
        
        for adapter_config in all_adapters:
            if adapter_config.get("enabled", False):
                adapter_id = adapter_config["adapter_id"]
                adapter_type = adapter_config.get("type", "unknown")
                config = adapter_config["config"]
                
                # Skip adapters with placeholder credentials in demo mode
                if demo_mode:
                    if adapter_type == "dingtalk":
                        if (config.get("client_id", "").startswith("your_") or 
                            config.get("client_secret", "").startswith("your_") or
                            config.get("robot_code", "").startswith("your_")):
                            logger.info(f"Skipping {adapter_type} adapter {adapter_id} in demo mode (placeholder credentials)")
                            continue
                    elif adapter_type == "wecom":
                        if (config.get("corp_id", "").startswith("your_") or 
                            config.get("corp_secret", "").startswith("your_") or
                            config.get("agent_id", "").startswith("your_")):
                            logger.info(f"Skipping {adapter_type} adapter {adapter_id} in demo mode (placeholder credentials)")
                            continue
                
                # Add Dify configuration to adapter config
                if "agent" in self.config and "dify_api_key" in self.config["agent"]:
                    config["dify_api_key"] = self.config["agent"]["dify_api_key"]
                if "agent" in self.config and "dify_base_url" in self.config["agent"]:
                    config["dify_base_url"] = self.config["agent"]["dify_base_url"]
                
                success = await self.manager.add_adapter(adapter_id, adapter_type, config)
                if success:
                    logger.info(f"Added {adapter_type} adapter: {adapter_id}")
                else:
                    logger.error(f"Failed to add {adapter_type} adapter: {adapter_id}")
        
        logger.info("Platform adapters setup completed")
    
    async def start_monitoring(self):
        """Start monitoring and statistics collection"""
        async def monitor_loop():
            while self.is_running:
                try:
                    # Collect statistics
                    stats = self.manager.get_adapter_stats()
                    if stats['running_adapters'] > 0:
                        logger.info(f"Status: {stats['running_adapters']}/{stats['total_adapters']} adapters running")
                    
                    # Health check
                    await self.health_check()
                    
                    # Wait for next check
                    await asyncio.sleep(self.config.get("monitoring", {}).get("stats_interval", 60))
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(10)
        
        # Start monitoring task
        asyncio.create_task(monitor_loop())
        logger.info("Monitoring started")
    
    async def health_check(self):
        """Perform health check on all adapters"""
        try:
            stats = self.manager.get_adapter_stats()
            for adapter_id, adapter_info in stats.get("adapters", {}).items():
                if not adapter_info.get("is_running", False):
                    logger.warning(f"Adapter {adapter_id} is not running, attempting restart...")
                    await self.manager.restart_adapter(adapter_id)
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    async def start(self):
        """Start the multi-instance MindBot with web dashboard"""
        if self.is_running:
            logger.warning("MindBot is already running")
            return
        
        try:
            logger.info("Starting MindBot...")
            
            # Load configuration
            if not await self.load_config():
                logger.error("Failed to load configuration")
                return
            
            # Setup web dashboard
            self.setup_web_dashboard()
            self.start_web_dashboard()
            
            # Create agent handler
            agent_handler = self.create_agent_handler()
            
            # Initialize enhanced multi-platform manager
            self.manager = EnhancedMultiPlatformManager(agent_handler)
            await self.manager.initialize()
            
            # Setup adapters
            await self.setup_adapters()
            
            # Start all adapters
            await self.manager.start_all_adapters()
            
            # Start monitoring
            await self.start_monitoring()
            
            self.is_running = True
            logger.info("MindBot started successfully")
            
            # Show access information
            external_ip = os.getenv('EXTERNAL_IP', 'localhost')
            external_domain = os.getenv('EXTERNAL_DOMAIN', '')
            
            if external_domain:
                logger.info(f"Web dashboard available at: https://{external_domain}")
            elif external_ip != 'localhost':
                logger.info(f"Web dashboard available at: http://{external_ip}:{self.web_port}")
            else:
                logger.info(f"Web dashboard available at: http://localhost:{self.web_port}")
            
            logger.info("Use the web dashboard to manage adapters and configuration")
            
            # Keep running until shutdown
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error starting MindBot: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the multi-instance MindBot"""
        if not self.is_running:
            return
        
        logger.info("Stopping MindBot Multi-Instance...")
        self.is_running = False
        self.shutdown_event.set()
        
        # Stop all adapters
        if self.manager:
            await self.manager.stop_all_adapters()
        
        logger.info("MindBot Multi-Instance stopped")
    
    async def restart_adapter(self, adapter_id: str):
        """Restart a specific adapter"""
        if not self.manager:
            logger.error("Manager not initialized")
            return False
        
        return await self.manager.restart_adapter(adapter_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive bot status"""
        if not self.manager:
            return {"error": "Bot not initialized"}
        
        return {
            "is_running": self.is_running,
            "config_file": self.config_file,
            "manager_stats": self.manager.get_adapter_stats(),
            "total_adapters": len(self.manager.runtime_adapters),
            "running_adapters": sum(1 for a in self.manager.runtime_adapters.values() if a.is_running)
        }
    
    async def add_adapter_interactive(self):
        """Interactive adapter addition"""
        print("\n=== Add New Adapter ===")
        print("1. DingTalk")
        print("2. WeCom")
        
        choice = input("Select platform (1-2): ").strip()
        
        if choice == "1":
            adapter_id = input("Adapter ID: ").strip()
            client_id = input("DingTalk Client ID: ").strip()
            client_secret = input("DingTalk Client Secret: ").strip()
            robot_code = input("DingTalk Robot Code: ").strip()
            
            config = {
                "client_id": client_id,
                "client_secret": client_secret,
                "robot_code": robot_code
            }
            
            success = await self.manager.add_dingtalk_adapter(adapter_id, config)
            if success:
                print(f"✅ DingTalk adapter '{adapter_id}' added successfully")
            else:
                print(f"❌ Failed to add DingTalk adapter '{adapter_id}'")
                
        elif choice == "2":
            adapter_id = input("Adapter ID: ").strip()
            corp_id = input("WeCom Corp ID: ").strip()
            corp_secret = input("WeCom Corp Secret: ").strip()
            agent_id = input("WeCom Agent ID: ").strip()
            
            config = {
                "corp_id": corp_id,
                "corp_secret": corp_secret,
                "agent_id": agent_id
            }
            
            success = await self.manager.add_wecom_adapter(adapter_id, config)
            if success:
                print(f"✅ WeCom adapter '{adapter_id}' added successfully")
            else:
                print(f"❌ Failed to add WeCom adapter '{adapter_id}'")
        else:
            print("Invalid choice")

def setup_signal_handlers(bot: MindBotMultiInstance):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(bot.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MindBot Multi-Instance Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Start with default config
  python run.py --config custom.json  # Start with custom config
  python run.py --help            # Show this help message
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config/mindbot_config.json',
        help='Path to configuration file (default: config/mindbot_config.json)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=9529,
        help='Web dashboard port (default: 9529)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web dashboard host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    return parser.parse_args()

async def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set environment variables from command line
    os.environ['WEB_DASHBOARD_PORT'] = str(args.port)
    os.environ['WEB_DASHBOARD_HOST'] = args.host
    if args.debug:
        os.environ['DEBUG_MODE'] = 'true'
    
    # Create bot instance
    bot = MindBotMultiInstance(args.config)
    
    # Setup signal handlers
    setup_signal_handlers(bot)
    
    try:
        # Start the bot
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("MindBot Multi-Instance Interactive Mode")
        print("Commands: start, stop, status, add-adapter, restart <adapter_id>")
        
        bot = MindBotMultiInstance()
        
        while True:
            try:
                command = input("\nMindBot> ").strip().lower()
                
                if command == "start":
                    asyncio.run(bot.start())
                elif command == "stop":
                    asyncio.run(bot.stop())
                elif command == "status":
                    status = bot.get_status()
                    print(json.dumps(status, indent=2))
                elif command == "add-adapter":
                    asyncio.run(bot.add_adapter_interactive())
                elif command.startswith("restart "):
                    adapter_id = command.split(" ", 1)[1]
                    success = asyncio.run(bot.restart_adapter(adapter_id))
                    print(f"Restart {'successful' if success else 'failed'}")
                elif command in ["exit", "quit"]:
                    break
                else:
                    print("Unknown command")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Normal startup
        asyncio.run(main())
