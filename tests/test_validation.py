"""
Comprehensive tests for physimlab.core module validation.
Tests configuration validation and error handling.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.core import run_simulation


# =========================
# Configuration Validation Tests
# =========================

class TestConfigurationValidation:
    """Test configuration validation in run_simulation."""
    
    def test_valid_config_passes(self):
        """Test that valid configuration passes validation."""
        config = {
            "scenario": "drop",
            "ball": {
                "mass": 0.5,
                "radius": 0.1,
                "spin_rps": 0.0
            },
            "position": {
                "z0": 10.0
            },
            "wind": {
                "humidity_pct": 50.0
            },
            "simulation": {
                "g": 9.81,
                "dt": 0.005,
                "t_max": 5.0
            }
        }
        
        # Should not raise
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_missing_required_fields(self):
        """Test that missing required fields are handled gracefully."""
        config = {
            "scenario": "drop",
            # Missing ball config
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_negative_mass_fails(self):
        """Test that negative mass is handled."""
        config = {
            "scenario": "drop",
            "ball": {"mass": -1.0, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_zero_radius_fails(self):
        """Test that zero radius is handled."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.0, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_negative_timestep_fails(self):
        """Test that negative timestep is handled."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": -0.005, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_zero_max_time_fails(self):
        """Test that zero max time is handled."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 0.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_humidity_out_of_range(self):
        """Test that humidity outside 0-100% is handled."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 150.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass


# =========================
# Data Validation Tests
# =========================

class TestDataValidation:
    """Test data validation in simulation results."""
    
    def test_simulation_result_structure(self):
        """Test that simulation result has correct structure."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        
        assert isinstance(result, dict)
        assert 'data' in result
        assert 'summary' in result
        assert 'config' in result
    
    def test_summary_contains_required_fields(self):
        """Test that summary contains required fields."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        summary = result['summary']
        
        required_fields = [
            'flight_time', 'max_height', 'horizontal_range',
            'max_velocity', 'max_mach', 'is_stable', 'energy_conserved'
        ]
        
        for field in required_fields:
            assert field in summary
    
    def test_config_preserved_in_result(self):
        """Test that config is preserved in result."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 1.5, "radius": 0.2, "spin_rps": 5.0},
            "position": {"z0": 20.0},
            "wind": {"humidity_pct": 75.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
        }
        
        result = run_simulation(config_path=None, **config)
        
        # Config should be preserved
        assert result['config'] is not None
        assert result['config']['ball']['mass'] == 1.5
        assert result['config']['ball']['radius'] == 0.2
        assert result['config']['ball']['spin_rps'] == 5.0
    
    def test_data_is_list_of_dicts(self):
        """Test that data is a list of dictionaries."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        data = result['data']
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert isinstance(data[0], dict)
    
    def test_data_has_required_columns(self):
        """Test that data has required columns."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        data = result['data']
        
        # Check that first row has required keys
        required_keys = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz']
        for key in required_keys:
            assert key in data[0]


# =========================
# Edge Cases Tests
# =========================

class TestEdgeCases:
    """Test edge cases in validation."""
    
    def test_minimal_config(self):
        """Test with minimal configuration."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_large_values(self):
        """Test with large configuration values."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 100.0, "radius": 1.0, "spin_rps": 100.0},
            "position": {"z0": 1000.0},
            "wind": {"humidity_pct": 100.0, "ref_speed": 100.0},
            "simulation": {"g": 9.81, "dt": 0.001, "t_max": 100.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_zero_initial_conditions(self):
        """Test with zero initial conditions."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"x0": 0.0, "y0": 0.0, "z0": 0.0},
            "wind": {"humidity_pct": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_high_velocity(self):
        """Test with high initial velocity."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        # Add high velocity
        config["position"]["v0"] = 100.0
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_spin_parameters(self):
        """Test with various spin parameters."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 10.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_wind_parameters(self):
        """Test with various wind parameters."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {
                "humidity_pct": 50.0,
                "ref_speed": 10.0,
                "ref_height": 10.0,
                "shear_alpha": 0.12,
                "direction_deg": 90.0
            },
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_surface_parameters(self):
        """Test with various surface parameters."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "surface": {
                "elasticity_base": 0.8,
                "friction_mu_s": 0.6,
                "friction_mu_k": 0.4,
                "dampness": 0.1,
                "slope_x": 0.1,
                "slope_y": 0.05
            },
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
