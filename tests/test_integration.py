"""
Integration tests for ball drop simulation.
Tests end-to-end workflows and cross-module interactions.
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind
from simulation import simulate_drop
from config_loader import load_config
from reporting import calculate_statistics, export_csv, generate_html_report
from validation import validate_inputs, validate_inputs_or_raise


# =========================
# Full Workflow Tests
# =========================

class TestFullWorkflow:
    """Test complete simulation workflow from config to output."""
    
    def test_full_workflow_from_config(self):
        """Test complete workflow from config file to results."""
        # Load config
        params, surface, wind, output_settings = load_config("config.json")
        
        # Validate inputs
        validate_inputs_or_raise(params, surface, wind)
        
        # Run simulation
        result = simulate_drop(params, surface, wind)
        
        # Check results
        assert result.stability_ok is True
        assert len(result.df) > 0
        
        # Calculate statistics
        stats = calculate_statistics(result)
        assert stats['flight_time'] > 0
    
    def test_full_workflow_with_output_files(self, temp_output_dir):
        """Test complete workflow including file output."""
        # Load and run
        params, surface, wind, _ = load_config("config.json")
        result = simulate_drop(params, surface, wind)
        
        # Generate output files
        csv_path = os.path.join(temp_output_dir, "output.csv")
        html_path = os.path.join(temp_output_dir, "report.html")
        
        csv_result = export_csv(result, csv_path)
        html_result = generate_html_report(result, html_path)
        
        assert os.path.exists(csv_result)
        assert os.path.exists(html_result)


# =========================
# Determinism Tests
# =========================

class TestDeterminism:
    """Test simulation determinism."""
    
    def test_same_seed_produces_identical_trajectory(self):
        """Test that same seed produces identical trajectory."""
        params = Params(seed=123, z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind(gust_sigma=1.0)  # With gusts
        
        result1 = simulate_drop(params, surface, wind)
        result2 = simulate_drop(params, surface, wind)
        
        pd.testing.assert_frame_equal(result1.df, result2.df)
    
    def test_different_seeds_produce_different_trajectories(self):
        """Test that different seeds produce different trajectories."""
        params1 = Params(seed=1, z0=10.0, t_max=5.0)
        params2 = Params(seed=2, z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind(gust_sigma=1.0)  # With gusts
        
        result1 = simulate_drop(params1, surface, wind)
        result2 = simulate_drop(params2, surface, wind)
        
        # Trajectories should differ
        assert not result1.df['X'].equals(result2.df['X'])
    
    def test_zero_gust_sigma_deterministic(self):
        """Test that zero gust sigma makes simulation deterministic."""
        params1 = Params(seed=1, z0=10.0, t_max=5.0)
        params2 = Params(seed=2, z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind(gust_sigma=0.0)  # No gusts
        
        result1 = simulate_drop(params1, surface, wind)
        result2 = simulate_drop(params2, surface, wind)
        
        # Should be identical regardless of seed
        pd.testing.assert_frame_equal(result1.df, result2.df)


# =========================
# Physical Bounds Tests
# =========================

class TestPhysicalBounds:
    """Test that simulation results stay within physical bounds."""
    
    def test_ball_does_not_go_below_ground(self):
        """Test that ball never goes below ground."""
        params = Params(z0=10.0, t_max=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        # Ball bottom (z - radius) should be >= ground
        clearance = result.df['Z'] - params.radius - result.df['Z_ground']
        assert (clearance >= -0.01).all()  # Small tolerance
    
    def test_velocity_does_not_exceed_terminal(self):
        """Test that velocity doesn't greatly exceed terminal velocity."""
        # Terminal velocity for a sphere: v_t = sqrt(2mg / (rho * Cd * A))
        # For our default ball, roughly 10-20 m/s
        params = Params(z0=100.0, t_max=10.0, v0=0.0)  # High drop
        surface = Surface()
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        speed = np.sqrt(
            result.df['Vx']**2 + 
            result.df['Vy']**2 + 
            result.df['Vz']**2
        )
        
        # Should not exceed reasonable terminal velocity (with wind)
        assert speed.max() < 50  # m/s
    
    def test_time_only_moves_forward(self):
        """Test that time is monotonically increasing."""
        params = Params(z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        time_diff = result.df['Time'].diff().dropna()
        assert (time_diff >= 0).all()
    
    def test_reynolds_number_positive(self):
        """Test that Reynolds number is non-negative."""
        params = Params(z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        assert (result.df['Re'] >= 0).all()
    
    def test_air_density_reasonable(self):
        """Test that air density is in reasonable range."""
        params = Params(z0=10.0, t_max=5.0)
        surface = Surface()
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        # Air density should be roughly 0.9 - 1.3 kg/m³
        assert (result.df['AirDensity'] > 0.8).all()
        assert (result.df['AirDensity'] < 1.5).all()


# =========================
# Energy Conservation Tests
# =========================

class TestEnergyConservationIntegration:
    """Test energy conservation in full simulation."""
    
    def test_total_energy_decreases_or_stays_same(self):
        """Test that total energy never increases (ignoring gusts)."""
        params = Params(z0=20.0, v0=0.0, t_max=3.0, spin_rps=0.0)
        surface = Surface(elasticity_base=0.0, base_height=-100.0)  # No ground
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)  # No wind
        
        result = simulate_drop(params, surface, wind)
        
        assert result.energy_ok is True
        assert result.max_energy_gain_pct < 1.0  # Less than 1% energy gain
    
    def test_bounce_reduces_energy(self):
        """Test that bounces reduce energy."""
        params = Params(z0=5.0, v0=0.0, t_max=5.0, spin_rps=0.0)
        surface = Surface(elasticity_base=0.8)
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        # Energy should decrease after each bounce
        # (This is implicitly tested by energy_ok flag)
        assert result.energy_ok is True


# =========================
# Ground Contact Tests
# =========================

class TestGroundContactIntegration:
    """Test ground contact physics."""
    
    def test_velocity_reverses_on_bounce(self):
        """Test that vertical velocity reverses on bounce."""
        params = Params(z0=2.0, v0=0.0, t_max=2.0, spin_rps=0.0)
        surface = Surface(elasticity_base=0.8)
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        # Find where Vz changes sign (bounce)
        vz = result.df['Vz'].values
        
        # Should have at least one sign change
        sign_changes = np.sum(np.diff(np.sign(vz)) != 0)
        assert sign_changes >= 1
    
    def test_bounce_height_decreases(self):
        """Test that bounce heights decrease."""
        params = Params(z0=5.0, v0=0.0, t_max=10.0, spin_rps=0.0)
        surface = Surface(elasticity_base=0.8)
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        z = result.df['Z'].values
        
        # Find local maxima
        peaks = []
        for i in range(1, len(z) - 1):
            if z[i] > z[i-1] and z[i] > z[i+1] and z[i] > params.radius + 0.1:
                peaks.append(z[i])
        
        # Peaks should generally decrease
        if len(peaks) > 1:
            decreases = sum(1 for i in range(1, len(peaks)) if peaks[i] <= peaks[i-1] * 1.01)
            assert decreases > len(peaks) * 0.3


# =========================
# Aerodynamic Effects Tests
# =========================

class TestAerodynamicEffectsIntegration:
    """Test aerodynamic effects in simulation."""
    
    def test_drag_slows_ball(self):
        """Test that drag slows the ball."""
        # Compare with and without drag effect (using very different ball sizes)
        params_small = Params(mass=0.1, radius=0.01, z0=50.0, v0=0.0, t_max=3.0, spin_rps=0.0)
        params_large = Params(mass=0.1, radius=0.2, z0=50.0, v0=0.0, t_max=3.0, spin_rps=0.0)
        
        surface = Surface(base_height=-100.0)  # No ground
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result_small = simulate_drop(params_small, surface, wind)
        result_large = simulate_drop(params_large, surface, wind)
        
        # Large ball should fall slower due to higher drag/mass ratio
        speed_small = np.sqrt(
            result_small.df['Vx']**2 + 
            result_small.df['Vy']**2 + 
            result_small.df['Vz']**2
        ).iloc[-1]
        
        speed_large = np.sqrt(
            result_large.df['Vx']**2 + 
            result_large.df['Vy']**2 + 
            result_large.df['Vz']**2
        ).iloc[-1]
        
        # Small ball should be faster at end
        assert speed_small > speed_large
    
    def test_wind_affects_trajectory(self):
        """Test that wind affects trajectory."""
        params = Params(z0=10.0, v0=10.0, drop_angle_deg=0.0, t_max=3.0, spin_rps=0.0)
        surface = Surface()
        wind_no = Wind(ref_speed=0.0, gust_sigma=0.0)
        wind_yes = Wind(ref_speed=10.0, gust_sigma=0.0, direction_deg=0.0)
        
        result_no = simulate_drop(params, surface, wind_no)
        result_yes = simulate_drop(params, surface, wind_yes)
        
        # X position should differ
        x_diff = abs(result_yes.df['X'].iloc[-1] - result_no.df['X'].iloc[-1])
        assert x_diff > 1.0  # At least 1m difference


# =========================
# Trajectory Shape Tests
# =========================

class TestTrajectoryShape:
    """Test that trajectory shapes are physically reasonable."""
    
    def test_trajectory_has_parabolic_shape(self):
        """Test that trajectory is approximately parabolic."""
        params = Params(z0=5.0, v0=10.0, drop_angle_deg=45.0, t_max=3.0, spin_rps=0.0)
        surface = Surface(base_height=-100.0)  # No ground
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        # For parabolic motion, Z should be quadratic in X
        # z = a*x^2 + b*x + c (approximately)
        x = result.df['X'].values
        z = result.df['Z'].values
        
        # Check that z initially increases then decreases
        assert z[0] < z[len(z)//4]  # Initial rise
        assert z[-1] < z[len(z)//4]  # Final fall
    
    def test_max_height_occurs_early(self):
        """Test that max height occurs in first half of flight."""
        params = Params(z0=5.0, v0=15.0, drop_angle_deg=60.0, t_max=5.0, spin_rps=0.0)
        surface = Surface(elasticity_base=0.0)
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result = simulate_drop(params, surface, wind)
        
        max_height_idx = result.df['Z'].idxmax()
        # Max height should be in first half
        assert max_height_idx < len(result.df) / 2


# =========================
# Multiple Configuration Tests
# =========================

class TestMultipleConfigurations:
    """Test simulation with various configurations."""
    
    def test_heavy_ball_falls_faster(self):
        """Test that heavier ball falls faster (less drag effect)."""
        params_light = Params(mass=0.1, radius=0.1, z0=20.0, v0=0.0, t_max=2.0, spin_rps=0.0)
        params_heavy = Params(mass=10.0, radius=0.1, z0=20.0, v0=0.0, t_max=2.0, spin_rps=0.0)
        
        surface = Surface()
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result_light = simulate_drop(params_light, surface, wind)
        result_heavy = simulate_drop(params_heavy, surface, wind)
        
        # Heavy ball should have higher final speed
        speed_light = np.sqrt(
            result_light.df['Vx']**2 + 
            result_light.df['Vy']**2 + 
            result_light.df['Vz']**2
        ).iloc[-1]
        
        speed_heavy = np.sqrt(
            result_heavy.df['Vx']**2 + 
            result_heavy.df['Vy']**2 + 
            result_heavy.df['Vz']**2
        ).iloc[-1]
        
        assert speed_heavy > speed_light
    
    def test_higher_elasticity_more_bounces(self):
        """Test that higher elasticity produces more bounces."""
        params = Params(z0=3.0, v0=0.0, t_max=10.0, spin_rps=0.0)
        
        surface_low = Surface(elasticity_base=0.3)
        surface_high = Surface(elasticity_base=0.95)
        
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        
        result_low = simulate_drop(params, surface_low, wind)
        result_high = simulate_drop(params, surface_high, wind)
        
        stats_low = calculate_statistics(result_low)
        stats_high = calculate_statistics(result_high)
        
        assert stats_high['bounce_count'] >= stats_low['bounce_count']


# =========================
# Validation Integration Tests
# =========================

class TestValidationIntegration:
    """Test validation integration with simulation."""
    
    def test_invalid_params_raises_before_simulation(self):
        """Test that invalid params raise error before simulation."""
        params = Params(mass=-1.0, z0=10.0)  # Invalid mass
        surface = Surface()
        wind = Wind()
        
        with pytest.raises(Exception):  # ValidationError
            simulate_drop(params, surface, wind)
    
    def test_valid_params_passes_validation(self):
        """Test that valid params pass validation."""
        params = Params(mass=0.5, radius=0.1, z0=10.0)
        surface = Surface()
        wind = Wind()
        
        # Should not raise
        validate_inputs_or_raise(params, surface, wind)


# =========================
# Performance Tests
# =========================

class TestPerformance:
    """Test simulation performance."""
    
    def test_simulation_completes_quickly(self):
        """Test that simulation completes in reasonable time."""
        import time
        
        params = Params(z0=10.0, t_max=10.0)
        surface = Surface()
        wind = Wind()
        
        start = time.time()
        result = simulate_drop(params, surface, wind)
        elapsed = time.time() - start
        
        # Should complete in less than 1 second
        assert elapsed < 1.0
        assert result.compute_time_ms < 1000
    
    def test_long_simulation_completes(self):
        """Test that long simulation completes."""
        params = Params(z0=100.0, t_max=30.0)
        surface = Surface()
        wind = Wind()
        
        result = simulate_drop(params, surface, wind)
        
        assert result.stability_ok is True
        assert len(result.df) > 0