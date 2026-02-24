"""
Core simulation engine for ball drop simulation.
Numba JIT-compiled for performance with adaptive timestep support.
"""

import numpy as np
import pandas as pd
from numba import njit
from typing import Tuple

from physics import (
    TWO_PI, T0_ISA, P0_ISA, L_ISA, R_GAS, G,
    mach_number, cd_sphere_multi_regime, magnus_cl_mehta,
    aerodynamic_torque_coefficient, velocity_dependent_restitution,
    virtual_mass_effect, ornstein_uhlenbeck_step_fast,
    surface_height_fast, surface_normal_fast,
    air_density_with_humidity, air_viscosity_with_humidity
)
from models import Params, Surface, Wind, SimulationResult
from validation import validate_inputs_or_raise


# RK45 Dormand-Prince coefficients (module-level for Numba)
RK45_A = np.array([0.0, 0.2, 0.3, 0.8, 8/9, 1.0, 1.0])
RK45_B = np.array([
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [1/5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [3/40, 9/40, 0.0, 0.0, 0.0, 0.0, 0.0],
    [44/45, -56/15, 32/9, 0.0, 0.0, 0.0, 0.0],
    [19372/6561, -25360/2187, 64448/6561, -212/729, 0.0, 0.0, 0.0],
    [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0.0, 0.0],
    [35/384, 0.0, 500/1113, 125/192, -2187/6784, 11/84, 0.0]
])
RK45_C4 = np.array([35/384, 0.0, 500/1113, 125/192, -2187/6784, 11/84, 0.0])
RK45_C5 = np.array([5179/57600, 0.0, 7571/16695, 393/640, -92097/339200, 187/2100, 1/40])


# =========================
# Stability Functions
# =========================

@njit(cache=True)
def check_numerical_stability(v, omega, pos):
    """Check for NaN/Inf in state variables. Returns True if stable."""
    for i in range(3):
        if np.isnan(v[i]) or np.isinf(v[i]):
            return False
        if np.isnan(omega[i]) or np.isinf(omega[i]):
            return False
        if np.isnan(pos[i]) or np.isinf(pos[i]):
            return False
    return True


@njit(cache=True)
def compute_total_energy(mass, v, z, g, I, omega):
    """Compute total mechanical energy (KE + PE + rotational KE)."""
    KE_trans = 0.5 * mass * (v[0]**2 + v[1]**2 + v[2]**2)
    PE = mass * g * z
    KE_rot = 0.5 * I * (omega[0]**2 + omega[1]**2 + omega[2]**2)
    return KE_trans + PE + KE_rot


@njit(cache=True)
def resolve_penetration(x, y, z, vx, vy, vz, R, ground_func_val, n, max_fix=0.1):
    """Resolve ground penetration with position and velocity correction."""
    penetration = (ground_func_val + R) - z
    if penetration > 0:
        fix = min(penetration, max_fix)
        x += n[0] * fix
        y += n[1] * fix
        z = ground_func_val + R
    return x, y, z


# =========================
# Core Derivatives
# =========================

@njit(cache=True)
def compute_derivatives(state, mass, radius, rho, mu, T_air, humidity_pct,
                        w_x, w_y, omega, buoyancy, g, V_sphere, A, I_sphere,
                        surface_roughness, use_virtual_mass, use_multi_regime_cd):
    """Compute derivatives for RK45 integration."""
    x, y, z, vx, vy, vz = state[0:6]
    
    R = radius
    v_rel_x = vx - w_x
    v_rel_y = vy - w_y
    v_rel_z = vz
    speed = np.sqrt(v_rel_x**2 + v_rel_y**2 + v_rel_z**2) + 1e-12
    
    nu = mu / rho
    Ma = mach_number(speed, T_air, humidity_pct)
    Re = 2.0 * R * speed / max(nu, 1e-12)
    
    if use_multi_regime_cd:
        Cd = cd_sphere_multi_regime(Re, Ma, surface_roughness)
    else:
        Cd = cd_sphere_multi_regime(Re, 0.0, 0.0)
    
    # Drag force
    drag_factor = -0.5 * rho * Cd * A * speed
    Fd_x = drag_factor * v_rel_x
    Fd_y = drag_factor * v_rel_y
    Fd_z = drag_factor * v_rel_z
    
    # Magnus force
    omega_mag = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2)
    FL_x, FL_y, FL_z = 0.0, 0.0, 0.0
    
    if omega_mag > 1e-9 and speed > 1e-6:
        spin_param = omega_mag * R / speed
        Cl = magnus_cl_mehta(Re, spin_param, surface_roughness)
        
        lift_dir = np.array([
            omega[1]*v_rel_z - omega[2]*v_rel_y,
            omega[2]*v_rel_x - omega[0]*v_rel_z,
            omega[0]*v_rel_y - omega[1]*v_rel_x
        ])
        lift_norm = np.sqrt(lift_dir[0]**2 + lift_dir[1]**2 + lift_dir[2]**2)
        if lift_norm > 1e-12:
            lift_dir = lift_dir / lift_norm
            lift_factor = 0.5 * rho * Cl * A * speed * speed
            FL_x = lift_factor * lift_dir[0]
            FL_y = lift_factor * lift_dir[1]
            FL_z = lift_factor * lift_dir[2]
    
    # Weight and buoyancy
    Fg_z = -g * mass
    Fb_z = g * rho * V_sphere if buoyancy else 0.0
    
    # Effective mass with virtual mass effect
    m_eff = virtual_mass_effect(mass, rho, V_sphere) if use_virtual_mass else mass
    
    # Accelerations
    ax = (Fd_x + FL_x) / m_eff
    ay = (Fd_y + FL_y) / m_eff
    az = (Fg_z + Fb_z + Fd_z + FL_z) / m_eff
    
    return np.array([vx, vy, vz, ax, ay, az])


# =========================
# Core Simulation Loop
# =========================

@njit(cache=True)
def simulate_core(
    mass, radius, v0, theta, phi, x0, y0, z0,
    spin_rps, spin_axis_x, spin_axis_y, spin_axis_z,
    c_spin_decay, c_spin_aero, dt, t_max,
    stop_speed_threshold, stop_angular_threshold, stop_hold_time,
    buoyancy, g, elasticity_base, elasticity_drop,
    friction_mu_s, friction_mu_k, dampness, wetness,
    slope_x, slope_y, base_height, rough_amp, rough_lambda_x,
    wind_ref_speed, wind_ref_height, wind_shear_alpha,
    wind_dir_x, wind_dir_y, gust_tau, gust_sigma,
    humidity_pct, surface_roughness, contact_stiffness,
    use_virtual_mass, use_multi_regime_cd, use_hertzian_contact,
    adaptive_timestep, rtol, atol, min_dt, max_dt,
    max_iterations, seed
):
    """
    Core simulation loop with optional adaptive timestep (RK45).
    """
    np.random.seed(seed)
    
    data = np.zeros((max_iterations, 23), dtype=np.float64)
    
    R = radius
    A = np.pi * R * R
    V_sphere = 4.0/3.0 * np.pi * R * R * R
    I_sphere = 0.4 * mass * R * R
    
    # State: [x, y, z, vx, vy, vz]
    state = np.array([
        x0, y0, z0,
        v0 * np.cos(theta) * np.cos(phi),
        v0 * np.cos(theta) * np.sin(phi),
        v0 * np.sin(theta)
    ])
    
    # Spin axis normalization
    spin_axis = np.array([spin_axis_x, spin_axis_y, spin_axis_z])
    spin_norm = np.sqrt(spin_axis[0]**2 + spin_axis[1]**2 + spin_axis[2]**2)
    if spin_norm > 1e-12:
        spin_axis = spin_axis / spin_norm
    omega = TWO_PI * spin_rps * spin_axis
    
    w_dir = np.array([wind_dir_x, wind_dir_y, 0.0])
    gust_xy = np.zeros(2)
    
    t = 0.0
    row_idx = 0
    rest_timer = 0.0
    current_dt = dt
    
    # Caching for air properties
    z_cached = -999.0
    rho, mu, T_air = 1.225, 1.81e-5, T0_ISA
    
    # Energy tracking
    E_initial = compute_total_energy(mass, state[3:6], state[2], g, I_sphere, omega)
    E_max_gain = 0.0
    
    # Status flags
    stability_ok = True
    energy_ok = True
    
    while t <= t_max and row_idx < max_iterations:
        x, y, z = state[0:3]
        v = state[3:6].copy()
        
        # Air properties cache (update when z changes significantly)
        if abs(z - z_cached) > 0.5:
            T_air = T0_ISA - L_ISA * min(max(z, 0.0), 11000.0)
            p_air = P0_ISA * (T_air / T0_ISA) ** (G / (R_GAS * L_ISA))
            rho = air_density_with_humidity(T_air, p_air, humidity_pct)
            mu = air_viscosity_with_humidity(T_air, humidity_pct)
            z_cached = z
        
        # Wind calculation
        z_ref = max(wind_ref_height, 0.1)
        z_wind = max(z, 0.1)
        mean_wind_speed = wind_ref_speed * (z_wind / z_ref) ** wind_shear_alpha
        w_mean_x = mean_wind_speed * w_dir[0]
        w_mean_y = mean_wind_speed * w_dir[1]
        
        gust_xy[0] = ornstein_uhlenbeck_step_fast(gust_xy[0], gust_tau, gust_sigma, current_dt)
        gust_xy[1] = ornstein_uhlenbeck_step_fast(gust_xy[1], gust_tau, gust_sigma, current_dt)
        w_x = w_mean_x + gust_xy[0]
        w_y = w_mean_y + gust_xy[1]
        
        if adaptive_timestep:
            # RK45 adaptive step
            step_accepted = False
            attempts = 0
            
            while not step_accepted and attempts < 10:
                k = np.zeros((7, 6))
                k[0] = compute_derivatives(state, mass, radius, rho, mu, T_air, humidity_pct,
                                          w_x, w_y, omega, buoyancy, g, V_sphere, A, I_sphere,
                                          surface_roughness, use_virtual_mass, use_multi_regime_cd)
                
                for i in range(1, 7):
                    state_temp = state + current_dt * np.sum(
                        k[:i] * np.array([RK45_B[i,j] for j in range(i)]).reshape(-1,1), 
                        axis=0
                    )
                    k[i] = compute_derivatives(state_temp, mass, radius, rho, mu, T_air, humidity_pct,
                                              w_x, w_y, omega, buoyancy, g, V_sphere, A, I_sphere,
                                              surface_roughness, use_virtual_mass, use_multi_regime_cd)
                
                y4 = state + current_dt * np.sum(k * RK45_C4.reshape(-1,1), axis=0)
                y5 = state + current_dt * np.sum(k * RK45_C5.reshape(-1,1), axis=0)
                
                err = np.max(np.abs(y5 - y4) / (atol + rtol * np.maximum(np.abs(state), np.abs(y5))))
                
                if err < 1e-10:
                    err = 1e-10
                
                if err <= 1.0:
                    step_accepted = True
                    state = y5
                else:
                    factor = max(0.1, min(0.9 * err**(-0.2), 0.9))
                    current_dt = max(current_dt * factor, min_dt)
                
                attempts += 1
            
            if not step_accepted:
                state = y4
            
            factor = max(0.1, min(5.0, 0.9 * err**(-0.2)))
            current_dt = min(max(current_dt * factor, min_dt), max_dt)
        else:
            # Fixed timestep Euler
            derivs = compute_derivatives(state, mass, radius, rho, mu, T_air, humidity_pct,
                                        w_x, w_y, omega, buoyancy, g, V_sphere, A, I_sphere,
                                        surface_roughness, use_virtual_mass, use_multi_regime_cd)
            state = state + current_dt * derivs
        
        x, y, z = state[0:3]
        v = state[3:6]
        
        # Stability check
        if not check_numerical_stability(v, omega, np.array([x, y, z])):
            stability_ok = False
            break
        
        # Energy check
        E_current = compute_total_energy(mass, v, z, g, I_sphere, omega)
        E_gain = (E_current - E_initial) / max(abs(E_initial), 1.0)
        if E_gain > E_max_gain:
            E_max_gain = E_gain
        if E_gain > 0.5:
            energy_ok = False
        
        # Spin decay
        speed = np.sqrt((v[0]-w_x)**2 + (v[1]-w_y)**2 + v[2]**2)
        omega_mag = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2)
        
        if omega_mag > 1e-9:
            spin_param = omega_mag * R / (speed + 1e-12)
            Re_omega = 2.0 * R * speed / (mu / rho + 1e-12)
            C_T = aerodynamic_torque_coefficient(Re_omega, spin_param)
            T_aero = 0.5 * rho * speed * speed * R * A * C_T
            torque_factor = max(1.0 - (T_aero / I_sphere) * current_dt / omega_mag, 0.0)
            omega = omega * torque_factor
        
        spin_decay_factor = 1.0 - (c_spin_decay + c_spin_aero * speed) * current_dt
        omega = omega * spin_decay_factor
        
        # Ground contact
        z_ground = surface_height_fast(x, y, base_height, slope_x, slope_y, rough_amp, rough_lambda_x)
        n = surface_normal_fast(x, y, slope_x, slope_y, rough_amp, rough_lambda_x)
        v_dot_n = v[0]*n[0] + v[1]*n[1] + v[2]*n[2]
        
        if z - R <= z_ground and v_dot_n < 0.0:
            # Resolve penetration
            x, y, z = resolve_penetration(x, y, z, v[0], v[1], v[2], R, z_ground, n)
            state[0:3] = x, y, z
            
            r = -R * n
            vc = v + np.array([
                omega[1]*r[2] - omega[2]*r[1],
                omega[2]*r[0] - omega[0]*r[2],
                omega[0]*r[1] - omega[1]*r[0]
            ])
            
            vn = vc[0]*n[0] + vc[1]*n[1] + vc[2]*n[2]
            vt = np.sqrt((vc[0] - vn*n[0])**2 + (vc[1] - vn*n[1])**2 + (vc[2] - vn*n[2])**2)
            
            t_dir = (vc - vn*n) / (vt + 1e-12)
            
            # Restitution
            if use_hertzian_contact:
                e = velocity_dependent_restitution(abs(vn), elasticity_base, 1.0, elasticity_drop)
            else:
                e = max(0.0, elasticity_base * (1.0 - 0.5*wetness) - elasticity_drop * abs(vn))
            e *= (1.0 - dampness)
            
            Jn = -(1.0 + e) * mass * vn
            v = v + (Jn / mass) * n
            
            mu_s = max(0.0, friction_mu_s * (1.0 - 0.7 * wetness))
            mu_k = max(0.0, friction_mu_k * (1.0 - 0.8 * wetness))
            
            m_eff_c = mass / (1.0 + I_sphere / (mass * R * R))
            Jt_star = m_eff_c * vt
            Jt_max = mu_s * abs(Jn)
            
            if Jt_star <= Jt_max:
                Jt = -Jt_star * t_dir
            else:
                Jt = -mu_k * abs(Jn) * t_dir
            
            v = v + Jt / mass
            omega = omega + np.array([
                r[1]*Jt[2] - r[2]*Jt[1],
                r[2]*Jt[0] - r[0]*Jt[2],
                r[0]*Jt[1] - r[1]*Jt[0]
            ]) / I_sphere
            
            # Rolling resistance
            vc_post = v + np.array([
                omega[1]*r[2] - omega[2]*r[1],
                omega[2]*r[0] - omega[0]*r[2],
                omega[0]*r[1] - omega[1]*r[0]
            ])
            vt_post = np.sqrt(np.sum((vc_post - (vc_post[0]*n[0]+vc_post[1]*n[1]+vc_post[2]*n[2])*n)**2))
            
            if vt_post < 0.05:
                c_rr = 0.02 + 0.08 * wetness
                v_plane = v - v_dot_n * n
                speed_plane = np.sqrt(v_plane[0]**2 + v_plane[1]**2 + v_plane[2]**2)
                if speed_plane > 1e-6:
                    reduction = min((c_rr * g) * current_dt, speed_plane)
                    v = v - v_plane / speed_plane * reduction
            
            state[3:6] = v
        
        # Mach number
        Ma = mach_number(speed, T_air, humidity_pct)
        
        # Store data
        data[row_idx, 0] = t
        data[row_idx, 1:6] = state[0:5]
        data[row_idx, 6] = z
        data[row_idx, 7:10] = v
        data[row_idx, 10:13] = omega
        data[row_idx, 13] = rho
        data[row_idx, 14] = mu
        data[row_idx, 15] = 2.0 * R * speed / (mu / rho + 1e-12)  # Re
        data[row_idx, 16] = cd_sphere_multi_regime(data[row_idx, 15], Ma, surface_roughness) if use_multi_regime_cd else 0.44
        data[row_idx, 17:20] = w_x, w_y, 0.0
        data[row_idx, 20] = z_ground
        data[row_idx, 21] = Ma
        data[row_idx, 22] = current_dt if adaptive_timestep else dt
        row_idx += 1
        
        # Stop condition
        v_mag = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        omega_mag = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2)
        on_ground = (z - R) <= (z_ground + 1e-4)
        
        if on_ground and v_mag < stop_speed_threshold and omega_mag < stop_angular_threshold:
            rest_timer += current_dt
            if rest_timer >= stop_hold_time:
                break
        else:
            rest_timer = 0.0
        
        t += current_dt
    
    return data, row_idx, stability_ok, energy_ok, E_max_gain


# =========================
# Main Simulation Wrapper
# =========================

def simulate_drop(params: Params, surface: Surface, wind: Wind) -> SimulationResult:
    """
    Run the optimized ball drop simulation with enhanced physics.
    
    Parameters:
        params: Simulation parameters
        surface: Surface properties
        wind: Wind conditions
    
    Returns:
        SimulationResult containing DataFrame and metadata
    """
    import time as time_module
    
    # Input validation
    validate_inputs_or_raise(params, surface, wind)
    
    theta = np.deg2rad(params.drop_angle_deg)
    phi = np.deg2rad(params.azimuth_deg)
    psi = np.deg2rad(wind.direction_deg)
    
    max_iterations = int(params.t_max / params.dt) + 1000
    
    start_time = time_module.perf_counter()
    
    data, actual_rows, stability_ok, energy_ok, E_max_gain = simulate_core(
        params.mass, params.radius, params.v0, theta, phi,
        params.x0, params.y0, params.z0,
        params.spin_rps, params.spin_axis[0], params.spin_axis[1], params.spin_axis[2],
        params.c_spin_decay, params.c_spin_aero, params.dt, params.t_max,
        params.stop_speed_threshold, params.stop_angular_threshold, params.stop_hold_time,
        params.buoyancy, params.g, surface.elasticity_base, surface.elasticity_drop,
        surface.friction_mu_s, surface.friction_mu_k, surface.dampness, surface.wetness,
        surface.slope_x, surface.slope_y, surface.base_height, surface.rough_amp, surface.rough_lambda_x,
        wind.ref_speed, wind.ref_height, wind.shear_alpha, np.cos(psi), np.sin(psi),
        wind.gust_tau, wind.gust_sigma, wind.humidity_pct,
        surface.surface_roughness, surface.contact_stiffness,
        params.use_virtual_mass, params.use_multi_regime_cd, params.use_hertzian_contact,
        params.adaptive_timestep, params.rtol, params.atol, params.min_dt, params.max_dt,
        max_iterations, params.seed
    )
    
    elapsed = time_module.perf_counter() - start_time
    
    data = data[:actual_rows]
    df = pd.DataFrame(data, columns=[
        "Time", "X", "Y", "Z", "Vx", "Vy", "Vz", "Ox", "Oy", "Oz",
        "AirDensity", "Mu", "Re", "Cd", "WindX", "WindY", "WindZ", "Z_ground",
        "Mach", "Dt_actual", "Extra1", "Extra2", "Extra3"
    ])
    
    # Select relevant columns
    df = df[[
        "Time", "X", "Y", "Z", "Vx", "Vy", "Vz", "Ox", "Oy", "Oz",
        "AirDensity", "Mu", "Re", "Cd", "WindX", "WindY", "WindZ", "Z_ground",
        "Mach", "Dt_actual"
    ]]
    
    return SimulationResult(
        df=df,
        params=params,
        surface=surface,
        wind=wind,
        stability_ok=stability_ok,
        energy_ok=energy_ok,
        max_energy_gain_pct=E_max_gain * 100,
        compute_time_ms=elapsed * 1000
    )