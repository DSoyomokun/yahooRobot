"""
Configuration loader for robot settings
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and manage robot configuration"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize config loader
        
        Args:
            config_dir: Directory containing config files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Any] = {}
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON config file"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        self.configs[filename] = config
        return config
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML config file"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        self.configs[filename] = config
        return config
    
    def get(self, filename: str) -> Dict[str, Any]:
        """Get loaded config by filename"""
        return self.configs.get(filename, {})

