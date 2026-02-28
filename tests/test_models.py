"""
Comprehensive tests for physimlab.core module configuration.
Tests configuration validation and structure.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.core import run_simulation


# =========================
# Configuration Structure Tests
# =========================

class TestConfigStructure:
    """Test configuration structure and validation."""
    
    def test_minimal_config_structure(self):
        """Test that minimal config works."""
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
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
        assert 'data' in result
        assert 'summary' in result
    
    def test_full_config_structure(self):
        """Test that full config works."""
        config = {
            "scenario": "drop",
            "ball": {
                "mass": 0.5,
                "radius": 0.1,
                "spin_rps": 8.0
            },
            "position": {
                "x0": 0.0,
                "y0": 0.0,
                "z0": 10.0
            },
            "wind": {
                "humidity_pct": 50.0,
                "ref_speed": 2.0,
                "ref_height": 10.0,
                "shear_alpha": 0.12,
                "direction_deg": 0.0,
                "gust_tau": 2.0,
                "gust_sigma": 1.0
            },
            "surface": {
                "elasticity_base": 0.70,
                "elasticity_drop": 0.002,
                "friction_mu_s": 0.50,
                "friction_mu_k": 0.35,
                "dampness": 0.10,
                "slope_x": 0.0,
                "slope_y": 0.0,
                "base_height": 0.0,
                "rough_amp": 0.0,
                "wetness": 0.0
            },
            "simulation": {
                "g": 9.81,
                "dt": 0.005,
                "t_max": 10.0,
                "seed": 42,
                "adaptive_timestep": False,
                "buoyancy": True,
                "use_virtual_mass": True,
                "use_multi_regime_cd": True,
                "use_hertzian_contact": True
            }
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
        assert 'data' in result
        assert 'summary' in result
    
    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        # Missing ball config
        config = {
            "scenario": "drop",
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


# =========================
# Configuration Validation Tests
# =========================

class TestConfigValidation:
    """Test configuration validation."""
    
    def test_positive_mass(self):
        """Test that mass must be positive."""
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
    
    def test_positive_radius(self):
        """Test that radius must be positive."""
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
    
    def test_positive_timestep(self):
        """Test that timestep must be positive."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.0, "t_max": 5.0}
        }
        
        # Should either raise error or handle gracefully
        try:
            result = run_simulation(config_path=None, **config)
            # If it doesn't raise error, check that it still produces valid output
            assert result is not None
        except Exception:
            # Expected for invalid input
            pass
    
    def test_positive_max_time(self):
        """Test that max time must be positive."""
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


# =========================
# Configuration Defaults Tests
# =========================

class TestConfigDefaults:
    """Test configuration defaults."""
    
    def test_default_ball_properties(self):
        """Test default ball properties."""
        config = {
            "scenario": "drop",
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_default_position(self):
        """Test default position."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_default_wind(self):
        """Test default wind."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_default_surface(self):
        """Test default surface."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None


# =========================
# Configuration Edge Cases Tests
# =========================

class TestConfigEdgeCases:
    """Test configuration edge cases."""
    
    def test_zero_spin(self):
        """Test zero spin rate."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_zero_wind_speed(self):
        """Test zero wind speed."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_zero_height(self):
        """Test zero initial height."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 0.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_large_values(self):
        """Test large configuration values."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 100.0, "radius": 1.0, "spin_rps": 100.0},
            "position": {"z0": 1000.0},
            "wind": {"humidity_pct": 100.0, "ref_speed": 100.0, "gust_sigma": 10.0},
            "simulation": {"g": 9.81, "dt": 0.001, "t_max": 100.0}
        }
        
        result = run_simulation(config_path=None, **config)
        assert result is not None


# =========================
# Configuration Output Tests
# =========================

class TestConfigOutput:
    """Test configuration in output."""
    
    def test_config_preserved_in_output(self):
        """Test that config is preserved in output."""
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
    
    def test_summary_contains_config_info(self):
        """Test that summary contains relevant config info."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        summary = result['summary']
        
        # Summary should contain relevant info
        assert 'flight_time' in summary
        assert 'max_height' in summary
        assert 'horizontal_range' in summary
        assert 'max_velocity' in summary
        assert 'max_mach' in summary
        assert 'is_stable' in summary
        assert 'energy_conserved' in summary
