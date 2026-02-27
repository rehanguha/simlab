"""
Wind and atmospheric effects.

Contains functions for wind velocity calculation, gust modeling, and atmospheric properties.
"""

import numpy as np
from typing import Tuple, Optional


def calculate_wind_velocity(
    z: float,
    ref_speed: float = 2.0,
    ref_height: float = 10.0,
    shear_alpha: float = 0.15,
    direction_deg: float = 0.0,
    gust_speed: float = 0.0
) -> np.ndarray:
    """
    Calculate wind velocity at height z using power law.
    
    Args:
        z (float): Height above ground (m)
        ref_speed (float): Reference wind speed at ref_height (m/s)
        ref_height (float): Reference height (m)
        shear_alpha (float): Power law exponent (typically 0.12-0.16)
        direction_deg (float): Wind direction in degrees (0-360)
        gust_speed (float): Additional gust component (m/s)
        
    Returns:
        np.ndarray: Wind velocity vector [u, v, w] in m/s
    """
    # Power law for wind speed variation with height
    if z <= 0:
        wind_speed = 0.0
    else:
        wind_speed = ref_speed * (z / ref_height) ** shear_alpha
    
    # Add gust component
    wind_speed += gust_speed
    
    # Convert direction to radians
    direction_rad = np.radians(direction_deg)
    
    # Wind velocity components
    u = wind_speed * np.cos(direction_rad)  # East component
    v = wind_speed * np.sin(direction_rad)  # North component
    w = 0.0  # Vertical component (usually negligible)
    
    return np.array([u, v, w])


def generate_gust_process(
    time: float,
    tau: float = 1.5,
    sigma: float = 0.5,
    dt: float = 0.001,
    seed: Optional[int] = None
) -> float:
    """
    Generate gust velocity using Ornstein-Uhlenbeck process.
    
    Args:
        time (float): Current time (s)
        tau (float): Correlation time constant (s)
        sigma (float): Gust intensity standard deviation (m/s)
        dt (float): Time step (s)
        seed (int): Random seed for reproducibility
        
    Returns:
        float: Gust velocity component (m/s)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Ornstein-Uhlenbeck process parameters
    # dx = -x/tau * dt + sigma * sqrt(2/tau) * dW
    
    # For discrete time simulation, we use the analytical solution
    # x(t+dt) = x(t) * exp(-dt/tau) + sigma * sqrt(1 - exp(-2*dt/tau)) * N(0,1)
    
    # This is a simplified version - in practice, we'd maintain state
    # For now, we'll use a simplified random process
    
    # Generate random normal variable
    xi = np.random.normal()
    
    # Simplified gust model
    gust = sigma * np.sin(2 * np.pi * time / tau) * np.exp(-time / (2 * tau))
    
    return gust


def calculate_relative_velocity(
    velocity: np.ndarray,
    wind_velocity: np.ndarray
) -> np.ndarray:
    """
    Calculate relative velocity between object and air.
    
    Args:
        velocity (np.ndarray): Object velocity vector [vx, vy, vz]
        wind_velocity (np.ndarray): Wind velocity vector [wx, wy, wz]
        
    Returns:
        np.ndarray: Relative velocity vector
    """
    return velocity - wind_velocity


def calculate_atmospheric_properties(
    altitude: float = 0.0,
    temperature: float = 288.15,
    humidity: float = 0.5
) -> Tuple[float, float, float]:
    """
    Calculate atmospheric properties using ISA model with humidity correction.
    
    Args:
        altitude (float): Altitude above sea level (m)
        temperature (float): Temperature (K)
        humidity (float): Relative humidity (0-1)
        
    Returns:
        Tuple of (density, viscosity, speed_of_sound)
    """
    # Standard ISA constants
    T0 = 288.15  # Sea level temperature (K)
    p0 = 101325  # Sea level pressure (Pa)
    R_d = 287.058  # Gas constant for dry air (J/kg·K)
    R_v = 461.495  # Gas constant for water vapor (J/kg·K)
    L = 0.0065  # Temperature lapse rate (K/m)
    g = 9.80665  # Gravitational acceleration (m/s²)
    
    # Temperature at altitude (troposphere)
    T = T0 - L * altitude
    
    # Pressure at altitude
    p = p0 * (T / T0) ** (g / (R_d * L))
    
    # Saturation vapor pressure (Buck equation)
    T_c = T - 273.15  # Celsius
    e_s = 611.21 * np.exp((18.678 - T_c/234.5) * T_c / (257.14 + T_c))
    
    # Actual vapor pressure
    e = e_s * humidity
    
    # Air density with humidity correction
    rho_dry = p / (R_d * T)
    rho_vapor = e / (R_v * T)
    density = rho_dry + rho_vapor
    
    # Dynamic viscosity (Sutherland's law)
    mu_ref = 1.716e-5
    T_ref = 273.15
    S = 110.4
    viscosity = mu_ref * (T / T_ref) ** 1.5 * (T_ref + S) / (T + S)
    
    # Speed of sound
    gamma = 1.4  # Ratio of specific heats
    speed_of_sound = np.sqrt(gamma * R_d * T)
    
    return density, viscosity, speed_of_sound


def calculate_wind_profile(
    heights: np.ndarray,
    ref_speed: float = 2.0,
    ref_height: float = 10.0,
    shear_alpha: float = 0.15,
    direction_deg: float = 0.0
) -> np.ndarray:
    """
    Calculate wind profile over a range of heights.
    
    Args:
        heights (np.ndarray): Array of heights (m)
        ref_speed (float): Reference wind speed
        ref_height (float): Reference height
        shear_alpha (float): Power law exponent
        direction_deg (float): Wind direction
        
    Returns:
        np.ndarray: Wind speeds at each height
    """
    wind_speeds = ref_speed * (heights / ref_height) ** shear_alpha
    
    # Set wind speed to 0 at and below ground
    wind_speeds[heights <= 0] = 0.0
    
    return wind_speeds


def calculate_turbulence_intensity(
    ref_speed: float = 2.0,
    turbulence_scale: float = 50.0,
    time: float = 0.0
) -> float:
    """
    Calculate turbulence intensity for gust modeling.
    
    Args:
        ref_speed (float): Reference wind speed
        turbulence_scale (float): Turbulence length scale
        time (float): Time for temporal variation
        
    Returns:
        float: Turbulence intensity
    """
    # Simplified turbulence model
    # In practice, this would use more sophisticated turbulence spectra
    
    base_intensity = 0.1  # 10% turbulence intensity
    temporal_variation = 0.1 * np.sin(2 * np.pi * time / 10.0)  # 10s period
    
    return base_intensity + temporal_variation


def calculate_wind_forces(
    velocity: np.ndarray,
    wind_velocity: np.ndarray,
    density: float,
    area: float,
    drag_coefficient: float
) -> np.ndarray:
    """
    Calculate wind forces on an object.
    
    Args:
        velocity (np.ndarray): Object velocity [vx, vy, vz]
        wind_velocity (np.ndarray): Wind velocity [wx, wy, wz]
        density (float): Air density
        area (float): Cross-sectional area
        drag_coefficient (float): Drag coefficient
        
    Returns:
        np.ndarray: Wind force vector [Fx, Fy, Fz]
    """
    # Relative velocity
    v_rel = calculate_relative_velocity(velocity, wind_velocity)
    v_rel_mag = np.linalg.norm(v_rel)
    
    if v_rel_mag < 1e-6:
        return np.zeros(3)
    
    # Wind force magnitude
    force_mag = 0.5 * density * v_rel_mag**2 * area * drag_coefficient
    
    # Force direction (opposite to relative velocity)
    force_vector = -force_mag * v_rel / v_rel_mag
    
    return force_vector


def calculate_wind_moment(
    velocity: np.ndarray,
    wind_velocity: np.ndarray,
    angular_velocity: np.ndarray,
    density: float,
    radius: float,
    area: float
) -> np.ndarray:
    """
    Calculate wind moment (torque) on a rotating object.
    
    Args:
        velocity (np.ndarray): Object velocity
        wind_velocity (np.ndarray): Wind velocity
        angular_velocity (np.ndarray): Angular velocity
        density (float): Air density
        radius (float): Object radius
        area (float): Cross-sectional area
        
    Returns:
        np.ndarray: Wind moment vector
    """
    # This is a simplified model
    # In practice, would need detailed aerodynamic coefficients
    
    v_rel = calculate_relative_velocity(velocity, wind_velocity)
    v_rel_mag = np.linalg.norm(v_rel)
    
    if v_rel_mag < 1e-6 or np.linalg.norm(angular_velocity) < 1e-6:
        return np.zeros(3)
    
    # Simplified moment calculation
    moment_mag = 0.1 * density * v_rel_mag * np.linalg.norm(angular_velocity) * radius**3
    
    # Direction depends on relative orientation
    moment_direction = np.cross(angular_velocity, v_rel)
    if np.linalg.norm(moment_direction) > 1e-6:
        moment_direction = moment_direction / np.linalg.norm(moment_direction)
    else:
        moment_direction = np.array([0, 0, 1])
    
    return moment_mag * moment_direction


class WindField:
    """Class for managing complex wind fields with multiple components."""
    
    def __init__(self, config: dict):
        """
        Initialize wind field from configuration.
        
        Args:
            config (dict): Wind configuration dictionary
        """
        self.config = config
        self.seed = config.get('seed', 42)
        self.gust_state = 0.0  # State for Ornstein-Uhlenbeck process
        
    def get_wind_velocity(self, position: np.ndarray, time: float) -> np.ndarray:
        """
        Get wind velocity at position and time.
        
        Args:
            position (np.ndarray): Position [x, y, z]
            time (float): Time
            
        Returns:
            np.ndarray: Wind velocity vector
        """
        z = position[2]  # Height
        
        # Base wind from power law
        base_wind = calculate_wind_velocity(
            z=z,
            ref_speed=self.config.get('ref_speed', 2.0),
            ref_height=self.config.get('ref_height', 10.0),
            shear_alpha=self.config.get('shear_alpha', 0.15),
            direction_deg=self.config.get('direction_deg', 0.0)
        )
        
        # Gust component
        gust_x = generate_gust_process(
            time=time,
            tau=self.config.get('gust_tau', 1.5),
            sigma=self.config.get('gust_sigma', 0.5),
            seed=self.seed
        )
        
        gust_y = generate_gust_process(
            time=time + 1.0,  # Phase shift
            tau=self.config.get('gust_tau', 1.5),
            sigma=self.config.get('gust_sigma', 0.5),
            seed=self.seed + 1
        )
        
        gust_z = generate_gust_process(
            time=time + 2.0,  # Phase shift
            tau=self.config.get('gust_tau', 1.5),
            sigma=self.config.get('gust_sigma', 0.2),  # Smaller vertical gusts
            seed=self.seed + 2
        )
        
        gust = np.array([gust_x, gust_y, gust_z])
        
        return base_wind + gust
    
    def get_atmospheric_properties(self, position: np.ndarray) -> Tuple[float, float, float]:
        """
        Get atmospheric properties at position.
        
        Args:
            position (np.ndarray): Position [x, y, z]
            
        Returns:
            Tuple of (density, viscosity, speed_of_sound)
        """
        z = position[2]
        humidity = self.config.get('humidity_pct', 50.0) / 100.0
        
        return calculate_atmospheric_properties(
            altitude=z,
            temperature=288.15,  # Default ISA temperature
            humidity=humidity
        )