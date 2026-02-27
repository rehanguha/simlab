"""
Physics Models - Unified physics calculation interface.

This module provides a unified interface for all physics calculations,
making the simulation engine more maintainable and extensible.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from ..utils.constants import PHYSICAL_CONSTANTS


class PhysicsModel:
    """Base class for physics models."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize physics model.
        
        Args:
            config (dict): Physics configuration
        """
        self.config = config
        self.constants = PHYSICAL_CONSTANTS
    
    def calculate_forces(self, state: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Calculate forces and torques acting on the object.
        
        Args:
            state (dict): Current state with velocity, angular_velocity, position, etc.
            
        Returns:
            Tuple of (force_vector, torque_vector, reynolds_number)
        """
        raise NotImplementedError
    
    def update_state(self, state: Dict[str, Any], dt: float) -> Dict[str, Any]:
        """
        Update state using the calculated forces.
        
        Args:
            state (dict): Current state
            dt (float): Time step
            
        Returns:
            Updated state
        """
        raise NotImplementedError


class AerodynamicModel(PhysicsModel):
    """Advanced aerodynamic force calculations."""
    
    def calculate_forces(self, state: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, float]:
        """Calculate aerodynamic forces including drag, lift, and buoyancy."""
        # Extract state variables
        velocity = state['velocity']
        angular_velocity = state['angular_velocity']
        position = state['position']
        radius = state['radius']
        mass = state['mass']
        
        # Get atmospheric properties
        density, viscosity, speed_of_sound = self._calculate_atmospheric_properties(position[2])
        
        # Get wind effects
        wind_velocity = self._calculate_wind_velocity(position[2])
        v_rel = velocity - wind_velocity
        
        v_mag = np.linalg.norm(v_rel)
        
        if v_mag < 1e-6:
            return np.zeros(3), np.zeros(3), 0.0
        
        # Calculate Reynolds number
        volume = (4.0/3.0) * np.pi * radius**3
        reynolds = (2.0 * radius * v_mag * density) / viscosity
        
        # Calculate Mach number
        mach = v_mag / speed_of_sound
        
        # Calculate drag coefficient with advanced correlations
        cd = self._calculate_drag_coefficient(reynolds, mach)
        
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
        buoyancy_force = density * volume * self.constants['g']
        buoyancy_vector = np.array([0.0, 0.0, buoyancy_force])
        
        # Gravitational force
        gravity_vector = np.array([0.0, 0.0, -mass * self.constants['g']])
        
        # Total force
        total_force = drag_vector + lift_vector + buoyancy_vector + gravity_vector
        
        # Aerodynamic torque
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
    
    def _calculate_atmospheric_properties(self, altitude: float) -> Tuple[float, float, float]:
        """Calculate atmospheric properties using ISA model."""
        # Temperature at altitude
        T = self.constants['T0'] - self.constants['L'] * altitude
        
        # Pressure at altitude
        p = self.constants['p0'] * (T / self.constants['T0'])**(self.constants['g'] / (self.constants['R'] * self.constants['L']))
        
        # Humidity effects
        humidity = self.config.get('wind', {}).get('humidity_pct', 50.0) / 100.0
        e_s = 611.21 * np.exp((18.678 - (T - 273.15)/234.5) * (T - 273.15) / (257.14 + (T - 273.15)))
        e = e_s * humidity
        
        # Density with humidity correction
        rho_dry = p / (self.constants['R'] * T)
        rho_vapor = e / (self.constants['R_v'] * T)
        density = rho_dry + rho_vapor
        
        # Dynamic viscosity (Sutherland's law)
        mu = self.constants['mu_ref'] * (T / self.constants['T_ref'])**1.5 * (self.constants['T_ref'] + self.constants['S']) / (T + self.constants['S'])
        
        # Speed of sound
        speed_of_sound = np.sqrt(self.constants['gamma'] * self.constants['R'] * T)
        
        return density, mu, speed_of_sound
    
    def _calculate_wind_velocity(self, height: float) -> np.ndarray:
        """Calculate wind velocity at given height."""
        wind_config = self.config.get('wind', {})
        
        ref_speed = wind_config.get('ref_speed', 2.0)
        ref_height = wind_config.get('ref_height', 10.0)
        shear_alpha = wind_config.get('shear_alpha', 0.15)
        direction_deg = wind_config.get('direction_deg', 0.0)
        gust_speed = wind_config.get('gust_speed', 0.0)
        
        # Power law for wind speed variation with height
        if height <= 0:
            wind_speed = 0.0
        else:
            wind_speed = ref_speed * (height / ref_height) ** shear_alpha
        
        # Add gust component
        wind_speed += gust_speed
        
        # Convert direction to radians
        direction_rad = np.radians(direction_deg)
        
        # Wind velocity components
        u = wind_speed * np.cos(direction_rad)  # East component
        v = wind_speed * np.sin(direction_rad)  # North component
        w = 0.0  # Vertical component
        
        return np.array([u, v, w])
    
    def _calculate_drag_coefficient(self, reynolds: float, mach: float = 0.0) -> float:
        """Calculate drag coefficient using multi-regime correlation."""
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
        
        # Surface roughness effect
        surface_roughness = self.config.get('surface_roughness', 0.0)
        if surface_roughness > 0:
            roughness_effect = min(surface_roughness * 1e4, 0.8)
            if reynolds > 2e5:
                cd = cd * (1.0 + 0.2 * roughness_effect)
        
        # Compressibility corrections for high Mach numbers
        if mach > 0.3:
            if mach < 0.8:
                beta = np.sqrt(1.0 - mach**2)
                cd = cd / beta
            else:
                cd = cd * (1.0 + 0.15 * mach**2)
                if mach > 1.0:
                    cd = cd * (1.0 + 0.5 * (mach - 1.0)**2)
        
        return cd


class ContactModel(PhysicsModel):
    """Advanced contact mechanics model."""
    
    def calculate_forces(self, state: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, bool]:
        """Calculate contact forces and check for collision."""
        position = state['position']
        radius = state['radius']
        mass = state['mass']
        inertia = state['inertia']
        
        # Get surface configuration
        surface_config = self.config.get('surface', {})
        physics_config = self.config.get('simulation', {})
        
        # Check for collision
        collision, penetration, surface_normal = self._detect_collision(position, radius, surface_config)
        
        if not collision:
            return np.zeros(3), np.zeros(3), False
        
        # Calculate impact parameters
        velocity = state['velocity']
        angular_velocity = state['angular_velocity']
        
        impact_velocity = np.dot(velocity, surface_normal)
        
        # Get surface properties
        base_restitution = surface_config.get('elasticity_base', 0.7)
        static_friction = surface_config.get('friction_mu_s', 0.5)
        kinetic_friction = surface_config.get('friction_mu_k', 0.3)
        dampness = surface_config.get('dampness', 0.0)
        wetness = surface_config.get('wetness', 0.0)
        
        # Calculate coefficients
        restitution = self._calculate_coefficient_of_restitution(
            abs(impact_velocity), base_restitution, dampness=dampness, wetness=wetness
        )
        
        # Calculate contact force (Hertzian)
        contact_force = self._calculate_hertzian_contact_force(
            penetration, radius,
            youngs_modulus=physics_config.get('youngs_modulus', 1e7),
            poisson_ratio=physics_config.get('poisson_ratio', 0.5)
        )
        
        # Calculate friction forces
        relative_velocity = self._calculate_contact_velocity(velocity, angular_velocity, position, radius, surface_normal)
        friction_force = self._calculate_friction_forces_advanced(
            contact_force, relative_velocity, angular_velocity, radius, self.config
        )
        
        # Calculate impulses
        impulse, angular_impulse = self._calculate_contact_impulse(
            velocity, angular_velocity, position, surface_normal, radius, mass, inertia, restitution, kinetic_friction
        )
        
        return impulse, angular_impulse, True
    
    def _detect_collision(self, position: np.ndarray, radius: float, surface_config: Dict[str, Any]) -> Tuple[bool, float, np.ndarray]:
        """Detect collision with surface."""
        # Calculate surface height and normal
        surface_normal, surface_height = self._calculate_surface_geometry(position, surface_config)
        
        # Distance from center to surface
        distance_to_surface = position[2] - surface_height
        
        # Check for collision
        if distance_to_surface <= radius:
            penetration = radius - distance_to_surface
            return True, penetration, surface_normal
        
        return False, 0.0, surface_normal
    
    def _calculate_surface_geometry(self, position: np.ndarray, surface_config: Dict[str, Any]) -> Tuple[np.ndarray, float]:
        """Calculate surface height and normal at given position."""
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
        dz_dx = slope_x
        dz_dy = slope_y
        
        if roughness_amp > 0:
            # Add roughness gradient
            dz_dx += roughness_amp * (2 * np.pi / roughness_wavelength) * np.cos(2 * np.pi * x / roughness_wavelength) * np.sin(2 * np.pi * y / roughness_wavelength)
            dz_dy += roughness_amp * (2 * np.pi / roughness_wavelength) * np.sin(2 * np.pi * x / roughness_wavelength) * np.cos(2 * np.pi * y / roughness_wavelength)
        
        normal = np.array([-dz_dx, -dz_dy, 1.0])
        normal = normal / np.linalg.norm(normal)
        
        return normal, surface_height
    
    def _calculate_contact_velocity(self, velocity: np.ndarray, angular_velocity: np.ndarray, 
                                   position: np.ndarray, radius: float, surface_normal: np.ndarray) -> np.ndarray:
        """Calculate velocity at contact point."""
        r = -radius * surface_normal  # Vector from center to contact point
        contact_velocity = velocity + np.cross(angular_velocity, r)
        return contact_velocity
    
    def _calculate_coefficient_of_restitution(self, impact_velocity: float, base_restitution: float, 
                                            dampness: float = 0.0, wetness: float = 0.0) -> float:
        """Calculate velocity-dependent coefficient of restitution."""
        # Base velocity dependence
        e = base_restitution * np.exp(-0.02 * impact_velocity)
        
        # Surface condition effects
        surface_factor = 1.0 - 0.3 * dampness - 0.2 * wetness
        
        # Ensure physical bounds
        e = max(0.0, min(e * surface_factor, 1.0))
        
        return e
    
    def _calculate_hertzian_contact_force(self, penetration: float, radius: float, 
                                        youngs_modulus: float = 1e7, poisson_ratio: float = 0.5) -> float:
        """Calculate Hertzian contact force."""
        if penetration <= 0:
            return 0.0
        
        # Effective elastic modulus
        E_eff = youngs_modulus / (1 - poisson_ratio**2)
        
        # Contact radius
        a = np.sqrt(radius * penetration)
        
        # Hertzian contact force
        force = (4.0/3.0) * E_eff * (a**3) / radius
        
        return force
    
    def _calculate_friction_forces_advanced(self, normal_force: float, relative_velocity: np.ndarray,
                                          angular_velocity: np.ndarray, radius: float, config: Dict[str, Any]) -> np.ndarray:
        """Calculate advanced friction forces."""
        v_tangent = np.linalg.norm(relative_velocity)
        omega_mag = np.linalg.norm(angular_velocity)
        
        # Calculate different friction components
        if v_tangent < 1e-6 and omega_mag < 1e-6:
            # Pure static friction (stiction)
            return self._calculate_static_friction(normal_force, relative_velocity, angular_velocity, config)
        elif v_tangent < 1e-3:
            # Mixed static/rolling friction
            static_friction = self._calculate_static_friction(normal_force, relative_velocity, angular_velocity, config)
            rolling_friction = self._calculate_rolling_friction_advanced(normal_force, relative_velocity, angular_velocity, radius, config)
            return static_friction + rolling_friction
        else:
            # Dynamic friction with rolling effects
            kinetic_friction = self._calculate_kinetic_friction(normal_force, relative_velocity, config)
            rolling_friction = self._calculate_rolling_friction_advanced(normal_force, relative_velocity, angular_velocity, radius, config)
            return kinetic_friction + rolling_friction
    
    def _calculate_static_friction(self, normal_force: float, relative_velocity: np.ndarray,
                                 angular_velocity: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        """Calculate static friction (stiction) forces."""
        friction_config = config.get('friction', {})
        
        # Base static friction coefficient
        mu_static = friction_config.get('static_friction', 0.5)
        
        # Surface condition effects
        surface_type = friction_config.get('surface_type', 'default')
        surface_factor = self._get_surface_factor(surface_type, config)
        
        # Temperature effects
        temperature = config.get('environment', {}).get('temperature', 293.15)
        temp_factor = self._calculate_temperature_factor(temperature, config)
        
        # Effective static friction coefficient
        effective_mu = mu_static * surface_factor * temp_factor
        
        # Maximum static friction force
        max_static_force = effective_mu * normal_force
        
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
    
    def _calculate_kinetic_friction(self, normal_force: float, relative_velocity: np.ndarray,
                                  config: Dict[str, Any]) -> np.ndarray:
        """Calculate kinetic (dynamic) friction forces."""
        friction_config = config.get('friction', {})
        
        # Base kinetic friction coefficient
        mu_kinetic = friction_config.get('kinetic_friction', 0.3)
        
        # Velocity-dependent friction (Stribeck effect)
        v_tangent = np.linalg.norm(relative_velocity)
        velocity_factor = self._calculate_velocity_factor(v_tangent, config)
        
        # Surface and temperature effects
        surface_type = friction_config.get('surface_type', 'default')
        surface_factor = self._get_surface_factor(surface_type, config)
        temperature = config.get('environment', {}).get('temperature', 293.15)
        temp_factor = self._calculate_temperature_factor(temperature, config)
        
        # Effective kinetic friction coefficient
        effective_mu = mu_kinetic * velocity_factor * surface_factor * temp_factor
        
        # Friction force magnitude
        friction_magnitude = effective_mu * normal_force
        
        # Direction opposite to relative velocity
        v_tangent = np.linalg.norm(relative_velocity)
        if v_tangent > 1e-6:
            friction_direction = -relative_velocity / v_tangent
        else:
            friction_direction = np.array([1, 0, 0])  # Default direction
        
        return friction_magnitude * friction_direction
    
    def _calculate_rolling_friction_advanced(self, normal_force: float, relative_velocity: np.ndarray,
                                           angular_velocity: np.ndarray, radius: float, config: Dict[str, Any]) -> np.ndarray:
        """Calculate advanced rolling friction with multiple effects."""
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
    
    def _get_surface_factor(self, surface_type: str, config: Dict[str, Any]) -> float:
        """Get surface-dependent friction factor."""
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
    
    def _calculate_temperature_factor(self, temperature: float, config: Dict[str, Any]) -> float:
        """Calculate temperature-dependent friction factor."""
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
    
    def _calculate_velocity_factor(self, velocity: float, config: Dict[str, Any]) -> float:
        """Calculate velocity-dependent friction factor (Stribeck effect)."""
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
    
    def _calculate_contact_impulse(self, velocity: np.ndarray, angular_velocity: np.ndarray,
                                 position: np.ndarray, surface_normal: np.ndarray, radius: float,
                                 mass: float, inertia: float, restitution: float, friction_coeff: float) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate contact impulse for collision response."""
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


class SpinDecayModel(PhysicsModel):
    """Advanced spin decay model."""
    
    def calculate_forces(self, state: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate spin decay effects."""
        angular_velocity = state['angular_velocity']
        velocity = state['velocity']
        position = state['position']
        radius = state['radius']
        dt = state.get('dt', 0.001)
        
        # Get atmospheric properties
        density, viscosity, _ = self._calculate_atmospheric_properties(position[2])
        
        # Calculate advanced spin decay
        new_omega = self._calculate_spin_decay_advanced(
            angular_velocity, velocity, density, viscosity, radius, dt, self.config
        )
        
        # Calculate aerodynamic torque
        if np.linalg.norm(angular_velocity) > 1e-6:
            # Simplified torque calculation
            omega_mag = np.linalg.norm(angular_velocity)
            v_mag = np.linalg.norm(velocity)
            
            torque_magnitude = 0.1 * density * v_mag * omega_mag * radius**3
            torque_direction = -angular_velocity / omega_mag
            torque_vector = torque_magnitude * torque_direction
        else:
            torque_vector = np.zeros(3)
        
        return np.zeros(3), torque_vector
    
    def _calculate_atmospheric_properties(self, altitude: float) -> Tuple[float, float, float]:
        """Calculate atmospheric properties using ISA model."""
        # Simplified version - could be shared with AerodynamicModel
        T = 288.15 - 0.0065 * altitude
        p = 101325 * (T / 288.15)**(9.81 / (287.058 * 0.0065))
        density = p / (287.058 * T)
        viscosity = 1.716e-5 * (T / 273.15)**1.5 * (273.15 + 110.4) / (T + 110.4)
        speed_of_sound = np.sqrt(1.4 * 287.058 * T)
        
        return density, viscosity, speed_of_sound
    
    def _calculate_spin_decay_advanced(self, angular_velocity: np.ndarray, velocity: np.ndarray,
                                     density: float, viscosity: float, radius: float,
                                     time_step: float, config: Dict[str, Any]) -> np.ndarray:
        """Calculate advanced spin decay with aerodynamic and contact effects."""
        omega_mag = np.linalg.norm(angular_velocity)
        v_mag = np.linalg.norm(velocity)
        
        if omega_mag < 1e-6:
            return angular_velocity
        
        # Aerodynamic torque coefficient
        if v_mag < 1e-6:
            # Pure rotation decay
            ct = 64.0 / (omega_mag * radius * 2 * radius / viscosity + 1)
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


class PhysicsEngine:
    """Unified physics engine that combines all physics models."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize physics engine.
        
        Args:
            config (dict): Complete simulation configuration
        """
        self.config = config
        self.aerodynamic_model = AerodynamicModel(config)
        self.contact_model = ContactModel(config)
        self.spin_decay_model = SpinDecayModel(config)
    
    def calculate_total_forces(self, state: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Calculate total forces and torques acting on the object.
        
        Args:
            state (dict): Current state
            
        Returns:
            Tuple of (total_force, total_torque, physics_info)
        """
        # Calculate aerodynamic forces
        aerodynamic_force, aerodynamic_torque, reynolds = self.aerodynamic_model.calculate_forces(state)
        
        # Calculate contact forces
        contact_impulse, contact_torque, collision = self.contact_model.calculate_forces(state)
        
        # Calculate spin decay effects
        spin_force, spin_torque = self.spin_decay_model.calculate_forces(state)
        
        # Combine forces
        total_force = aerodynamic_force + contact_impulse + spin_force
        total_torque = aerodynamic_torque + contact_torque + spin_torque
        
        # Physics information
        physics_info = {
            'reynolds': reynolds,
            'collision': collision,
            'aerodynamic_force': aerodynamic_force,
            'contact_impulse': contact_impulse,
            'spin_torque': spin_torque
        }
        
        return total_force, total_torque, physics_info
    
    def update_state(self, state: Dict[str, Any], dt: float) -> Dict[str, Any]:
        """
        Update state using physics calculations.
        
        Args:
            state (dict): Current state
            dt (float): Time step
            
        Returns:
            Updated state
        """
        # Calculate forces
        force, torque, physics_info = self.calculate_total_forces(state)
        
        # Update linear motion
        acceleration = force / state['mass']
        state['velocity'] += acceleration * dt
        state['position'] += state['velocity'] * dt
        
        # Update angular motion
        angular_acceleration = torque / state['inertia']
        state['angular_velocity'] += angular_acceleration * dt
        
        # Store physics info
        state['physics_info'] = physics_info
        
        return state