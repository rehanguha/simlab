"""
Enhanced aerodynamics calculations.

Contains advanced aerodynamic functions including multi-regime drag coefficient,
buoyancy force, virtual mass effect, and compressibility corrections.
"""

import numpy as np
from typing import Tuple, Optional
from .wind import calculate_atmospheric_properties


def calculate_multi_regime_drag_coefficient(
    reynolds: float,
    mach: float = 0.0,
    surface_roughness: float = 0.0,
    config: Optional[dict] = None
) -> float:
    """
    Calculate drag coefficient using multi-regime correlation with compressibility corrections.
    
    Args:
        reynolds (float): Reynolds number
        mach (float): Mach number
        surface_roughness (float): Surface roughness height (m)
        config (dict): Configuration parameters
        
    Returns:
        float: Drag coefficient
    """
    if config is None:
        config = {}
    
    # Get configuration parameters
    roughness_factor = config.get('roughness_factor', 1.0)
    compressibility_correction = config.get('compressibility_correction', True)
    
    # Determine flow regime and calculate base drag coefficient
    if reynolds <= 1:
        # Stokes flow regime
        cd = 24.0 / reynolds
    
    elif reynolds <= 1000:
        # Intermediate regime (Schiller-Naumann)
        cd = (24.0 / reynolds) * (1.0 + 0.15 * reynolds**0.687)
    
    elif reynolds <= 3e5:
        # Newton regime (subcritical)
        cd = 0.44
    
    elif reynolds <= 3.5e5:
        # Drag crisis regime
        cd = 0.44 - 0.35 * np.sqrt((reynolds - 3e5) / 5e4)
    
    else:
        # Post-crisis regime (supercritical)
        cd = 0.09 + 0.06 * np.exp(-(reynolds - 3.5e5) / 1e6)
    
    # Surface roughness effect (shifts drag crisis to lower Reynolds numbers)
    if surface_roughness > 0:
        roughness_effect = min(surface_roughness * 1e4, 0.8)
        # Shift critical Reynolds number
        re_crit_shift = 1e5 * roughness_effect
        # Modify drag coefficient based on roughness
        if reynolds > 2e5:
            cd = cd * (1.0 + 0.2 * roughness_effect)
    
    # Compressibility corrections for high Mach numbers
    if compressibility_correction and mach > 0.3:
        # Prandtl-Glauert correction for subsonic flow
        if mach < 0.8:
            beta = np.sqrt(1.0 - mach**2)
            cd = cd / beta
        else:
            # Transonic and supersonic corrections
            cd = cd * (1.0 + 0.15 * mach**2)
            if mach > 1.0:
                cd = cd * (1.0 + 0.5 * (mach - 1.0)**2)
    
    return cd


def calculate_buoyancy_force(
    density: float,
    volume: float,
    gravity: float = 9.81
) -> float:
    """
    Calculate buoyancy force using Archimedes' principle.
    
    Args:
        density (float): Fluid density (kg/m³)
        volume (float): Displaced volume (m³)
        gravity (float): Gravitational acceleration (m/s²)
        
    Returns:
        float: Buoyancy force (N)
    """
    return density * volume * gravity


def calculate_virtual_mass(
    density: float,
    volume: float,
    added_mass_coefficient: float = 0.5
) -> float:
    """
    Calculate virtual (added) mass effect.
    
    Args:
        density (float): Fluid density (kg/m³)
        volume (float): Object volume (m³)
        added_mass_coefficient (float): Added mass coefficient (0.5 for sphere)
        
    Returns:
        float: Added mass (kg)
    """
    return added_mass_coefficient * density * volume


def calculate_effective_mass(
    mass: float,
    density: float,
    volume: float,
    added_mass_coefficient: float = 0.5
) -> float:
    """
    Calculate effective mass including virtual mass effect.
    
    Args:
        mass (float): Object mass (kg)
        density (float): Fluid density (kg/m³)
        volume (float): Object volume (m³)
        added_mass_coefficient (float): Added mass coefficient
        
    Returns:
        float: Effective mass (kg)
    """
    added_mass = calculate_virtual_mass(density, volume, added_mass_coefficient)
    return mass + added_mass


def calculate_aerodynamic_forces(
    velocity: np.ndarray,
    angular_velocity: np.ndarray,
    density: float,
    viscosity: float,
    radius: float,
    mass: float,
    gravity: float = 9.81,
    wind_velocity: Optional[np.ndarray] = None,
    surface_roughness: float = 0.0,
    config: Optional[dict] = None
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Calculate complete aerodynamic forces including drag, lift, and buoyancy.
    
    Args:
        velocity (np.ndarray): Object velocity [vx, vy, vz]
        angular_velocity (np.ndarray): Angular velocity [wx, wy, wz]
        density (float): Air density (kg/m³)
        viscosity (float): Dynamic viscosity (Pa·s)
        radius (float): Object radius (m)
        mass (float): Object mass (kg)
        gravity (float): Gravitational acceleration (m/s²)
        wind_velocity (np.ndarray): Wind velocity [wx, wy, wz]
        surface_roughness (float): Surface roughness (m)
        config (dict): Configuration parameters
        
    Returns:
        Tuple of (force_vector, torque_vector, reynolds_number)
    """
    if config is None:
        config = {}
    
    # Calculate relative velocity
    if wind_velocity is not None:
        v_rel = velocity - wind_velocity
    else:
        v_rel = velocity
    
    v_mag = np.linalg.norm(v_rel)
    
    if v_mag < 1e-6:
        return np.zeros(3), np.zeros(3), 0.0
    
    # Calculate Reynolds number
    volume = (4.0/3.0) * np.pi * radius**3
    reynolds = (2.0 * radius * v_mag * density) / viscosity
    
    # Calculate Mach number
    speed_of_sound = np.sqrt(1.4 * 287.058 * 288.15)  # Simplified
    mach = v_mag / speed_of_sound
    
    # Calculate drag coefficient
    cd = calculate_multi_regime_drag_coefficient(reynolds, mach, surface_roughness, config)
    
    # Calculate lift coefficient (Magnus effect)
    omega_mag = np.linalg.norm(angular_velocity)
    if omega_mag > 1e-6:
        spin_parameter = (omega_mag * radius) / v_mag
        cl = (0.4 * spin_parameter) / (1.0 + 2.0 * spin_parameter)
    else:
        cl = 0.0
    
    # Aerodynamic forces
    area = np.pi * radius**2
    dynamic_pressure = 0.5 * density * v_mag**2
    
    # Drag force (opposite to relative velocity)
    drag_force = dynamic_pressure * area * cd
    drag_vector = -drag_force * v_rel / v_mag
    
    # Lift force (perpendicular to velocity and spin axis)
    lift_force = dynamic_pressure * area * cl
    if omega_mag > 1e-6:
        lift_direction = np.cross(angular_velocity, v_rel)
        if np.linalg.norm(lift_direction) > 1e-6:
            lift_direction = lift_direction / np.linalg.norm(lift_direction)
            lift_vector = lift_force * lift_direction
        else:
            lift_vector = np.zeros(3)
    else:
        lift_vector = np.zeros(3)
    
    # Buoyancy force (upward)
    buoyancy_force = calculate_buoyancy_force(density, volume, gravity)
    buoyancy_vector = np.array([0.0, 0.0, buoyancy_force])
    
    # Gravitational force
    gravity_vector = np.array([0.0, 0.0, -mass * gravity])
    
    # Total force
    total_force = drag_vector + lift_vector + buoyancy_vector + gravity_vector
    
    # Aerodynamic torque (Magnus effect)
    if omega_mag > 1e-6:
        # Simplified torque calculation
        torque_magnitude = 0.1 * density * v_mag * omega_mag * radius**3
        torque_direction = np.cross(angular_velocity, v_rel)
        if np.linalg.norm(torque_direction) > 1e-6:
            torque_direction = torque_direction / np.linalg.norm(torque_direction)
            torque_vector = torque_magnitude * torque_direction
        else:
            torque_vector = np.zeros(3)
    else:
        torque_vector = np.zeros(3)
    
    return total_force, torque_vector, reynolds


def calculate_spin_decay_advanced(
    angular_velocity: np.ndarray,
    velocity: np.ndarray,
    density: float,
    viscosity: float,
    radius: float,
    time_step: float,
    config: Optional[dict] = None
) -> np.ndarray:
    """
    Calculate advanced spin decay with aerodynamic and contact effects.
    
    Args:
        angular_velocity (np.ndarray): Current angular velocity
        velocity (np.ndarray): Linear velocity
        density (float): Air density
        viscosity (float): Dynamic viscosity
        radius (float): Object radius
        time_step (float): Time step
        config (dict): Configuration parameters
        
    Returns:
        np.ndarray: New angular velocity
    """
    if config is None:
        config = {}
    
    omega_mag = np.linalg.norm(angular_velocity)
    v_mag = np.linalg.norm(velocity)
    
    if omega_mag < 1e-6:
        return angular_velocity
    
    # Aerodynamic torque coefficient
    if v_mag < 1e-6:
        # Pure rotation decay
        ct = 64.0 / (np.linalg.norm(angular_velocity) * radius * 2 * radius / viscosity + 1)
    elif v_mag < 10.0:
        # Intermediate regime
        ct = 0.5 / (v_mag / (radius * omega_mag))**0.3
    else:
        # High speed regime
        ct = 0.05 * (1.0 + 0.5 * v_mag / (radius * omega_mag))
    
    # Aerodynamic torque magnitude
    torque_mag = 0.5 * density * v_mag**2 * np.pi * radius**2 * ct * radius
    
    # Torque direction (opposes spin)
    torque_vector = -torque_mag * angular_velocity / omega_mag
    
    # Moment of inertia for sphere
    I = (2.0/5.0) * 1.0 * radius**2  # Assuming unit mass for coefficient
    
    # Angular acceleration
    alpha = torque_vector / I
    
    # Update angular velocity
    new_omega = angular_velocity + alpha * time_step
    
    # Additional decay factors
    c_decay = config.get('c_spin_decay', 0.05)
    c_aero = config.get('c_spin_aero', 0.02)
    
    decay_factor = np.exp(-(c_decay + c_aero * v_mag) * time_step)
    new_omega *= decay_factor
    
    return new_omega


def calculate_compressibility_correction(
    mach: float,
    flow_type: str = 'subsonic'
) -> float:
    """
    Calculate compressibility correction factor.
    
    Args:
        mach (float): Mach number
        flow_type (str): Flow type ('subsonic', 'transonic', 'supersonic')
        
    Returns:
        float: Correction factor
    """
    if mach < 0.3:
        return 1.0
    
    if flow_type == 'subsonic':
        # Prandtl-Glauert correction
        beta = np.sqrt(1.0 - mach**2)
        return 1.0 / beta
    
    elif flow_type == 'transonic':
        # Transonic correction
        if mach < 1.0:
            return 1.0 + 0.5 * mach**2
        else:
            return 1.0 + 0.5 * (mach - 1.0)**2
    
    else:  # supersonic
        # Supersonic correction
        return 1.0 + 0.1 * mach**2


class AerodynamicModel:
    """Advanced aerodynamic model with all effects."""
    
    def __init__(self, config: dict):
        """
        Initialize aerodynamic model.
        
        Args:
            config (dict): Aerodynamic configuration
        """
        self.config = config
        self.force_history = []
        
    def calculate_forces(self, state: dict) -> dict:
        """
        Calculate aerodynamic forces for current state.
        
        Args:
            state (dict): Current state with velocity, angular_velocity, etc.
            
        Returns:
            dict: Forces and torques
        """
        # Extract state variables
        velocity = state['velocity']
        angular_velocity = state['angular_velocity']
        position = state['position']
        radius = state['radius']
        mass = state['mass']
        
        # Get atmospheric properties
        density, viscosity, speed_of_sound = calculate_atmospheric_properties(
            altitude=position[2],
            temperature=288.15,
            humidity=self.config.get('humidity', 0.5)
        )
        
        # Get wind effects
        wind_velocity = None
        if 'wind_field' in self.config:
            wind_field = self.config['wind_field']
            wind_velocity = wind_field.get_wind_velocity(position, state.get('time', 0.0))
        
        # Calculate forces
        force, torque, reynolds = calculate_aerodynamic_forces(
            velocity, angular_velocity, density, viscosity, radius, mass,
            wind_velocity=wind_velocity,
            surface_roughness=self.config.get('surface_roughness', 0.0),
            config=self.config
        )
        
        # Calculate spin decay
        new_angular_velocity = calculate_spin_decay_advanced(
            angular_velocity, velocity, density, viscosity, radius,
            self.config.get('time_step', 0.001), self.config
        )
        
        # Store results
        result = {
            'force': force,
            'torque': torque,
            'reynolds': reynolds,
            'new_angular_velocity': new_angular_velocity,
            'density': density,
            'viscosity': viscosity,
            'speed_of_sound': speed_of_sound
        }
        
        # Track history
        self.force_history.append({
            'time': state.get('time', 0.0),
            'position': position.copy(),
            'velocity': velocity.copy(),
            'force': force.copy(),
            'reynolds': reynolds
        })
        
        return result
    
    def get_force_history(self) -> list:
        """Get force calculation history."""
        return self.force_history.copy()
    
    def get_average_reynolds(self) -> float:
        """Get average Reynolds number."""
        if not self.force_history:
            return 0.0
        reynolds_values = [entry['reynolds'] for entry in self.force_history]
        return np.mean(reynolds_values)


