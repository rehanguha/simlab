"""
Physics constants and functions for ball drop simulation.
Numba JIT-compiled for performance.

Phase 1 Enhanced Physics:
- Multi-regime drag coefficient (Stokes, Schiller-Naumann, Newton, drag crisis)
- Mehta correlation for Magnus effect with spin decay torque
- Air properties with humidity correction and Mach number
- Hertzian contact model with velocity-dependent restitution
- Virtual mass effect for accelerating spheres
"""

import numpy as np
from numba import njit


# =========================
# Physics constants (module-level for Numba)
# =========================
G = 9.80665
R_GAS = 287.058
R_VAPOR = 461.495
T0_ISA = 288.15
P0_ISA = 101325.0
L_ISA = 0.0065
T_REF_VISC = 273.15
MU_REF = 1.716e-5
S_SUTHERLAND = 111.0
TWO_PI = 2.0 * np.pi
GAMMA_AIR = 1.4

RE_STOKES_LIMIT = 1.0
RE_TRANSITION_LIMIT = 1000.0
RE_NEWTON_LIMIT = 3.0e5
RE_CRISIS_LIMIT = 3.5e5
C_ADDED_MASS = 0.5


# =========================
# Air Properties Functions
# =========================

@njit(cache=True)
def isa_air_density_fast(z_m, T0, p0):
    """Calculate air density using International Standard Atmosphere model."""
    z_clip = min(max(z_m, 0.0), 11000.0)
    T = T0 - L_ISA * z_clip
    p = p0 * (T / T0) ** (G / (R_GAS * L_ISA))
    return p / (R_GAS * T)


@njit(cache=True)
def sutherland_viscosity_fast(T):
    """Calculate dynamic viscosity using Sutherland's formula."""
    return MU_REF * ((T / T_REF_VISC) ** 1.5) * (T_REF_VISC + S_SUTHERLAND) / (T + S_SUTHERLAND)


@njit(cache=True)
def saturation_vapor_pressure(T):
    """Calculate saturation vapor pressure using Magnus formula."""
    T_celsius = T - 273.15
    return 611.21 * np.exp((18.678 - T_celsius / 234.5) * (T_celsius / (257.14 + T_celsius)))


@njit(cache=True)
def air_density_with_humidity(T, p, humidity_pct):
    """Calculate air density with humidity correction."""
    e_s = saturation_vapor_pressure(T)
    e = e_s * (humidity_pct / 100.0)
    p_d = p - e
    return p_d / (R_GAS * T) + e / (R_VAPOR * T)


@njit(cache=True)
def air_viscosity_with_humidity(T, humidity_pct):
    """Calculate air viscosity with humidity correction."""
    mu_dry = sutherland_viscosity_fast(T)
    return mu_dry * (1.0 - 0.0004 * (humidity_pct / 100.0))


@njit(cache=True)
def speed_of_sound(T, humidity_pct=0.0):
    """Calculate speed of sound in air with humidity correction."""
    e_s = saturation_vapor_pressure(T)
    e = e_s * (humidity_pct / 100.0)
    x_v = e / P0_ISA
    R_m = R_GAS * (1.0 - 0.378 * x_v)
    gamma_m = GAMMA_AIR * (1.0 - 0.1 * x_v)
    return np.sqrt(gamma_m * R_m * T)


@njit(cache=True)
def mach_number(speed, T, humidity_pct=0.0):
    """Calculate Mach number."""
    return speed / speed_of_sound(T, humidity_pct)


# =========================
# Drag and Lift Functions
# =========================

@njit(cache=True)
def cd_sphere_multi_regime(Re, Ma=0.0, surface_roughness=0.0):
    """
    Calculate drag coefficient for sphere across multiple flow regimes.
    
    Regimes:
    - Stokes (Re <= 1): Cd = 24/Re
    - Transition (1 < Re <= 1000): Schiller-Naumann correlation
    - Newton (1000 < Re <= 3e5): Cd ~ 0.44
    - Drag crisis (3e5 < Re <= 3.5e5): Rapid Cd decrease
    - Post-crisis (Re > 3.5e5): Low Cd regime
    """
    Re = max(Re, 1e-8)
    Re_crit = RE_NEWTON_LIMIT
    Re_crit_end = RE_CRISIS_LIMIT
    
    if surface_roughness > 0:
        rf = min(surface_roughness * 1e4, 0.8)
        Re_crit *= (1.0 - rf * 0.5)
        Re_crit_end *= (1.0 - rf * 0.3)
    
    if Re <= RE_STOKES_LIMIT:
        Cd = 24.0 / Re
    elif Re <= RE_TRANSITION_LIMIT:
        Cd = 24.0 / Re * (1.0 + 0.15 * Re ** 0.687)
    elif Re <= Re_crit:
        Cd = 0.44 + (0.42 / (1.0 + 42500.0 / (Re ** 1.16)) - 0.44) * np.exp(-(Re - RE_TRANSITION_LIMIT) / 500.0)
    elif Re <= Re_crit_end:
        progress = (Re - Re_crit) / (Re_crit_end - Re_crit)
        Cd = 0.44 - 0.35 * progress ** 0.5
    else:
        Cd = max(0.09 + 0.06 * np.exp(-(Re - Re_crit_end) / 1e6), 0.1)
    
    # Compressibility correction
    if Ma > 0.3:
        Cd *= 1.0 + 0.15 * Ma * Ma
    if Ma > 0.8:
        Cd *= 1.0 + 0.5 * (Ma - 0.8) ** 2
    
    return Cd


@njit(cache=True)
def magnus_cl_mehta(Re, spin_param, surface_roughness=0.0):
    """
    Calculate lift coefficient due to Magnus effect using Mehta correlation.
    
    Parameters:
    - Re: Reynolds number
    - spin_param: Non-dimensional spin parameter (ωR/V)
    - surface_roughness: Surface roughness in meters
    """
    S = min(max(spin_param, 0.0), 5.0)
    Cl_base = 0.4 * S / (1.0 + 2.0 * S)
    
    if Re < 1e4:
        Re_factor = max(Re / 1e4, 0.1)
    elif Re > 1e6:
        Re_factor = 1.0 + 0.1 * np.log10(Re / 1e6)
    else:
        Re_factor = 1.0
    
    roughness_factor = 1.0 + 0.2 * min(surface_roughness * 1e3, 1.0)
    return min(Cl_base * Re_factor * roughness_factor, 0.8)


@njit(cache=True)
def aerodynamic_torque_coefficient(Re, spin_param):
    """Calculate aerodynamic torque coefficient for spin decay."""
    if Re < 1.0:
        return 64.0 * np.pi / (Re + 1.0)
    elif Re < 1000.0:
        return 0.5 / (Re ** 0.3) * (1.0 + spin_param)
    else:
        return 0.05 * (1.0 + spin_param * 0.5)


# =========================
# Contact Mechanics Functions
# =========================

@njit(cache=True)
def velocity_dependent_restitution(v_impact, e_ref=0.8, v_ref=1.0, material_param=0.02):
    """
    Calculate velocity-dependent coefficient of restitution using Hertzian contact model.
    
    At low impact velocities, restitution approaches the reference value.
    At higher velocities, restitution decreases due to increased energy dissipation.
    """
    if v_impact <= 0.001:
        return e_ref
    if v_impact <= v_ref:
        return e_ref * (1.0 - 0.1 * (v_ref - v_impact) / v_ref)
    return min(max(e_ref * np.exp(-material_param * np.log(v_impact / v_ref)), 0.1), e_ref)


@njit(cache=True)
def virtual_mass_effect(mass, rho_fluid, volume):
    """Calculate effective mass including virtual mass effect."""
    return mass + C_ADDED_MASS * rho_fluid * volume


# =========================
# Wind and Surface Functions
# =========================

@njit(cache=True)
def ornstein_uhlenbeck_step_fast(x, tau, sigma, dt):
    """Generate Ornstein-Uhlenbeck process step for wind gusts."""
    if tau <= 0 or sigma <= 0:
        return 0.0
    return x - x / tau * dt + sigma * np.sqrt(2.0 / tau) * np.sqrt(dt) * np.random.randn()


@njit(cache=True)
def surface_height_fast(x, y, base_height, slope_x, slope_y, rough_amp, rough_lambda_x):
    """Calculate ground surface height at position (x, y)."""
    z = base_height + slope_x * x + slope_y * y
    if rough_amp > 0 and rough_lambda_x > 1e-6:
        z += rough_amp * np.sin(TWO_PI * x / rough_lambda_x) * np.sin(TWO_PI * y / rough_lambda_x)
    return z


@njit(cache=True)
def surface_normal_fast(x, y, slope_x, slope_y, rough_amp, rough_lambda_x):
    """Calculate surface normal vector at position (x, y)."""
    dzdx, dzdy = slope_x, slope_y
    if rough_amp > 0 and rough_lambda_x > 1e-6:
        k = TWO_PI / rough_lambda_x
        dzdx += rough_amp * k * np.cos(k * x) * np.sin(k * y)
        dzdy += rough_amp * k * np.sin(k * x) * np.cos(k * y)
    n = np.array([-dzdx, -dzdy, 1.0])
    norm = np.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
    return n / norm