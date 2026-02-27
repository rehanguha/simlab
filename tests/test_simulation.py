"""
Comprehensive tests for simlab.core module.
Tests the modern simulation API and functionality.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simlab.core import run_simulation


# =========================
# Basic Simulation Tests
# =========================

class TestRunSimulationBasic:
    """Test basic simulation functionality."""
    
    def test_run_simulation_runs_without_error(self, default_config):
        """Test that simulation runs without error."""
        result = run_simulation(config_path=None, **default_config)
        assert result is not None
    
    def test_run_simulation_returns_dict(self, default_config):
        """Test that run_simulation returns a dictionary."""
        result = run_simulation(config_path=None, **default_config)
        assert isinstance(result, dict)
    
    def test_run_simulation_returns_data(self, default_config):
        """Test that result contains data."""
        result = run_simulation(config_path=None, **default_config)
        assert 'data' in result
        assert 'summary' in result
        assert 'config' in result
    
    def test_run_simulation_data_is_dataframe(self, default_config):
        """Test that data is a DataFrame."""
        result = run_simulation(config_path=None, **default_config)
        assert isinstance(result['data'], pd.DataFrame)
    
    def test_run_simulation_dataframe_not_empty(self, default_config):
        """Test that DataFrame has data."""
        result = run_simulation(config_path=None, **default_config)
        assert len(result['data']) > 0


class TestRunSimulationDataFrameColumns:
    """Test DataFrame column structure."""
    
    def test_all_required_columns_present(self, default_config):
        """Test that all required columns are present."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        required_columns = [
            'time', 'x', 'y', 'z', 'vx', 'vy', 'vz',
            'speed', 'omega_z', 'air_density', 'reynolds',
            'cd', 'mach'
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_time_column_starts_at_zero(self, default_config):
        """Test that time starts at or near zero."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        assert df['time'].iloc[0] >= 0.0
    
    def test_time_column_monotonic_increasing(self, default_config):
        """Test that time is monotonically increasing."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        time_diff = df['time'].diff().dropna()
        assert (time_diff >= 0).all()


class TestRunSimulationPhysics:
    """Test physical correctness of simulation."""
    
    def test_height_non_negative(self, default_config):
        """Test that height is non-negative (ball doesn't go below ground)."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        # Ball bottom should be at or above ground (z >= 0)
        assert (df['z'] >= -0.01).all()
    
    def test_initial_position_correct(self, default_config):
        """Test that initial position is correct."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        assert abs(df['x'].iloc[0] - default_config['position']['x0']) < 0.01
        assert abs(df['y'].iloc[0] - default_config['position']['y0']) < 0.01
        assert abs(df['z'].iloc[0] - default_config['position']['z0']) < 0.01
    
    def test_initial_velocity_direction(self, default_config):
        """Test that initial velocity has correct direction."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        # For 45 degree drop angle, should have both horizontal and vertical components
        vx0 = df['vx'].iloc[0]
        vz0 = df['vz'].iloc[0]
        
        # Allow for small integration steps
        assert abs(vx0) > 0.01  # Should have horizontal component
        assert abs(vz0) > 0.01  # Should have vertical component
    
    def test_gravity_causes_acceleration(self, default_config):
        """Test that gravity causes downward acceleration."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        # Vz should change over time due to gravity
        vz = df['vz'].values
        # Should have acceleration (change in velocity)
        assert abs(vz[-1] - vz[0]) > 0.01


class TestRunSimulationFreeFall:
    """Test free fall behavior."""
    
    def test_free_fall_approximation(self):
        """Test that free fall approximates analytical solution."""
        # Drop from rest with no air resistance (high mass, small radius)
        config = {
            "scenario": "drop",
            "ball": {
                "mass": 100.0,  # Heavy ball
                "radius": 0.01,  # Small radius = less drag
                "spin_rps": 0.0
            },
            "position": {
                "z0": 5.0,
                "x0": 0.0,
                "y0": 0.0
            },
            "wind": {
                "humidity_pct": 0.0
            },
            "simulation": {
                "g": 9.81,
                "dt": 0.001,
                "t_max": 0.5,  # Short time
                "buoyancy": False,
                "use_virtual_mass": False
            }
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        # After time t, position should be approximately z0 - 0.5*g*t^2
        # and velocity should be approximately g*t
        # Check at some intermediate point
        t_check = 0.3
        idx = np.argmin(np.abs(df['time'].values - t_check))
        
        expected_z = config['position']['z0'] - 0.5 * config['simulation']['g'] * t_check**2
        expected_vz = -config['simulation']['g'] * t_check
        
        actual_z = df['z'].iloc[idx]
        actual_vz = df['vz'].iloc[idx]
        
        # Allow for some drag
        assert abs(actual_z - expected_z) < 0.2
        assert abs(actual_vz - expected_vz) < 1.0


class TestRunSimulationSpin:
    """Test spin behavior."""
    
    def test_spin_decay_over_time(self, default_config):
        """Test that spin decays over time."""
        result = run_simulation(config_path=None, **default_config)
        df = result['data']
        
        # Omega should generally decrease
        omega_initial = df['omega_z'].iloc[0]
        omega_final = df['omega_z'].iloc[-1]
        
        # Spin should decay (decrease in magnitude)
        assert abs(omega_final) < abs(omega_initial)
    
    def test_no_spin_no_rotation(self, no_spin_config):
        """Test that no spin means no rotation."""
        result = run_simulation(config_path=None, **no_spin_config)
        df = result['data']
        
        # Omega should be zero throughout
        assert (abs(df['omega_z']) < 0.1).all()


class TestRunSimulationWind:
    """Test wind effects."""
    
    def test_wind_causes_drift(self, default_config):
        """Test that wind causes horizontal drift."""
        config_no_wind = default_config.copy()
        config_no_wind['wind'] = {'humidity_pct': 50.0, 'ref_speed': 0.0, 'gust_sigma': 0.0}
        
        config_with_wind = default_config.copy()
        config_with_wind['wind'] = {'humidity_pct': 50.0, 'ref_speed': 5.0, 'gust_sigma': 0.0, 'direction_deg': 0.0}
        
        result_no_wind = run_simulation(config_path=None, **config_no_wind)
        result_with_wind = run_simulation(config_path=None, **config_with_wind)
        
        df_no_wind = result_no_wind['data']
        df_with_wind = result_with_wind['data']
        
        # X position should differ with wind in X direction
        x_no_wind = df_no_wind['x'].iloc[-1]
        x_with_wind = df_with_wind['x'].iloc[-1]
        
        assert abs(x_with_wind - x_no_wind) > 0.1


class TestRunSimulationReproducibility:
    """Test simulation reproducibility."""
    
    def test_same_seed_same_results(self, default_config):
        """Test that same seed produces identical results."""
        result1 = run_simulation(config_path=None, **default_config)
        result2 = run_simulation(config_path=None, **default_config)
        
        pd.testing.assert_frame_equal(result1['data'], result2['data'])
    
    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results (due to gusts)."""
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
        
        # Results should differ due to random gusts
        # (at least some values should be different)
        assert not result1['data'].equals(result2['data'])


class TestRunSimulationStopConditions:
    """Test simulation stop conditions."""
    
    def test_simulation_stops_at_t_max(self):
        """Test that simulation stops at t_max."""
        config = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 100.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 3.0}
        }
        
        result = run_simulation(config_path=None, **config)
        df = result['data']
        
        assert df['time'].iloc[-1] <= config['simulation']['t_max'] + config['simulation']['dt']


class TestRunSimulationPhysicsFlags:
    """Test physics feature flags."""
    
    def test_buoyancy_disabled(self, default_config):
        """Test simulation with buoyancy disabled."""
        config = default_config.copy()
        config['simulation']['buoyancy'] = False
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_virtual_mass_disabled(self, default_config):
        """Test simulation with virtual mass disabled."""
        config = default_config.copy()
        config['simulation']['use_virtual_mass'] = False
        
        result = run_simulation(config_path=None, **config)
        assert result is not None
    
    def test_multi_regime_cd_disabled(self, default_config):
        """Test simulation with multi-regime CD disabled."""
        config = default_config.copy()
        config['simulation']['use_multi_regime_cd'] = False
        
        result = run_simulation(config_path=None, **config)
        assert result is not None


class TestRunSimulationSummary:
    """Test summary statistics."""
    
    def test_summary_contains_required_fields(self, default_config):
        """Test that summary contains required fields."""
        result = run_simulation(config_path=None, **default_config)
        summary = result['summary']
        
        required_fields = [
            'flight_time',
            'max_height',
            'horizontal_range',
            'max_velocity',
            'max_mach',
            'is_stable',
            'energy_conserved'
        ]
        
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"
    
    def test_summary_values_reasonable(self, default_config):
        """Test that summary values are reasonable."""
        result = run_simulation(config_path=None, **default_config)
        summary = result['summary']
        
        # Basic sanity checks
        assert summary['flight_time'] > 0
        assert summary['max_height'] > 0
        assert summary['max_velocity'] > 0
        assert summary['max_mach'] >= 0
        assert isinstance(summary['is_stable'], bool)
        assert isinstance(summary['energy_conserved'], bool)


class TestRunSimulationVariousConfigs:
    """Test various configuration scenarios."""
    
    def test_various_ball_configs(self, various_ball_configs):
        """Test simulation with various ball configurations."""
        result = run_simulation(config_path=None, **various_ball_configs)
        assert result is not None
        assert len(result['data']) > 0
    
    def test_various_initial_velocities(self, various_initial_velocities):
        """Test simulation with various initial velocities."""
        result = run_simulation(config_path=None, **various_initial_velocities)
        assert result is not None
        assert len(result['data']) > 0


# =========================
# Error Handling Tests
# =========================

class TestRunSimulationErrorHandling:
    """Test error handling in simulation."""
    
    def test_missing_required_config(self):
        """Test that missing required config raises error."""
        with pytest.raises(Exception):  # Should raise some kind of error
            run_simulation(config_path=None, scenario="drop")  # Missing ball config
    
    def test_invalid_config_values(self):
        """Test that invalid config values are handled."""
        config = {
            "scenario": "drop",
            "ball": {
                "mass": -1.0,  # Invalid: negative mass
                "radius": 0.1,
                "spin_rps": 0.0
            },
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
# Performance Tests
# =========================

class TestRunSimulationPerformance:
    """Test simulation performance."""
    
    def test_simulation_runs_in_reasonable_time(self, default_config):
        """Test that simulation runs in reasonable time."""
        import time
        
        start_time = time.time()
        result = run_simulation(config_path=None, **default_config)
        end_time = time.time()
        
        # Should complete in less than 30 seconds
        assert (end_time - start_time) < 30.0
    
    def test_simulation_scales_reasonably(self):
        """Test that simulation scales reasonably with time."""
        config_short = {
            "scenario": "drop",
            "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
            "position": {"z0": 10.0},
            "wind": {"humidity_pct": 50.0},
            "simulation": {"g": 9.81, "dt": 0.005, "t_max": 5.0}
        }
        
        config_long = config_short.copy()
        config_long['simulation']['t_max'] = 20.0  # 4x longer
        
        import time
        
        start_time = time.time()
        result_short = run_simulation(config_path=None, **config_short)
        time_short = time.time() - start_time
        
        start_time = time.time()
        result_long = run_simulation(config_path=None, **config_long)
        time_long = time.time() - start_time
        
        # Long simulation should take longer but not excessively so
        assert time_long > time_short
        assert time_long < time_short * 10  # Shouldn't be more than 10x slower
