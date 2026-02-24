"""
Aerodynamics calculations.

Contains functions for calculating air density, viscosity, speed of sound,
Reynolds number, drag coefficient, Magnus force, and wind force.
"""

import numpy as np
from ..config.loader import ConfigLoader

def calculate_density(temperature: float, humidity: float = 0.5, config: dict = None) -> float:
    """
    Calculate air density using the ideal gas law.
    
    Args:
        temperature (float): Temperature in Kelvin
        humidity (float): Relative humidity (0-1)
        
    Returns:
        float: Air density in kg/m³
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        aerodynamics = constants.get('aerodynamics', {})
        pressure = aerodynamics.get('pressure_sea_level', 101325.0)
        R_dry = aerodynamics.get('R_dry', 287.058)
        R_vapor = aerodynamics.get('R_vapor', 461.495)
    else:
        # Standard atmospheric pressure at sea level
        pressure = 101325.0  # Pa
        
        # Gas constants
        R_dry = 287.058  # J/(kg·K) - gas constant for dry air
        R_vapor = 461.495  # J/(kg·K) - gas constant for water vapor
    
    # Calculate vapor pressure
    # Simplified Magnus formula for saturation vapor pressure
    T_celsius = temperature - 273.15
    saturation_vapor_pressure = 611.2 * np.exp((17.67 * T_celsius) / (T_celsius + 243.5))
    vapor_pressure = humidity * saturation_vapor_pressure
    
    # Calculate density
    dry_air_pressure = pressure - vapor_pressure
    density = (dry_air_pressure / (R_dry * temperature)) + (vapor_pressure / (R_vapor * temperature))
    
    return density

def calculate_viscosity(temperature: float, config: dict = None) -> float:
    """
    Calculate dynamic viscosity of air using Sutherland's formula.
    
    Args:
        temperature (float): Temperature in Kelvin
        
    Returns:
        float: Dynamic viscosity in Pa·s
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        aerodynamics = constants.get('aerodynamics', {})
        mu_0 = aerodynamics.get('sutherland_mu0', 1.716e-5)
        T_0 = aerodynamics.get('sutherland_t0', 273.15)
        S = aerodynamics.get('sutherland_s', 110.4)
    else:
        # Sutherland's constants for air
        mu_0 = 1.716e-5  # Reference viscosity at T_0
        T_0 = 273.15     # Reference temperature in K
        S = 110.4        # Sutherland's constant for air in K
    
    # Sutherland's formula
    viscosity = mu_0 * (temperature / T_0)**1.5 * (T_0 + S) / (temperature + S)
    
    return viscosity

def calculate_speed_of_sound(temperature: float, config: dict = None) -> float:
    """
    Calculate speed of sound in air.
    
    Args:
        temperature (float): Temperature in Kelvin
        
    Returns:
        float: Speed of sound in m/s
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        aerodynamics = constants.get('aerodynamics', {})
        gamma = aerodynamics.get('gamma_air', 1.4)
        R = aerodynamics.get('R_dry', 287.058)
    else:
        # Ratio of specific heats for air
        gamma = 1.4
        # Gas constant for dry air
        R = 287.058  # J/(kg·K)
    
    speed_of_sound = np.sqrt(gamma * R * temperature)
    return speed_of_sound

def calculate_reynolds_number(
    density: float,
    velocity: float,
    diameter: float,
    viscosity: float
) -> float:
    """
    Calculate Reynolds number.
    
    Args:
        density (float): Air density in kg/m³
        velocity (float): Velocity in m/s
        diameter (float): Characteristic diameter in m
        viscosity (float): Dynamic viscosity in Pa·s
        
    Returns:
        float: Reynolds number
    """
    return (density * velocity * diameter) / viscosity

def calculate_drag_coefficient(reynolds: float, config: dict = None) -> float:
    """
    Calculate drag coefficient based on Reynolds number.
    
    Args:
        reynolds (float): Reynolds number
        
    Returns:
        float: Drag coefficient
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        aerodynamics = constants.get('aerodynamics', {})
        stokes_coeff = aerodynamics.get('stokes_coefficient', 24.0)
        intermediate_coeff = aerodynamics.get('intermediate_coefficient', 4.0)
        turbulent_cd = aerodynamics.get('turbulent_cd', 0.47)
    else:
        stokes_coeff = 24.0
        intermediate_coeff = 4.0
        turbulent_cd = 0.47
    
    if reynolds < 1:
        # Stokes flow
        return stokes_coeff / reynolds
    elif reynolds < 1000:
        # Intermediate flow
        return stokes_coeff / reynolds + intermediate_coeff / np.sqrt(reynolds) + 0.4
    else:
        # Turbulent flow
        return turbulent_cd

def calculate_magnus_force(
    density: float,
    velocity: float,
    radius: float,
    angular_velocity: float,
    config: dict = None
) -> float:
    """
    Calculate Magnus force magnitude.
    
    Args:
        density (float): Air density in kg/m³
        velocity (float): Velocity in m/s
        radius (float): Radius in m
        angular_velocity (float): Angular velocity in rad/s
        
    Returns:
        float: Magnus force magnitude
    """
    # Get constants from config or use defaults
    if config:
        constants = config.get('constants', {})
        aerodynamics = constants.get('aerodynamics', {})
        magnus_coeff = aerodynamics.get('magnus_coefficient', 0.5)
    else:
        magnus_coeff = 0.5
    
    # Simplified Magnus force calculation
    # F_magnus = coefficient * density * velocity * angular_velocity * radius^3
    magnus_force = magnus_coeff * density * velocity * angular_velocity * (radius**3)
    return magnus_force

def calculate_wind_force(
    density: float,
    velocity: float,
    area: float,
    drag_coefficient: float,
    wind_velocity: float = 0.0,
    config: dict = None
) -> float:
    """
    Calculate wind force on an object.
    
    Args:
        density (float): Air density in kg/m³
        velocity (float): Object velocity in m/s
        area (float): Cross-sectional area in m²
        drag_coefficient (float): Drag coefficient
        wind_velocity (float): Wind velocity in m/s
        
    Returns:
        float: Wind force
    """
    relative_velocity = velocity - wind_velocity
    wind_force = 0.5 * density * (relative_velocity**2) * area * drag_coefficient
    return wind_force
