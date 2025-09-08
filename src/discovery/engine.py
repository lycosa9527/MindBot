"""
Component Discovery Engine
Based on LangBot's component discovery system
"""

import os
import yaml
import asyncio
import importlib
from typing import Dict, List, Type, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field

class AdapterExecution(BaseModel):
    """Adapter execution configuration"""
    python_path: str = Field(..., description="Python module path")
    class_name: str = Field(..., description="Adapter class name")
    
class AdapterManifest(BaseModel):
    """Adapter manifest metadata"""
    api_version: str = Field(default="v1", description="API version")
    kind: str = Field(default="MessagePlatformAdapter", description="Component kind")
    
    metadata: Dict[str, Any] = Field(..., description="Adapter metadata")
    spec: Dict[str, Any] = Field(..., description="Adapter specification")
    execution: AdapterExecution = Field(..., description="Execution configuration")
    
    @property
    def name(self) -> str:
        return self.metadata.get("name", "")
    
    @property
    def platform_type(self) -> str:
        return self.metadata.get("name", "")
    
    @property
    def config_schema(self) -> List[Dict[str, Any]]:
        return self.spec.get("config", [])
    
    @property
    def capabilities(self) -> List[str]:
        return self.spec.get("capabilities", [])

class ComponentDiscovery:
    """Component discovery engine"""
    
    def __init__(self, adapters_dir: str = "adapters"):
        self.adapters_dir = Path(adapters_dir)
        self.manifests: Dict[str, AdapterManifest] = {}
        self.adapter_classes: Dict[str, Type] = {}
        
    async def discover_adapters(self) -> Dict[str, AdapterManifest]:
        """Discover all available adapters"""
        if not self.adapters_dir.exists():
            return {}
        
        manifests = {}
        
        # Scan for adapter directories
        for adapter_dir in self.adapters_dir.iterdir():
            if not adapter_dir.is_dir():
                continue
                
            manifest_file = adapter_dir / "manifest.yaml"
            if not manifest_file.exists():
                continue
                
            try:
                # Load manifest
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    manifest_data = yaml.safe_load(f)
                
                manifest = AdapterManifest(**manifest_data)
                manifests[manifest.name] = manifest
                
            except Exception as e:
                print(f"Error loading manifest for {adapter_dir.name}: {e}")
                continue
        
        self.manifests = manifests
        return manifests
    
    async def load_adapter_class(self, adapter_name: str) -> Optional[Type]:
        """Load adapter class dynamically"""
        if adapter_name in self.adapter_classes:
            return self.adapter_classes[adapter_name]
        
        manifest = self.manifests.get(adapter_name)
        if not manifest:
            return None
        
        try:
            # Import the module
            module_path = manifest.execution.python_path
            if module_path.startswith('./'):
                module_path = module_path[2:]
            
            module = importlib.import_module(module_path)
            
            # Get the class
            adapter_class = getattr(module, manifest.execution.class_name)
            self.adapter_classes[adapter_name] = adapter_class
            
            return adapter_class
            
        except Exception as e:
            print(f"Error loading adapter class {adapter_name}: {e}")
            return None
    
    def get_manifest(self, adapter_name: str) -> Optional[AdapterManifest]:
        """Get adapter manifest by name"""
        return self.manifests.get(adapter_name)
    
    def get_available_adapters(self) -> List[str]:
        """Get list of available adapter names"""
        return list(self.manifests.keys())
    
    def validate_config(self, adapter_name: str, config: Dict[str, Any]) -> bool:
        """Validate configuration against adapter schema"""
        manifest = self.get_manifest(adapter_name)
        if not manifest:
            return False
        
        config_schema = manifest.config_schema
        required_fields = [field["name"] for field in config_schema if field.get("required", False)]
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                return False
        
        return True
