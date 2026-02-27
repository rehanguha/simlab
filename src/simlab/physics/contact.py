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
    
    Args:
        penetration (float): Penetration depth (m)
        radius (float): Sphere radius (m)
        youngs_modulus (float): Young's modulus of material (Pa)
        poisson_ratio (float): Poisson's ratio
        
    Returns:
        float: Contact force magnitude (N)
    """
    if penetration <= 0:
        return 0.0
    
    # Effective elastic modulus
    E_eff = youngs_modulus / (1 - poisson_ratio**2)
    
    # Contact radius
    a = np.sqrt(radius * penetration)
    
    # Hertzian contact force
    # F = (4/3) * E_eff * a^3 / R
    force = (4.0/3.0) * E_eff * (a**3) / radius
    
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