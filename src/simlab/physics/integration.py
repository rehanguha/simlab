"""
Advanced numerical integration methods for physics simulations.

This module provides sophisticated numerical integration techniques including
adaptive step size control, error estimation, and stability monitoring.
"""

import numpy as np
from typing import Callable, Tuple, List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class IntegrationResult:
    """Result of numerical integration."""
    times: List[float]
    solutions: List[np.ndarray]
    step_sizes: List[float]
    error_estimates: List[float]
    stability_info: Dict[str, Any]


class AdaptiveRK45:
    """Adaptive Runge-Kutta 4(5) method using Dormand-Prince coefficients."""
    
    def __init__(self, rtol: float = 1e-6, atol: float = 1e-8, 
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
        
        # Dormand-Prince coefficients
        self.a = np.array([
            [0, 0, 0, 0, 0, 0],
            [1/5, 0, 0, 0, 0, 0],
            [3/40, 9/40, 0, 0, 0, 0],
            [44/45, -56/15, 32/9, 0, 0, 0],
            [19372/6561, -25360/2187, 64448/6561, -212/729, 0, 0],
            [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0],
            [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]
        ])
        
        self.b = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0])
        self.b_star = np.array([5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100, 1/40])
        self.c = np.array([0, 1/5, 3/10, 4/5, 8/9, 1, 1])
    
    def integrate(self, func: Callable, t0: float, y0: np.ndarray, 
                  t_end: float, dt: float) -> IntegrationResult:
        """
        Integrate ODE using adaptive RK45 method.
        
        Args:
            func: Function to integrate, dy/dt = func(t, y)
            t0: Initial time
            y0: Initial state vector
            t_end: Final time
            dt: Initial timestep
            
        Returns:
            IntegrationResult containing times, solutions, and metadata
        """
        times = [t0]
        solutions = [y0.copy()]
        step_sizes = [dt]
        error_estimates = [0.0]
        
        t = t0
        y = y0.copy()
        current_dt = min(dt, self.max_dt)
        
        # Stability monitoring
        energy_history = []
        max_solution_history = []
        
        while t < t_end:
            # Ensure we don't overshoot the end time
            if t + current_dt > t_end:
                current_dt = t_end - t
            
            # Calculate RK stages
            k = self._calculate_rk_stages(func, t, y, current_dt)
            
            # Calculate solutions with different orders
            y_new = y + current_dt * np.dot(self.b, k)
            y_star = y + current_dt * np.dot(self.b_star, k)
            
            # Estimate error
            error = np.abs(y_new - y_star)
            error_norm = self._calculate_error_norm(error, y)
            
            # Store error estimate
            error_estimates.append(error_norm)
            
            # Check if step is acceptable
            if error_norm <= 1.0:
                # Step accepted
                t += current_dt
                y = y_new
                times.append(t)
                solutions.append(y.copy())
                step_sizes.append(current_dt)
                
                # Monitor stability
                energy = self._calculate_energy(y)
                energy_history.append(energy)
                max_solution = np.max(np.abs(y))
                max_solution_history.append(max_solution)
                
                # Check for instability
                if max_solution > 1e6:
                    raise ValueError(f"Solution became unstable at t={t}, max|y|={max_solution}")
                
                # Adaptive step size control
                if error_norm > 0:
                    safety_factor = 0.9
                    exponent = 1.0 / 5.0
                    new_dt = current_dt * safety_factor * (error_norm ** (-exponent))
                    current_dt = max(self.min_dt, min(new_dt, self.max_dt))
                else:
                    # Error is very small, allow larger step
                    current_dt = min(current_dt * 2.0, self.max_dt)
            else:
                # Step rejected, reduce step size
                safety_factor = 0.5
                exponent = 1.0 / 5.0
                current_dt = max(self.min_dt, current_dt * safety_factor * (error_norm ** (-exponent)))
        
        # Stability analysis
        stability_info = self._analyze_stability(energy_history, max_solution_history)
        
        return IntegrationResult(
            times=times,
            solutions=solutions,
            step_sizes=step_sizes,
            error_estimates=error_estimates,
            stability_info=stability_info
        )
    
    def _calculate_rk_stages(self, func: Callable, t: float, y: np.ndarray, dt: float) -> np.ndarray:
        """Calculate Runge-Kutta stages."""
        k = np.zeros((7, len(y)))
        
        for i in range(7):
            if i == 0:
                k[i] = func(t, y)
            else:
                stage_time = t + self.c[i] * dt
                stage_y = y + dt * np.dot(self.a[i, :i], k[:i])
                k[i] = func(stage_time, stage_y)
        
        return k
    
    def _calculate_error_norm(self, error: np.ndarray, y: np.ndarray) -> float:
        """Calculate error norm for adaptive step size control."""
        # Use a combination of absolute and relative error
        scale = self.atol + np.maximum(np.abs(y), np.abs(y + error)) * self.rtol
        return np.max(np.abs(error) / scale)
    
    def _calculate_energy(self, y: np.ndarray) -> float:
        """Calculate total mechanical energy for stability monitoring."""
        # Assuming y = [x, y, z, vx, vy, vz, omega_x, omega_y, omega_z]
        if len(y) >= 6:
            v = y[3:6]  # velocity components
            z = y[2]    # height
            omega = y[6:9] if len(y) > 6 else np.zeros(3)  # angular velocity
            
            # Kinetic energy
            ke = 0.5 * np.dot(v, v)
            
            # Rotational kinetic energy (assuming unit mass moment of inertia)
            re = 0.5 * np.dot(omega, omega)
            
            # Potential energy (assuming unit mass and g=1)
            pe = z
            
            return ke + re + pe
        return 0.0
    
    def _analyze_stability(self, energy_history: List[float], max_solution_history: List[float]) -> Dict[str, Any]:
        """Analyze numerical stability."""
        if not energy_history:
            return {'stable': True, 'energy_conserved': True, 'max_growth': 0.0}
        
        # Check energy conservation
        initial_energy = energy_history[0]
        final_energy = energy_history[-1]
        
        if abs(initial_energy) > 1e-10:
            energy_change = abs(final_energy - initial_energy) / abs(initial_energy)
            energy_conserved = energy_change < 0.1  # 10% energy change threshold
        else:
            energy_conserved = True
        
        # Check solution growth
        if len(max_solution_history) > 1:
            max_growth = max_solution_history[-1] / max_solution_history[0]
        else:
            max_growth = 1.0
        
        # Overall stability
        stable = (max_growth < 1000) and energy_conserved
        
        return {
            'stable': stable,
            'energy_conserved': energy_conserved,
            'max_growth': max_growth,
            'energy_change': energy_change if 'energy_change' in locals() else 0.0
        }


class FixedStepEuler:
    """Simple fixed-step Euler integration for comparison."""
    
    def __init__(self, dt: float):
        """
        Initialize fixed-step Euler integrator.
        
        Args:
            dt (float): Fixed timestep
        """
        self.dt = dt
    
    def integrate(self, func: Callable, t0: float, y0: np.ndarray, 
                  t_end: float) -> IntegrationResult:
        """
        Integrate ODE using fixed-step Euler method.
        
        Args:
            func: Function to integrate, dy/dt = func(t, y)
            t0: Initial time
            y0: Initial state vector
            t_end: Final time
            
        Returns:
            IntegrationResult containing times, solutions, and metadata
        """
        times = [t0]
        solutions = [y0.copy()]
        step_sizes = [self.dt]
        error_estimates = [0.0]
        
        t = t0
        y = y0.copy()
        
        while t < t_end:
            # Ensure we don't overshoot the end time
            if t + self.dt > t_end:
                current_dt = t_end - t
            else:
                current_dt = self.dt
            
            # Euler step
            dy = func(t, y)
            y_new = y + current_dt * dy
            
            t += current_dt
            y = y_new
            
            times.append(t)
            solutions.append(y.copy())
            step_sizes.append(current_dt)
            error_estimates.append(0.0)  # No error estimation in simple Euler
        
        return IntegrationResult(
            times=times,
            solutions=solutions,
            step_sizes=step_sizes,
            error_estimates=error_estimates,
            stability_info={'stable': True, 'energy_conserved': False, 'max_growth': 1.0}
        )


class IntegrationController:
    """Controller for managing integration methods and adaptive behavior."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize integration controller.
        
        Args:
            config (dict): Integration configuration
        """
        self.config = config
        self.adaptive_enabled = config.get('adaptive_timestep', False)
        self.rtol = config.get('rtol', 1e-6)
        self.atol = config.get('atol', 1e-8)
        self.min_dt = config.get('min_dt', 1e-5)
        self.max_dt = config.get('max_dt', 0.05)
        self.fixed_dt = config.get('dt', 0.001)
    
    def integrate(self, func: Callable, t0: float, y0: np.ndarray, 
                  t_end: float, initial_dt: Optional[float] = None) -> IntegrationResult:
        """
        Integrate ODE using appropriate method based on configuration.
        
        Args:
            func: Function to integrate, dy/dt = func(t, y)
            t0: Initial time
            y0: Initial state vector
            t_end: Final time
            initial_dt: Initial timestep (optional)
            
        Returns:
            IntegrationResult containing times, solutions, and metadata
        """
        if self.adaptive_enabled:
            # Use adaptive integration
            dt = initial_dt or self.fixed_dt
            integrator = AdaptiveRK45(
                rtol=self.rtol,
                atol=self.atol,
                min_dt=self.min_dt,
                max_dt=self.max_dt
            )
        else:
            # Use fixed-step integration
            integrator = FixedStepEuler(dt=self.fixed_dt)
        
        return integrator.integrate(func, t0, y0, t_end, self.fixed_dt)
    
    def check_stability(self, result: IntegrationResult) -> bool:
        """Check if integration result is numerically stable."""
        return result.stability_info['stable']
    
    def get_integration_stats(self, result: IntegrationResult) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            'total_steps': len(result.times),
            'final_time': result.times[-1],
            'avg_step_size': np.mean(result.step_sizes),
            'min_step_size': np.min(result.step_sizes),
            'max_step_size': np.max(result.step_sizes),
            'max_error': np.max(result.error_estimates),
            'stability': result.stability_info,
            'adaptive_steps': len([s for s in result.step_sizes if s != self.fixed_dt]) if self.adaptive_enabled else 0
        }


def adaptive_timestep_controller(error: float, dt: float, rtol: float = 1e-4, 
                                atol: float = 1e-6, min_dt: float = 1e-5, 
                                max_dt: float = 0.05) -> float:
    """
    Adaptive timestep controller based on error estimate.
    
    Args:
        error: Error estimate from integration step
        dt: Current timestep
        rtol: Relative tolerance
        atol: Absolute tolerance
        min_dt: Minimum allowed timestep
        max_dt: Maximum allowed timestep
        
    Returns:
        New timestep
    """
    if error <= 0:
        # No error, allow larger step
        new_dt = min(dt * 2.0, max_dt)
    else:
        # Calculate safety factor and exponent
        safety_factor = 0.9
        exponent = 0.2  # Conservative exponent for stability
        
        # Calculate error tolerance
        error_tol = rtol + atol
        
        # Calculate new timestep
        if error > error_tol:
            # Error too large, reduce step
            new_dt = max(min_dt, dt * safety_factor * (error_tol / error) ** exponent)
        else:
            # Error acceptable, allow slightly larger step
            new_dt = min(max_dt, dt * safety_factor * (error_tol / error) ** exponent)
    
    return new_dt


def energy_monitor(y: np.ndarray, g: float = 9.81, m: float = 1.0, I: float = 1.0) -> float:
    """
    Calculate total mechanical energy for stability monitoring.
    
    Args:
        y: State vector [x, y, z, vx, vy, vz, ωx, ωy, ωz]
        g: Gravitational acceleration
        m: Mass
        I: Moment of inertia
        
    Returns:
        Total mechanical energy
    """
    if len(y) < 6:
        return 0.0
    
    # Extract state variables
    v = y[3:6]  # velocity
    z = y[2]    # height
    omega = y[6:9] if len(y) > 6 else np.zeros(3)  # angular velocity
    
    # Calculate energies
    kinetic_energy = 0.5 * m * np.dot(v, v)
    potential_energy = m * g * z
    rotational_energy = 0.5 * I * np.dot(omega, omega)
    
    return kinetic_energy + potential_energy + rotational_energy


def check_stability(y: np.ndarray, y_prev: np.ndarray, threshold: float = 1e6) -> bool:
    """
    Check numerical stability by monitoring solution growth.
    
    Args:
        y: Current solution
        y_prev: Previous solution
        threshold: Maximum allowed solution magnitude
        
    Returns:
        True if stable, False otherwise
    """
    if np.max(np.abs(y)) > threshold:
        return False
    
    if len(y_prev) > 0:
        growth_factor = np.max(np.abs(y)) / (np.max(np.abs(y_prev)) + 1e-10)
        if growth_factor > 1000:
            return False
    
    return True


def convergence_test(func: Callable, t0: float, y0: np.ndarray, t_end: float,
                    dt_values: List[float]) -> Dict[str, Any]:
    """
    Test convergence of numerical integration methods.
    
    Args:
        func: Function to integrate
        t0: Initial time
        y0: Initial state
        t_end: Final time
        dt_values: List of timesteps to test
        
    Returns:
        Convergence analysis results
    """
    results = {}
    
    for dt in dt_values:
        # Integrate with current timestep
        integrator = FixedStepEuler(dt=dt)
        result = integrator.integrate(func, t0, y0, t_end)
        
        results[dt] = {
            'times': result.times,
            'solutions': result.solutions,
            'final_solution': result.solutions[-1],
            'num_steps': len(result.times)
        }
    
    # Calculate convergence rates
    dt_list = sorted(dt_values)
    convergence_rates = {}
    
    for i in range(1, len(dt_list)):
        dt1 = dt_list[i-1]
        dt2 = dt_list[i]
        
        sol1 = results[dt1]['final_solution']
        sol2 = results[dt2]['final_solution']
        
        error = np.linalg.norm(sol1 - sol2)
        rate = np.log(error) / np.log(dt2 / dt1) if dt2 > 0 else 0
        
        convergence_rates[f"{dt1}->{dt2}"] = {
            'error': error,
            'rate': rate,
            'dt_ratio': dt2 / dt1
        }
    
    return {
        'results': results,
        'convergence_rates': convergence_rates,
        'dt_values': dt_list
    }