"""
Numerical integration methods.

Contains functions for adaptive timestep control and advanced integration methods.
"""

import numpy as np
from typing import Callable, Tuple, Optional


class AdaptiveRK45:
    """Adaptive Runge-Kutta 4(5) method using Dormand-Prince coefficients."""
    
    def __init__(self, rtol: float = 1e-4, atol: float = 1e-6, 
                 min_dt: float = 1e-5, max_dt: float = 0.05):
        """
        Initialize adaptive RK45 integrator.
        
        Args:
            rtol (float): Relative tolerance
            atol (float): Absolute tolerance
            min_dt (float): Minimum timestep
            max_dt (float): Maximum timestep
        """
        self.rtol = rtol
        self.atol = atol
        self.min_dt = min_dt
        self.max_dt = max_dt
        
        # Dormand-Prince coefficients for RK45
        self.a = np.array([
            [0, 0, 0, 0, 0, 0],
            [1/5, 0, 0, 0, 0, 0],
            [3/40, 9/40, 0, 0, 0, 0],
            [44/45, -56/15, 32/9, 0, 0, 0],
            [19372/6561, -25360/2187, 64448/6561, -212/729, 0, 0],
            [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0],
            [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]
        ])
        
        self.b4 = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0])
        self.b5 = np.array([5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100, 1/40])
        
        self.c = np.array([0, 1/5, 3/10, 4/5, 8/9, 1, 1])
    
    def integrate(self, func: Callable, t0: float, y0: np.ndarray, 
                  t_end: float, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Integrate ODE using adaptive RK45 method.
        
        Args:
            func: Function to integrate, dy/dt = func(t, y)
            t0: Initial time
            y0: Initial state vector
            t_end: Final time
            dt: Initial timestep
            
        Returns:
            Tuple of (time_array, solution_array)
        """
        t = t0
        y = y0.copy()
        
        times = [t0]
        solutions = [y0.copy()]
        
        while t < t_end:
            # Ensure we don't overshoot the end time
            dt = min(dt, t_end - t)
            
            # Calculate RK stages
            k = np.zeros((7, len(y)))
            
            # Stage 1
            k[0] = func(t, y)
            
            # Stages 2-7
            for i in range(1, 7):
                y_temp = y.copy()
                for j in range(i):
                    y_temp += self.a[i, j] * k[j] * dt
                k[i] = func(t + self.c[i] * dt, y_temp)
            
            # Calculate 4th and 5th order solutions
            y4 = y + dt * np.sum(self.b4[:, np.newaxis] * k, axis=0)
            y5 = y + dt * np.sum(self.b5[:, np.newaxis] * k, axis=0)
            
            # Error estimate
            error = np.abs(y5 - y4)
            error_norm = np.max(error / (self.atol + np.maximum(np.abs(y5), np.abs(y)) * self.rtol))
            
            # Accept or reject step
            if error_norm <= 1.0:
                # Step accepted
                t += dt
                y = y5
                times.append(t)
                solutions.append(y.copy())
                
                # Update timestep
                if error_norm > 0:
                    dt_new = dt * min(5.0, max(0.1, 0.9 * error_norm**(-0.2)))
                else:
                    dt_new = dt * 2.0
                
                dt = max(self.min_dt, min(dt_new, self.max_dt))
            else:
                # Step rejected, reduce timestep
                dt_new = max(self.min_dt, dt * 0.5)
                dt = dt_new
        
        return np.array(times), np.array(solutions)


def fixed_step_euler(func: Callable, t0: float, y0: np.ndarray, 
                     t_end: float, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple fixed-step Euler integration for comparison.
    
    Args:
        func: Function to integrate, dy/dt = func(t, y)
        t0: Initial time
        y0: Initial state vector
        t_end: Final time
        dt: Fixed timestep
        
    Returns:
        Tuple of (time_array, solution_array)
    """
    t = t0
    y = y0.copy()
    
    times = [t0]
    solutions = [y0.copy()]
    
    while t < t_end:
        dt_step = min(dt, t_end - t)
        y += func(t, y) * dt_step
        t += dt_step
        
        times.append(t)
        solutions.append(y.copy())
    
    return np.array(times), np.array(solutions)


def check_stability(y: np.ndarray, y_prev: np.ndarray, threshold: float = 1e6) -> bool:
    """
    Check numerical stability by monitoring solution growth.
    
    Args:
        y: Current solution
        y_prev: Previous solution
        threshold: Maximum allowed solution magnitude
        
    Returns:
        True if stable, False if unstable
    """
    if np.any(np.abs(y) > threshold):
        return False
    
    if np.any(np.isnan(y)) or np.any(np.isinf(y)):
        return False
    
    return True


def energy_monitor(y: np.ndarray, g: float = 9.81, m: float = 1.0, 
                   I: float = 1.0) -> float:
    """
    Calculate total mechanical energy for stability monitoring.
    
    Args:
        y: State vector [x, y, z, vx, vy, vz, omega_x, omega_y, omega_z]
        g: Gravitational acceleration
        m: Mass
        I: Moment of inertia
        
    Returns:
        Total mechanical energy
    """
    # Extract state variables
    z = y[2]  # height
    vx, vy, vz = y[3:6]  # velocities
    omega_x, omega_y, omega_z = y[6:9]  # angular velocities
    
    # Calculate energies
    kinetic_trans = 0.5 * m * (vx**2 + vy**2 + vz**2)
    kinetic_rot = 0.5 * I * (omega_x**2 + omega_y**2 + omega_z**2)
    potential = m * g * z
    
    return kinetic_trans + kinetic_rot + potential


def adaptive_timestep_controller(error: float, dt: float, rtol: float = 1e-4, 
                                atol: float = 1e-6, min_dt: float = 1e-5, 
                                max_dt: float = 0.05) -> float:
    """
    Adaptive timestep controller based on error estimate.
    
    Args:
        error: Error estimate from integration
        dt: Current timestep
        rtol: Relative tolerance
        atol: Absolute tolerance
        min_dt: Minimum timestep
        max_dt: Maximum timestep
        
    Returns:
        New timestep
    """
    if error <= 0:
        # No error, can increase timestep
        dt_new = dt * 2.0
    else:
        # Calculate error norm
        error_norm = error / (atol + rtol)
        
        if error_norm <= 1.0:
            # Error acceptable, adjust timestep
            dt_new = dt * min(5.0, max(0.1, 0.9 * error_norm**(-0.2)))
        else:
            # Error too large, reduce timestep
            dt_new = dt * 0.5
    
    return max(min_dt, min(dt_new, max_dt))