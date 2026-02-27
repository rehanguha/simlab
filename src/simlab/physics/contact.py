"""
Ground contact mechanics.

Contains functions for Hertzian contact, friction modeling, and advanced collision physics.
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any


def calculate_hertzian_contact_force(
    penetration: float,
    radius: float,
    youngs_modulus: float = 1e7,  # Pa (typical for rubber)
    poisson_ratio: float = 0.5
) -> float:
    """
    Calculate Hertzian contact force for sphere-surface collision.
    
    This corrected implementation uses proper Hertzian contact theory with
    accurate material property handling.
    
    Args:
        penetration (float): Penetration depth (m)
        radius (float): Sphere radius (m)
        youngs_modulus (float): Young's modulus of material (Pa)
        poisson_ratio (float): Poisson's ratio
        
    Returns:
        float: Contact force magnitude (N)
    """
    # Import corrections module for advanced Hertzian contact
    from .corrections import calculate_advanced_hertzian_contact
    
    force, contact_radius = calculate_advanced_hertzian_contact(
        penetration, radius, youngs_modulus, poisson_ratio
    )
    
    return force


def calculate_coefficient_of_restitution(
    impact_velocity: float,
    base_restitution: float = 0.7,
    velocity_dependence: float = 0.02,
    dampness: float = 0.0,
    wetness: float = 0.0
) -> float:
    """
    Calculate velocity-dependent coefficient of restitution.
    
    Args:
        impact_velocity (float): Impact velocity magnitude (m/s)
        base_restitution (float): Base coefficient at 1 m/s
        velocity_dependence (float): Velocity dependence parameter
        dampness (float): Surface dampness (0-1)
        wetness (float): Surface wetness (0-1)
        
    Returns:
        float: Coefficient of restitution
    """
    # Base velocity dependence
    e = base_restitution * np.exp(-velocity_dependence * impact_velocity)
    
    # Surface condition effects
    surface_factor = 1.0 - 0.3 * dampness - 0.2 * wetness
    
    # Ensure physical bounds
    e = max(0.0, min(e * surface_factor, 1.0))
    
    return e


def calculate_friction_forces_advanced(
    normal_force: float,
    relative_velocity: np.ndarray,
    angular_velocity: np.ndarray,
    radius: float,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate advanced friction forces with comprehensive physics modeling.
    
    Args:
        normal_force (float): Normal contact force (N)
        relative_velocity (np.ndarray): Relative velocity at contact point
        angular_velocity (np.ndarray): Angular velocity vector
        radius (float): Object radius (m)
        config (dict): Physics configuration
        
    Returns:
        np.ndarray: Total friction force vector
    """
    # Extract friction configuration
    friction_config = config.get('friction', {})
    model_type = friction_config.get('model', 'advanced')
    
    if model_type == 'simple':
        return calculate_friction_forces(
            normal_force, relative_velocity,
            friction_config.get('static_friction', 0.5),
            friction_config.get('kinetic_friction', 0.3),
            friction_config.get('rolling_friction', 0.02)
        )
    
    # Advanced friction model
    v_tangent = np.linalg.norm(relative_velocity)
    omega_mag = np.linalg.norm(angular_velocity)
    
    # Calculate different friction components
    static_friction_force = calculate_static_friction(
        normal_force, relative_velocity, angular_velocity, config
    )
    
    kinetic_friction_force = calculate_kinetic_friction(
        normal_force, relative_velocity, config
    )
    
    rolling_friction_force = calculate_rolling_friction_advanced(
        normal_force, relative_velocity, angular_velocity, radius, config
    )
    
    # Combine friction forces based on motion state
    if v_tangent < 1e-6 and omega_mag < 1e-6:
        # Pure static friction (stiction)
        return static_friction_force
    elif v_tangent < 1e-3:
        # Mixed static/rolling friction
        return static_friction_force + rolling_friction_force
    else:
        # Dynamic friction with rolling effects
        return kinetic_friction_force + rolling_friction_force


def calculate_static_friction(
    normal_force: float,
    relative_velocity: np.ndarray,
    angular_velocity: np.ndarray,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate static friction (stiction) forces.
    
    Args:
        normal_force (float): Normal force (N)
        relative_velocity (np.ndarray): Relative velocity
        angular_velocity (np.ndarray): Angular velocity
        config (dict): Physics configuration
        
    Returns:
        np.ndarray: Static friction force vector
    """
    friction_config = config.get('friction', {})
    
    # Base static friction coefficient
    mu_static = friction_config.get('static_friction', 0.5)
    
    # Surface condition effects
    surface_type = friction_config.get('surface_type', 'default')
    surface_factor = get_surface_factor(surface_type, config)
    
    # Temperature effects
    temperature = config.get('environment', {}).get('temperature', 293.15)
    temp_factor = calculate_temperature_factor(temperature, config)
    
    # Pressure effects (Stribeck effect at low speeds)
    effective_mu = mu_static * surface_factor * temp_factor
    
    # Maximum static friction force
    max_static_force = effective_mu * normal_force
    
    # For static friction, we need to know the applied force to determine
    # the actual friction force (up to the maximum). For now, we'll return
    # the maximum possible static friction in the direction opposite to
    # any potential motion.
    
    # Determine direction based on angular velocity (rolling tendency)
    if np.linalg.norm(angular_velocity) > 1e-6:
        # Rolling direction
        rolling_direction = np.cross(angular_velocity, np.array([0, 0, 1]))
        if np.linalg.norm(rolling_direction) > 1e-6:
            friction_direction = -rolling_direction / np.linalg.norm(rolling_direction)
        else:
            friction_direction = np.array([1, 0, 0])  # Default direction
    else:
        # Default static friction direction
        friction_direction = np.array([1, 0, 0])
    
    return max_static_force * friction_direction


def calculate_kinetic_friction(
    normal_force: float,
    relative_velocity: np.ndarray,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate kinetic (dynamic) friction forces.
    
    Args:
        normal_force (float): Normal force (N)
        relative_velocity (np.ndarray): Relative velocity
        config (dict): Physics configuration
        
    Returns:
        np.ndarray: Kinetic friction force vector
    """
    friction_config = config.get('friction', {})
    
    # Base kinetic friction coefficient
    mu_kinetic = friction_config.get('kinetic_friction', 0.3)
    
    # Velocity-dependent friction (Stribeck effect)
    v_tangent = np.linalg.norm(relative_velocity)
    velocity_factor = calculate_velocity_factor(v_tangent, config)
    
    # Surface and temperature effects
    surface_type = friction_config.get('surface_type', 'default')
    surface_factor = get_surface_factor(surface_type, config)
    temperature = config.get('environment', {}).get('temperature', 293.15)
    temp_factor = calculate_temperature_factor(temperature, config)
    
    # Effective kinetic friction coefficient
    effective_mu = mu_kinetic * velocity_factor * surface_factor * temp_factor
    
    # Friction force magnitude
    friction_magnitude = effective_mu * normal_force
    
    # Direction opposite to relative velocity
    if v_tangent > 1e-6:
        friction_direction = -relative_velocity / v_tangent
    else:
        friction_direction = np.array([1, 0, 0])  # Default direction
    
    return friction_magnitude * friction_direction


def calculate_rolling_friction_advanced(
    normal_force: float,
    relative_velocity: np.ndarray,
    angular_velocity: np.ndarray,
    radius: float,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Calculate advanced rolling friction with multiple effects.
    
    Args:
        normal_force (float): Normal force (N)
        relative_velocity (np.ndarray): Relative velocity
        angular_velocity (np.ndarray): Angular velocity
        radius (float): Object radius (m)
        config (dict): Physics configuration
        
    Returns:
        np.ndarray: Rolling friction force vector
    """
    friction_config = config.get('friction', {})
    
    # Base rolling friction coefficient
    mu_rolling = friction_config.get('rolling_friction', 0.02)
    
    # Rolling resistance force magnitude
    rolling_force_mag = mu_rolling * normal_force
    
    # Velocity-dependent rolling resistance
    v_tangent = np.linalg.norm(relative_velocity)
    omega_mag = np.linalg.norm(angular_velocity)
    
    if omega_mag > 1e-6:
        # Pure rolling - friction opposes rolling direction
        rolling_direction = np.cross(angular_velocity, np.array([0, 0, 1]))
        if np.linalg.norm(rolling_direction) > 1e-6:
            friction_direction = -rolling_direction / np.linalg.norm(rolling_direction)
        else:
            friction_direction = np.array([1, 0, 0])
    elif v_tangent > 1e-6:
        # Sliding - friction opposes sliding direction
        friction_direction = -relative_velocity / v_tangent
    else:
        # Stationary
        return np.zeros(3)
    
    return rolling_force_mag * friction_direction


def get_surface_factor(surface_type: str, config: Dict[str, Any]) -> float:
    """
    Get surface-dependent friction factor.
    
    Args:
        surface_type (str): Type of surface
        config (dict): Physics configuration
        
    Returns:
        float: Surface factor multiplier
    """
    # Base surface factors
    surface_factors = {
        'default': 1.0,
        'ice': 0.1,
        'wet_ice': 0.05,
        'concrete': 1.2,
        'asphalt': 1.1,
        'grass': 0.8,
        'sand': 0.6,
        'rubber': 1.5,
        'metal': 0.9,
        'wood': 1.0
    }
    
    base_factor = surface_factors.get(surface_type, 1.0)
    
    # Wetness effects
    wetness = config.get('environment', {}).get('wetness', 0.0)
    wetness_factor = 1.0 - 0.5 * wetness  # Wetness reduces friction
    
    # Roughness effects
    roughness = config.get('environment', {}).get('surface_roughness', 0.0)
    roughness_factor = 1.0 + 0.2 * roughness  # Roughness increases friction
    
    return base_factor * wetness_factor * roughness_factor


def calculate_temperature_factor(temperature: float, config: Dict[str, Any]) -> float:
    """
    Calculate temperature-dependent friction factor.
    
    Args:
        temperature (float): Temperature in Kelvin
        config (dict): Physics configuration
        
    Returns:
        float: Temperature factor multiplier
    """
    # Reference temperature (20°C)
    T_ref = 293.15
    
    # Temperature coefficient (friction decreases with temperature for most materials)
    temp_coeff = config.get('friction', {}).get('temperature_coefficient', -0.001)
    
    # Temperature difference
    delta_T = temperature - T_ref
    
    # Temperature factor
    temp_factor = 1.0 + temp_coeff * delta_T
    
    # Ensure physical bounds
    return max(0.5, min(temp_factor, 1.5))


def calculate_velocity_factor(velocity: float, config: Dict[str, Any]) -> float:
    """
    Calculate velocity-dependent friction factor (Stribeck effect).
    
    Args:
        velocity (float): Relative velocity magnitude
        config (dict): Physics configuration
        
    Returns:
        float: Velocity factor multiplier
    """
    # Stribeck curve parameters
    v_static = config.get('friction', {}).get('static_velocity_threshold', 0.01)
    v_mixed = config.get('friction', {}).get('mixed_velocity_threshold', 0.1)
    v_dynamic = config.get('friction', {}).get('dynamic_velocity_threshold', 1.0)
    
    if velocity < v_static:
        # Static friction region
        return 1.0
    elif velocity < v_mixed:
        # Mixed friction region (decreasing)
        return 1.0 - 0.5 * (velocity - v_static) / (v_mixed - v_static)
    elif velocity < v_dynamic:
        # Transition to dynamic friction
        return 0.5 + 0.3 * (velocity - v_mixed) / (v_dynamic - v_mixed)
    else:
        # Pure dynamic friction
        return 0.8


def calculate_friction_forces(
    normal_force: float,
    relative_velocity: np.ndarray,
    static_friction: float = 0.5,
    kinetic_friction: float = 0.3,
    rolling_friction: float = 0.02
) -> np.ndarray:
    """
    Calculate friction forces using Coulomb friction model.
    
    Args:
        normal_force (float): Normal contact force (N)
        relative_velocity (np.ndarray): Relative velocity at contact point
        static_friction (float): Static friction coefficient
        kinetic_friction (float): Kinetic friction coefficient
        rolling_friction (float): Rolling friction coefficient
        
    Returns:
        np.ndarray: Friction force vector
    """
    v_tangent = np.linalg.norm(relative_velocity)
    
    if v_tangent < 1e-6:
        # Static friction - force opposes applied force up to limit
        # For now, return zero (would need to track applied forces)
        return np.zeros(3)
    
    # Kinetic friction
    friction_magnitude = kinetic_friction * normal_force
    
    # Direction opposite to relative velocity
    friction_direction = -relative_velocity / v_tangent
    
    return friction_magnitude * friction_direction


def calculate_contact_impulse(
    velocity: np.ndarray,
    angular_velocity: np.ndarray,
    position: np.ndarray,
    surface_normal: np.ndarray,
    radius: float,
    mass: float,
    inertia: float,
    restitution: float,
    friction_coeff: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate contact impulse for collision response.
    
    Args:
        velocity (np.ndarray): Linear velocity before collision
        angular_velocity (np.ndarray): Angular velocity before collision
        position (np.ndarray): Position vector
        surface_normal (np.ndarray): Surface normal at contact point
        radius (float): Object radius
        mass (float): Object mass
        inertia (float): Moment of inertia
        restitution (float): Coefficient of restitution
        friction_coeff (float): Friction coefficient
        
    Returns:
        Tuple of (linear_impulse, angular_impulse)
    """
    # Contact point velocity
    r = -radius * surface_normal  # Vector from center to contact point
    contact_velocity = velocity + np.cross(angular_velocity, r)
    
    # Normal and tangential components
    v_normal = np.dot(contact_velocity, surface_normal) * surface_normal
    v_tangent = contact_velocity - v_normal
    
    # Normal impulse (restitution)
    j_normal = -(1 + restitution) * np.dot(velocity, surface_normal)
    j_normal /= (1/mass + np.dot(np.cross(r, surface_normal), np.cross(r, surface_normal)) / inertia)
    
    # Tangential impulse (friction)
    if np.linalg.norm(v_tangent) > 1e-6:
        tangent_direction = v_tangent / np.linalg.norm(v_tangent)
        
        # Maximum static friction impulse
        j_max = friction_coeff * abs(j_normal)
        
        # Tangential impulse for perfect sticking
        j_tangent_stick = -np.dot(contact_velocity, tangent_direction)
        j_tangent_stick /= (1/mass + np.dot(np.cross(r, tangent_direction), np.cross(r, tangent_direction)) / inertia)
        
        # Apply friction limit
        j_tangent = max(-j_max, min(j_tangent_stick, j_max))
        
        # Total impulse
        impulse = j_normal * surface_normal + j_tangent * tangent_direction
    else:
        impulse = j_normal * surface_normal
    
    # Angular impulse
    angular_impulse = np.cross(r, impulse)
    
    return impulse, angular_impulse


def calculate_rolling_resistance(
    normal_force: float,
    velocity: np.ndarray,
    rolling_coefficient: float = 0.02
) -> np.ndarray:
    """
    Calculate rolling resistance force.
    
    Args:
        normal_force (float): Normal force (N)
        velocity (np.ndarray): Velocity vector
        rolling_coefficient (float): Rolling resistance coefficient
        
    Returns:
        np.ndarray: Rolling resistance force
    """
    v_mag = np.linalg.norm(velocity)
    if v_mag < 1e-6:
        return np.zeros(3)
    
    # Rolling resistance magnitude
    f_roll = rolling_coefficient * normal_force
    
    # Direction opposite to velocity
    return -f_roll * velocity / v_mag


def calculate_surface_geometry(
    position: np.ndarray,
    surface_config: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate surface height and normal at given position.
    
    Args:
        position (np.ndarray): Object position [x, y, z]
        surface_config (dict): Surface configuration
        
    Returns:
        Tuple of (surface_normal, surface_height)
    """
    x, y, z = position
    
    # Extract surface parameters
    base_height = surface_config.get('base_height', 0.0)
    slope_x = surface_config.get('slope_x', 0.0)
    slope_y = surface_config.get('slope_y', 0.0)
    roughness_amp = surface_config.get('surface_roughness', 0.0)
    roughness_wavelength = surface_config.get('roughness_wavelength', 10.0)
    
    # Surface height
    if roughness_amp > 0:
        # Sinusoidal roughness
        roughness = roughness_amp * np.sin(2 * np.pi * x / roughness_wavelength) * np.sin(2 * np.pi * y / roughness_wavelength)
    else:
        roughness = 0.0
    
    surface_height = base_height + slope_x * x + slope_y * y + roughness
    
    # Surface normal
    # For z = f(x,y), normal = (-df/dx, -df/dy, 1)
    dz_dx = slope_x
    dz_dy = slope_y
    
    if roughness_amp > 0:
        # Add roughness gradient
        dz_dx += roughness_amp * (2 * np.pi / roughness_wavelength) * np.cos(2 * np.pi * x / roughness_wavelength) * np.sin(2 * np.pi * y / roughness_wavelength)
        dz_dy += roughness_amp * (2 * np.pi / roughness_wavelength) * np.sin(2 * np.pi * x / roughness_wavelength) * np.cos(2 * np.pi * y / roughness_wavelength)
    
    normal = np.array([-dz_dx, -dz_dy, 1.0])
    normal = normal / np.linalg.norm(normal)
    
    return normal, surface_height


def detect_collision(
    position: np.ndarray,
    radius: float,
    surface_config: Dict[str, Any]
) -> Tuple[bool, float, np.ndarray]:
    """
    Detect collision with surface.
    
    Args:
        position (np.ndarray): Object position
        radius (float): Object radius
        surface_config (dict): Surface configuration
        
    Returns:
        Tuple of (collision_detected, penetration_depth, surface_normal)
    """
    surface_normal, surface_height = calculate_surface_geometry(position, surface_config)
    
    # Distance from center to surface
    distance_to_surface = position[2] - surface_height
    
    # Check for collision
    if distance_to_surface <= radius:
        penetration = radius - distance_to_surface
        return True, penetration, surface_normal
    
    return False, 0.0, surface_normal


def apply_collision_response(
    velocity: np.ndarray,
    angular_velocity: np.ndarray,
    position: np.ndarray,
    radius: float,
    mass: float,
    inertia: float,
    surface_config: Dict[str, Any],
    physics_config: Dict[str, Any]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Apply complete collision response with Hertzian contact and friction.
    
    Args:
        velocity (np.ndarray): Current linear velocity
        angular_velocity (np.ndarray): Current angular velocity
        position (np.ndarray): Current position
        radius (float): Object radius
        mass (float): Object mass
        inertia (float): Moment of inertia
        surface_config (dict): Surface configuration
        physics_config (dict): Physics configuration
        
    Returns:
        Tuple of (new_velocity, new_angular_velocity, new_position)
    """
    # Detect collision
    collision, penetration, surface_normal = detect_collision(position, radius, surface_config)
    
    if not collision:
        return velocity, angular_velocity, position
    
    # Calculate impact parameters
    impact_velocity = np.dot(velocity, surface_normal)
    
    # Get surface properties
    base_restitution = surface_config.get('elasticity_base', 0.7)
    static_friction = surface_config.get('friction_mu_s', 0.5)
    kinetic_friction = surface_config.get('friction_mu_k', 0.3)
    rolling_friction = surface_config.get('rolling_friction', 0.02)
    dampness = surface_config.get('dampness', 0.0)
    wetness = surface_config.get('wetness', 0.0)
    
    # Calculate coefficients
    restitution = calculate_coefficient_of_restitution(
        abs(impact_velocity), base_restitution, dampness=dampness, wetness=wetness
    )
    
    # Calculate contact force (Hertzian)
    contact_force = calculate_hertzian_contact_force(
        penetration, radius,
        youngs_modulus=physics_config.get('youngs_modulus', 1e7),
        poisson_ratio=physics_config.get('poisson_ratio', 0.5)
    )
    
    # Calculate impulses
    impulse, angular_impulse = calculate_contact_impulse(
        velocity, angular_velocity, position, surface_normal,
        radius, mass, inertia, restitution, kinetic_friction
    )
    
    # Update velocities
    new_velocity = velocity + impulse / mass
    new_angular_velocity = angular_velocity + angular_impulse / inertia
    
    # Apply rolling resistance if object is rolling
    if np.linalg.norm(new_velocity) > 1e-3:
        rolling_force = calculate_rolling_resistance(
            contact_force, new_velocity, rolling_friction
        )
        new_velocity += rolling_force / mass
    
    # Update position to prevent sinking
    new_position = position.copy()
    new_position[2] = surface_config.get('base_height', 0.0) + radius + 1e-6
    
    return new_velocity, new_angular_velocity, new_position


class ContactModel:
    """Advanced contact model with Hertzian contact and friction."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize contact model from configuration.
        
        Args:
            config (dict): Contact configuration
        """
        self.config = config
        self.contact_history = []
        
    def process_contact(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process contact for current state.
        
        Args:
            state (dict): Current state with velocity, angular_velocity, position, etc.
            
        Returns:
            dict: Updated state
        """
        # Extract state variables
        velocity = state['velocity']
        angular_velocity = state['angular_velocity']
        position = state['position']
        radius = state['radius']
        mass = state['mass']
        inertia = state['inertia']
        
        # Get surface and physics configs
        surface_config = self.config.get('surface', {})
        physics_config = self.config.get('simulation', {})
        
        # Apply collision response
        new_velocity, new_angular_velocity, new_position = apply_collision_response(
            velocity, angular_velocity, position, radius, mass, inertia,
            surface_config, physics_config
        )
        
        # Update state
        state['velocity'] = new_velocity
        state['angular_velocity'] = new_angular_velocity
        state['position'] = new_position
        
        # Track contact events
        if np.linalg.norm(new_velocity - velocity) > 1e-6:
            contact_event = {
                'time': state.get('time', 0.0),
                'position': position.copy(),
                'velocity_change': new_velocity - velocity,
                'angular_velocity_change': new_angular_velocity - angular_velocity
            }
            self.contact_history.append(contact_event)
        
        return state
    
    def get_contact_count(self) -> int:
        """Get number of contact events."""
        return len(self.contact_history)
    
    def get_contact_history(self) -> list:
        """Get contact event history."""
        return self.contact_history.copy()