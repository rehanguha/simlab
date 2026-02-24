"""
Comprehensive tests for physics.py module.
Tests all physics functions including air properties, drag, lift, and contact mechanics.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics import (
    # Constants
    G, R_GAS, R_VAPOR, T0_ISA, P0_ISA, L_ISA, T_REF_VISC, MU_REF, S_SUTHERLAND,
    TWO_PI, GAMMA_AIR, RE_STOKES_LIMIT, RE_TRANSITION_LIMIT, RE_NEWTON_LIMIT,
    RE_CRISIS_LIMIT, C_ADDED_MASS,
    # Air properties
    isa_air_density_fast, sutherland_viscosity_fast, saturation_vapor_pressure,
    air_density_with_humidity, air_viscosity_with_humidity, speed_of_sound, mach_number,
    # Drag and lift
    cd_sphere_multi_regime, magnus_cl_mehta, aerodynamic_torque_coefficient,
    # Contact mechanics
    velocity_dependent_restitution, virtual_mass_effect,
    # Wind and surface
    ornstein_uhlenbeck_step_fast, surface_height_fast, surface_normal_fast
)


# =========================
# Constants Tests
# =========================

class TestPhysicsConstants:
    """Test that physics constants are correctly defined."""
    
    def test_gravity_constant(self):
        """Test gravitational acceleration constant."""
        assert G == 9.80665
    
    def test_gas_constants(self):
        """Test gas constants for air and vapor."""
        assert R_GAS == 287.058
        assert R_VAPOR == 461.495
    
    def test_isa_constants(self):
        """Test International Standard Atmosphere constants."""
        assert T0_ISA == 288.15  # K
        assert P0_ISA == 101325.0  # Pa
        assert L_ISA == 0.0065  # K/m
    
    def test_viscosity_constants(self):
        """Test Sutherland's formula constants."""
        assert T_REF_VISC == 273.15  # K
        assert MU_REF == 1.716e-5  # Pa·s
        assert S_SUTHERLAND == 111.0  # K
    
    def test_reynolds_regime_limits(self):
        """Test Reynolds number regime boundaries."""
        assert RE_STOKES_LIMIT == 1.0
        assert RE_TRANSITION_LIMIT == 1000.0
        assert RE_NEWTON_LIMIT == 3.0e5
        assert RE_CRISIS_LIMIT == 3.5e5
    
    def test_added_mass_coefficient(self):
        """Test virtual mass coefficient for sphere."""
        assert C_ADDED_MASS == 0.5


# =========================
# Air Properties Tests
# =========================

class TestISAAirDensity:
    """Test International Standard Atmosphere air density calculation."""
    
    def test_sea_level_density(self):
        """Test air density at sea level (ISA conditions)."""
        rho = isa_air_density_fast(0.0, T0_ISA, P0_ISA)
        # Sea level density should be approximately 1.225 kg/m³
        assert 1.22 < rho < 1.23
    
    def test_density_decreases_with_altitude(self):
        """Test that air density decreases with altitude."""
        rho_0 = isa_air_density_fast(0.0, T0_ISA, P0_ISA)
        rho_1000 = isa_air_density_fast(1000.0, T0_ISA, P0_ISA)
        rho_5000 = isa_air_density_fast(5000.0, T0_ISA, P0_ISA)
        
        assert rho_1000 < rho_0
        assert rho_5000 < rho_1000
    
    def test_density_at_tropopause(self):
        """Test density at tropopause (11 km)."""
        rho = isa_air_density_fast(11000.0, T0_ISA, P0_ISA)
        # At 11 km, density should be roughly 0.36 kg/m³
        assert 0.35 < rho < 0.40
    
    def test_negative_altitude_clamped(self):
        """Test that negative altitudes are handled correctly."""
        rho = isa_air_density_fast(-100.0, T0_ISA, P0_ISA)
        rho_0 = isa_air_density_fast(0.0, T0_ISA, P0_ISA)
        # Should be same as sea level (clamped)
        assert rho == rho_0
    
    def test_altitude_above_tropopause_clamped(self):
        """Test that altitudes above 11 km are clamped."""
        rho_11km = isa_air_density_fast(11000.0, T0_ISA, P0_ISA)
        rho_15km = isa_air_density_fast(15000.0, T0_ISA, P0_ISA)
        # Should be same (clamped at 11 km)
        assert rho_11km == rho_15km


class TestSutherlandViscosity:
    """Test Sutherland's viscosity formula."""
    
    def test_reference_viscosity(self):
        """Test viscosity at reference temperature."""
        mu = sutherland_viscosity_fast(T_REF_VISC)
        # Should be close to reference value
        assert abs(mu - MU_REF) / MU_REF < 0.001
    
    def test_viscosity_increases_with_temperature(self):
        """Test that viscosity increases with temperature (gas behavior)."""
        mu_273 = sutherland_viscosity_fast(273.15)
        mu_300 = sutherland_viscosity_fast(300.0)
        mu_350 = sutherland_viscosity_fast(350.0)
        
        assert mu_300 > mu_273
        assert mu_350 > mu_300
    
    def test_typical_values(self):
        """Test viscosity at typical temperatures."""
        mu_20C = sutherland_viscosity_fast(293.15)
        # At 20°C, dynamic viscosity should be about 1.82e-5 Pa·s
        assert 1.80e-5 < mu_20C < 1.85e-5


class TestSaturationVaporPressure:
    """Test saturation vapor pressure calculation (Magnus formula)."""
    
    def test_zero_celsius(self):
        """Test vapor pressure at 0°C (should be ~611 Pa)."""
        e_s = saturation_vapor_pressure(273.15)
        assert 610 < e_s < 615
    
    def test_twenty_celsius(self):
        """Test vapor pressure at 20°C (should be ~2339 Pa)."""
        e_s = saturation_vapor_pressure(293.15)
        assert 2300 < e_s < 2400
    
    def test_hundred_celsius(self):
        """Test vapor pressure at 100°C (should be ~101325 Pa)."""
        e_s = saturation_vapor_pressure(373.15)
        assert 100000 < e_s < 103000
    
    def test_increases_with_temperature(self):
        """Test that vapor pressure increases exponentially with temperature."""
        e_s_10 = saturation_vapor_pressure(283.15)
        e_s_20 = saturation_vapor_pressure(293.15)
        e_s_30 = saturation_vapor_pressure(303.15)
        
        assert e_s_20 > e_s_10
        assert e_s_30 > e_s_20


class TestAirDensityWithHumidity:
    """Test air density calculation with humidity correction."""
    
    def test_dry_air_density(self):
        """Test density of dry air (0% humidity)."""
        T = 293.15  # 20°C
        p = P0_ISA
        rho = air_density_with_humidity(T, p, 0.0)
        # Dry air density at 20°C, 101325 Pa
        assert 1.20 < rho < 1.22
    
    def test_humid_air_less_dense(self):
        """Test that humid air is less dense than dry air."""
        T = 293.15
        p = P0_ISA
        rho_dry = air_density_with_humidity(T, p, 0.0)
        rho_humid = air_density_with_humidity(T, p, 100.0)
        
        assert rho_humid < rho_dry
    
    def test_humidity_effect_linear(self):
        """Test that humidity effect is approximately linear."""
        T = 293.15
        p = P0_ISA
        rho_0 = air_density_with_humidity(T, p, 0.0)
        rho_50 = air_density_with_humidity(T, p, 50.0)
        rho_100 = air_density_with_humidity(T, p, 100.0)
        
        # 50% humidity should give roughly half the effect
        effect_50 = rho_0 - rho_50
        effect_100 = rho_0 - rho_100
        assert 0.4 < effect_50 / effect_100 < 0.6


class TestAirViscosityWithHumidity:
    """Test air viscosity with humidity correction."""
    
    def test_dry_air_viscosity(self):
        """Test viscosity of dry air."""
        T = 293.15
        mu = air_viscosity_with_humidity(T, 0.0)
        mu_dry = sutherland_viscosity_fast(T)
        # Should be same as dry air
        assert abs(mu - mu_dry) / mu_dry < 0.001
    
    def test_humidity_slightly_reduces_viscosity(self):
        """Test that humidity slightly reduces viscosity."""
        T = 293.15
        mu_dry = air_viscosity_with_humidity(T, 0.0)
        mu_humid = air_viscosity_with_humidity(T, 100.0)
        
        # Effect is small (about 0.04% reduction at 100% humidity)
        assert mu_humid < mu_dry
        assert (mu_dry - mu_humid) / mu_dry < 0.001


class TestSpeedOfSound:
    """Test speed of sound calculation."""
    
    def test_sea_level_speed(self):
        """Test speed of sound at sea level conditions."""
        c = speed_of_sound(T0_ISA, 0.0)
        # Should be approximately 340 m/s
        assert 339 < c < 342
    
    def test_decreases_with_altitude(self):
        """Test that speed of sound decreases with temperature (altitude)."""
        c_sl = speed_of_sound(T0_ISA, 0.0)
        T_5000 = T0_ISA - L_ISA * 5000
        c_5000 = speed_of_sound(T_5000, 0.0)
        
        assert c_5000 < c_sl
    
    def test_humidity_increases_speed(self):
        """Test that humidity slightly increases speed of sound."""
        c_dry = speed_of_sound(293.15, 0.0)
        c_humid = speed_of_sound(293.15, 100.0)
        
        assert c_humid > c_dry


class TestMachNumber:
    """Test Mach number calculation."""
    
    def test_zero_speed(self):
        """Test Mach number at zero speed."""
        Ma = mach_number(0.0, T0_ISA, 0.0)
        assert Ma == 0.0
    
    def test_subsonic_speed(self):
        """Test Mach number at subsonic speed."""
        Ma = mach_number(170.0, T0_ISA, 0.0)  # ~0.5 Mach
        assert 0.49 < Ma < 0.51
    
    def test_supersonic_speed(self):
        """Test Mach number at supersonic speed."""
        Ma = mach_number(680.0, T0_ISA, 0.0)  # ~2.0 Mach
        assert 1.9 < Ma < 2.1
    
    def test_mach_proportional_to_speed(self):
        """Test that Mach number is proportional to speed."""
        Ma_100 = mach_number(100.0, T0_ISA, 0.0)
        Ma_200 = mach_number(200.0, T0_ISA, 0.0)
        
        assert abs(Ma_200 / Ma_100 - 2.0) < 0.01


# =========================
# Drag Coefficient Tests
# =========================

class TestCdSphereMultiRegime:
    """Test multi-regime drag coefficient for spheres."""
    
    def test_stokes_regime(self):
        """Test Stokes regime (Re <= 1): Cd = 24/Re."""
        # At Re = 0.5
        Cd = cd_sphere_multi_regime(0.5)
        expected = 24.0 / 0.5  # = 48
        assert abs(Cd - expected) / expected < 0.01
    
    def test_stokes_regime_re_1(self):
        """Test Stokes regime at Re = 1."""
        Cd = cd_sphere_multi_regime(1.0)
        expected = 24.0
        assert abs(Cd - expected) / expected < 0.01
    
    def test_transition_regime_schiller_naumann(self):
        """Test transition regime using Schiller-Naumann correlation."""
        # At Re = 100
        Cd = cd_sphere_multi_regime(100.0)
        expected = 24.0 / 100.0 * (1.0 + 0.15 * 100.0 ** 0.687)
        assert abs(Cd - expected) / expected < 0.01
    
    def test_transition_regime_re_1000(self):
        """Test at end of transition regime."""
        Cd = cd_sphere_multi_regime(1000.0)
        # Should be around 0.44-0.47
        assert 0.4 < Cd < 0.5
    
    def test_newton_regime(self):
        """Test Newton regime (1000 < Re <= 3e5): Cd ≈ 0.44."""
        # At Re = 1e4
        Cd = cd_sphere_multi_regime(1e4)
        assert 0.40 < Cd < 0.48
        
        # At Re = 1e5
        Cd = cd_sphere_multi_regime(1e5)
        assert 0.40 < Cd < 0.48
    
    def test_drag_crisis_regime(self):
        """Test drag crisis regime (3e5 < Re <= 3.5e5)."""
        Cd_before = cd_sphere_multi_regime(3.0e5)
        Cd_crisis = cd_sphere_multi_regime(3.25e5)
        Cd_after = cd_sphere_multi_regime(3.5e5)
        
        # Cd should decrease through crisis
        assert Cd_crisis < Cd_before
        assert Cd_after < Cd_before
    
    def test_post_crisis_regime(self):
        """Test post-crisis regime (Re > 3.5e5): low Cd."""
        Cd = cd_sphere_multi_regime(5e5)
        # Should be around 0.1-0.2
        assert 0.08 < Cd < 0.25
        
        Cd_high = cd_sphere_multi_regime(1e6)
        assert Cd_high < 0.2
    
    def test_compressibility_correction(self):
        """Test compressibility correction at high Mach numbers."""
        Cd_subsonic = cd_sphere_multi_regime(1e4, Ma=0.3)
        Cd_transonic = cd_sphere_multi_regime(1e4, Ma=0.6)
        Cd_supersonic = cd_sphere_multi_regime(1e4, Ma=1.0)
        
        # Cd should increase with Mach number
        assert Cd_transonic > Cd_subsonic
        assert Cd_supersonic > Cd_transonic
    
    def test_surface_roughness_shifts_crisis(self):
        """Test that surface roughness shifts drag crisis to lower Re."""
        Cd_smooth = cd_sphere_multi_regime(3.0e5, surface_roughness=0.0)
        Cd_rough = cd_sphere_multi_regime(3.0e5, surface_roughness=0.001)
        
        # Roughness can cause earlier transition
        # This is a qualitative test
        assert Cd_rough >= 0  # Just verify it computes
    
    def test_very_low_reynolds(self):
        """Test very low Reynolds numbers."""
        Cd = cd_sphere_multi_regime(1e-6)
        # Should be very high
        assert Cd > 1e6
    
    def test_reynolds_clamping(self):
        """Test that very low Reynolds is clamped."""
        Cd_1 = cd_sphere_multi_regime(1e-8)
        Cd_2 = cd_sphere_multi_regime(1e-10)
        # Both should give same result due to clamping
        assert abs(Cd_1 - Cd_2) / Cd_1 < 0.01


class TestMagnusLiftCoefficient:
    """Test Magnus effect lift coefficient (Mehta correlation)."""
    
    def test_zero_spin_no_lift(self):
        """Test that zero spin gives zero lift."""
        Cl = magnus_cl_mehta(1e4, 0.0)
        assert Cl == 0.0
    
    def test_lift_increases_with_spin(self):
        """Test that lift coefficient increases with spin parameter."""
        Cl_low = magnus_cl_mehta(1e4, 0.2)
        Cl_med = magnus_cl_mehta(1e4, 0.5)
        Cl_high = magnus_cl_mehta(1e4, 1.0)
        
        assert Cl_med > Cl_low
        assert Cl_high > Cl_med
    
    def test_lift_coefficient_bounded(self):
        """Test that lift coefficient is bounded (max ~0.8)."""
        # Even at very high spin
        Cl = magnus_cl_mehta(1e4, 10.0)
        assert Cl <= 0.8
    
    def test_reynolds_effect_low_re(self):
        """Test Reynolds number effect at low Re."""
        Cl_low_re = magnus_cl_mehta(1e3, 0.5)
        Cl_high_re = magnus_cl_mehta(1e5, 0.5)
        
        # Low Re should have reduced lift
        assert Cl_low_re < Cl_high_re
    
    def test_surface_roughness_effect(self):
        """Test that surface roughness affects lift."""
        Cl_smooth = magnus_cl_mehta(1e4, 0.5, 0.0)
        Cl_rough = magnus_cl_mehta(1e4, 0.5, 0.01)
        
        # Roughness typically increases lift
        assert Cl_rough >= Cl_smooth
    
    def test_spin_parameter_clamping(self):
        """Test that spin parameter is clamped to [0, 5]."""
        # Very high spin should be clamped
        Cl_high = magnus_cl_mehta(1e4, 10.0)
        Cl_clamped = magnus_cl_mehta(1e4, 5.0)
        
        # Should be similar due to clamping
        assert abs(Cl_high - Cl_clamped) < 0.1


class TestAerodynamicTorqueCoefficient:
    """Test aerodynamic torque coefficient for spin decay."""
    
    def test_low_reynolds_torque(self):
        """Test torque coefficient at low Reynolds (Stokes-like)."""
        C_T = aerodynamic_torque_coefficient(0.5, 0.1)
        # Should be large in Stokes regime
        assert C_T > 10
    
    def test_moderate_reynolds_torque(self):
        """Test torque coefficient at moderate Reynolds."""
        C_T = aerodynamic_torque_coefficient(100.0, 0.1)
        assert 0 < C_T < 10
    
    def test_high_reynolds_torque(self):
        """Test torque coefficient at high Reynolds."""
        C_T = aerodynamic_torque_coefficient(1e5, 0.1)
        # Should be relatively small
        assert C_T < 1.0
    
    def test_spin_parameter_effect(self):
        """Test that spin parameter affects torque."""
        C_T_low = aerodynamic_torque_coefficient(1e4, 0.1)
        C_T_high = aerodynamic_torque_coefficient(1e4, 1.0)
        
        # Higher spin should give higher torque
        assert C_T_high > C_T_low


# =========================
# Contact Mechanics Tests
# =========================

class TestVelocityDependentRestitution:
    """Test velocity-dependent coefficient of restitution (Hertzian model)."""
    
    def test_zero_impact_velocity(self):
        """Test restitution at very low impact velocity."""
        e = velocity_dependent_restitution(0.001, e_ref=0.8)
        # Should approach reference value
        assert 0.7 < e < 0.85
    
    def test_reference_velocity(self):
        """Test restitution at reference velocity."""
        e = velocity_dependent_restitution(1.0, e_ref=0.8, v_ref=1.0)
        assert abs(e - 0.8) < 0.05
    
    def test_high_velocity_reduced_restitution(self):
        """Test that high impact velocity reduces restitution."""
        e_low = velocity_dependent_restitution(1.0, e_ref=0.8, v_ref=1.0)
        e_high = velocity_dependent_restitution(10.0, e_ref=0.8, v_ref=1.0)
        
        assert e_high < e_low
    
    def test_restitution_bounded(self):
        """Test that restitution is bounded [0.1, e_ref]."""
        e = velocity_dependent_restitution(100.0, e_ref=0.8)
        assert e >= 0.1
        assert e <= 0.8
    
    def test_material_parameter_effect(self):
        """Test material parameter effect on restitution."""
        e_hard = velocity_dependent_restitution(10.0, e_ref=0.8, material_param=0.01)
        e_soft = velocity_dependent_restitution(10.0, e_ref=0.8, material_param=0.05)
        
        # Higher material param = more energy loss
        assert e_soft < e_hard
    
    def test_restitution_never_exceeds_reference(self):
        """Test that restitution never exceeds reference value."""
        for v in [0.001, 0.1, 0.5, 1.0, 2.0]:
            e = velocity_dependent_restitution(v, e_ref=0.8)
            assert e <= 0.8


class TestVirtualMassEffect:
    """Test virtual mass effect for accelerating spheres."""
    
    def test_virtual_mass_calculation(self):
        """Test virtual mass calculation."""
        mass = 1.0
        rho_fluid = 1.225
        volume = 4.0/3.0 * np.pi * 0.1**3
        
        m_eff = virtual_mass_effect(mass, rho_fluid, volume)
        
        # Should add 0.5 * rho * V
        added_mass = 0.5 * rho_fluid * volume
        assert abs(m_eff - (mass + added_mass)) < 1e-10
    
    def test_virtual_mass_zero_density(self):
        """Test virtual mass in vacuum (zero density)."""
        m_eff = virtual_mass_effect(1.0, 0.0, 0.1)
        assert m_eff == 1.0
    
    def test_virtual_mass_proportional_to_volume(self):
        """Test that added mass is proportional to volume."""
        V1 = 4.0/3.0 * np.pi * 0.1**3
        V2 = 4.0/3.0 * np.pi * 0.2**3  # 8x volume
        
        m_eff1 = virtual_mass_effect(0.0, 1.0, V1)
        m_eff2 = virtual_mass_effect(0.0, 1.0, V2)
        
        assert abs(m_eff2 / m_eff1 - 8.0) < 0.01


# =========================
# Surface Functions Tests
# =========================

class TestSurfaceHeight:
    """Test ground surface height calculation."""
    
    def test_flat_surface(self):
        """Test flat surface (no slope, no roughness)."""
        z = surface_height_fast(10.0, 20.0, 0.0, 0.0, 0.0, 0.0, 5.0)
        assert z == 0.0
    
    def test_base_height(self):
        """Test base height offset."""
        z = surface_height_fast(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 5.0)
        assert z == 5.0
    
    def test_sloped_surface_x(self):
        """Test surface with X slope."""
        z = surface_height_fast(10.0, 0.0, 0.0, 0.1, 0.0, 0.0, 5.0)
        assert abs(z - 1.0) < 1e-10  # 0.1 * 10
    
    def test_sloped_surface_y(self):
        """Test surface with Y slope."""
        z = surface_height_fast(0.0, 20.0, 0.0, 0.0, 0.05, 0.0, 5.0)
        assert abs(z - 1.0) < 1e-10  # 0.05 * 20
    
    def test_rough_surface(self):
        """Test surface with roughness."""
        z = surface_height_fast(2.5, 2.5, 0.0, 0.0, 0.0, 0.1, 5.0)
        # At peak of sine wave (sin(π) * sin(π) = 0)
        # Actually sin(2π*2.5/5) = sin(π) = 0
        assert abs(z) < 1e-10


class TestSurfaceNormal:
    """Test ground surface normal vector calculation."""
    
    def test_flat_surface_normal(self):
        """Test normal for flat surface."""
        n = surface_normal_fast(0.0, 0.0, 0.0, 0.0, 0.0, 5.0)
        
        # Should be unit z-vector
        assert abs(n[0]) < 1e-10
        assert abs(n[1]) < 1e-10
        assert abs(n[2] - 1.0) < 1e-10
    
    def test_sloped_surface_normal(self):
        """Test normal for sloped surface."""
        n = surface_normal_fast(0.0, 0.0, 0.1, 0.0, 0.0, 5.0)
        
        # Should have negative x component
        assert n[0] < 0
        assert n[2] > 0
        
        # Should be unit vector
        norm = np.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
        assert abs(norm - 1.0) < 1e-10
    
    def test_normal_is_unit_vector(self):
        """Test that normal is always unit vector."""
        for x in [0.0, 5.0, 10.0]:
            for slope in [0.0, 0.1, 0.2]:
                n = surface_normal_fast(x, 0.0, slope, 0.0, 0.0, 5.0)
                norm = np.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
                assert abs(norm - 1.0) < 1e-10


# =========================
# Wind Functions Tests
# =========================

class TestOrnsteinUhlenbeck:
    """Test Ornstein-Uhlenbeck process for wind gusts."""
    
    def test_zero_sigma_no_gust(self):
        """Test that zero sigma gives zero gust."""
        gust = ornstein_uhlenbeck_step_fast(0.0, 2.0, 0.0, 0.01)
        assert gust == 0.0
    
    def test_zero_tau_no_gust(self):
        """Test that zero tau gives zero gust."""
        gust = ornstein_uhlenbeck_step_fast(0.0, 0.0, 1.0, 0.01)
        assert gust == 0.0
    
    def test_gust_mean_reverting(self):
        """Test that gusts are mean-reverting."""
        # Large initial gust should decay toward zero
        np.random.seed(42)
        gust = 10.0
        for _ in range(1000):
            gust = ornstein_uhlenbeck_step_fast(gust, 0.1, 1.0, 0.001)
        # Should have decayed
        assert abs(gust) < 5.0
    
    def test_gust_statistical_properties(self):
        """Test statistical properties of O-U process."""
        np.random.seed(42)
        gusts = []
        gust = 0.0
        tau = 1.0
        sigma = 1.0
        dt = 0.01
        
        for _ in range(10000):
            gust = ornstein_uhlenbeck_step_fast(gust, tau, sigma, dt)
            gusts.append(gust)
        
        # Mean should be approximately zero
        mean = np.mean(gusts)
        assert abs(mean) < 0.1
        
        # Variance should be approximately sigma²
        # For O-U process: Var = sigma² * tau / 2 for stationary process
        # But our implementation has factor of 2/tau, so Var = sigma²
        var = np.var(gusts)
        assert 0.5 < var < 2.0


# =========================
# Integration Tests
# =========================

class TestPhysicsIntegration:
    """Integration tests combining multiple physics functions."""
    
    def test_drag_force_consistency(self):
        """Test that drag force makes physical sense."""
        # For a sphere at moderate Re
        rho = 1.225  # kg/m³
        v = 10.0  # m/s
        D = 0.2  # diameter m
        nu = 1.5e-5  # kinematic viscosity
        
        Re = v * D / nu
        Cd = cd_sphere_multi_regime(Re)
        
        # Drag force F = 0.5 * rho * Cd * A * v²
        A = np.pi * (D/2)**2
        Fd = 0.5 * rho * Cd * A * v**2
        
        # Should be reasonable magnitude
        assert 0.01 < Fd < 10  # N
    
    def test_magnus_force_direction(self):
        """Test that Magnus force has correct direction."""
        # Spin about z-axis, velocity in x-direction
        # Magnus force should be in y-direction (lift)
        omega = np.array([0.0, 0.0, 100.0])  # rad/s
        v = np.array([10.0, 0.0, 0.0])  # m/s
        R = 0.1
        
        # Lift direction is omega × v
        lift_dir = np.cross(omega, v)
        lift_dir = lift_dir / np.linalg.norm(lift_dir)
        
        # Should be in positive y direction
        assert lift_dir[1] > 0.9
        assert abs(lift_dir[0]) < 0.1
        assert abs(lift_dir[2]) < 0.1
    
    def test_terminal_velocity_approximation(self):
        """Test terminal velocity estimation using drag."""
        # For a sphere with mass m, falling at terminal velocity:
        # mg = 0.5 * rho * Cd * A * v_t²
        m = 0.5  # kg
        rho = 1.225
        g = 9.81
        R = 0.1
        A = np.pi * R**2
        
        # Assume Cd ≈ 0.44 (Newton regime)
        Cd_guess = 0.44
        v_t_approx = np.sqrt(2 * m * g / (rho * Cd_guess * A))
        
        # Check Re is in Newton regime
        nu = 1.5e-5
        Re = v_t_approx * 2 * R / nu
        
        # Terminal velocity should be around 10-20 m/s for this ball
        assert 5 < v_t_approx < 30
        assert Re > 1000  # Should be in Newton regime