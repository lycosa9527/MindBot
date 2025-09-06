#!/usr/bin/env python3
"""
MindBot Startup Script
Runs both the DingTalk bot and Flask web interface simultaneously
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

def run_dingtalk_bot():
    """Run the DingTalk bot in a separate process"""
    print("🤖 Starting DingTalk Bot...")
    try:
        subprocess.run([sys.executable, "run.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ DingTalk Bot failed: {e}")
    except KeyboardInterrupt:
        print("🛑 DingTalk Bot stopped")

def run_flask_app():
    """Run the Flask web interface in a separate process"""
    print("🌐 Starting Flask Web Interface...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Flask App failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Flask App stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down MindBot...")
    sys.exit(0)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 Starting MindBot - DingTalk Bot + Web Dashboard")
    print("=" * 60)
    print("📱 DingTalk Bot: Handles messages")
    print("🌐 Web Dashboard: http://localhost:9529")
    print("=" * 60)
    print("Press Ctrl+C to stop both services")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start both processes in separate threads
    bot_thread = threading.Thread(target=run_dingtalk_bot, daemon=True)
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    
    try:
        # Start both threads
        bot_thread.start()
        time.sleep(2)  # Give bot time to start
        flask_thread.start()
        
        # Wait for both threads to complete
        bot_thread.join()
        flask_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MindBot...")
        sys.exit(0)

if __name__ == "__main__":
    main()
