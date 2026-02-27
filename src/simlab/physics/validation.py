"""
Physics validation framework.

Contains comprehensive validation functions for mathematical accuracy,
numerical stability, and energy conservation.
"""

import numpy as np
from typing import Dict, Any, Tuple, List
from .corrections import (
    validate_energy_conservation,
    check_numerical_stability,
    PhysicsCorrector
)


class PhysicsValidator:
    """Comprehensive physics validation framework."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize physics validator.
        
        Args:
            config (dict): Validation configuration
        """
        self.config = config or {}
        self.validation_history = []
        self.energy_history = []
        self.stability_history = []
        
        # Validation thresholds
        self.energy_tolerance = self.config.get('energy_tolerance', 0.01)
        self.stability_threshold = self.config.get('stability_threshold', 1e6)
        self.growth_factor_threshold = self.config.get('growth_factor_threshold', 1000.0)
    
    def validate_simulation_step(
        self,
        state: Dict[str, Any],
        forces: np.ndarray,
        torques: np.ndarray,
        dt: float
    ) -> Dict[str, Any]:
        """
        Validate a single simulation step.
        
        Args:
            state (dict): Current state
            forces (np.ndarray): Applied forces
            torques (np.ndarray): Applied torques
            dt (float): Time step
            
        Returns:
            dict: Validation results
        """
        # Calculate energy
        current_energy = self._calculate_total_energy(state)
        self.energy_history.append(current_energy)
        
        # Check numerical stability
        solution_array = np.array([
            state['position'], state['velocity'], 
            state['angular_velocity']
        ]).flatten()
        
        is_stable, stability_info = check_numerical_stability(
            solution_array,
            self.stability_threshold,
            self.growth_factor_threshold
        )
        
        self.stability_history.append(stability_info)
        
        # Validate energy conservation (if we have previous energy)
        energy_conserved = True
        energy_error = 0.0
        
        if len(self.energy_history) > 1:
            prev_energy = self.energy_history[-2]
            energy_conserved, energy_error = validate_energy_conservation(
                prev_energy, current_energy, self.energy_tolerance
            )
        
        # Check force magnitudes
        force_magnitude = np.linalg.norm(forces)
        torque_magnitude = np.linalg.norm(torques)
        
        # Force sanity checks
        max_reasonable_force = 1e6  # N
        max_reasonable_torque = 1e3  # N·m
        
        force_valid = force_magnitude < max_reasonable_force
        torque_valid = torque_magnitude < max_reasonable_torque
        
        # Position sanity checks
        max_reasonable_position = 1e6  # m
        position_valid = np.all(np.abs(state['position']) < max_reasonable_position)
        
        # Velocity sanity checks
        max_reasonable_velocity = 1e3  # m/s (hypersonic)
        velocity_valid = np.all(np.abs(state['velocity']) < max_reasonable_velocity)
        
        # Angular velocity sanity checks
        max_reasonable_angular_velocity = 1e4  # rad/s
        angular_velocity_valid = np.all(np.abs(state['angular_velocity']) < max_reasonable_angular_velocity)
        
        # Compile validation results
        validation_result = {
            'step_valid': all([
                is_stable, energy_conserved, force_valid, 
                torque_valid, position_valid, velocity_valid, angular_velocity_valid
            ]),
            'stability': {
                'is_stable': is_stable,
                'max_value': stability_info['max_value'],
                'growth_factor': stability_info['growth_factor'],
                'has_nan': stability_info['has_nan'],
                'has_inf': stability_info['has_inf']
            },
            'energy': {
                'conserved': energy_conserved,
                'error': energy_error,
                'current': current_energy,
                'tolerance': self.energy_tolerance
            },
            'forces': {
                'valid': force_valid,
                'magnitude': force_magnitude,
                'max_reasonable': max_reasonable_force
            },
            'torques': {
                'valid': torque_valid,
                'magnitude': torque_magnitude,
                'max_reasonable': max_reasonable_torque
            },
            'kinematics': {
                'position_valid': position_valid,
                'velocity_valid': velocity_valid,
                'angular_velocity_valid': angular_velocity_valid,
                'position': state['position'].copy(),
                'velocity': state['velocity'].copy(),
                'angular_velocity': state['angular_velocity'].copy()
            },
            'time_step': dt
        }
        
        self.validation_history.append(validation_result)
        
        return validation_result
    
    def _calculate_total_energy(self, state: Dict[str, Any]) -> float:
        """
        Calculate total mechanical energy.
        
        Args:
            state (dict): Current state
            
        Returns:
            float: Total energy
        """
        # Extract state variables
        position = state['position']
        velocity = state['velocity']
        angular_velocity = state['angular_velocity']
        mass = state['mass']
        inertia = state['inertia']
        
        # Kinetic energy
        ke_trans = 0.5 * mass * np.dot(velocity, velocity)
        ke_rot = 0.5 * inertia * np.dot(angular_velocity, angular_velocity)
        
        # Potential energy (gravitational)
        g = self.config.get('gravity', 9.81)
        pe = mass * g * position[2]
        
        return ke_trans + ke_rot + pe
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive validation summary.
        
        Returns:
            dict: Validation summary
        """
        if not self.validation_history:
            return {'error': 'No validation data available'}
        
        # Energy conservation summary
        energy_errors = [v['energy']['error'] for v in self.validation_history]
        max_energy_error = max(energy_errors) if energy_errors else 0.0
        avg_energy_error = np.mean(energy_errors) if energy_errors else 0.0
        
        # Stability summary
        stability_issues = sum(1 for v in self.validation_history if not v['stability']['is_stable'])
        max_growth_factor = max(v['stability']['growth_factor'] for v in self.validation_history)
        
        # Force/torque summary
        max_force = max(v['forces']['magnitude'] for v in self.validation_history)
        max_torque = max(v['torques']['magnitude'] for v in self.validation_history)
        
        # Overall validation
        all_valid = all(v['step_valid'] for v in self.validation_history)
        
        return {
            'overall_valid': all_valid,
            'total_steps': len(self.validation_history),
            'stability_issues': stability_issues,
            'max_growth_factor': max_growth_factor,
            'energy': {
                'max_error': max_energy_error,
                'avg_error': avg_energy_error,
                'tolerance': self.energy_tolerance,
                'conservation_valid': max_energy_error <= self.energy_tolerance
            },
            'forces': {
                'max_force': max_force,
                'max_reasonable_force': 1e6,
                'force_valid': max_force < 1e6
            },
            'torques': {
                'max_torque': max_torque,
                'max_reasonable_torque': 1e3,
                'torque_valid': max_torque < 1e3
            },
            'stability': {
                'max_value': max(v['stability']['max_value'] for v in self.validation_history),
                'has_nan': any(v['stability']['has_nan'] for v in self.validation_history),
                'has_inf': any(v['stability']['has_inf'] for v in self.validation_history)
            }
        }
    
    def validate_mathematical_accuracy(
        self,
        reference_solution: np.ndarray,
        computed_solution: np.ndarray,
        tolerance: float = 1e-3
    ) -> Dict[str, Any]:
        """
        Validate mathematical accuracy against reference solution.
        
        Args:
            reference_solution (np.ndarray): Reference solution
            computed_solution (np.ndarray): Computed solution
            tolerance (float): Accuracy tolerance
            
        Returns:
            dict: Accuracy validation results
        """
        if reference_solution.shape != computed_solution.shape:
            return {
                'valid': False,
                'error': 'Solution shapes do not match',
                'reference_shape': reference_solution.shape,
                'computed_shape': computed_solution.shape
            }
        
        # Calculate relative error
        diff = np.abs(reference_solution - computed_solution)
        relative_error = diff / (np.abs(reference_solution) + 1e-10)
        
        max_relative_error = np.max(relative_error)
        mean_relative_error = np.mean(relative_error)
        
        # Check if within tolerance
        accuracy_valid = max_relative_error <= tolerance
        
        return {
            'valid': accuracy_valid,
            'max_relative_error': max_relative_error,
            'mean_relative_error': mean_relative_error,
            'tolerance': tolerance,
            'error_distribution': {
                'min': np.min(relative_error),
                'median': np.median(relative_error),
                '95_percentile': np.percentile(relative_error, 95),
                '99_percentile': np.percentile(relative_error, 99)
            }
        }
    
    def validate_numerical_convergence(
        self,
        solutions: List[np.ndarray],
        time_steps: List[float]
    ) -> Dict[str, Any]:
        """
        Validate numerical convergence with different time steps.
        
        Args:
            solutions (list): Solutions with different time steps
            time_steps (list): Corresponding time steps
            
        Returns:
            dict: Convergence validation results
        """
        if len(solutions) < 2:
            return {'error': 'Need at least 2 solutions for convergence analysis'}
        
        # Calculate convergence rates
        errors = []
        for i in range(1, len(solutions)):
            # Compare with finest solution as reference
            reference = solutions[0]
            solution = solutions[i]
            
            error = np.linalg.norm(solution - reference) / np.linalg.norm(reference)
            errors.append(error)
        
        # Calculate convergence rates
        convergence_rates = []
        for i in range(1, len(errors)):
            rate = np.log(errors[i] / errors[i-1]) / np.log(time_steps[i] / time_steps[i-1])
            convergence_rates.append(rate)
        
        avg_convergence_rate = np.mean(convergence_rates) if convergence_rates else 0.0
        
        # Check for expected convergence (typically 1st or 2nd order)
        expected_min_rate = 0.8  # Allow some tolerance
        convergence_valid = avg_convergence_rate >= expected_min_rate
        
        return {
            'valid': convergence_valid,
            'convergence_rates': convergence_rates,
            'avg_convergence_rate': avg_convergence_rate,
            'expected_min_rate': expected_min_rate,
            'errors': errors,
            'time_steps': time_steps
        }
    
    def reset(self) -> None:
        """Reset validation history."""
        self.validation_history = []
        self.energy_history = []
        self.stability_history = []


class MathematicalAccuracyValidator:
    """Validator for mathematical formulation accuracy."""
    
    def __init__(self):
        """Initialize mathematical accuracy validator."""
        self.corrector = PhysicsCorrector()
    
    def validate_drag_coefficient(
        self,
        reynolds_values: np.ndarray,
        mach_values: np.ndarray = None,
        surface_roughness: float = 0.0
    ) -> Dict[str, Any]:
        """
        Validate drag coefficient calculations.
        
        Args:
            reynolds_values (np.ndarray): Reynolds number range
            mach_values (np.ndarray): Mach number range
            surface_roughness (float): Surface roughness
            
        Returns:
            dict: Validation results
        """
        if mach_values is None:
            mach_values = np.zeros_like(reynolds_values)
        
        # Calculate drag coefficients
        cd_values = []
        for re, mach in zip(reynolds_values, mach_values):
            cd = self.corrector.apply_drag_correction(re, mach, surface_roughness)
            cd_values.append(cd)
        
        cd_values = np.array(cd_values)
        
        # Validate smoothness (no discontinuities)
        gradients = np.gradient(cd_values, reynolds_values)
        max_gradient_change = np.max(np.abs(np.gradient(gradients)))
        
        # Validate physical bounds
        physical_bounds_valid = np.all((cd_values >= 0.05) & (cd_values <= 2.0))
        
        # Validate monotonicity in certain regimes
        # In drag crisis region, should be decreasing
        crisis_start = np.where(reynolds_values >= 2e5)[0][0]
        crisis_end = np.where(reynolds_values >= 4e5)[0][0]
        crisis_slope = np.mean(np.gradient(cd_values[crisis_start:crisis_end]))
        
        crisis_valid = crisis_slope < 0  # Should be negative (decreasing)
        
        return {
            'smoothness_valid': max_gradient_change < 100,  # Arbitrary threshold
            'physical_bounds_valid': physical_bounds_valid,
            'crisis_behavior_valid': crisis_valid,
            'max_gradient_change': max_gradient_change,
            'crisis_slope': crisis_slope,
            'drag_coefficients': cd_values.tolist(),
            'reynolds_numbers': reynolds_values.tolist()
        }
    
    def validate_magnus_force(
        self,
        velocities: np.ndarray,
        angular_velocities: np.ndarray,
        density: float = 1.225,
        radius: float = 0.1
    ) -> Dict[str, Any]:
        """
        Validate Magnus force calculations.
        
        Args:
            velocities (np.ndarray): Velocity vectors
            angular_velocities (np.ndarray): Angular velocity vectors
            density (float): Air density
            radius (float): Object radius
            
        Returns:
            dict: Validation results
        """
        # Calculate Magnus forces
        forces = []
        for v, omega in zip(velocities, angular_velocities):
            force = self.corrector.apply_magnus_correction(v, omega, density, radius)
            forces.append(force)
        
        forces = np.array(forces)
        
        # Validate vector properties
        # Force should be perpendicular to both velocity and angular velocity
        perpendicular_errors = []
        for i, (v, omega, f) in enumerate(zip(velocities, angular_velocities, forces)):
            # Check perpendicular to velocity
            v_perp_error = np.abs(np.dot(f, v)) / (np.linalg.norm(f) * np.linalg.norm(v) + 1e-10)
            
            # Check perpendicular to angular velocity
            omega_perp_error = np.abs(np.dot(f, omega)) / (np.linalg.norm(f) * np.linalg.norm(omega) + 1e-10)
            
            perpendicular_errors.append(max(v_perp_error, omega_perp_error))
        
        max_perp_error = np.max(perpendicular_errors)
        
        # Validate magnitude scaling
        # Force should scale with velocity and angular velocity
        force_magnitudes = np.linalg.norm(forces, axis=1)
        v_magnitudes = np.linalg.norm(velocities, axis=1)
        omega_magnitudes = np.linalg.norm(angular_velocities, axis=1)
        
        # Check if force scales roughly with v * omega
        expected_scaling = v_magnitudes * omega_magnitudes
        scaling_correlation = np.corrcoef(force_magnitudes, expected_scaling)[0, 1]
        
        return {
            'perpendicular_valid': max_perp_error < 0.1,  # 10% tolerance
            'scaling_valid': abs(scaling_correlation) > 0.8,  # Strong correlation
            'max_perpendicular_error': max_perp_error,
            'scaling_correlation': scaling_correlation,
            'force_magnitudes': force_magnitudes.tolist(),
            'expected_scaling': expected_scaling.tolist()
        }
    
    def validate_contact_mechanics(
        self,
        penetrations: np.ndarray,
        radii: np.ndarray,
        youngs_moduli: np.ndarray
    ) -> Dict[str, Any]:
        """
        Validate contact mechanics calculations.
        
        Args:
            penetrations (np.ndarray): Penetration depths
            radii (np.ndarray): Object radii
            youngs_moduli (np.ndarray): Young's moduli
            
        Returns:
            dict: Validation results
        """
        # Calculate contact forces
        forces = []
        contact_radii = []
        
        for p, r, E in zip(penetrations, radii, youngs_moduli):
            force, contact_r = self.corrector.apply_contact_correction(p, r, E)
            forces.append(force)
            contact_radii.append(contact_r)
        
        forces = np.array(forces)
        contact_radii = np.array(contact_radii)
        
        # Validate Hertzian scaling laws
        # Force should scale with penetration^(3/2)
        # Contact radius should scale with penetration^(1/2)
        
        # Check force scaling
        expected_force_scaling = penetrations ** 1.5
        force_correlation = np.corrcoef(forces, expected_force_scaling)[0, 1]
        
        # Check contact radius scaling
        expected_radius_scaling = penetrations ** 0.5
        radius_correlation = np.corrcoef(contact_radii, expected_radius_scaling)[0, 1]
        
        return {
            'force_scaling_valid': abs(force_correlation) > 0.95,
            'radius_scaling_valid': abs(radius_correlation) > 0.95,
            'force_scaling_correlation': force_correlation,
            'radius_scaling_correlation': radius_correlation,
            'contact_forces': forces.tolist(),
            'contact_radii': contact_radii.tolist()
        }


def create_validation_report(
    validator: PhysicsValidator,
    accuracy_validator: MathematicalAccuracyValidator = None
) -> Dict[str, Any]:
    """
    Create comprehensive validation report.
    
    Args:
        validator (PhysicsValidator): Physics validator instance
        accuracy_validator (MathematicalAccuracyValidator): Mathematical accuracy validator
        
    Returns:
        dict: Comprehensive validation report
    """
    report = {
        'timestamp': '2026-02-28T00:00:00Z',
        'simulation_validation': validator.get_validation_summary(),
        'mathematical_accuracy': {},
        'recommendations': []
    }
    
    if accuracy_validator:
        # Add mathematical accuracy tests
        reynolds = np.logspace(0, 6, 50)
        mach = np.zeros_like(reynolds)
        
        drag_validation = accuracy_validator.validate_drag_coefficient(reynolds, mach)
        report['mathematical_accuracy']['drag_coefficient'] = drag_validation
        
        # Add recommendations based on validation results
        sim_valid = report['simulation_validation']['overall_valid']
        if not sim_valid:
            report['recommendations'].append(
                "Simulation validation failed - check for numerical instabilities or energy conservation issues"
            )
        
        if drag_validation['smoothness_valid'] and drag_validation['physical_bounds_valid']:
            report['recommendations'].append(
                "Drag coefficient calculations are mathematically sound"
            )
        else:
            report['recommendations'].append(
                "Drag coefficient calculations may have discontinuities or unphysical values"
            )
    
    return report