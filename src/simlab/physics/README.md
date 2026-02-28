# Physics Module

This directory contains all the physics calculations and models used by physimlab for simulating physical systems.

## Overview

The physics module implements advanced mathematical models for aerodynamics, mechanics, numerical integration, wind effects, and contact physics. Each sub-module focuses on a specific domain of physics calculations.

## Module Structure

```
physics/
├── __init__.py                    # Module exports and public API
├── aerodynamics.py               # Basic aerodynamic calculations
├── aerodynamics_enhanced.py      # Advanced aerodynamic models
├── mechanics.py                  # Mechanical physics calculations
├── numerical.py                  # Numerical integration methods
├── wind.py                       # Wind and atmospheric effects
├── contact.py                    # Contact mechanics and collisions
├── models.py                     # Physics model definitions
├── integration.py                # Integration utilities
├── corrections.py                # Mathematical corrections
└── validation.py                 # Physics validation functions
```

## Physics Domains

### Aerodynamics (`aerodynamics.py`)
- **Air Properties**: Density, viscosity, speed of sound calculations
- **Flow Analysis**: Reynolds number, Mach number calculations
- **Drag Forces**: Drag coefficient calculations based on flow regime
- **Magnus Effect**: Spin-induced lift force calculations
- **Wind Forces**: Relative velocity and wind force calculations

**Key Functions:**
```python
calculate_density(temperature, humidity)
calculate_viscosity(temperature)
calculate_reynolds_number(velocity, diameter, density, viscosity)
calculate_drag_coefficient(reynolds)
calculate_magnus_force(velocity, spin_rate, radius)
```

### Enhanced Aerodynamics (`aerodynamics_enhanced.py`)
- **Multi-Regime Drag**: Advanced drag coefficient across flow regimes
- **Buoyancy Forces**: Archimedes' principle calculations
- **Virtual Mass**: Added mass effects for acceleration
- **Compressibility**: High-speed flow corrections
- **Complete Aerodynamic Model**: Integrated force calculations

**Key Features:**
- Reynolds number-dependent drag coefficient
- Compressibility corrections for high Mach numbers
- Virtual mass effects on acceleration
- Comprehensive aerodynamic force integration

### Mechanics (`mechanics.py`)
- **Gravitational Forces**: Altitude-dependent gravity calculations
- **Terminal Velocity**: Equilibrium between drag and gravity
- **Spin Decay**: Rotational energy dissipation due to air resistance

**Key Functions:**
```python
calculate_gravity(altitude)
calculate_terminal_velocity(mass, drag_coefficient, area, density)
calculate_spin_decay(spin_rate, time_step)
```

### Numerical Methods (`numerical.py`)
- **Adaptive Integration**: RK45 Dormand-Prince with error control
- **Fixed-Step Euler**: Simple integration for comparison
- **Stability Monitoring**: Energy-based stability checks
- **Adaptive Timestep**: Automatic step size control

**Key Classes:**
```python
class AdaptiveRK45:
    """Adaptive Runge-Kutta 45 integrator with error control"""
    
class FixedStepEuler:
    """Fixed-step Euler integrator for simple cases"""
```

### Wind Effects (`wind.py`)
- **Atmospheric Properties**: Temperature, pressure, density profiles
- **Wind Profiles**: Power law and logarithmic wind profiles
- **Turbulence Modeling**: Gust generation and turbulence intensity
- **Wind Forces**: Complete wind force and moment calculations
- **Wind Field**: Comprehensive atmospheric modeling

**Key Functions:**
```python
calculate_wind_velocity(height, wind_speed_ref, height_ref)
generate_gust_process(time, gust_intensity, gust_duration)
calculate_atmospheric_properties(altitude, temperature, humidity)
```

### Contact Physics (`contact.py`)
- **Collision Detection**: Sphere-surface intersection testing
- **Hertzian Contact**: Elastic deformation force calculations
- **Restitution**: Energy loss during impacts
- **Friction Models**: Static and dynamic friction forces
- **Rolling Resistance**: Rolling friction calculations
- **Surface Geometry**: Complex surface shape modeling

**Key Functions:**
```python
calculate_hertzian_contact_force(penetration, radius, youngs_modulus)
calculate_coefficient_of_restitution(velocity, material_properties)
detect_collision(position, surface_geometry)
apply_collision_response(velocity, normal, restitution, friction)
```

### Physics Models (`models.py`)
- **Model Definitions**: Base classes for physics models
- **Integration**: Model integration with simulation engine
- **Validation**: Physics model validation and testing

### Integration Utilities (`integration.py`)
- **Integration Helpers**: Utility functions for numerical integration
- **Error Control**: Integration error monitoring and control
- **Performance**: Optimization utilities for integration

### Mathematical Corrections (`corrections.py`)
- **Numerical Corrections**: Fixes for mathematical inaccuracies
- **Edge Cases**: Handling of special cases and boundary conditions
- **Precision**: High-precision calculations where needed

### Validation (`validation.py`)
- **Physics Validation**: Validation of physics calculations
- **Consistency Checks**: Ensuring physical consistency
- **Error Detection**: Detection of unphysical results

## Usage Examples

### Basic Aerodynamics
```python
from physimlab.physics import calculate_density, calculate_drag_coefficient

# Calculate air density at 25°C with 50% humidity
density = calculate_density(temperature=298.15, humidity=0.5)

# Calculate drag coefficient for given Reynolds number
reynolds = 100000
cd = calculate_drag_coefficient(reynolds)
```

### Advanced Integration
```python
from physimlab.physics.numerical import AdaptiveRK45

# Create adaptive integrator
integrator = AdaptiveRK45(
    func=equations_of_motion,
    y0=initial_conditions,
    t_span=[0, 10],
    rtol=1e-6,
    atol=1e-8
)

# Integrate
solution = integrator.solve()
```

### Wind Effects
```python
from physimlab.physics.wind import calculate_wind_velocity, generate_gust_process

# Calculate wind velocity at different heights
wind_speed = calculate_wind_velocity(
    height=10.0,
    wind_speed_ref=10.0,
    height_ref=10.0
)

# Generate gust process
gust = generate_gust_process(
    time=np.linspace(0, 10, 1000),
    gust_intensity=5.0,
    gust_duration=2.0
)
```

### Contact Physics
```python
from physimlab.physics.contact import detect_collision, apply_collision_response

# Detect collision with ground
collision_detected = detect_collision(position, surface_geometry)

if collision_detected:
    # Apply collision response
    new_velocity = apply_collision_response(
        velocity=current_velocity,
        normal=ground_normal,
        restitution=0.8,
        friction=0.3
    )
```

## Mathematical Models

### Aerodynamic Forces
The total aerodynamic force is calculated as:
```
F_aero = F_drag + F_magnus + F_buoyancy + F_virtual_mass
```

Where:
- **F_drag**: Pressure drag and skin friction
- **F_magnus**: Spin-induced lift (Magnus effect)
- **F_buoyancy**: Archimedes' principle
- **F_virtual_mass**: Added mass effects

### Drag Coefficient Model
The drag coefficient varies with Reynolds number:
```
Cd = f(Re) = Cd_laminar + (Cd_turbulent - Cd_laminar) * transition_function(Re)
```

### Magnus Force
The Magnus force is calculated using:
```
F_magnus = 0.5 * ρ * v * ω * r³ * Cl
```

Where Cl is the lift coefficient dependent on spin parameter.

## Performance Considerations

- **Vectorization**: Use NumPy arrays for batch calculations
- **Caching**: Cache expensive calculations where possible
- **Precision**: Balance numerical precision with performance
- **Integration**: Choose appropriate integration method for accuracy vs speed

## Testing

Each physics module includes comprehensive tests:
```bash
# Run physics tests
pytest tests/test_physics.py

# Run specific physics domain tests
pytest tests/test_physics_detailed.py
pytest tests/test_physics_complete.py
```

## Dependencies

- **NumPy**: Array operations and mathematical functions
- **SciPy**: Special functions and numerical utilities
- **Math**: Standard mathematical functions

## Integration with Simulation Engine

The physics modules integrate with the main simulation engine through:
1. **Configuration**: Physics parameters from configuration files
2. **State Updates**: Physics calculations update simulation state
3. **Output**: Physics results included in simulation outputs
4. **Validation**: Physics consistency checks during simulation

## Best Practices

1. **Unit Consistency**: Always use SI units (meters, kilograms, seconds)
2. **Error Handling**: Handle edge cases and numerical instabilities
3. **Documentation**: Document all mathematical models and assumptions
4. **Testing**: Validate physics calculations against known solutions
5. **Performance**: Optimize critical path calculations
6. **Extensibility**: Design for easy addition of new physics models