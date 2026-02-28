"""
physimlab Core - Main Simulation Engine

Wraps the existing physics simulation code into a clean, modern API.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import pandas as pd
import numpy as np

# Import existing modules
from .physics import (
    calculate_density, calculate_viscosity, calculate_speed_of_sound,
    calculate_reynolds_number, calculate_drag_coefficient,
    calculate_magnus_force, calculate_spin_decay
)
from .physics.aerodynamics_enhanced import (
    calculate_buoyancy_force,
    calculate_effective_mass,
    calculate_aerodynamic_forces,
    calculate_spin_decay_advanced
)
from .physics.contact import (
    calculate_hertzian_contact_force,
    calculate_coefficient_of_restitution,
    calculate_friction_forces_advanced
)
from .config.loader import ConfigLoader
from .output.manager import OutputManager
from .output.result import Result

class physimlabError(Exception):
    """Base exception for physimlab errors."""
    pass

class SimulationError(physimlabError):
    """Error during simulation execution."""
    pass

def run_simulation(
    config_path: str = "config.json",
    output_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run a ball drop simulation with the specified configuration.
    
    Args:
        config_path (str): Path to configuration file (JSON or YAML)
        output_dir (str): Output directory (auto-generated if None)
        **kwargs: Additional configuration overrides
        
    Returns:
        dict: Simulation results and summary statistics
        
    Example:
        >>> result = run_simulation()
        >>> print(result['summary']['flight_time'])
        19.995
    """
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load(config_path)
    
    # Apply overrides
    if kwargs:
        config = config_loader.merge_config(config, kwargs)
    
    # Validate configuration only if we have a config file
    if config_path is not None and config:
        try:
            config_loader.validate(config)
        except ValueError as e:
            # For backward compatibility, create a basic config from kwargs if validation fails
            if kwargs:
                config = kwargs
            else:
                raise SimulationError(f"Configuration validation failed: {e}") from e

    # Create output manager
    output_manager = OutputManager(output_dir=output_dir)

    # Run simulation
    try:
        result = _run_simulation_core(config, output_manager)
        return result
    except Exception as e:
        raise SimulationError(f"Simulation failed: {e}") from e


def create_scenario_config(scenario: str, height: float, mass: float, radius: float, spin: float) -> Dict[str, Any]:
    """Create a configuration for a specific scenario."""
    return {
        "scenario": scenario,
        "ball": {
            "mass": mass,
            "radius": radius,
            "spin_rps": spin
        },
        "position": {
            "z0": height
        },
        "wind": {
            "humidity_pct": 50.0
        },
        "simulation": {
            "g": 9.81,
            "dt": 0.001,
            "t_max": 30.0,
            "output_dir": f"outputs/scenario_{scenario}_{int(height)}m"
        }
    }

def run_scenario_simulation(scenario: str = "drop", height: float = 100.0, 
                           mass: float = 0.5, radius: float = 0.1, 
                           spin: float = 0.0, output_dir: Optional[str] = None,
                           quiet: bool = False, verbose: bool = False) -> None:
    """Run a simulation with predefined scenarios.
    
    Args:
        scenario: Scenario type ('drop', 'bounce', 'spin')
        height: Initial height in meters
        mass: Mass in kg
        radius: Radius in meters
        spin: Spin rate in rev/s
        output_dir: Output directory
        quiet: Suppress output
        verbose: Verbose output
    """
    try:
        # Create scenario configuration
        config = create_scenario_config(scenario, height, mass, radius, spin)
        
        if output_dir:
            config['simulation']['output_dir'] = output_dir
            
        # Create output directory
        output_path = Path(config['simulation']['output_dir'])
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize simulation
        sim = BallDropSimulation(config)
        
        # Run simulation
        if not quiet:
            print(f"Running {scenario} scenario...")
        sim.run()
        
        # Generate outputs
        if not quiet:
            print("Generating outputs...")
        sim.generate_outputs()
        
        if not quiet:
            print(f"Simulation completed. Results saved to {output_path}")
            
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        raise SimulationError(f"Simulation failed: {str(e)}")

class BallDropSimulation:
    """Legacy simulation class for backward compatibility."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = None
        self.summary = None
    
    def run(self) -> None:
        """Run the simulation."""
        result = _run_simulation_core(self.config, OutputManager())
        self.data = pd.DataFrame(result['data'])
        self.summary = result['summary']
    
    def generate_outputs(self) -> None:
        """Generate output files."""
        output_manager = OutputManager(output_dir=self.config['simulation']['output_dir'])
        result = Result(
            data=self.data,
            summary=self.summary,
            config=self.config,
            output_manager=output_manager
        )
        output_manager.save_all(result)

def batch_simulation(
    config_path: str = "config.json",
    parameters: List[Dict[str, Any]] = None,
    output_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Run batch simulations with parameter sweep.
    
    Args:
        config_path (str): Base configuration file
        parameters (list): List of parameter dictionaries to vary
        output_dir (str): Output directory
        
    Returns:
        list: List of simulation results
    """
    
    if parameters is None:
        parameters = []
    
    # Load base configuration
    config_loader = ConfigLoader()
    base_config = config_loader.load(config_path)
    
    # Generate parameter combinations
    configs = _generate_parameter_combinations(base_config, parameters)
    
    # Run simulations
    results = []
    for i, config in enumerate(configs):
        try:
            result = run_simulation(config_path=None, output_dir=output_dir, **config)
            result['config'] = config
            results.append(result)
        except Exception as e:
            print(f"Warning: Simulation {i+1} failed: {e}")
            continue
    
    return results

def compare_results(
    result1_path: str,
    result2_path: str,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compare two simulation results.
    
    Args:
        result1_path (str): Path to first result directory
        result2_path (str): Path to second result directory
        output_dir (str): Output directory for comparison
        
    Returns:
        dict: Comparison results
    """
    
    # Load results
    result1 = _load_result(result1_path)
    result2 = _load_result(result2_path)
    
    # Compare
    comparison = _compare_results_data(result1, result2)
    
    # Save comparison
    if output_dir:
        output_manager = OutputManager(output_dir=output_dir)
        output_manager.save_comparison(comparison, result1, result2)
    
    return comparison

def _apply_scenario_config(config: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Apply scenario-specific physics configurations."""
    
    # Create a copy to avoid modifying the original
    config = config.copy()
    
    # Get simulation config
    physics_config = config.get('simulation', {})
    
    # Scenario-specific configurations
    if scenario == 'terminal_velocity':
        # Terminal velocity test - disable buoyancy and virtual mass for pure gravity
        physics_config['buoyancy'] = False
        physics_config['use_virtual_mass'] = False
        physics_config['use_multi_regime_cd'] = True  # Use advanced drag
        physics_config['stop_speed_threshold'] = 0.01  # More precise stopping
        physics_config['c_spin_decay'] = 0.0  # No spin decay for terminal velocity
        physics_config['c_spin_aero'] = 0.0
        
    elif scenario == 'bounce':
        # Bounce test - enable hertzian contact for realistic bouncing
        physics_config['use_hertzian_contact'] = True
        physics_config['stop_speed_threshold'] = 0.05
        physics_config['stop_angular_threshold'] = 0.5
        physics_config['stop_hold_time'] = 0.5
        
    elif scenario == 'spin':
        # Spin test - enable advanced spin decay and Magnus effect
        physics_config['use_multi_regime_cd'] = True
        physics_config['c_spin_decay'] = 0.05
        physics_config['c_spin_aero'] = 0.02
        physics_config['buoyancy'] = False  # Focus on spin effects
        
    elif scenario == 'vacuum':
        # Vacuum test - disable all aerodynamic effects
        physics_config['buoyancy'] = False
        physics_config['use_virtual_mass'] = False
        physics_config['use_multi_regime_cd'] = False
        physics_config['c_spin_decay'] = 0.0
        physics_config['c_spin_aero'] = 0.0
        
    elif scenario == 'high_wind':
        # High wind test - enable all advanced features
        physics_config['buoyancy'] = True
        physics_config['use_virtual_mass'] = True
        physics_config['use_multi_regime_cd'] = True
        physics_config['adaptive_timestep'] = True
        physics_config['rtol'] = 1e-5
        physics_config['atol'] = 1e-7
        
    # Update the config
    config['simulation'] = physics_config
    
    return config


def _run_simulation_core(config: Dict[str, Any], output_manager: OutputManager) -> Dict[str, Any]:
    """Core simulation execution."""
    
    # Extract configuration - scenario is optional now
    scenario = config.get('scenario', 'drop')
    
    # Apply scenario-specific physics configurations
    config = _apply_scenario_config(config, scenario)
    
    # Get physics parameters from simulation section
    physics_config = config.get('simulation', {})
    gravity = physics_config.get('g', 9.81)
    time_step = physics_config.get('dt', 0.001)
    max_time = physics_config.get('t_max', 30.0)
    
    # Get object properties from ball section
    ball_config = config.get('ball', {})
    mass = ball_config.get('mass', 0.5)
    radius = ball_config.get('radius', 0.1)
    spin_rps = ball_config.get('spin_rps', 0.0)
    
    # Get position from position section
    position_config = config.get('position', {})
    initial_height = position_config.get('z0', 100.0)
    
    # Get environment parameters from wind section
    wind_config = config.get('wind', {})
    humidity = wind_config.get('humidity_pct', 50.0) / 100.0  # Convert percentage to fraction
    
    # Get temperature from wind config or use default
    # Note: Temperature is not explicitly in the new config, using default
    temperature = 288.15
    
    # Get additional simulation parameters
    physics_config = config.get('simulation', {})
    adaptive_timestep = physics_config.get('adaptive_timestep', False)
    rtol = physics_config.get('rtol', 1e-4)
    atol = physics_config.get('atol', 1e-6)
    min_dt = physics_config.get('min_dt', 1e-5)
    max_dt = physics_config.get('max_dt', 0.05)
    buoyancy = physics_config.get('buoyancy', True)
    use_virtual_mass = physics_config.get('use_virtual_mass', True)
    use_multi_regime_cd = physics_config.get('use_multi_regime_cd', True)
    use_hertzian_contact = physics_config.get('use_hertzian_contact', True)
    stop_speed_threshold = physics_config.get('stop_speed_threshold', 0.05)
    stop_angular_threshold = physics_config.get('stop_angular_threshold', 0.5)
    stop_hold_time = physics_config.get('stop_hold_time', 0.5)
    c_spin_decay = physics_config.get('c_spin_decay', 0.05)
    c_spin_aero = physics_config.get('c_spin_aero', 0.02)
    
    # Initialize state
    t = 0.0
    x, y, z = 0.0, 0.0, initial_height
    vx, vy, vz = 0.0, 0.0, 0.0
    omega_x, omega_y, omega_z = 0.0, 0.0, spin_rps * 2 * np.pi  # Convert to rad/s
    
    # Data collection
    data = []
    
    # Stopping condition tracking
    stopped_time = 0.0
    last_speed = float('inf')
    last_angular_speed = float('inf')
    
    # Simulation loop
    while t < max_time:
        # Calculate physics
        air_density = calculate_density(temperature, humidity, config)
        viscosity = calculate_viscosity(temperature, config)
        speed_of_sound = calculate_speed_of_sound(temperature, config)
        
        # Velocity magnitude
        speed = np.sqrt(vx**2 + vy**2 + vz**2)
        angular_speed = np.sqrt(omega_x**2 + omega_y**2 + omega_z**2)
        
        # Initialize variables for zero speed case
        reynolds = 0.0
        cd = 0.47
        drag_force = 0.0
        drag_x = drag_y = drag_z = 0.0
        magnus = 0.0
        magnus_x = magnus_y = 0.0
        buoyancy_force = 0.0
        
        # Initialize acceleration variables
        ax, ay, az = 0.0, 0.0, 0.0
        
        # Calculate aerodynamic forces
        if speed < 1e-6:
            # Very low speed - minimal forces
            ax, ay, az = 0.0, -gravity, 0.0
        else:
            # Enhanced aerodynamic calculations based on config flags
            velocity_vector = np.array([vx, vy, vz])
            angular_velocity_vector = np.array([omega_x, omega_y, omega_z])
            
            # Use enhanced aerodynamics if enabled
            if use_multi_regime_cd or buoyancy or use_virtual_mass:
                # Calculate enhanced aerodynamic forces
                force_vector, torque_vector, reynolds = calculate_aerodynamic_forces(
                    velocity_vector, angular_velocity_vector, air_density, viscosity, 
                    radius, mass, gravity, config=config
                )
                
                fx, fy, fz = force_vector
                tx, ty, tz = torque_vector
                
                # Apply virtual mass effect if enabled
                if use_virtual_mass:
                    effective_mass = calculate_effective_mass(mass, air_density, (4.0/3.0) * np.pi * radius**3)
                    ax = fx / effective_mass
                    ay = fy / effective_mass
                    az = fz / effective_mass
                else:
                    ax = fx / mass
                    ay = fy / mass
                    az = fz / mass
                
                # Update angular velocity with enhanced decay
                if use_virtual_mass:
                    # Apply torque effects
                    I = (2.0/5.0) * mass * radius**2  # Moment of inertia
                    alpha_x = tx / I
                    alpha_y = ty / I
                    alpha_z = tz / I
                    omega_x += alpha_x * time_step
                    omega_y += alpha_y * time_step
                    omega_z += alpha_z * time_step
                
                # Enhanced spin decay with configurable coefficients
                c_spin_decay = physics_config.get('c_spin_decay', 0.05)
                c_spin_aero = physics_config.get('c_spin_aero', 0.02)
                
                # Apply spin decay
                angular_velocity_vector = calculate_spin_decay_advanced(
                    angular_velocity_vector, velocity_vector, air_density, viscosity, 
                    radius, time_step, config
                )
                
                # Apply configurable spin decay coefficient
                angular_velocity_vector *= (1.0 - c_spin_decay * time_step)
                
                # Apply aerodynamic spin effects
                if np.linalg.norm(velocity_vector) > 1e-6:
                    # Aerodynamic torque based on velocity and spin
                    v_unit = velocity_vector / np.linalg.norm(velocity_vector)
                    spin_axis = angular_velocity_vector / (np.linalg.norm(angular_velocity_vector) + 1e-10)
                    
                    # Cross product gives torque direction
                    torque_direction = np.cross(v_unit, spin_axis)
                    torque_magnitude = c_spin_aero * air_density * np.linalg.norm(velocity_vector)**2 * radius**3
                    
                    # Apply aerodynamic torque
                    angular_velocity_vector += torque_magnitude * torque_direction * time_step
                
                omega_x, omega_y, omega_z = angular_velocity_vector
                
            else:
                # Standard aerodynamic forces
                reynolds = calculate_reynolds_number(air_density, speed, radius, viscosity)
                cd = calculate_drag_coefficient(reynolds, config)
                
                # Drag force
                drag_force = 0.5 * air_density * speed**2 * np.pi * radius**2 * cd
                drag_x = -drag_force * vx / speed
                drag_y = -drag_force * vy / speed
                drag_z = -drag_force * vz / speed
                
                # Magnus force
                magnus = calculate_magnus_force(air_density, speed, radius, omega_z, config)
                magnus_x = magnus * vy / speed if speed > 0 else 0.0
                magnus_y = -magnus * vx / speed if speed > 0 else 0.0
                
                # Gravity
                gravity_force = mass * gravity
                
                # Buoyancy force if enabled
                if buoyancy:
                    volume = (4.0/3.0) * np.pi * radius**3
                    buoyancy_force = calculate_buoyancy_force(air_density, volume, gravity)
                else:
                    buoyancy_force = 0.0
                
                # Total forces
                fx = drag_x + magnus_x
                fy = drag_y + magnus_y
                fz = drag_z - gravity_force + buoyancy_force
                
                # Accelerations
                ax = fx / mass
                ay = fy / mass
                az = fz / mass
                
                # Standard spin decay
                omega_z = calculate_spin_decay(omega_z, time_step, air_density, viscosity, radius, config)
        
        # Update velocities
        vx += ax * time_step
        vy += ay * time_step
        vz += az * time_step
        
        # Update positions
        x += vx * time_step
        y += vy * time_step
        z += vz * time_step
        
        # Ground collision with enhanced contact physics
        if z <= 0:
            z = 0
            if use_hertzian_contact:
                # Enhanced contact model with advanced friction
                penetration = -z
                contact_force = calculate_hertzian_contact_force(penetration, radius, mass, config)
                normal_velocity = abs(vz)
                restitution = calculate_coefficient_of_restitution(normal_velocity, 0.7, 0.02, 0.0, 0.0)
                
                # Calculate advanced friction forces
                relative_velocity = np.array([vx, vy, 0.0])  # Horizontal velocity at contact
                angular_velocity = np.array([omega_x, omega_y, omega_z])
                
                friction_force = calculate_friction_forces_advanced(
                    contact_force, relative_velocity, angular_velocity, radius, config
                )
                
                # Apply restitution and friction
                vz = -vz * restitution
                vx += friction_force[0] * time_step / mass
                vy += friction_force[1] * time_step / mass
            else:
                # Standard contact model
                vz = -vz * 0.8  # Elasticity
                if abs(vz) < 0.1:  # Stop bouncing
                    break
        
        # Check stopping conditions
        if speed < stop_speed_threshold and angular_speed < stop_angular_threshold:
            if t - stopped_time > stop_hold_time:
                break
            elif stopped_time == 0.0:
                stopped_time = t
        else:
            stopped_time = 0.0
        
        # Store data
        data.append({
            'time': t,
            'x': x,
            'y': y,
            'z': z,
            'vx': vx,
            'vy': vy,
            'vz': vz,
            'speed': speed,
            'omega_x': omega_x,
            'omega_y': omega_y,
            'omega_z': omega_z,
            'air_density': air_density,
            'reynolds': reynolds,
            'cd': cd,
            'mach': speed / speed_of_sound if speed_of_sound > 0 else 0.0,
            'buoyancy_force': buoyancy_force,
            'effective_mass': calculate_effective_mass(mass, air_density, (4.0/3.0) * np.pi * radius**3) if use_virtual_mass else mass
        })
        
        # Adaptive timestep control with proper error control
        if adaptive_timestep:
            # Calculate error estimate using both relative and absolute tolerances
            acceleration = np.sqrt(ax**2 + ay**2 + az**2)
            if acceleration > 0:
                # Richardson extrapolation style error estimation
                # Use both rtol (relative) and atol (absolute) for error control
                error_estimate = max(atol, rtol * acceleration)
                suggested_dt = np.sqrt(2 * error_estimate / acceleration)
                time_step = max(min_dt, min(max_dt, suggested_dt))
        
        t += time_step
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Calculate summary statistics
    summary = {
        'flight_time': float(df['time'].iloc[-1]),
        'max_height': float(df['z'].max()),
        'horizontal_range': float(df['x'].iloc[-1]),
        'max_velocity': float(df['speed'].max()),
        'ground_contacts': int((df['z'] == 0).sum()),
        'max_mach': float(df['mach'].max()),
        'is_stable': True,
        'energy_conserved': True
    }
    
    # Create result object
    result = Result(
        data=df,
        summary=summary,
        config=config,
        output_manager=output_manager
    )
    
    # Save outputs with enhanced reporting
    output_manager.save_all(result)
    
    # Get the enhanced summary from the output manager
    enhanced_summary = summary.copy()
    if hasattr(output_manager, 'calculate_detailed_statistics'):
        stats = output_manager.calculate_detailed_statistics(df, config)
        enhanced_summary.update({
            "max_speed": stats["max_speed"],
            "max_mach": stats["max_mach"],
            "max_reynolds": stats["max_reynolds"],
            "bounce_count": stats["bounce_count"],
            "energy_loss": stats["energy_loss"],
            "energy_loss_pct": stats["energy_loss_pct"],
            "is_stable": stats["is_stable"],
            "energy_conserved": stats["energy_conserved"],
            "max_energy_gain": stats["max_energy_gain"],
            "max_energy_gain_pct": stats["max_energy_gain_pct"],
        })
    
    return {
        'data': df.to_dict('records'),
        'summary': enhanced_summary,
        'config': config,
        'output_files': output_manager.get_output_files()
    }

def _generate_parameter_combinations(base_config: Dict[str, Any], parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate parameter combinations for batch simulation."""
    
    configs = [base_config.copy()]
    
    for param in parameters:
        name = param['name']
        min_val = param['min']
        max_val = param['max']
        steps = param['steps']
        
        new_configs = []
        for config in configs:
            for i in range(steps):
                value = min_val + (max_val - min_val) * i / (steps - 1)
                new_config = config.copy()
                new_config[name] = value
                new_configs.append(new_config)
        
        configs = new_configs
    
    return configs

def _load_result(result_path: str) -> Dict[str, Any]:
    """Load a saved simulation result."""
    
    result_file = os.path.join(result_path, 'result.json')
    if os.path.exists(result_file):
        with open(result_file, 'r') as f:
            return json.load(f)
    
    raise physimlabError(f"Result file not found: {result_file}")

def _compare_results_data(result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two simulation results."""
    
    comparison = {}
    
    # Compare summary statistics
    for key in result1.get('summary', {}):
        if key in result2.get('summary', {}):
            val1 = result1['summary'][key]
            val2 = result2['summary'][key]
            diff = val2 - val1
            pct_diff = (diff / val1 * 100) if val1 != 0 else 0
            comparison[f"{key}_diff"] = diff
            comparison[f"{key}_pct_diff"] = pct_diff
    
    return comparison