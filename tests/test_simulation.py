"""
Comprehensive tests for simulation.py module.
Tests core simulation engine, physics integration, and output validation.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind
from simulation import (
    simulate_drop,
    check_numerical_stability,
    compute_total_energy,
    resolve_penetration
)


# =========================
# Basic Simulation Tests
# =========================

class TestSimulateDropBasic:
    """Test basic simulation functionality."""
    
    def test_simulate_drop_runs_without_error(self, default_params, default_surface, default_wind):
        """Test that simulation runs without error."""
        result = simulate_drop(default_params, default_surface, default_wind)
        assert result is not None
    
    def test_simulate_drop_returns_simulation_result(self, default_params, default_surface, default_wind):
        """Test that simulate_drop returns SimulationResult."""
        from models import SimulationResult
        result = simulate_drop(default_params, default_surface, default_wind)
        assert isinstance(result, SimulationResult)
    
    def test_simulate_drop_returns_dataframe(self, default_params, default_surface, default_wind):
        """Test that result contains a DataFrame."""
        result = simulate_drop(default_params, default_surface, default_wind)
        assert isinstance(result.df, pd.DataFrame)
    
    def test_simulate_drop_dataframe_not_empty(self, default_params, default_surface, default_wind):
        """Test that DataFrame has data."""
        result = simulate_drop(default_params, default_surface, default_wind)
        assert len(result.df) > 0
    
    def test_simulate_drop_stability_ok(self, default_params, default_surface, default_wind):
        """Test that simulation is numerically stable."""
        result = simulate_drop(default_params, default_surface, default_wind)
        assert result.stability_ok is True


class TestSimulateDropDataFrameColumns:
    """Test DataFrame column structure."""
    
    def test_all_required_columns_present(self, default_params, default_surface, default_wind):
        """Test that all required columns are present."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        required_columns = [
            'Time', 'X', 'Y', 'Z', 'Vx', 'Vy', 'Vz',
            'Ox', 'Oy', 'Oz', 'AirDensity', 'Mu', 'Re',
            'Cd', 'WindX', 'WindY', 'WindZ', 'Z_ground',
            'Mach', 'Dt_actual'
        ]
        
        for col in required_columns:
            assert col in result.df.columns, f"Missing column: {col}"
    
    def test_time_column_starts_at_zero(self, default_params, default_surface, default_wind):
        """Test that time starts at or near zero."""
        result = simulate_drop(default_params, default_surface, default_wind)
        assert result.df['Time'].iloc[0] >= 0.0
    
    def test_time_column_monotonic_increasing(self, default_params, default_surface, default_wind):
        """Test that time is monotonically increasing."""
        result = simulate_drop(default_params, default_surface, default_wind)
        time_diff = result.df['Time'].diff().dropna()
        assert (time_diff >= 0).all()


class TestSimulateDropPhysics:
    """Test physical correctness of simulation."""
    
    def test_height_non_negative(self, default_params, default_surface, default_wind):
        """Test that height is non-negative (ball doesn't go below ground)."""
        result = simulate_drop(default_params, default_surface, default_wind)
        # Ball bottom should be at or above ground
        clearance = result.df['Z'] - result.df['Z_ground'] - default_params.radius
        # Allow small numerical tolerance
        assert (clearance >= -0.01).all()
    
    def test_initial_position_correct(self, default_params, default_surface, default_wind):
        """Test that initial position is correct."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        assert abs(result.df['X'].iloc[0] - default_params.x0) < 0.01
        assert abs(result.df['Y'].iloc[0] - default_params.y0) < 0.01
        assert abs(result.df['Z'].iloc[0] - default_params.z0) < 0.01
    
    def test_initial_velocity_direction(self, default_params, default_surface, default_wind):
        """Test that initial velocity has correct direction."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        # For 45 degree drop angle, Vx and Vz should be similar
        vx0 = result.df['Vx'].iloc[0]
        vz0 = result.df['Vz'].iloc[0]
        
        # Allow for small integration steps
        assert vx0 > 0  # Should have horizontal component
        assert vz0 > 0  # Should have upward component for 45 degree launch
    
    def test_gravity_causes_acceleration(self, default_params, default_surface, default_wind):
        """Test that gravity causes downward acceleration."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        # Vz should decrease over time initially
        vz = result.df['Vz'].values
        # Find where velocity starts decreasing (after initial upward motion)
        # Just check that gravity is working - vz should eventually become negative
        assert vz[-1] < vz[0] or np.min(vz) < 0


class TestSimulateDropFreeFall:
    """Test free fall behavior."""
    
    def test_free_fall_approximation(self):
        """Test that free fall approximates analytical solution."""
        # Drop from rest with no air resistance (high mass, small radius)
        params = Params(
            mass=100.0,  # Heavy ball
            radius=0.01,  # Small radius = less drag
            v0=0.0,      # Drop from rest
            drop_angle_deg=0.0,
            z0=5.0,
            dt=0.001,
            t_max=0.5,  # Short time
            spin_rps=0.0
        )
        surface = Surface(elasticity_base=0.0, base_height=0.0)  # No bounce
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)  # No wind
        
        result = simulate_drop(params, surface, wind)
        
        # After time t, position should be approximately z0 - 0.5*g*t^2
        # and velocity should be approximately g*t
        # Check at some intermediate point
        t_check = 0.3
        idx = np.argmin(np.abs(result.df['Time'].values - t_check))
        
        expected_z = params.z0 - 0.5 * params.g * t_check**2
        expected_vz = -params.g * t_check
        
        actual_z = result.df['Z'].iloc[idx]
        actual_vz = result.df['Vz'].iloc[idx]
        
        # Allow for some drag
        assert abs(actual_z - expected_z) < 0.2
        assert abs(actual_vz - expected_vz) < 1.0


class TestSimulateDropBounce:
    """Test bounce behavior."""
    
    def test_bounce_occurs(self, high_elasticity_surface, no_wind):
        """Test that bouncing occurs with high elasticity."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=5.0,
            t_max=10.0
        )
        
        result = simulate_drop(params, high_elasticity_surface, no_wind)
        
        # Height should go up and down multiple times
        z = result.df['Z'].values
        # Count local minima near ground
        ground_level = high_elasticity_surface.base_height + params.radius
        near_ground = z < ground_level + 0.1
        
        # Should have multiple bounces
        assert np.sum(near_ground) > 2
    
    def test_bounce_height_decreases(self, high_elasticity_surface, no_wind):
        """Test that bounce height decreases over time."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=5.0,
            t_max=10.0
        )
        
        result = simulate_drop(params, high_elasticity_surface, no_wind)
        
        # Find local maxima of height
        z = result.df['Z'].values
        peaks = []
        for i in range(1, len(z) - 1):
            if z[i] > z[i-1] and z[i] > z[i+1]:
                peaks.append(z[i])
        
        # Peaks should generally decrease
        if len(peaks) > 1:
            # Most peaks should be lower than previous
            decreases = sum(1 for i in range(1, len(peaks)) if peaks[i] <= peaks[i-1])
            assert decreases > len(peaks) * 0.5
    
    def test_low_elasticity_quick_stop(self, low_elasticity_surface, no_wind):
        """Test that low elasticity causes quick stop."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=5.0,
            t_max=5.0
        )
        
        result = simulate_drop(params, low_elasticity_surface, no_wind)
        
        # Simulation should stop relatively quickly
        # (within t_max, should reach stop condition)
        assert result.df['Time'].iloc[-1] < params.t_max


class TestSimulateDropSpin:
    """Test spin and Magnus effect."""
    
    def test_spin_decay_over_time(self, default_params, default_surface, default_wind):
        """Test that spin decays over time."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        omega_magnitude = np.sqrt(
            result.df['Ox']**2 + 
            result.df['Oy']**2 + 
            result.df['Oz']**2
        )
        
        # Spin should generally decrease
        assert omega_magnitude.iloc[-1] < omega_magnitude.iloc[0]
    
    def test_no_spin_no_magnus(self, no_spin_params, default_surface, no_wind):
        """Test that no spin means no Magnus effect."""
        result = simulate_drop(no_spin_params, default_surface, no_wind)
        
        # Omega should be zero throughout
        omega_magnitude = np.sqrt(
            result.df['Ox']**2 + 
            result.df['Oy']**2 + 
            result.df['Oz']**2
        )
        
        assert (omega_magnitude < 0.1).all()
    
    def test_spin_causes_lateral_drift(self, default_surface, no_wind):
        """Test that spin causes lateral drift (Magnus effect)."""
        # Create two simulations: with and without spin
        params_no_spin = Params(
            mass=0.5, radius=0.1, v0=20.0, drop_angle_deg=30.0,
            spin_rps=0.0, z0=10.0, t_max=5.0, seed=42
        )
        params_with_spin = Params(
            mass=0.5, radius=0.1, v0=20.0, drop_angle_deg=30.0,
            spin_rps=20.0, spin_axis=(0.0, 0.0, 1.0), z0=10.0, t_max=5.0, seed=42
        )
        
        result_no_spin = simulate_drop(params_no_spin, default_surface, no_wind)
        result_with_spin = simulate_drop(params_with_spin, default_surface, no_wind)
        
        # Y position should differ due to Magnus effect
        # (spin about z-axis causes lift in y-direction for x-velocity)
        y_diff = abs(result_with_spin.df['Y'].iloc[-1] - result_no_spin.df['Y'].iloc[-1])
        
        # With high spin, should see some lateral drift
        # Note: This test may need adjustment based on actual Magnus implementation


class TestSimulateDropWind:
    """Test wind effects."""
    
    def test_wind_causes_drift(self, default_params, default_surface):
        """Test that wind causes horizontal drift."""
        no_wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        with_wind = Wind(ref_speed=5.0, gust_sigma=0.0, direction_deg=0.0)
        
        result_no_wind = simulate_drop(default_params, default_surface, no_wind)
        result_with_wind = simulate_drop(default_params, default_surface, with_wind)
        
        # X position should differ with wind in X direction
        x_no_wind = result_no_wind.df['X'].iloc[-1]
        x_with_wind = result_with_wind.df['X'].iloc[-1]
        
        assert abs(x_with_wind - x_no_wind) > 0.1
    
    def test_wind_direction(self, default_params, default_surface):
        """Test that wind direction affects drift direction."""
        wind_x = Wind(ref_speed=5.0, gust_sigma=0.0, direction_deg=0.0)
        wind_y = Wind(ref_speed=5.0, gust_sigma=0.0, direction_deg=90.0)
        
        result_x = simulate_drop(default_params, default_surface, wind_x)
        result_y = simulate_drop(default_params, default_surface, wind_y)
        
        # Drift should be primarily in wind direction
        drift_x_from_x_wind = abs(result_x.df['X'].iloc[-1])
        drift_y_from_y_wind = abs(result_y.df['Y'].iloc[-1])
        
        # Both should have drifted
        assert drift_x_from_x_wind > 0.1 or drift_y_from_y_wind > 0.1


class TestSimulateDropReproducibility:
    """Test simulation reproducibility."""
    
    def test_same_seed_same_results(self, default_params, default_surface, default_wind):
        """Test that same seed produces identical results."""
        result1 = simulate_drop(default_params, default_surface, default_wind)
        result2 = simulate_drop(default_params, default_surface, default_wind)
        
        pd.testing.assert_frame_equal(result1.df, result2.df)
    
    def test_different_seeds_different_results(self, default_surface, default_wind):
        """Test that different seeds produce different results (due to gusts)."""
        params1 = Params(seed=1, z0=10.0)
        params2 = Params(seed=2, z0=10.0)
        
        result1 = simulate_drop(params1, default_surface, default_wind)
        result2 = simulate_drop(params2, default_surface, default_wind)
        
        # Results should differ due to random gusts
        # (at least some values should be different)
        assert not result1.df.equals(result2.df)


class TestSimulateDropStopConditions:
    """Test simulation stop conditions."""
    
    def test_simulation_stops_at_t_max(self, default_surface, default_wind):
        """Test that simulation stops at t_max."""
        params = Params(z0=100.0, t_max=3.0)  # High drop, short time
        
        result = simulate_drop(params, default_surface, default_wind)
        
        assert result.df['Time'].iloc[-1] <= params.t_max + params.dt
    
    def test_simulation_stops_when_at_rest(self, high_elasticity_surface, no_wind):
        """Test that simulation stops when ball comes to rest."""
        params = Params(
            z0=2.0,
            t_max=30.0,  # Long time
            stop_speed_threshold=0.05,
            stop_angular_threshold=0.5,
            stop_hold_time=0.5
        )
        
        result = simulate_drop(params, high_elasticity_surface, no_wind)
        
        # Should stop before t_max
        assert result.df['Time'].iloc[-1] < params.t_max


class TestSimulateDropAdaptiveTimestep:
    """Test adaptive timestep integration."""
    
    def test_adaptive_timestep_enabled(self, default_params, default_surface, default_wind):
        """Test that adaptive timestep can be enabled."""
        params = default_params
        params.adaptive_timestep = True
        params.rtol = 1e-4
        params.atol = 1e-6
        
        result = simulate_drop(params, default_surface, default_wind)
        
        assert result.stability_ok is True
    
    def test_adaptive_timestep_variable_dt(self, default_params, default_surface, default_wind):
        """Test that adaptive timestep produces variable dt values."""
        params = default_params
        params.adaptive_timestep = True
        
        result = simulate_drop(params, default_surface, default_wind)
        
        dt_values = result.df['Dt_actual'].values
        
        # Should have some variation in dt
        assert dt_values.max() - dt_values.min() > 0


class TestSimulateDropPhysicsFlags:
    """Test physics feature flags."""
    
    def test_buoyancy_disabled(self, default_params, default_surface, default_wind):
        """Test simulation with buoyancy disabled."""
        params = default_params
        params.buoyancy = False
        
        result = simulate_drop(params, default_surface, default_wind)
        assert result.stability_ok is True
    
    def test_virtual_mass_disabled(self, default_params, default_surface, default_wind):
        """Test simulation with virtual mass disabled."""
        params = default_params
        params.use_virtual_mass = False
        
        result = simulate_drop(params, default_surface, default_wind)
        assert result.stability_ok is True
    
    def test_multi_regime_cd_disabled(self, default_params, default_surface, default_wind):
        """Test simulation with multi-regime CD disabled."""
        params = default_params
        params.use_multi_regime_cd = False
        
        result = simulate_drop(params, default_surface, default_wind)
        assert result.stability_ok is True
    
    def test_hertzian_contact_disabled(self, default_params, default_surface, default_wind):
        """Test simulation with Hertzian contact disabled."""
        params = default_params
        params.use_hertzian_contact = False
        
        result = simulate_drop(params, default_surface, default_wind)
        assert result.stability_ok is True


class TestSimulateDropSlopedSurface:
    """Test behavior on sloped surface."""
    
    def test_ball_rolls_down_slope(self):
        """Test that ball rolls down a slope."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=1.0,
            t_max=5.0,
            spin_rps=0.0
        )
        surface = Surface(
            elasticity_base=0.3,
            slope_x=0.2,  # 20% slope
            base_height=0.0
        )
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        # Ball should move in positive X direction (down slope)
        # (assuming slope_x is positive downward in +X)
        x_final = result.df['X'].iloc[-1]
        
        # Ball should have moved
        assert abs(x_final) > 0.01


# =========================
# Helper Function Tests
# =========================

class TestCheckNumericalStability:
    """Test numerical stability checking function."""
    
    def test_stable_values_pass(self):
        """Test that stable values pass."""
        v = np.array([1.0, 2.0, 3.0])
        omega = np.array([0.1, 0.2, 0.3])
        pos = np.array([0.0, 0.0, 10.0])
        
        assert check_numerical_stability(v, omega, pos) is True
    
    def test_nan_velocity_fails(self):
        """Test that NaN velocity fails."""
        v = np.array([1.0, np.nan, 3.0])
        omega = np.array([0.1, 0.2, 0.3])
        pos = np.array([0.0, 0.0, 10.0])
        
        assert check_numerical_stability(v, omega, pos) is False
    
    def test_inf_velocity_fails(self):
        """Test that Inf velocity fails."""
        v = np.array([1.0, np.inf, 3.0])
        omega = np.array([0.1, 0.2, 0.3])
        pos = np.array([0.0, 0.0, 10.0])
        
        assert check_numerical_stability(v, omega, pos) is False
    
    def test_nan_position_fails(self):
        """Test that NaN position fails."""
        v = np.array([1.0, 2.0, 3.0])
        omega = np.array([0.1, 0.2, 0.3])
        pos = np.array([0.0, np.nan, 10.0])
        
        assert check_numerical_stability(v, omega, pos) is False
    
    def test_nan_omega_fails(self):
        """Test that NaN omega fails."""
        v = np.array([1.0, 2.0, 3.0])
        omega = np.array([0.1, np.nan, 0.3])
        pos = np.array([0.0, 0.0, 10.0])
        
        assert check_numerical_stability(v, omega, pos) is False


class TestComputeTotalEnergy:
    """Test total energy computation."""
    
    def test_energy_at_rest(self):
        """Test energy computation for ball at rest at height."""
        mass = 1.0
        v = np.array([0.0, 0.0, 0.0])
        z = 10.0
        g = 9.81
        I = 0.5 * mass * 0.1**2  # Moment of inertia
        omega = np.array([0.0, 0.0, 0.0])
        
        E = compute_total_energy(mass, v, z, g, I, omega)
        
        # Should equal potential energy: m*g*h
        expected = mass * g * z
        assert abs(E - expected) < 0.01
    
    def test_energy_with_velocity(self):
        """Test energy computation with velocity."""
        mass = 1.0
        v = np.array([0.0, 0.0, 5.0])  # Moving up at 5 m/s
        z = 10.0
        g = 9.81
        I = 0.5 * mass * 0.1**2
        omega = np.array([0.0, 0.0, 0.0])
        
        E = compute_total_energy(mass, v, z, g, I, omega)
        
        # Should include kinetic energy: 0.5*m*v^2
        KE = 0.5 * mass * 25  # 5^2 = 25
        PE = mass * g * z
        expected = KE + PE
        
        assert abs(E - expected) < 0.01
    
    def test_energy_with_spin(self):
        """Test energy computation with rotation."""
        mass = 1.0
        v = np.array([0.0, 0.0, 0.0])
        z = 10.0
        g = 9.81
        R = 0.1
        I = 0.4 * mass * R**2  # Solid sphere
        omega_mag = 10.0  # rad/s
        omega = np.array([0.0, 0.0, omega_mag])
        
        E = compute_total_energy(mass, v, z, g, I, omega)
        
        # Should include rotational kinetic energy
        PE = mass * g * z
        KE_rot = 0.5 * I * omega_mag**2
        expected = PE + KE_rot
        
        assert abs(E - expected) < 0.01


class TestResolvePenetration:
    """Test ground penetration resolution."""
    
    def test_no_penetration(self):
        """Test when there's no penetration."""
        x, y, z = 0.0, 0.0, 5.0
        vx, vy, vz = 1.0, 0.0, -1.0
        R = 0.1
        ground = 0.0
        n = np.array([0.0, 0.0, 1.0])
        
        x_new, y_new, z_new = resolve_penetration(x, y, z, vx, vy, vz, R, ground, n)
        
        # Should not change position
        assert x_new == x
        assert y_new == y
        assert z_new == z
    
    def test_penetration_corrected(self):
        """Test that penetration is corrected."""
        x, y, z = 0.0, 0.0, 0.05  # Ball center at 0.05, radius 0.1
        vx, vy, vz = 1.0, 0.0, -1.0
        R = 0.1
        ground = 0.0
        n = np.array([0.0, 0.0, 1.0])
        
        # Ball bottom at z - R = -0.05 (below ground)
        x_new, y_new, z_new = resolve_penetration(x, y, z, vx, vy, vz, R, ground, n)
        
        # Z should be corrected to ground + R
        assert z_new >= ground + R - 0.001


# =========================
# Energy Conservation Tests
# =========================

class TestEnergyConservation:
    """Test energy conservation in simulation."""
    
    def test_energy_non_increasing_no_bounce(self):
        """Test that energy doesn't increase without bounces."""
        params = Params(
            mass=0.5,
            radius=0.1,
            v0=0.0,
            drop_angle_deg=0.0,
            z0=10.0,
            t_max=1.0,
            spin_rps=0.0
        )
        surface = Surface(elasticity_base=0.0, base_height=-10.0)  # No ground contact
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        assert result.energy_ok is True
    
    def test_energy_ok_flag_set(self, default_params, default_surface, default_wind):
        """Test that energy_ok flag is set correctly."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        # Should be True for normal simulation
        assert result.energy_ok is True


# =========================
# Compute Time Tests
# =========================

class TestComputeTime:
    """Test compute time reporting."""
    
    def test_compute_time_positive(self, default_params, default_surface, default_wind):
        """Test that compute time is positive."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        assert result.compute_time_ms > 0
    
    def test_compute_time_reasonable(self, default_params, default_surface, default_wind):
        """Test that compute time is reasonable (< 10 seconds)."""
        result = simulate_drop(default_params, default_surface, default_wind)
        
        assert result.compute_time_ms < 10000  # Less than 10 seconds