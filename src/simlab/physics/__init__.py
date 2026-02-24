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

from .mechanics import (
    calculate_gravity,
    calculate_terminal_velocity,
    calculate_spin_decay
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
    'calculate_spin_decay'
]