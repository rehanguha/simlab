"""
Configuration loader.

Handles loading and validation of configuration files in JSON and YAML format.
"""

import json
import yaml
import os
from typing import Dict, Any, Union
from pathlib import Path

class ConfigLoader:
    """Configuration loader for SimLab."""
    
    def load(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        if config_path is None:
            # Return empty config when no path is provided
            return {}
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        config_path = Path(config_path)
        
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            return self._load_yaml(config_path)
        elif config_path.suffix.lower() == '.json':
            return self._load_json(config_path)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    def _load_json(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}") from e
    
    def _load_yaml(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}") from e
    
    def validate(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure and values.
        
        Args:
            config (dict): Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        # For backward compatibility, only validate if we have a config file
        # The new config format is more flexible and doesn't require strict validation
        if not config:
            return
            
        # Check for new config format (scenario-based)
        if 'scenario' in config:
            # Validate new format
            if 'ball' not in config:
                raise ValueError("Missing required configuration section: ball")
            if 'position' not in config:
                raise ValueError("Missing required configuration section: position")
            if 'wind' not in config:
                raise ValueError("Missing required configuration section: wind")
            if 'simulation' not in config:
                raise ValueError("Missing required configuration section: simulation")
            
            # Validate ball properties
            ball_config = config['ball']
            if 'mass' not in ball_config or ball_config['mass'] <= 0:
                raise ValueError("Invalid ball mass")
            
            if 'radius' not in ball_config or ball_config['radius'] <= 0:
                raise ValueError("Invalid ball radius")
            
            # Validate position properties
            position_config = config['position']
            if 'z0' not in position_config or position_config['z0'] <= 0:
                raise ValueError("Invalid initial height")
        else:
            # Check for old config format
            required_sections = ['ball', 'position', 'surface', 'wind', 'simulation', 'output']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required configuration section: {section}")
            
            # Validate ball properties
            ball_config = config['ball']
            if 'mass' not in ball_config or ball_config['mass'] <= 0:
                raise ValueError("Invalid ball mass")
            
            if 'radius' not in ball_config or ball_config['radius'] <= 0:
                raise ValueError("Invalid ball radius")
            
            # Validate position properties
            position_config = config['position']
            if 'z0' not in position_config or position_config['z0'] <= 0:
                raise ValueError("Invalid initial height")
            
            # Validate optional environment section
            if 'environment' in config:
                env = config['environment']
                if 'gravity' in env and env['gravity'] <= 0:
                    raise ValueError("Invalid gravity value")
                if 'temperature' in env and env['temperature'] <= 0:
                    raise ValueError("Invalid temperature value")
            
            # Validate optional simulation section
            if 'simulation' in config:
                sim = config['simulation']
                if 'time_step' in sim and sim['time_step'] <= 0:
                    raise ValueError("Invalid time step")
                if 'max_time' in sim and sim['max_time'] <= 0:
                    raise ValueError("Invalid max time")
    
    def merge_config(self, base_config: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration overrides into base configuration.
        
        Args:
            base_config (dict): Base configuration
            overrides (dict): Configuration overrides
            
        Returns:
            dict: Merged configuration
        """
        merged = base_config.copy()
        
        for key, value in overrides.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_config(merged[key], value)
            else:
                merged[key] = value
        
        return merged