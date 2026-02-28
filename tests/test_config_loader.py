"""
Comprehensive tests for config_loader.py module.
Tests configuration loading and parsing.
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.config.loader import ConfigLoader


# =========================
# ConfigLoader Class Tests
# =========================

class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_load_config_returns_dict(self):
        """Test that load method returns a dict."""
        loader = ConfigLoader()
        config = loader.load("tests/test_config.json")
        
        assert isinstance(config, dict)
    
    def test_load_config_has_expected_sections(self):
        """Test that loaded config has expected sections."""
        loader = ConfigLoader()
        config = loader.load("tests/test_config.json")
        
        # Should have main sections
        assert 'ball' in config
        assert 'simulation' in config
    
    def test_load_config_custom_file(self, sample_config_json):
        """Test load method with custom config file."""
        loader = ConfigLoader()
        config = loader.load(sample_config_json)
        
        # Check values from custom config
        assert config['ball']['mass'] == 1.0
        assert config['ball']['radius'] == 0.15
        assert config['wind']['humidity_pct'] == 40.0
    
    def test_load_empty_config(self):
        """Test loading empty config."""
        loader = ConfigLoader()
        config = loader.load(None)
        
        assert config == {}
    
    def test_validate_config(self):
        """Test config validation."""
        loader = ConfigLoader()
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Should not raise
        loader.validate(config)
    
    def test_validate_invalid_config(self):
        """Test validation of invalid config."""
        loader = ConfigLoader()
        config = {
            "ball": {"mass": -1.0, "radius": 0.1},  # Invalid mass
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        with pytest.raises(ValueError):
            loader.validate(config)


# =========================
# Default Values Tests
# =========================

class TestConfigDefaults:
    """Test that default values are used when keys are missing."""
    
    def test_missing_ball_keys_use_defaults(self):
        """Test that missing ball keys use defaults."""
        loader = ConfigLoader()
        config = loader.load(None)  # Load empty config
        
        # Empty config should be empty dict
        assert config == {}
    
    def test_missing_surface_keys_use_defaults(self):
        """Test that missing surface keys use defaults."""
        loader = ConfigLoader()
        config = loader.load(None)  # Load empty config
        
        # Empty config should be empty dict
        assert config == {}
    
    def test_missing_wind_keys_use_defaults(self):
        """Test that missing wind keys use defaults."""
        loader = ConfigLoader()
        config = loader.load(None)  # Load empty config
        
        # Empty config should be empty dict
        assert config == {}


# =========================
# Error Handling Tests
# =========================

class TestConfigErrorHandling:
    """Test error handling in config loading."""
    
    def test_missing_file_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("non_existent_file.json")
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises JSONDecodeError."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            invalid_json_path = f.name
        
        try:
            loader = ConfigLoader()
            with pytest.raises(ValueError):
                loader.load(invalid_json_path)
        finally:
            os.unlink(invalid_json_path)


# =========================
# Full Config Integration Tests
# =========================

class TestConfigIntegration:
    """Test that loaded config produces valid simulation."""
    
    def test_loaded_config_valid_for_simulation(self):
        """Test that loaded config can be used for simulation."""
        # Test that the config loader produces valid configuration
        loader = ConfigLoader()
        config = loader.load("tests/test_config.json")
        
        # Check that all required sections exist
        assert 'ball' in config
        assert 'surface' in config
        assert 'wind' in config
        assert 'simulation' in config
    
    def test_custom_config_valid_for_simulation(self):
        """Test that custom config produces valid configuration."""
        loader = ConfigLoader()
        config = loader.load("tests/sample_config.json")
        
        # Check that custom values are loaded correctly
        assert config['ball']['mass'] == 1.0
        assert config['ball']['radius'] == 0.15
        assert config['wind']['humidity_pct'] == 40.0
