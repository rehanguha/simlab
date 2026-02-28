# Utilities Module

This directory contains utility functions and constants used throughout the SimLab physics simulation library.

## Overview

The utils module provides essential utilities including physical constants, helper functions for data processing, formatting, and mathematical operations that support the core simulation functionality.

## Module Structure

```
utils/
├── __init__.py      # Module exports and public API
├── constants.py     # Physical constants and mathematical values
└── helpers.py       # Formatting and utility functions
```

## Physical Constants (`constants.py`)

This module defines all the physical constants used throughout the simulation:

### Fundamental Constants
- **GRAVITATIONAL_CONSTANT**: Newton's gravitational constant (6.67430e-11 m³ kg⁻¹ s⁻²)
- **SPEED_OF_LIGHT**: Speed of light in vacuum (299792458 m/s)
- **PLANCK_CONSTANT**: Planck's constant (6.62607015e-34 J⋅s)
- **BOLTZMANN_CONSTANT**: Boltzmann constant (1.380649e-23 J/K)

### Earth and Atmospheric Constants
- **EARTH_MASS**: Mass of Earth (5.972e24 kg)
- **EARTH_RADIUS**: Mean radius of Earth (6.371e6 m)
- **STANDARD_GRAVITY**: Standard acceleration due to gravity (9.80665 m/s²)
- **ATMOSPHERIC_PRESSURE**: Standard atmospheric pressure at sea level (101325 Pa)
- **STANDARD_TEMPERATURE**: Standard temperature (288.15 K / 15°C)

### Material Properties
- **DENSITY_AIR**: Density of air at standard conditions (1.225 kg/m³)
- **DENSITY_WATER**: Density of water (1000 kg/m³)
- **YOUNGS_MODULUS_STEEL**: Young's modulus for steel (200e9 Pa)
- **YOUNGS_MODULUS_RUBBER**: Young's modulus for rubber (0.01-0.1 GPa range)
- **COEFFICIENT_OF_RESTITUTION**: Typical values for different materials

### Mathematical Constants
- **PI**: π (3.141592653589793)
- **E**: Euler's number (2.718281828459045)
- **SQRT2**: Square root of 2 (1.4142135623730951)
- **SQRT3**: Square root of 3 (1.7320508075688772)

### Conversion Factors
- **DEG_TO_RAD**: Degrees to radians conversion (π/180)
- **RAD_TO_DEG**: Radians to degrees conversion (180/π)
- **KMH_TO_MPS**: km/h to m/s conversion (1000/3600)
- **MPS_TO_KMH**: m/s to km/h conversion (3600/1000)
- **ATM_TO_PA**: Atmospheres to Pascals conversion (101325)

## Helper Functions (`helpers.py`)

This module provides utility functions for data processing, formatting, and common operations:

### Data Processing Helpers
```python
def interpolate_data(x, y, x_new):
    """Linear interpolation between data points"""
    
def smooth_data(data, window_size=5):
    """Apply moving average smoothing"""
    
def normalize_vector(vector):
    """Normalize a vector to unit length"""
    
def clamp(value, min_val, max_val):
    """Clamp a value between minimum and maximum"""
```

### Formatting Functions
```python
def format_time(seconds):
    """Format time in human-readable format (HH:MM:SS.mmm)"""
    
def format_distance(meters):
    """Format distance with appropriate units (m, km)"""
    
def format_velocity(mps):
    """Format velocity with appropriate units (m/s, km/h)"""
    
def format_angle(radians):
    """Format angle in degrees with degree symbol"""
    
def format_scientific(value, precision=3):
    """Format number in scientific notation"""
```

### Mathematical Utilities
```python
def safe_divide(numerator, denominator, default=0.0):
    """Safe division that handles zero denominators"""
    
def safe_sqrt(value, default=0.0):
    """Safe square root that handles negative values"""
    
def signum(value):
    """Return sign of a value (-1, 0, 1)"""
    
def weighted_average(values, weights):
    """Calculate weighted average of values"""
    
def moving_average(data, window_size):
    """Calculate moving average with specified window size"""
```

### File and Path Utilities
```python
def ensure_directory(path):
    """Ensure directory exists, create if necessary"""
    
def get_file_size(filepath):
    """Get file size in human-readable format"""
    
def validate_file_extension(filepath, extensions):
    """Validate file has expected extension"""
    
def sanitize_filename(filename):
    """Remove invalid characters from filename"""
```

### Configuration Utilities
```python
def merge_dicts(dict1, dict2):
    """Recursively merge two dictionaries"""
    
def validate_range(value, min_val, max_val, name):
    """Validate value is within specified range"""
    
def parse_boolean(value):
    """Parse string to boolean (handles various formats)"""
    
def get_default_config():
    """Get default configuration with all parameters"""
```

## Usage Examples

### Using Physical Constants
```python
from simlab.utils.constants import (
    STANDARD_GRAVITY, 
    DENSITY_AIR,
    PI
)

# Calculate gravitational force
mass = 1.0  # kg
gravity_force = mass * STANDARD_GRAVITY

# Calculate air resistance
area = PI * radius**2
drag_force = 0.5 * DENSITY_AIR * velocity**2 * cd * area
```

### Using Helper Functions
```python
from simlab.utils.helpers import (
    format_time,
    format_velocity,
    normalize_vector,
    clamp
)

# Format simulation results
print(f"Flight time: {format_time(flight_time)}")
print(f"Max velocity: {format_velocity(max_velocity)}")

# Process simulation data
normalized_velocity = normalize_vector(velocity_vector)
clamped_angle = clamp(angle, -PI, PI)

# Smooth noisy data
smoothed_data = smooth_data(raw_data, window_size=10)
```

### Configuration Utilities
```python
from simlab.utils.helpers import merge_dicts, validate_range

# Merge user config with defaults
default_config = get_default_config()
user_config = load_config("user_config.json")
final_config = merge_dicts(default_config, user_config)

# Validate parameters
validate_range(final_config['object']['mass'], 0.001, 10.0, 'mass')
validate_range(final_config['simulation']['time_step'], 1e-6, 0.1, 'time_step')
```

## Integration with Other Modules

### Physics Module Integration
```python
# constants.py used in physics calculations
from simlab.utils.constants import STANDARD_GRAVITY, DENSITY_AIR

def calculate_gravity(altitude):
    return STANDARD_GRAVITY * (EARTH_RADIUS / (EARTH_RADIUS + altitude))**2

def calculate_density(temperature, humidity):
    return DENSITY_AIR * (temperature / STANDARD_TEMPERATURE) * (1 - 0.378 * humidity)
```

### Output Module Integration
```python
# helpers.py used in output formatting
from simlab.utils.helpers import format_time, format_velocity, format_distance

def format_summary(summary):
    return {
        'flight_time': format_time(summary['flight_time']),
        'max_height': format_distance(summary['max_height']),
        'max_velocity': format_velocity(summary['max_velocity']),
        'horizontal_range': format_distance(summary['horizontal_range'])
    }
```

### Configuration Module Integration
```python
# helpers.py used in configuration validation
from simlab.utils.helpers import validate_range, parse_boolean

def validate_config(config):
    errors = []
    
    # Validate object properties
    validate_range(config['object']['mass'], 0.001, 100.0, 'mass', errors)
    validate_range(config['object']['radius'], 0.001, 1.0, 'radius', errors)
    
    # Parse boolean values
    config['simulation']['adaptive'] = parse_boolean(
        config['simulation'].get('adaptive', True)
    )
    
    return len(errors) == 0, errors
```

## Performance Considerations

### Optimization Strategies
- **Constant Caching**: Frequently used constants are cached for performance
- **Vectorization**: Helper functions support NumPy arrays for batch operations
- **Memory Efficiency**: Functions minimize memory allocation where possible
- **Lazy Evaluation**: Expensive calculations are deferred until needed

### Best Practices
1. **Import Specific Constants**: Import only needed constants to reduce memory
2. **Reuse Helper Functions**: Use existing helpers rather than duplicating logic
3. **Batch Operations**: Use vectorized operations for array processing
4. **Error Handling**: Always handle edge cases in utility functions

## Testing

The utils module includes comprehensive tests:
```bash
# Run utils tests
pytest tests/test_utils.py

# Test specific utility functions
pytest tests/test_utils.py::test_format_time
pytest tests/test_utils.py::test_normalize_vector
pytest tests/test_utils.py::test_physical_constants
```

## Dependencies

- **NumPy**: Array operations and mathematical functions
- **Math**: Standard mathematical functions and constants
- **OS/Pathlib**: File and path operations
- **Datetime**: Time formatting and manipulation

## Best Practices

### Code Organization
1. **Separate Concerns**: Keep constants and helpers in separate modules
2. **Clear Naming**: Use descriptive names for constants and functions
3. **Documentation**: Document all public functions and constants
4. **Type Hints**: Use type annotations for better code documentation

### Maintainability
1. **Version Control**: Track changes to constants and utilities
2. **Backward Compatibility**: Maintain compatibility when updating utilities
3. **Testing**: Comprehensive test coverage for all utility functions
4. **Documentation**: Keep documentation up-to-date with code changes

### Performance
1. **Efficient Algorithms**: Use optimal algorithms for common operations
2. **Memory Management**: Minimize memory usage in utility functions
3. **Caching**: Cache expensive calculations where appropriate
4. **Profiling**: Regularly profile utility functions for performance bottlenecks