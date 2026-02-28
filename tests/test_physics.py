"""
Comprehensive tests for physimlab.physics module.
Tests physics calculations including aerodynamics and mechanics.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.physics import (
    calculate_density,
    calculate_viscosity,
    calculate_speed_of_sound,
    calculate_reynolds_number,
    calculate_drag_coefficient,
    calculate_magnus_force,
    calculate_wind_force,
    calculate_gravity,
    calculate_terminal_velocity,
    calculate_spin_decay
)


# =========================
# Density Tests
# =========================

class TestDensityCalculation:
    """Test air density calculation."""
    
    def test_sea_level_density(self):
        """Test air density at sea level."""
        rho = calculate_density(288.15, 101325.0, 0.0)
        # Should be approximately 1.225 kg/m³
        assert 1.20 < rho < 1.25
    
    def test_density_decreases_with_altitude(self):
        """Test that density decreases with altitude."""
        rho_sl = calculate_density(288.15, 101325.0, 0.0)
        rho_1000 = calculate_density(281.65, 89876.0, 0.0)  # Approximate ISA at 1000m
        assert rho_1000 < rho_sl
    
    def test_humidity_effect(self):
        """Test that humidity slightly reduces density."""
        rho_dry = calculate_density(293.15, 101325.0, 0.0)
        rho_humid = calculate_density(293.15, 101325.0, 50.0)
        assert rho_humid < rho_dry


# =========================
# Viscosity Tests
# =========================

class TestViscosityCalculation:
    """Test air viscosity calculation."""
    
    def test_reference_viscosity(self):
        """Test viscosity at reference temperature."""
        mu = calculate_viscosity(273.15, 0.0)
        # Should be close to reference value
        assert 1.7e-5 < mu < 1.8e-5
    
    def test_viscosity_increases_with_temperature(self):
        """Test that viscosity increases with temperature."""
        mu_273 = calculate_viscosity(273.15, 0.0)
        mu_300 = calculate_viscosity(300.0, 0.0)
        assert mu_300 > mu_273
    
    def test_humidity_effect_on_viscosity(self):
        """Test humidity effect on viscosity."""
        mu_dry = calculate_viscosity(293.15, 0.0)
        mu_humid = calculate_viscosity(293.15, 100.0)
        # Humidity slightly reduces viscosity
        assert mu_humid < mu_dry


# =========================
# Speed of Sound Tests
# =========================

class TestSpeedOfSound:
    """Test speed of sound calculation."""
    
    def test_sea_level_speed(self):
        """Test speed of sound at sea level."""
        c = calculate_speed_of_sound(288.15, 0.0)
        # Should be approximately 340 m/s
        assert 339 < c < 342
    
    def test_decreases_with_altitude(self):
        """Test that speed of sound decreases with altitude."""
        c_sl = calculate_speed_of_sound(288.15, 0.0)
        c_5000 = calculate_speed_of_sound(255.65, 0.0)  # Approximate ISA at 5000m
        assert c_5000 < c_sl
    
    def test_humidity_effect(self):
        """Test that humidity slightly increases speed of sound."""
        c_dry = calculate_speed_of_sound(293.15, 0.0)
        c_humid = calculate_speed_of_sound(293.15, 100.0)
        assert c_humid > c_dry


# =========================
# Reynolds Number Tests
# =========================

class TestReynoldsNumber:
    """Test Reynolds number calculation."""
    
    def test_typical_reynolds_number(self):
        """Test Reynolds number for typical conditions."""
        Re = calculate_reynolds_number(10.0, 0.2, 288.15, 101325.0, 0.0)
        # Should be in reasonable range
        assert 1000 < Re < 100000
    
    def test_reynolds_increases_with_velocity(self):
        """Test that Reynolds number increases with velocity."""
        Re_5 = calculate_reynolds_number(5.0, 0.2, 288.15, 101325.0, 0.0)
        Re_10 = calculate_reynolds_number(10.0, 0.2, 288.15, 101325.0, 0.0)
        assert Re_10 > Re_5
    
    def test_reynolds_decreases_with_viscosity(self):
        """Test that Reynolds number decreases with viscosity."""
        Re_cold = calculate_reynolds_number(10.0, 0.2, 273.15, 101325.0, 0.0)
        Re_hot = calculate_reynolds_number(10.0, 0.2, 300.0, 101325.0, 0.0)
        assert Re_hot > Re_cold


# =========================
# Drag Coefficient Tests
# =========================

class TestDragCoefficient:
    """Test drag coefficient calculation."""
    
    def test_drag_coefficient_range(self):
        """Test that drag coefficient is in reasonable range."""
        Cd = calculate_drag_coefficient(10000.0, 0.0, 0.0)
        # Should be between 0.1 and 1.0 for typical conditions
        assert 0.1 < Cd < 1.0
    
    def test_drag_crisis(self):
        """Test drag crisis behavior."""
        Cd_before = calculate_drag_coefficient(200000.0, 0.0, 0.0)
        Cd_after = calculate_drag_coefficient(400000.0, 0.0, 0.0)
        # Should show drag crisis (decrease)
        assert Cd_after < Cd_before
    
    def test_mach_effect(self):
        """Test Mach number effect on drag."""
        Cd_subsonic = calculate_drag_coefficient(10000.0, 0.3, 0.0)
        Cd_supersonic = calculate_drag_coefficient(10000.0, 1.2, 0.0)
        # Supersonic should have higher drag
        assert Cd_supersonic > Cd_subsonic


# =========================
# Magnus Force Tests
# =========================

class TestMagnusForce:
    """Test Magnus force calculation."""
    
    def test_zero_spin_no_force(self):
        """Test that zero spin gives zero Magnus force."""
        F = calculate_magnus_force(10.0, 0.0, 10000.0, 1.225, 0.0)
        assert F == 0.0
    
    def test_magnus_force_increases_with_spin(self):
        """Test that Magnus force increases with spin."""
        F_low = calculate_magnus_force(10.0, 5.0, 10000.0, 1.225, 0.0)
        F_high = calculate_magnus_force(10.0, 10.0, 10000.0, 1.225, 0.0)
        assert F_high > F_low
    
    def test_magnus_force_direction(self):
        """Test Magnus force direction."""
        # Spin about z-axis, velocity in x-direction
        # Force should be in y-direction
        omega = np.array([0.0, 0.0, 100.0])
        v = np.array([10.0, 0.0, 0.0])
        F = calculate_magnus_force(v, omega, 10000.0, 1.225, 0.0)
        
        # Force should be perpendicular to both spin and velocity
        assert abs(np.dot(F, omega)) < 1e-10
        assert abs(np.dot(F, v)) < 1e-10


# =========================
# Wind Force Tests
# =========================

class TestWindForce:
    """Test wind force calculation."""
    
    def test_no_wind_no_force(self):
        """Test that no wind gives no force."""
        F = calculate_wind_force(10.0, 0.0, 1.225, 0.0)
        assert F == 0.0
    
    def test_wind_force_increases_with_velocity(self):
        """Test that wind force increases with relative velocity."""
        F_low = calculate_wind_force(5.0, 2.0, 1.225, 0.0)
        F_high = calculate_wind_force(10.0, 2.0, 1.225, 0.0)
        assert F_high > F_low
    
    def test_wind_force_quadratic(self):
        """Test that wind force is quadratic with velocity."""
        F_10 = calculate_wind_force(10.0, 0.0, 1.225, 0.0)
        F_20 = calculate_wind_force(20.0, 0.0, 1.225, 0.0)
        # Should be approximately 4x
        assert 3.5 < F_20 / F_10 < 4.5


# =========================
# Gravity Tests
# =========================

class TestGravity:
    """Test gravity calculation."""
    
    def test_standard_gravity(self):
        """Test standard gravity value."""
        g = calculate_gravity(0.0)
        assert abs(g - 9.81) < 0.01
    
    def test_gravity_decreases_with_altitude(self):
        """Test that gravity decreases with altitude."""
        g_sl = calculate_gravity(0.0)
        g_1000 = calculate_gravity(1000.0)
        assert g_1000 < g_sl
    
    def test_gravity_at_poles_vs_equator(self):
        """Test gravity variation with latitude."""
        g_poles = calculate_gravity(0.0, 90.0)  # Poles
        g_equator = calculate_gravity(0.0, 0.0)  # Equator
        assert g_poles > g_equator


# =========================
# Terminal Velocity Tests
# =========================

class TestTerminalVelocity:
    """Test terminal velocity calculation."""
    
    def test_terminal_velocity_reasonable(self):
        """Test that terminal velocity is reasonable."""
        v_t = calculate_terminal_velocity(0.5, 0.1, 1.225, 0.44)
        # Should be reasonable for a ball
        assert 5 < v_t < 50
    
    def test_terminal_velocity_increases_with_mass(self):
        """Test that terminal velocity increases with mass."""
        v_t_light = calculate_terminal_velocity(0.1, 0.1, 1.225, 0.44)
        v_t_heavy = calculate_terminal_velocity(1.0, 0.1, 1.225, 0.44)
        assert v_t_heavy > v_t_light
    
    def test_terminal_velocity_decreases_with_drag(self):
        """Test that terminal velocity decreases with drag."""
        v_t_low = calculate_terminal_velocity(0.5, 0.1, 1.225, 0.2)
        v_t_high = calculate_terminal_velocity(0.5, 0.1, 1.225, 0.8)
        assert v_t_low > v_t_high


# =========================
# Spin Decay Tests
# =========================

class TestSpinDecay:
    """Test spin decay calculation."""
    
    def test_spin_decay_positive(self):
        """Test that spin decay is positive (slowing down)."""
        decay = calculate_spin_decay(100.0, 10000.0, 0.1, 1.225)
        assert decay > 0
    
    def test_spin_decay_increases_with_spin(self):
        """Test that spin decay increases with spin rate."""
        decay_low = calculate_spin_decay(50.0, 10000.0, 0.1, 1.225)
        decay_high = calculate_spin_decay(100.0, 10000.0, 0.1, 1.225)
        assert decay_high > decay_low
    
    def test_spin_decay_increases_with_density(self):
        """Test that spin decay increases with air density."""
        decay_low = calculate_spin_decay(100.0, 10000.0, 0.1, 1.0)
        decay_high = calculate_spin_decay(100.0, 10000.0, 0.1, 1.5)
        assert decay_high > decay_low


# =========================
# Integration Tests
# =========================

class TestPhysicsIntegration:
    """Integration tests combining multiple physics functions."""
    
    def test_complete_physics_calculation(self):
        """Test complete physics calculation chain."""
        # Given conditions
        T = 288.15  # K
        p = 101325.0  # Pa
        humidity = 0.0  # %
        v = 10.0  # m/s
        omega = 100.0  # rad/s
        R = 0.1  # m
        m = 0.5  # kg
        
        # Calculate physics
        rho = calculate_density(T, p, humidity)
        mu = calculate_viscosity(T, humidity)
        Re = calculate_reynolds_number(v, 2*R, T, p, humidity)
        Cd = calculate_drag_coefficient(Re, 0.0, 0.0)
        F_drag = 0.5 * rho * Cd * np.pi * R**2 * v**2
        
        # Should be reasonable
        assert 0.1 < F_drag < 10.0
        assert 1000 < Re < 100000
    
    def test_terminal_velocity_consistency(self):
        """Test terminal velocity consistency with drag."""
        m = 0.5
        R = 0.1
        rho = 1.225
        
        v_t = calculate_terminal_velocity(m, R, rho, 0.44)
        
        # At terminal velocity, drag should equal weight
        A = np.pi * R**2
        F_drag = 0.5 * rho * 0.44 * A * v_t**2
        F_weight = m * 9.81
        
        assert abs(F_drag - F_weight) / F_weight < 0.01
    
    def test_magnus_force_scaling(self):
        """Test Magnus force scaling with parameters."""
        # Base case
        F_base = calculate_magnus_force(10.0, 100.0, 10000.0, 1.225, 0.0)
        
        # Double velocity
        F_double_v = calculate_magnus_force(20.0, 100.0, 10000.0, 1.225, 0.0)
        
        # Double spin
        F_double_omega = calculate_magnus_force(10.0, 200.0, 10000.0, 1.225, 0.0)
        
        # Should scale appropriately
        assert 1.8 < F_double_v / F_base < 2.2
        assert 1.8 < F_double_omega / F_base < 2.2
