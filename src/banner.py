#!/usr/bin/env python3
"""
MindBot Banner Module
Displays application banner and startup information
"""

import logging

logger = logging.getLogger(__name__)

def display_banner():
    """
    Display the MindBot banner with author information.
    Uses logger for consistency with the rest of the application.
    """
    banner = """
================================================================================
    ███╗   ███╗██╗███╗   ██╗██████╗ ███╗   ███╗ █████╗ ████████╗███████╗
    ████╗ ████║██║████╗  ██║██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
    ██╔████╔██║██║██╔██╗ ██║██║  ██║██╔████╔██║███████║   ██║   █████╗  
    ██║╚██╔╝██║██║██║╚██╗██║██║  ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
    ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
================================================================================
                              DingTalk Stream Bot
                              Powered by LangChain
                              Integrated with Dify API
================================================================================
                              Author: lyc9527
                              Made by MindSpring Team
================================================================================
"""
    # Use logger instead of print for consistency
    logger.info("MindBot banner displayed")
    # Still print the banner for visual effect, but also log it
    print(banner)

if __name__ == "__main__":
    display_banner() 