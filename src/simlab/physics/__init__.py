"""
Physics calculations module.

Contains all the physics functions for aerodynamics, thermodynamics,
and mechanics calculations.
"""

from .aerodynamics import (
    calculate_density,
    calculate_viscosity,
    calculate_speed_of_sound,
    calculate_reynolds_number,
    calculate_drag_coefficient,
    calculate_magnus_force,
    calculate_wind_force
)

from .aerodynamics_enhanced import (
    calculate_multi_regime_drag_coefficient,
    calculate_buoyancy_force,
    calculate_virtual_mass,
    calculate_effective_mass,
    calculate_aerodynamic_forces,
    calculate_spin_decay_advanced,
    calculate_compressibility_correction,
    AerodynamicModel
)

from .mechanics import (
    calculate_gravity,
    calculate_terminal_velocity,
    calculate_spin_decay
)

from .numerical import (
    AdaptiveRK45,
    fixed_step_euler,
    check_stability,
    energy_monitor,
    adaptive_timestep_controller
)

from .wind import (
    calculate_wind_velocity,
    generate_gust_process,
    calculate_relative_velocity,
    calculate_atmospheric_properties,
    calculate_wind_profile,
    calculate_turbulence_intensity,
    calculate_wind_forces,
    calculate_wind_moment,
    WindField
)

from .contact import (
    calculate_hertzian_contact_force,
    calculate_coefficient_of_restitution,
    calculate_friction_forces,
    calculate_contact_impulse,
    calculate_rolling_resistance,
    calculate_surface_geometry,
    detect_collision,
    apply_collision_response,
    ContactModel
)

__all__ = [
    'calculate_density',
    'calculate_viscosity',
    'calculate_speed_of_sound',
    'calculate_reynolds_number',
    'calculate_drag_coefficient',
    'calculate_magnus_force',
    'calculate_wind_force',
    'calculate_gravity',
    'calculate_terminal_velocity',
    'calculate_spin_decay',
    'AdaptiveRK45',
    'fixed_step_euler',
    'check_stability',
    'energy_monitor',
    'adaptive_timestep_controller',
    'calculate_wind_velocity',
    'generate_gust_process',
    'calculate_relative_velocity',
    'calculate_atmospheric_properties',
    'calculate_wind_profile',
    'calculate_turbulence_intensity',
    'calculate_wind_forces',
    'calculate_wind_moment',
    'WindField',
    'calculate_hertzian_contact_force',
    'calculate_coefficient_of_restitution',
    'calculate_friction_forces',
    'calculate_contact_impulse',
    'calculate_rolling_resistance',
    'calculate_surface_geometry',
    'detect_collision',
    'apply_collision_response',
    'ContactModel',
    'calculate_multi_regime_drag_coefficient',
    'calculate_buoyancy_force',
    'calculate_virtual_mass',
    'calculate_effective_mass',
    'calculate_aerodynamic_forces',
    'calculate_spin_decay_advanced',
    'calculate_compressibility_correction',
    'AerodynamicModel'
]
