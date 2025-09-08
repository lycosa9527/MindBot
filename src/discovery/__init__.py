"""
Component Discovery System
Inspired by LangBot's sophisticated component discovery
"""

from .engine import ComponentDiscovery, AdapterManifest, AdapterExecution
from .registry import AdapterRegistry

__all__ = [
    "ComponentDiscovery",
    "AdapterManifest", 
    "AdapterExecution",
    "AdapterRegistry"
]
