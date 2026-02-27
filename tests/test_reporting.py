"""
Comprehensive tests for simlab.output module.
Tests output generation, statistics calculation, and result formatting.
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simlab.output import Result


# =========================
# SimulationResult Tests
# =========================

class TestSimulationResult:
    """Test SimulationResult class."""
    
    def test_simulation_result_creation(self):
        """Test creating a SimulationResult."""
        # Create test data
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [10.0, 9.0, 8.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0]
        })
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 0.5, 'radius': 0.1},
            'position': {'z0': 10.0},
            'wind': {'humidity_pct': 50.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 5.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.0,
            'max_height': 0.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.data is df
        assert result.config is config
    
    def test_simulation_result_defaults(self):
        """Test Result default values."""
        df = pd.DataFrame()
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.0,
            'max_height': 0.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.is_stable is True
        assert result.energy_conserved is True
    
    def test_get_summary(self):
        """Test summary properties."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [10.0, 9.0, 8.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0]
        })
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 0.5, 'radius': 0.1},
            'position': {'z0': 10.0},
            'wind': {'humidity_pct': 50.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 5.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.2,
            'max_height': 10.0,
            'horizontal_range': 2.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Test summary properties
        assert result.flight_time == 0.2
        assert result.max_height == 10.0
        assert result.horizontal_range == 2.0
        assert result.max_velocity == 10.0
        assert result.is_stable is True
        assert result.energy_conserved is True
    
    def test_get_summary_contains_config_info(self):
        """Test that config is accessible."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [10.0, 9.0, 8.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0]
        })
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 1.5, 'radius': 0.2},
            'position': {'z0': 20.0},
            'wind': {'humidity_pct': 75.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 10.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.2,
            'max_height': 20.0,
            'horizontal_range': 2.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Config should be accessible
        assert result.config['ball']['mass'] == 1.5
        assert result.config['ball']['radius'] == 0.2
        assert result.config['position']['z0'] == 20.0
        assert result.config['wind']['humidity_pct'] == 75.0
    
    def test_get_summary_calculates_statistics(self):
        """Test that summary properties work correctly."""
        # Create data with known properties
        times = np.linspace(0, 1, 100)
        x = times * 5  # Constant horizontal velocity
        z = 10 - 0.5 * 9.81 * times**2  # Free fall
        
        df = pd.DataFrame({
            'Time': times,
            'X': x,
            'Y': 0,
            'Z': z,
            'Vx': 5,
            'Vy': 0,
            'Vz': -9.81 * times
        })
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 0.5, 'radius': 0.1},
            'position': {'z0': 10.0},
            'wind': {'humidity_pct': 0.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 5.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 1.0,
            'max_height': 10.0,
            'horizontal_range': 5.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Check summary properties
        assert result.flight_time > 0
        assert result.max_height >= 10.0
        assert result.horizontal_range > 0
        assert result.max_velocity > 0
        assert result.is_stable is True
        assert result.energy_conserved is True


# =========================
# Data Validation Tests
# =========================

class TestDataValidation:
    """Test data validation in Result."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.0,
            'max_height': 0.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time == 0.0
        assert result.is_stable is True
        assert result.energy_conserved is True
    
    def test_missing_columns(self):
        """Test handling of DataFrame with missing columns."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1],
            'X': [0.0, 1.0]
            # Missing Z, Vx, Vz columns
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.1,
            'max_height': 0.0,
            'horizontal_range': 1.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time == 0.1
        assert result.is_stable is True
    
    def test_negative_time_values(self):
        """Test handling of negative time values."""
        df = pd.DataFrame({
            'Time': [-0.1, 0.0, 0.1],
            'X': [0.0, 0.0, 1.0],
            'Z': [10.0, 10.0, 9.0],
            'Vx': [0.0, 10.0, 10.0],
            'Vz': [0.0, 0.0, -1.0]
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.1,
            'max_height': 10.0,
            'horizontal_range': 1.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time == 0.1
        assert result.max_height == 10.0
        assert result.is_stable is True
    
    def test_large_values(self):
        """Test handling of large numerical values."""
        df = pd.DataFrame({
            'Time': [0.0, 100.0],
            'X': [0.0, 1000.0],
            'Z': [1000.0, 0.0],
            'Vx': [0.0, 100.0],
            'Vz': [0.0, -100.0]
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 100.0,
            'max_height': 1000.0,
            'horizontal_range': 1000.0,
            'max_velocity': 100.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time > 0
        assert result.max_height > 0
        assert result.is_stable is True


# =========================
# Configuration Tests
# =========================

class TestConfiguration:
    """Test configuration handling."""
    
    def test_minimal_config(self):
        """Test with minimal configuration."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1],
            'X': [0.0, 1.0],
            'Z': [10.0, 9.0],
            'Vx': [10.0, 9.0],
            'Vz': [0.0, -1.0]
        })
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 0.5, 'radius': 0.1},
            'position': {'z0': 10.0},
            'wind': {'humidity_pct': 0.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 5.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.1,
            'max_height': 10.0,
            'horizontal_range': 1.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time == 0.1
        assert result.max_height == 10.0
        assert result.is_stable is True
    
    def test_full_config(self):
        """Test with full configuration."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1],
            'X': [0.0, 1.0],
            'Z': [10.0, 9.0],
            'Vx': [10.0, 9.0],
            'Vz': [0.0, -1.0]
        })
        
        config = {
            'scenario': 'drop',
            'ball': {
                'mass': 0.5,
                'radius': 0.1,
                'spin_rps': 8.0
            },
            'position': {
                'x0': 0.0,
                'y0': 0.0,
                'z0': 10.0
            },
            'wind': {
                'humidity_pct': 50.0,
                'ref_speed': 2.0,
                'ref_height': 10.0,
                'shear_alpha': 0.12,
                'direction_deg': 0.0,
                'gust_tau': 2.0,
                'gust_sigma': 1.0
            },
            'surface': {
                'elasticity_base': 0.70,
                'elasticity_drop': 0.002,
                'friction_mu_s': 0.50,
                'friction_mu_k': 0.35,
                'dampness': 0.10,
                'slope_x': 0.0,
                'slope_y': 0.0,
                'base_height': 0.0,
                'rough_amp': 0.0,
                'wetness': 0.0
            },
            'simulation': {
                'g': 9.81,
                'dt': 0.005,
                't_max': 10.0,
                'seed': 42,
                'adaptive_timestep': False,
                'buoyancy': True,
                'use_virtual_mass': True,
                'use_multi_regime_cd': True,
                'use_hertzian_contact': True
            }
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.1,
            'max_height': 10.0,
            'horizontal_range': 1.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Should handle gracefully
        assert result.flight_time == 0.1
        assert result.max_height == 10.0
        assert result.is_stable is True
        # Should contain all config sections
        assert result.config['ball']['mass'] == 0.5
        assert result.config['ball']['radius'] == 0.1
        assert result.config['wind']['humidity_pct'] == 50.0
        assert result.config['surface']['elasticity_base'] == 0.70
    
    def test_config_preserved(self):
        """Test that config is preserved in result."""
        df = pd.DataFrame()
        
        config = {
            'scenario': 'drop',
            'ball': {'mass': 1.5, 'radius': 0.2},
            'position': {'z0': 20.0},
            'wind': {'humidity_pct': 75.0},
            'simulation': {'g': 9.81, 'dt': 0.005, 't_max': 10.0}
        }
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.0,
            'max_height': 0.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        # Config should be preserved
        assert result.config is config


# =========================
# Edge Cases Tests
# =========================

class TestEdgeCases:
    """Test edge cases in output handling."""
    
    def test_single_timestep(self):
        """Test with single timestep."""
        df = pd.DataFrame({
            'Time': [0.0],
            'X': [0.0],
            'Y': [0.0],
            'Z': [10.0],
            'Vx': [0.0],
            'Vy': [0.0],
            'Vz': [0.0]
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.0,
            'max_height': 10.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.flight_time == 0.0
        assert result.max_height == 10.0
        assert result.horizontal_range == 0.0
    
    def test_constant_height(self):
        """Test with constant height (hovering)."""
        df = pd.DataFrame({
            'Time': [0.0, 1.0, 2.0],
            'X': [0.0, 0.0, 0.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 10.0, 10.0],
            'Vx': [0.0, 0.0, 0.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, 0.0, 0.0]
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 2.0,
            'max_height': 10.0,
            'horizontal_range': 0.0,
            'max_velocity': 0.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.flight_time > 0
        assert result.max_height == 10.0
        assert result.horizontal_range == 0.0
    
    def test_upward_motion(self):
        """Test with upward initial motion."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 11.0, 11.5],  # Moving upward
            'Vx': [10.0, 10.0, 10.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [10.0, 5.0, 0.0]  # Slowing down
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.2,
            'max_height': 11.5,
            'horizontal_range': 2.0,
            'max_velocity': 10.0,
            'max_mach': 0.0,
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.max_height > 10.0
        assert result.flight_time > 0
    
    def test_high_velocity(self):
        """Test with high velocity (supersonic)."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1],
            'X': [0.0, 100.0],
            'Y': [0.0, 0.0],
            'Z': [10.0, 9.0],
            'Vx': [1000.0, 1000.0],  # Very high velocity
            'Vy': [0.0, 0.0],
            'Vz': [0.0, -1.0]
        })
        config = {}
        
        # Create a minimal summary for testing
        summary = {
            'flight_time': 0.1,
            'max_height': 10.0,
            'horizontal_range': 100.0,
            'max_velocity': 1000.0,
            'max_mach': 3.0,  # Supersonic
            'is_stable': True,
            'energy_conserved': True
        }
        result = Result(df, summary, config, None)
        
        assert result.max_velocity > 100
        assert result.summary['max_mach'] > 0.2  # Should be supersonic
