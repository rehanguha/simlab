"""
Mechanics calculations.

Contains functions for calculating gravity, terminal velocity, and spin decay.
"""

import numpy as np

def calculate_gravity(altitude: float = 0.0, config: dict = None) -> float:
    """
    Calculate gravitational acceleration at a given altitude.
    
    Args:
        altitude (float): Altitude above sea level in meters
        
    Returns:
        float: Gravitational acceleration in m/s²
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        mechanics = constants.get('mechanics', {})
        g_0 = mechanics.get('g_standard', 9.80665)
        R = mechanics.get('earth_radius', 6371000)
    else:
        # Standard gravitational acceleration at sea level
        g_0 = 9.80665  # m/s²
        
        # Earth's radius
        R = 6371000  # meters
    
    # Gravitational acceleration at altitude
    gravity = g_0 * (R / (R + altitude))**2
    
    return gravity

def calculate_terminal_velocity(
    mass: float,
    radius: float,
    drag_coefficient: float = 0.47,
    density: float = 1.225,
    config: dict = None
) -> float:
    """
    Calculate terminal velocity of a falling object.
    
    Args:
        mass (float): Mass of the object in kg
        radius (float): Radius of the object in m
        drag_coefficient (float): Drag coefficient
        density (float): Air density in kg/m³
        
    Returns:
        float: Terminal velocity in m/s
    """
    # Cross-sectional area
    area = np.pi * radius**2
    
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        mechanics = constants.get('mechanics', {})
        g = mechanics.get('g_standard', 9.81)
    else:
        g = 9.81  # m/s²
    
    # Terminal velocity formula
    # v_t = sqrt(2 * m * g / (rho * Cd * A))
    terminal_velocity = np.sqrt((2 * mass * g) / (density * drag_coefficient * area))
    
    return terminal_velocity

def calculate_spin_decay(
    initial_angular_velocity: float,
    time_step: float,
    density: float,
    viscosity: float,
    radius: float,
    config: dict = None
) -> float:
    """
    Calculate spin decay due to air resistance.
    
    Args:
        initial_angular_velocity (float): Initial angular velocity in rad/s
        time_step (float): Time step in seconds
        density (float): Air density in kg/m³
        viscosity (float): Dynamic viscosity in Pa·s
        radius (float): Radius in m
        
    Returns:
        float: Angular velocity after time step
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        mechanics = constants.get('mechanics', {})
        decay_constant = mechanics.get('spin_decay_constant', 0.1)
    else:
        # Simplified spin decay model
        # Assumes exponential decay with time constant based on air resistance
        
        # Moment of inertia for a sphere
        # I = (2/5) * m * r^2
        # For a typical ball, we can use a simplified decay constant
        
        # Decay constant (simplified model)
        decay_constant = 0.1  # This would depend on ball properties
    
    # Exponential decay
    angular_velocity = initial_angular_velocity * np.exp(-decay_constant * time_step)
    
    return angular_velocity