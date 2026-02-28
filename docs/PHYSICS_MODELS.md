# Physics Models Documentation

This document provides comprehensive documentation for all physics models implemented in physimlab, including detailed explanations of the mathematical formulations, parameters, and usage.

## Table of Contents

1. [Aerodynamics](#aerodynamics)
2. [Mechanics](#mechanics)
3. [Contact Physics](#contact-physics)
4. [Wind and Atmospheric Effects](#wind-and-atmospheric-effects)
5. [Numerical Integration](#numerical-integration)
6. [Advanced Physics Features](#advanced-physics-features)

---

## Aerodynamics

### Overview
The aerodynamics module implements comprehensive models for calculating drag forces, lift forces, and air properties. It includes multi-regime drag coefficient calculations, Magnus effect modeling, and advanced air property calculations.

### Key Functions

#### `calculate_drag_coefficient(reynolds, config=None)`
Calculates drag coefficient based on Reynolds number using piecewise correlations for different flow regimes.

**Parameters:**
- `reynolds` (float): Reynolds number
- `config` (dict): Configuration parameters

**Flow Regimes:**
- **Stokes Flow** (Re ≤ 1): `Cd = 24/Re`
- **Intermediate Flow** (1 < Re ≤ 1000): Schiller-Naumann correlation
- **Newton Regime** (1000 < Re ≤ 3×10⁵): Constant Cd ≈ 0.44
- **Drag Crisis** (3×10⁵ < Re ≤ 3.5×10⁵): Sharp drop in Cd
- **Post-Crisis** (Re > 3.5×10⁵): Gradual recovery

**Example:**
```python
from physimlab.physics import calculate_drag_coefficient

# Calculate drag coefficient for Re = 100,000
cd = calculate_drag_coefficient(1e5)
print(f"Drag coefficient: {cd:.3f}")
```

#### `calculate_magnus_force(density, velocity, radius, angular_velocity, config=None)`
Calculates Magnus force magnitude for spinning objects.

**Parameters:**
- `density` (float): Air density (kg/m³)
- `velocity` (float): Object velocity (m/s)
- `radius` (float): Object radius (m)
- `angular_velocity` (float): Angular velocity (rad/s)
- `config` (dict): Configuration parameters

**Formula:**
`F_magnus = coefficient * density * velocity * angular_velocity * radius³`

**Example:**
```python
from physimlab.physics import calculate_magnus_force

# Calculate Magnus force
magnus_force = calculate_magnus_force(
    density=1.225, velocity=20.0, radius=0.1, angular_velocity=100.0
)
print(f"Magnus force: {magnus_force:.3f} N")
```

#### `calculate_multi_regime_drag_coefficient(reynolds, mach=0.0, surface_roughness=0.0, config=None)`
Advanced drag coefficient calculation with compressibility and roughness corrections.

**Parameters:**
- `reynolds` (float): Reynolds number
- `mach` (float): Mach number
- `surface_roughness` (float): Surface roughness height (m)
- `config` (dict): Configuration parameters

**Features:**
- Compressibility corrections for high Mach numbers
- Surface roughness effects on drag crisis
- Enhanced accuracy across all flow regimes

**Example:**
```python
from physimlab.physics import calculate_multi_regime_drag_coefficient

# Calculate with compressibility effects
cd = calculate_multi_regime_drag_coefficient(
    reynolds=1e5, mach=0.5, surface_roughness=0.001
)
print(f"Compressible drag coefficient: {cd:.3f}")
```

### Air Properties

#### `calculate_density(temperature, humidity=0.5, config=None)`
Calculates air density using ideal gas law with humidity corrections.

**Formula:**
`ρ = ρ_dry + ρ_vapor`

Where:
- `ρ_dry = p_dry / (R_d * T)`
- `ρ_vapor = e / (R_v * T)`

**Parameters:**
- `temperature` (float): Temperature in Kelvin
- `humidity` (float): Relative humidity (0-1)
- `config` (dict): Configuration parameters

#### `calculate_viscosity(temperature, config=None)`
Calculates dynamic viscosity using Sutherland's formula.

**Formula:**
`μ = μ₀ * (T/T₀)^1.5 * (T₀ + S)/(T + S)`

**Parameters:**
- `temperature` (float): Temperature in Kelvin
- `config` (dict): Configuration parameters

#### `calculate_speed_of_sound(temperature, config=None)`
Calculates speed of sound in air.

**Formula:**
`c = √(γ * R * T)`

**Parameters:**
- `temperature` (float): Temperature in Kelvin
- `config` (dict): Configuration parameters

---

## Mechanics

### Overview
The mechanics module implements fundamental physics calculations including gravity, terminal velocity, and spin decay.

### Key Functions

#### `calculate_gravity(altitude=0.0, config=None)`
Calculates gravitational acceleration at a given altitude.

**Formula:**
`g = g₀ * (R/(R + h))²`

**Parameters:**
- `altitude` (float): Altitude above sea level (m)
- `config` (dict): Configuration parameters

**Example:**
```python
from physimlab.physics import calculate_gravity

# Calculate gravity at 1000m altitude
g = calculate_gravity(altitude=1000.0)
print(f"Gravity at 1000m: {g:.6f} m/s²")
```

#### `calculate_terminal_velocity(mass, radius, drag_coefficient=0.47, density=1.225, config=None)`
Calculates terminal velocity of a falling object.

**Formula:**
`v_t = √(2 * m * g / (ρ * Cd * A))`

**Parameters:**
- `mass` (float): Object mass (kg)
- `radius` (float): Object radius (m)
- `drag_coefficient` (float): Drag coefficient
- `density` (float): Air density (kg/m³)
- `config` (dict): Configuration parameters

**Example:**
```python
from physimlab.physics import calculate_terminal_velocity

# Calculate terminal velocity for a 0.5kg, 0.1m radius sphere
v_t = calculate_terminal_velocity(mass=0.5, radius=0.1)
print(f"Terminal velocity: {v_t:.2f} m/s")
```

#### `calculate_spin_decay(initial_angular_velocity, time_step, density, viscosity, radius, config=None)`
Calculates spin decay due to air resistance.

**Parameters:**
- `initial_angular_velocity` (float): Initial angular velocity (rad/s)
- `time_step` (float): Time step (s)
- `density` (float): Air density (kg/m³)
- `viscosity` (float): Dynamic viscosity (Pa·s)
- `radius` (float): Object radius (m)
- `config` (dict): Configuration parameters

---

## Contact Physics

### Overview
The contact physics module implements advanced ground contact mechanics including Hertzian contact theory, friction modeling, and collision response.

### Key Functions

#### `calculate_hertzian_contact_force(penetration, radius, youngs_modulus=1e7, poisson_ratio=0.5)`
Calculates Hertzian contact force for sphere-surface collision.

**Formula:**
`F = (4/3) * E_eff * a³ / R`

Where:
- `E_eff = E / (1 - ν²)` (effective elastic modulus)
- `a = √(R * δ)` (contact radius)
- `δ` = penetration depth

**Parameters:**
- `penetration` (float): Penetration depth (m)
- `radius` (float): Sphere radius (m)
- `youngs_modulus` (float): Young's modulus (Pa)
- `poisson_ratio` (float): Poisson's ratio

**Example:**
```python
from physimlab.physics import calculate_hertzian_contact_force

# Calculate contact force for 1mm penetration
force = calculate_hertzian_contact_force(penetration=0.001, radius=0.1)
print(f"Contact force: {force:.2f} N")
```

#### `calculate_coefficient_of_restitution(impact_velocity, base_restitution=0.7, velocity_dependence=0.02, dampness=0.0, wetness=0.0)`
Calculates velocity-dependent coefficient of restitution.

**Formula:**
`e = e_base * exp(-k * v) * (1 - dampness) * (1 - 0.5 * wetness)`

**Parameters:**
- `impact_velocity` (float): Impact velocity magnitude (m/s)
- `base_restitution` (float): Base coefficient at 1 m/s
- `velocity_dependence` (float): Velocity dependence parameter
- `dampness` (float): Surface dampness (0-1)
- `wetness` (float): Surface wetness (0-1)

#### `calculate_friction_forces_advanced(normal_force, relative_velocity, angular_velocity, radius, config)`
Calculates advanced friction forces with comprehensive physics modeling.

**Features:**
- Static friction (stiction) modeling
- Kinetic friction with Stribeck effect
- Rolling resistance
- Surface condition effects
- Temperature effects

**Parameters:**
- `normal_force` (float): Normal contact force (N)
- `relative_velocity` (np.ndarray): Relative velocity at contact point
- `angular_velocity` (np.ndarray): Angular velocity vector
- `radius` (float): Object radius (m)
- `config` (dict): Physics configuration

#### `apply_collision_response(velocity, angular_velocity, position, radius, mass, inertia, surface_config, physics_config)`
Applies complete collision response with Hertzian contact and friction.

**Features:**
- Hertzian contact force calculation
- Advanced friction modeling
- Rolling resistance
- Surface geometry effects
- Energy conservation

**Parameters:**
- `velocity` (np.ndarray): Current linear velocity
- `angular_velocity` (np.ndarray): Current angular velocity
- `position` (np.ndarray): Current position
- `radius` (float): Object radius
- `mass` (float): Object mass
- `inertia` (float): Moment of inertia
- `surface_config` (dict): Surface configuration
- `physics_config` (dict): Physics configuration

---

## Wind and Atmospheric Effects

### Overview
The wind module implements comprehensive atmospheric and wind modeling including power law profiles, gust modeling, and atmospheric property calculations.

### Key Functions

#### `calculate_wind_velocity(z, ref_speed=2.0, ref_height=10.0, shear_alpha=0.15, direction_deg=0.0, gust_speed=0.0)`
Calculates wind velocity at height z using power law.

**Formula:**
`w(z) = w_ref * (z/z_ref)^α`

**Parameters:**
- `z` (float): Height above ground (m)
- `ref_speed` (float): Reference wind speed (m/s)
- `ref_height` (float): Reference height (m)
- `shear_alpha` (float): Power law exponent
- `direction_deg` (float): Wind direction (degrees)
- `gust_speed` (float): Additional gust component (m/s)

**Example:**
```python
from physimlab.physics import calculate_wind_velocity

# Calculate wind at 20m height
wind = calculate_wind_velocity(z=20.0, ref_speed=5.0, ref_height=10.0)
print(f"Wind velocity: {wind} m/s")
```

#### `calculate_atmospheric_properties(altitude=0.0, temperature=288.15, humidity=0.5)`
Calculates atmospheric properties using ISA model with humidity correction.

**Returns:**
- `density` (float): Air density (kg/m³)
- `viscosity` (float): Dynamic viscosity (Pa·s)
- `speed_of_sound` (float): Speed of sound (m/s)

**Features:**
- International Standard Atmosphere model
- Humidity corrections
- Temperature lapse rate
- Pressure calculations

#### `generate_gust_process(time, tau=1.5, sigma=0.5, dt=0.001, seed=None)`
Generates gust velocity using Ornstein-Uhlenbeck process.

**Parameters:**
- `time` (float): Current time (s)
- `tau` (float): Correlation time constant (s)
- `sigma` (float): Gust intensity standard deviation (m/s)
- `dt` (float): Time step (s)
- `seed` (int): Random seed for reproducibility

#### `calculate_wind_forces(velocity, wind_velocity, density, area, drag_coefficient)`
Calculates wind forces on an object.

**Formula:**
`F = 0.5 * ρ * |v_rel|² * A * Cd * (-v_rel/|v_rel|)`

**Parameters:**
- `velocity` (np.ndarray): Object velocity
- `wind_velocity` (np.ndarray): Wind velocity
- `density` (float): Air density
- `area` (float): Cross-sectional area
- `drag_coefficient` (float): Drag coefficient

---

## Numerical Integration

### Overview
The numerical integration module provides advanced integration methods including adaptive RK45 and stability monitoring.

### Key Classes

#### `AdaptiveRK45`
Adaptive Runge-Kutta 4(5) method using Dormand-Prince coefficients.

**Features:**
- Adaptive timestep control
- Error estimation and control
- Stability monitoring
- Energy conservation checks

**Example:**
```python
from physimlab.physics import AdaptiveRK45

# Create integrator
integrator = AdaptiveRK45(rtol=1e-6, atol=1e-8)

# Integrate ODE
def simple_ode(t, y):
    return np.array([-y[0]])

times, solutions = integrator.integrate(simple_ode, 0.0, np.array([1.0]), 1.0, 0.1)
```

**Parameters:**
- `rtol` (float): Relative tolerance
- `atol` (float): Absolute tolerance
- `min_dt` (float): Minimum timestep
- `max_dt` (float): Maximum timestep

#### `fixed_step_euler(func, t0, y0, t_end, dt)`
Simple fixed-step Euler integration for comparison.

**Parameters:**
- `func`: Function to integrate, dy/dt = func(t, y)
- `t0` (float): Initial time
- `y0` (np.ndarray): Initial state vector
- `t_end` (float): Final time
- `dt` (float): Fixed timestep

### Utility Functions

#### `check_stability(y, y_prev, threshold=1e6)`
Checks numerical stability by monitoring solution growth.

**Parameters:**
- `y` (np.ndarray): Current solution
- `y_prev` (np.ndarray): Previous solution
- `threshold` (float): Maximum allowed solution magnitude

#### `energy_monitor(y, g=9.81, m=1.0, I=1.0)`
Calculates total mechanical energy for stability monitoring.

**Formula:**
`E = 0.5*m*v² + m*g*z + 0.5*I*ω²`

**Parameters:**
- `y` (np.ndarray): State vector [x, y, z, vx, vy, vz, ωx, ωy, ωz]
- `g` (float): Gravitational acceleration
- `m` (float): Mass
- `I` (float): Moment of inertia

#### `adaptive_timestep_controller(error, dt, rtol=1e-4, atol=1e-6, min_dt=1e-5, max_dt=0.05)`
Adaptive timestep controller based on error estimate.

**Parameters:**
- `error` (float): Error estimate
- `dt` (float): Current timestep
- `rtol` (float): Relative tolerance
- `atol` (float): Absolute tolerance
- `min_dt` (float): Minimum timestep
- `max_dt` (float): Maximum timestep

---

## Advanced Physics Features

### Overview
The enhanced aerodynamics module implements cutting-edge physics models including virtual mass effects, compressibility corrections, and advanced force calculations.

### Key Functions

#### `calculate_buoyancy_force(density, volume, gravity=9.81)`
Calculates buoyancy force using Archimedes' principle.

**Formula:**
`F_b = ρ * V * g`

**Parameters:**
- `density` (float): Fluid density (kg/m³)
- `volume` (float): Displaced volume (m³)
- `gravity` (float): Gravitational acceleration (m/s²)

#### `calculate_virtual_mass(density, volume, added_mass_coefficient=0.5)`
Calculates virtual (added) mass effect.

**Formula:**
`m_added = C_m * ρ * V`

**Parameters:**
- `density` (float): Fluid density (kg/m³)
- `volume` (float): Object volume (m³)
- `added_mass_coefficient` (float): Added mass coefficient (0.5 for sphere)

#### `calculate_effective_mass(mass, density, volume, added_mass_coefficient=0.5)`
Calculates effective mass including virtual mass effect.

**Formula:**
`m_eff = m + m_added`

**Parameters:**
- `mass` (float): Object mass (kg)
- `density` (float): Fluid density (kg/m³)
- `volume` (float): Object volume (m³)
- `added_mass_coefficient` (float): Added mass coefficient

#### `calculate_aerodynamic_forces(velocity, angular_velocity, density, viscosity, radius, mass, gravity=9.81, wind_velocity=None, surface_roughness=0.0, config=None)`
Calculates complete aerodynamic forces including drag, lift, and buoyancy.

**Features:**
- Multi-regime drag coefficient
- Magnus effect with advanced correlations
- Buoyancy force
- Virtual mass effects
- Wind effects
- Surface roughness corrections

**Parameters:**
- `velocity` (np.ndarray): Object velocity [vx, vy, vz]
- `angular_velocity` (np.ndarray): Angular velocity [ωx, ωy, ωz]
- `density` (float): Air density (kg/m³)
- `viscosity` (float): Dynamic viscosity (Pa·s)
- `radius` (float): Object radius (m)
- `mass` (float): Object mass (kg)
- `gravity` (float): Gravitational acceleration (m/s²)
- `wind_velocity` (np.ndarray): Wind velocity [wx, wy, wz]
- `surface_roughness` (float): Surface roughness (m)
- `config` (dict): Configuration parameters

#### `calculate_spin_decay_advanced(angular_velocity, velocity, density, viscosity, radius, time_step, config=None)`
Calculates advanced spin decay with aerodynamic and contact effects.

**Features:**
- Aerodynamic torque modeling
- Velocity-dependent decay
- Configuration-driven parameters
- Contact effects

**Parameters:**
- `angular_velocity` (np.ndarray): Current angular velocity
- `velocity` (np.ndarray): Linear velocity
- `density` (float): Air density
- `viscosity` (float): Dynamic viscosity
- `radius` (float): Object radius
- `time_step` (float): Time step
- `config` (dict): Configuration parameters

#### `calculate_compressibility_correction(mach, flow_type='subsonic')`
Calculates compressibility correction factor.

**Features:**
- Prandtl-Glauert correction for subsonic flow
- Transonic corrections
- Supersonic corrections

**Parameters:**
- `mach` (float): Mach number
- `flow_type` (str): Flow type ('subsonic', 'transonic', 'supersonic')

### Key Classes

#### `AerodynamicModel`
Advanced aerodynamic model with all effects integrated.

**Features:**
- Unified force calculation interface
- Configuration-driven physics
- History tracking
- Advanced correlations

**Example:**
```python
from physimlab.physics import AerodynamicModel

# Create model
config = {
    'surface_roughness': 0.001,
    'humidity': 0.5,
    'wind_field': wind_config
}
model = AerodynamicModel(config)

# Calculate forces
state = {
    'velocity': np.array([10.0, 0.0, 0.0]),
    'angular_velocity': np.array([0.0, 0.0, 100.0]),
    'position': np.array([0.0, 0.0, 10.0]),
    'radius': 0.1,
    'mass': 0.5
}

result = model.calculate_forces(state)
print(f"Force: {result['force']}")
print(f"Torque: {result['torque']}")
print(f"Reynolds: {result['reynolds']}")
```

#### `WindField`
Class for managing complex wind fields with multiple components.

**Features:**
- Power law wind profiles
- Gust modeling with Ornstein-Uhlenbeck process
- Atmospheric property calculations
- Time-dependent wind variations

**Example:**
```python
from physimlab.physics import WindField

# Create wind field
config = {
    'ref_speed': 5.0,
    'ref_height': 10.0,
    'direction_deg': 90.0,
    'gust_tau': 1.5,
    'gust_sigma': 0.5,
    'humidity_pct': 50.0
}
wind_field = WindField(config)

# Get wind at position and time
position = np.array([0.0, 0.0, 10.0])
time = 5.0
wind_vel = wind_field.get_wind_velocity(position, time)
density, viscosity, speed_of_sound = wind_field.get_atmospheric_properties(position)
```

---

## Configuration Parameters

### Physics Configuration
All physics models accept configuration dictionaries with the following common parameters:

```python
physics_config = {
    # Aerodynamics
    'buoyancy': True,                    # Enable buoyancy forces
    'use_virtual_mass': True,            # Enable virtual mass effects
    'use_multi_regime_cd': True,         # Use advanced drag correlations
    'compressibility_correction': True,  # Enable compressibility effects
    
    # Contact physics
    'use_hertzian_contact': True,        # Use Hertzian contact model
    'surface_roughness': 0.001,          # Surface roughness (m)
    'elasticity_base': 0.7,              # Base coefficient of restitution
    'friction_mu_s': 0.5,                # Static friction coefficient
    'friction_mu_k': 0.3,                # Kinetic friction coefficient
    
    # Numerical integration
    'adaptive_timestep': True,           # Use adaptive integration
    'rtol': 1e-6,                        # Relative tolerance
    'atol': 1e-8,                        # Absolute tolerance
    'min_dt': 1e-5,                      # Minimum timestep
    'max_dt': 0.05,                      # Maximum timestep
    
    # Spin decay
    'c_spin_decay': 0.05,                # Spin decay coefficient
    'c_spin_aero': 0.02,                 # Aerodynamic spin effects
    
    # Wind effects
    'wind_speed': 5.0,                   # Reference wind speed
    'wind_direction': 90.0,              # Wind direction (degrees)
    'gust_intensity': 0.5,               # Gust intensity
}
```

### Constants
The physics modules use the following physical constants:

```python
# Gas constants
R_d = 287.058      # J/(kg·K) - gas constant for dry air
R_v = 461.495      # J/(kg·K) - gas constant for water vapor

# Standard conditions
T_0 = 288.15       # K - standard temperature at sea level
p_0 = 101325       # Pa - standard pressure at sea level
g_0 = 9.80665      # m/s² - standard gravity

# Sutherland constants
mu_0 = 1.716e-5    # Pa·s - reference viscosity
T_0_suth = 273.15  # K - reference temperature
S = 110.4          # K - Sutherland constant

# Material properties
E_default = 1e7    # Pa - default Young's modulus
nu_default = 0.5   # - default Poisson's ratio
```

---

## Usage Examples

### Complete Physics Simulation
```python
import numpy as np
from physimlab.physics import (
    calculate_aerodynamic_forces,
    calculate_hertzian_contact_force,
    calculate_wind_velocity,
    calculate_atmospheric_properties
)

# Object properties
mass = 0.5         # kg
radius = 0.1       # m
volume = (4/3) * np.pi * radius**3

# State variables
velocity = np.array([10.0, 5.0, -20.0])      # m/s
angular_velocity = np.array([0.0, 0.0, 100.0]) # rad/s
position = np.array([0.0, 0.0, 50.0])        # m

# Environmental conditions
temperature = 288.15  # K
humidity = 0.5        # relative humidity
altitude = position[2]  # m

# Calculate atmospheric properties
density, viscosity, speed_of_sound = calculate_atmospheric_properties(
    altitude, temperature, humidity
)

# Calculate wind effects
wind_velocity = calculate_wind_velocity(
    altitude, ref_speed=5.0, ref_height=10.0, direction_deg=90.0
)

# Calculate aerodynamic forces
force, torque, reynolds = calculate_aerodynamic_forces(
    velocity, angular_velocity, density, viscosity, radius, mass,
    wind_velocity=wind_velocity,
    surface_roughness=0.001
)

print(f"Aerodynamic force: {force} N")
print(f"Aerodynamic torque: {torque} N·m")
print(f"Reynolds number: {reynolds:.0f}")

# Check for ground contact
if position[2] <= radius:
    penetration = radius - position[2]
    contact_force = calculate_hertzian_contact_force(penetration, radius)
    print(f"Contact force: {contact_force:.2f} N")
```

### Advanced Configuration
```python
# Advanced physics configuration
config = {
    'simulation': {
        'adaptive_timestep': True,
        'buoyancy': True,
        'use_virtual_mass': True,
        'use_multi_regime_cd': True,
        'use_hertzian_contact': True,
        'rtol': 1e-6,
        'atol': 1e-8,
        'min_dt': 1e-5,
        'max_dt': 0.05
    },
    'ball': {
        'mass': 0.5,
        'radius': 0.1,
        'spin_rps': 10.0
    },
    'wind': {
        'ref_speed': 10.0,
        'ref_height': 10.0,
        'direction_deg': 90.0,
        'gust_tau': 2.0,
        'gust_sigma': 1.0,
        'humidity_pct': 60.0
    },
    'surface': {
        'elasticity_base': 0.8,
        'friction_mu_s': 0.6,
        'friction_mu_k': 0.4,
        'surface_roughness': 0.002
    }
}

# Use with simulation
result = run_simulation(config_path=None, **config)
```

This comprehensive documentation provides detailed information about all physics models, their parameters, and usage examples. The physics implementation in physimlab is designed to be both accurate and flexible, supporting a wide range of simulation scenarios from simple ball drops to complex aerodynamic analyses.