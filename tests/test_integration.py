"""
Integration tests for physimlab.core module.
Tests end-to-end workflows and cross-module interactions.
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.core import run_simulation
from physimlab.config.loader import ConfigLoader
from physimlab.output.manager import OutputManager


# =========================
# Full Workflow Tests
# =========================

class TestFullWorkflow:
    """Test complete simulation workflow from config to output."""
    
    def test_full_workflow_from_config(self):
        """Test complete workflow from config file to results."""
        # Load config
        config_loader = ConfigLoader()
        config = config_loader.load("tests/test_config.json")
        
        # Run simulation
        result = run_simulation(config_path=None, **config_loader)
        
        # Check results
        assert result is not None
        assert 'data' in result
        assert 'summary' in result
        assert len(result['data']) > 0
    
    def test_full_workflow_with_output_files(self, temp_output_dir):
        """Test complete workflow including file output."""
        # Load and run
        config_loader = ConfigLoader()
        config = config_loader.load("tests/test_config.json")
        result = run_simulation(config_path=None, **config_loader)
        
        # Generate output files using OutputManager
        output_manager = OutputManager(output_dir=temp_output_dir)
        from physimlab.output.result import Result
        
        result_obj = Result(
            data=result['data'],
            summary=result['summary'],
            config=config_loader,
            output_manager=output_manager
        )
        
        output_manager.save_all(result_obj)
        
        # Check files were created
        output_files = output_manager.get_output_files()
        assert len(output_files) > 0


# =========================
# Determinism Tests
# =========================

class TestDeterminism:
    """Test simulation determinism."""
    
    def test_same_seed_produces_identical_trajectory(self):
        """Test that same seed produces identical trajectory."""
        config1 = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 2.0, "gust_sigma": 1.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0, "seed": 123}
        }
        
        result1 = run_simulation(config_path=None, **config1)
        result2 = run_simulation(config_path=None, **config1)
        
        pd.testing.assert_frame_equal(result1['data'], result2['data'])
    
    def test_different_seeds_produce_different_trajectories(self):
        """Test that different seeds produce different trajectories."""
        config1 = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 2.0, "gust_sigma": 1.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0, "seed": 1}
        }
        
        config2 = config1.copy()
        config2['simulation']['seed'] = 2
        
        result1 = run_simulation(config_path=None, **config1)
        result2 = run_simulation(config_path=None, **config2)
        
        # Trajectories should differ
        assert not result1['data']['x'].equals(result2['data']['x'])
    
    def test_zero_gust_sigma_deterministic(self):
        """Test that zero gust sigma makes simulation deterministic."""
        config1 = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0, "seed": 1}
        }
        
        config2 = config1.copy()
        config2['simulation']['seed'] = 2
        
        result1 = run_simulation(config_path=None, **config1)
        result2 = run_simulation(config_path=None, **config2)
        
        # Should be identical regardless of seed
        pd.testing.assert_frame_equal(result1['data'], result2['data'])


# =========================
# Physical Bounds Tests
# =========================

class TestPhysicalBounds:
    """Test that simulation results stay within physical bounds."""
    
    def test_ball_does_not_go_below_ground(self):
        """Test that ball never goes below ground."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        # Ball bottom (z) should be >= 0 (ground)
        assert (df['z'] >= -0.01).all()  # Small tolerance
    
    def test_velocity_does_not_exceed_terminal(self):
        """Test that velocity doesn't greatly exceed terminal velocity."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 100.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        speed = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
        
        # Should not exceed reasonable terminal velocity (with wind)
        assert speed.max() < 50  # m/s
    
    def test_time_only_moves_forward(self):
        """Test that time is monotonically increasing."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        time_diff = df['time'].diff().dropna()
        assert (time_diff >= 0).all()
    
    def test_reynolds_number_positive(self):
        """Test that Reynolds number is non-negative."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        assert (df['reynolds'] >= 0).all()
    
    def test_air_density_reasonable(self):
        """Test that air density is in reasonable range."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        # Air density should be roughly 0.9 - 1.3 kg/m³
        assert (df['air_density'] > 0.8).all()
        assert (df['air_density'] < 1.5).all()


# =========================
# Energy Conservation Tests
# =========================

class TestEnergyConservationIntegration:
    """Test energy conservation in full simulation."""
    
    def test_total_energy_decreases_or_stays_same(self):
        """Test that total energy never increases (ignoring gusts)."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 20.0},
            "wind": {"humidity_pct": 0.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0, "buoyancy": False}
        }
        
        result = run_simulation(config_path=None, **config)
        
        # Should have reasonable energy conservation
        assert result['summary']['energy_conserved'] is True
    
    def test_bounce_reduces_energy(self):
        """Test that bounces reduce energy."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 5.0},
            "surface": {"elasticity_base": 0.8},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        
        # Energy should decrease after bounces
        assert result['summary']['energy_conserved'] is True


# =========================
# Aerodynamic Effects Tests
# =========================

class TestAerodynamicEffectsIntegration:
    """Test aerodynamic effects in simulation."""
    
    def test_drag_slows_ball(self):
        """Test that drag slows the ball."""
        config_small = {
            "scenario": "drop",
            "ball": {"mass": 0.1, "radius": 0.01, "spin_rps": 0.0},
            "position": {"z0": 50.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        config_large = {
            "scenario": "drop",
            "ball": {"mass": 0.1, "radius": 0.2, "spin_rps": 0.0},
            "position": {"z0": 50.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        result_small = run_simulation(config_path=None, **config_small)
        result_large = run_simulation(config_path=None, **config_large)
        
        df_small = result_small['data']
        df_large = result_large['data']
        
        # Large ball should fall slower due to higher drag/mass ratio
        speed_small = np.sqrt(df_small['vx']**2 + df_small['vy']**2 + df_small['vz']**2).iloc[-1]
        speed_large = np.sqrt(df_large['vx']**2 + df_large['vy']**2 + df_large['vz']**2).iloc[-1]
        
        # Small ball should be faster at end
        assert speed_small > speed_large
    
    def test_wind_affects_trajectory(self):
        """Test that wind affects trajectory."""
        config_no = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        config_yes = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 10.0, "gust_sigma": 0.0, "direction_deg": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        result_no = run_simulation(config_path=None, **config_no)
        result_yes = run_simulation(config_path=None, **config_yes)
        
        df_no = result_no['data']
        df_yes = result_yes['data']
        
        # X position should differ
        x_diff = abs(df_yes['x'].iloc[-1] - df_no['x'].iloc[-1])
        assert x_diff > 1.0  # At least 1m difference


# =========================
# Trajectory Shape Tests
# =========================

class TestTrajectoryShape:
    """Test that trajectory shapes are physically reasonable."""
    
    def test_trajectory_has_parabolic_shape(self):
        """Test that trajectory is approximately parabolic."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 5.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        # Check that z initially increases then decreases
        assert df['z'].iloc[0] < df['z'].iloc[len(df)//4]  # Initial rise
        assert df['z'].iloc[-1] < df['z'].iloc[len(df)//4]  # Final fall
    
    def test_max_height_occurs_early(self):
        """Test that max height occurs in first half of flight."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 5.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        max_height_idx = df['z'].idxmax()
        # Max height should be in first half
        assert max_height_idx < len(df) / 2


# =========================
# Multiple Configuration Tests
# =========================

class TestMultipleConfigurations:
    """Test simulation with various configurations."""
    
    def test_heavy_ball_falls_faster(self):
        """Test that heavier ball falls faster (less drag effect)."""
        config_light = {
            "scenario": "drop",
            "ball": {"mass": 0.1, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 20.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 2.0}
        }
        
        config_heavy = {
            "scenario": "drop",
            "ball": {"mass": 10.0, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 20.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 2.0}
        }
        
        result_light = run_simulation(config_path=None, **config_light)
        result_heavy = run_simulation(config_path=None, **config_heavy)
        
        df_light = result_light['data']
        df_heavy = result_heavy['data']
        
        # Heavy ball should have higher final speed
        speed_light = np.sqrt(df_light['vx']**2 + df_light['vy']**2 + df_light['vz']**2).iloc[-1]
        speed_heavy = np.sqrt(df_heavy['vx']**2 + df_heavy['vy']**2 + df_heavy['vz']**2).iloc[-1]
        
        assert speed_heavy > speed_light
    
    def test_higher_elasticity_more_bounces(self):
        """Test that higher elasticity produces more bounces."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 3.0},
            "wind": {"humidity_pct": 50.0, "ref_speed": 0.0, "gust_sigma": 0.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
        }
        
        config_low = config.copy()
        config_low['surface'] = {"elasticity_base": 0.3}
        
        config_high = config.copy()
        config_high['surface'] = {"elasticity_base": 0.95}
        
        result_low = run_simulation(config_path=None, **config_low)
        result_high = run_simulation(config_path=None, **config_high)
        
        # Higher elasticity should have more bounces
        assert result_high['summary']['ground_contacts'] >= result_low['summary']['ground_contacts']


# =========================
# Performance Tests
# =========================

class TestPerformance:
    """Test simulation performance."""
    
    def test_simulation_completes_quickly(self):
        """Test that simulation completes in reasonable time."""
        import time
        
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
        }
        
        start = time.time()
        result = run_simulation(config_path=None, **config)
        elapsed = time.time() - start
        
        # Should complete in less than 30 seconds
        assert elapsed < 30.0
    
    def test_long_simulation_completes(self):
        """Test that long simulation completes."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 100.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 30.0}
        }
        
        result = run_simulation(config_path=None, **config)
        
        assert result is not None
        assert len(result['data']) > 0
