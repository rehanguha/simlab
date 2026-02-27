"""
Comprehensive tests for config_loader.py module.
Tests configuration loading and parsing.
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind
from config_loader import ConfigLoader, load_config


# =========================
# ConfigLoader Class Tests
# =========================

class TestConfigLoaderInit:
    """Test ConfigLoader initialization."""
    
    def test_init_with_default_path(self):
        """Test initialization with default config path."""
        # This requires config.json to exist in project root
        loader = ConfigLoader("config.json")
        assert loader.config_path == "config.json"
    
    def test_init_loads_config(self):
        """Test that initialization loads the config."""
        loader = ConfigLoader("config.json")
        assert isinstance(loader.config, dict)
    
    def test_config_has_expected_sections(self):
        """Test that config has expected sections."""
        loader = ConfigLoader("config.json")
        
        # Should have main sections
        assert 'ball' in loader.config or 'simulation' in loader.config


class TestConfigLoaderGetParams:
    """Test get_params method."""
    
    def test_get_params_returns_params_object(self):
        """Test that get_params returns Params object."""
        loader = ConfigLoader("config.json")
        params = loader.get_params()
        
        assert isinstance(params, Params)
    
    def test_get_params_has_ball_properties(self):
        """Test that params has ball properties."""
        loader = ConfigLoader("config.json")
        params = loader.get_params()
        
        assert hasattr(params, 'mass')
        assert hasattr(params, 'radius')
        assert hasattr(params, 'v0')
    
    def test_get_params_has_position_properties(self):
        """Test that params has position properties."""
        loader = ConfigLoader("config.json")
        params = loader.get_params()
        
        assert hasattr(params, 'x0')
        assert hasattr(params, 'y0')
        assert hasattr(params, 'z0')
    
    def test_get_params_has_simulation_properties(self):
        """Test that params has simulation properties."""
        loader = ConfigLoader("config.json")
        params = loader.get_params()
        
        assert hasattr(params, 'dt')
        assert hasattr(params, 't_max')
        assert hasattr(params, 'g')
    
    def test_get_params_custom_config(self, sample_config_json):
        """Test get_params with custom config file."""
        loader = ConfigLoader(sample_config_json)
        params = loader.get_params()
        
        # Check values from custom config
        assert params.mass == 1.0
        assert params.radius == 0.15
        assert params.v0 == 15.0


class TestConfigLoaderGetSurface:
    """Test get_surface method."""
    
    def test_get_surface_returns_surface_object(self):
        """Test that get_surface returns Surface object."""
        loader = ConfigLoader("config.json")
        surface = loader.get_surface()
        
        assert isinstance(surface, Surface)
    
    def test_get_surface_has_elasticity(self):
        """Test that surface has elasticity properties."""
        loader = ConfigLoader("config.json")
        surface = loader.get_surface()
        
        assert hasattr(surface, 'elasticity_base')
        assert hasattr(surface, 'elasticity_drop')
    
    def test_get_surface_has_friction(self):
        """Test that surface has friction properties."""
        loader = ConfigLoader("config.json")
        surface = loader.get_surface()
        
        assert hasattr(surface, 'friction_mu_s')
        assert hasattr(surface, 'friction_mu_k')
    
    def test_get_surface_custom_config(self, sample_config_json):
        """Test get_surface with custom config file."""
        loader = ConfigLoader(sample_config_json)
        surface = loader.get_surface()
        
        assert surface.elasticity_base == 0.8
        assert surface.friction_mu_s == 0.6


class TestConfigLoaderGetWind:
    """Test get_wind method."""
    
    def test_get_wind_returns_wind_object(self):
        """Test that get_wind returns Wind object."""
        loader = ConfigLoader("config.json")
        wind = loader.get_wind()
        
        assert isinstance(wind, Wind)
    
    def test_get_wind_has_speed_properties(self):
        """Test that wind has speed properties."""
        loader = ConfigLoader("config.json")
        wind = loader.get_wind()
        
        assert hasattr(wind, 'ref_speed')
        assert hasattr(wind, 'ref_height')
    
    def test_get_wind_has_gust_properties(self):
        """Test that wind has gust properties."""
        loader = ConfigLoader("config.json")
        wind = loader.get_wind()
        
        assert hasattr(wind, 'gust_tau')
        assert hasattr(wind, 'gust_sigma')
    
    def test_get_wind_custom_config(self, sample_config_json):
        """Test get_wind with custom config file."""
        loader = ConfigLoader(sample_config_json)
        wind = loader.get_wind()
        
        assert wind.ref_speed == 3.0
        assert wind.direction_deg == 90.0
        assert wind.humidity_pct == 40.0


class TestConfigLoaderGetOutputSettings:
    """Test get_output_settings method."""
    
    def test_get_output_settings_returns_dict(self):
        """Test that get_output_settings returns dict."""
        loader = ConfigLoader("config.json")
        output = loader.get_output_settings()
        
        assert isinstance(output, dict)
    
    def test_get_output_settings_has_required_keys(self):
        """Test that output settings has required keys."""
        loader = ConfigLoader("config.json")
        output = loader.get_output_settings()
        
        assert 'run_name' in output
        assert 'output_dir' in output
    
    def test_get_output_settings_custom_config(self, sample_config_json):
        """Test get_output_settings with custom config file."""
        loader = ConfigLoader(sample_config_json)
        output = loader.get_output_settings()
        
        assert output['run_name'] == 'test_run'


# =========================
# load_config Function Tests
# =========================

class TestLoadConfigFunction:
    """Test load_config convenience function."""
    
    def test_load_config_returns_tuple(self):
        """Test that load_config returns a tuple."""
        result = load_config("config.json")
        
        assert isinstance(result, tuple)
        assert len(result) == 4
    
    def test_load_config_returns_correct_types(self):
        """Test that load_config returns correct types."""
        params, surface, wind, output = load_config("config.json")
        
        assert isinstance(params, Params)
        assert isinstance(surface, Surface)
        assert isinstance(wind, Wind)
        assert isinstance(output, dict)
    
    def test_load_config_custom_file(self, sample_config_json):
        """Test load_config with custom config file."""
        params, surface, wind, output = load_config(sample_config_json)
        
        assert params.mass == 1.0
        assert surface.elasticity_base == 0.8
        assert wind.ref_speed == 3.0
        assert output['run_name'] == 'test_run'


# =========================
# Default Values Tests
# =========================

class TestConfigDefaults:
    """Test that default values are used when keys are missing."""
    
    def test_missing_ball_keys_use_defaults(self, temp_output_dir):
        """Test that missing ball keys use defaults."""
        minimal_config = {"simulation": {}, "position": {"z0": 10.0}}
        config_path = os.path.join(temp_output_dir, "minimal.json")
        
        with open(config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        loader = ConfigLoader(config_path)
        params = loader.get_params()
        
        # Should use default values
        assert params.mass == 0.5  # Default
        assert params.radius == 0.1  # Default
    
    def test_missing_surface_keys_use_defaults(self, temp_output_dir):
        """Test that missing surface keys use defaults."""
        minimal_config = {}
        config_path = os.path.join(temp_output_dir, "minimal.json")
        
        with open(config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        loader = ConfigLoader(config_path)
        surface = loader.get_surface()
        
        # Should use default values
        assert surface.elasticity_base == 0.70  # Default
        assert surface.friction_mu_s == 0.50  # Default
    
    def test_missing_wind_keys_use_defaults(self, temp_output_dir):
        """Test that missing wind keys use defaults."""
        minimal_config = {}
        config_path = os.path.join(temp_output_dir, "minimal.json")
        
        with open(config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        loader = ConfigLoader(config_path)
        wind = loader.get_wind()
        
        # Should use default values
        assert wind.ref_speed == 2.0  # Default
        assert wind.humidity_pct == 50.0  # Default


# =========================
# Error Handling Tests
# =========================

class TestConfigErrorHandling:
    """Test error handling in config loading."""
    
    def test_missing_file_raises_error(self, temp_output_dir):
        """Test that missing file raises FileNotFoundError."""
        non_existent = os.path.join(temp_output_dir, "does_not_exist.json")
        
        with pytest.raises(FileNotFoundError):
            ConfigLoader(non_existent)
    
    def test_invalid_json_raises_error(self, temp_output_dir):
        """Test that invalid JSON raises JSONDecodeError."""
        invalid_json_path = os.path.join(temp_output_dir, "invalid.json")
        
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            ConfigLoader(invalid_json_path)


# =========================
# Spin Axis Tests
# =========================

class TestSpinAxisConfig:
    """Test spin axis configuration parsing."""
    
    def test_spin_axis_from_config(self, sample_config_json):
        """Test that spin axis is correctly parsed from config."""
        loader = ConfigLoader(sample_config_json)
        params = loader.get_params()
        
        # From sample config: spin_axis = [1.0, 0.0, 0.0]
        assert params.spin_axis == (1.0, 0.0, 0.0)
    
    def test_default_spin_axis(self):
        """Test default spin axis from config."""
        loader = ConfigLoader("config.json")
        params = loader.get_params()
        
        # Should be a tuple of 3 floats
        assert isinstance(params.spin_axis, tuple)
        assert len(params.spin_axis) == 3


# =========================
# Full Config Integration Tests
# =========================

class TestConfigIntegration:
    """Test that loaded config produces valid simulation."""
    
    def test_loaded_params_valid_for_simulation(self):
        """Test that loaded params can be used for simulation."""
        from simulation import simulate_drop
        
        params, surface, wind, _ = load_config("config.json")
        
        # Should run without error
        result = simulate_drop(params, surface, wind)
        
        assert result.stability_ok is True
    
    def test_custom_config_valid_for_simulation(self, sample_config_json):
        """Test that custom config produces valid simulation."""
        from simulation import simulate_drop
        
        params, surface, wind, _ = load_config(sample_config_json)
        
        # Should run without error
        result = simulate_drop(params, surface, wind)
        
        assert result.stability_ok is True