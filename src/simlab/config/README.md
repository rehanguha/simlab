# Configuration Module

This directory contains the configuration handling system for SimLab, responsible for loading, validating, and managing simulation parameters.

## Overview

The configuration module provides a flexible system for defining simulation parameters through JSON or YAML configuration files. It includes validation, default value handling, and integration with the main simulation engine.

## Module Structure

```
config/
├── __init__.py      # Module exports and public API
└── loader.py        # Configuration loading and validation logic
```

## Configuration File Format

SimLab supports both JSON and YAML configuration files with the same structure. The configuration defines all parameters needed for a simulation including:

- **Scenario Settings**: Type of simulation to run
- **Object Properties**: Physical properties of the simulated object
- **Environment Parameters**: Atmospheric conditions and gravity
- **Simulation Settings**: Time steps, tolerances, and integration methods
- **Output Configuration**: Output formats and file paths

## Configuration Structure

### Basic Configuration Example (JSON)
```json
{
  "scenario": "drop",
  "object": {
    "type": "sphere",
    "mass": 0.5,
    "radius": 0.1,
    "spin_rate": 8.0
  },
  "initial_height": 100,
  "environment": {
    "gravity": 9.81,
    "temperature": 288.15,
    "humidity": 0.5
  },
  "simulation": {
    "time_step": 0.001,
    "max_time": 30.0,
    "tolerance": 1e-6
  },
  "output": {
    "format": ["csv", "json", "html"],
    "directory": "./results"
  }
}
```

### YAML Configuration Example
```yaml
scenario: drop
object:
  type: sphere
  mass: 0.5
  radius: 0.1
  spin_rate: 8.0
initial_height: 100
environment:
  gravity: 9.81
  temperature: 288.15
  humidity: 0.5
simulation:
  time_step: 0.001
  max_time: 30.0
  tolerance: 1e-6
output:
  format:
    - csv
    - json
    - html
  directory: ./results
```

## Configuration Sections

### Scenario Configuration
Defines the type of simulation to run:
- **drop**: Ball drop simulation with aerodynamics
- **wind-tunnel**: Aerodynamics testing with controlled airflow
- **terminal-velocity**: Free fall with complete drag force analysis
- **projectile**: Projectile motion with full aerodynamic effects
- **spin-analysis**: Rotational dynamics with advanced decay modeling

### Object Configuration
Defines the physical properties of the simulated object:
- **type**: Object shape (sphere, cylinder, etc.)
- **mass**: Object mass in kilograms
- **radius**: Object radius in meters
- **spin_rate**: Initial spin rate in radians per second
- **material**: Material properties for contact physics

### Environment Configuration
Defines atmospheric and environmental conditions:
- **gravity**: Gravitational acceleration (m/s²)
- **temperature**: Ambient temperature (Kelvin)
- **humidity**: Relative humidity (0.0 to 1.0)
- **pressure**: Atmospheric pressure (Pascals)
- **wind_speed**: Wind speed at reference height (m/s)
- **wind_direction**: Wind direction in degrees

### Simulation Configuration
Defines numerical integration and simulation parameters:
- **time_step**: Integration time step (seconds)
- **max_time**: Maximum simulation time (seconds)
- **tolerance**: Integration error tolerance
- **method**: Integration method (adaptive, fixed-step)
- **adaptive**: Enable adaptive time stepping

### Output Configuration
Defines output formats and file management:
- **format**: List of output formats (csv, json, html, png, gif)
- **directory**: Output directory path
- **filename**: Base filename for output files
- **overwrite**: Allow overwriting existing files

## Usage Examples

### Loading Configuration
```python
from simlab.config import load_config

# Load from JSON file
config = load_config("config.json")

# Load from YAML file
config = load_config("config.yaml")

# Load with validation
config = load_config("config.json", validate=True)
```

### Configuration Validation
```python
from simlab.config import validate_config

# Validate configuration
is_valid, errors = validate_config(config)

if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
```

### Default Values
The configuration system provides sensible defaults for missing parameters:
```python
# Minimal configuration - defaults will be applied
minimal_config = {
    "scenario": "drop",
    "object": {"mass": 0.5, "radius": 0.1},
    "initial_height": 100
}

# Load with defaults applied
config = load_config(minimal_config)
```

## Configuration Schema

The configuration system uses a comprehensive schema to validate all parameters:

### Required Fields
- **scenario**: Must be a valid simulation scenario
- **object**: Must contain valid object properties
- **initial_height**: Must be positive number

### Optional Fields with Defaults
- **environment.gravity**: Defaults to 9.81 m/s²
- **environment.temperature**: Defaults to 288.15 K (15°C)
- **environment.humidity**: Defaults to 0.5 (50%)
- **simulation.time_step**: Defaults to 0.001 s
- **simulation.max_time**: Defaults to 30.0 s
- **simulation.tolerance**: Defaults to 1e-6

### Validation Rules
- All numerical values must be positive where applicable
- Object properties must be physically reasonable
- Simulation parameters must ensure numerical stability
- Output paths must be valid and writable

## Advanced Configuration

### Custom Scenarios
You can define custom scenarios by extending the configuration:
```json
{
  "scenario": "custom",
  "custom_parameters": {
    "parameter1": 1.0,
    "parameter2": 2.0
  }
}
```

### Environment Profiles
Define complex atmospheric conditions:
```json
{
  "environment": {
    "temperature_profile": {
      "type": "linear",
      "gradient": -0.0065,
      "base_temperature": 288.15
    },
    "wind_profile": {
      "type": "power_law",
      "exponent": 0.143,
      "reference_height": 10.0
    }
  }
}
```

### Output Customization
Customize output generation:
```json
{
  "output": {
    "format": ["csv", "json", "html", "png", "gif"],
    "directory": "./custom_results",
    "filename": "simulation_results",
    "overwrite": false,
    "compression": true,
    "precision": 6
  }
}
```

## Error Handling

The configuration system provides comprehensive error handling:

### File Loading Errors
- File not found
- Invalid JSON/YAML syntax
- File permission issues

### Validation Errors
- Missing required fields
- Invalid parameter values
- Type mismatches
- Logical inconsistencies

### Error Messages
Error messages include:
- Clear description of the problem
- Location of the error in the configuration
- Suggested fixes
- Example of correct configuration

## Integration with Simulation Engine

The configuration system integrates seamlessly with the simulation engine:

1. **Parameter Loading**: Configuration parameters are loaded and validated
2. **Default Application**: Missing parameters get sensible defaults
3. **Type Conversion**: String values are converted to appropriate types
4. **Validation**: All parameters are validated before simulation
5. **Error Reporting**: Clear error messages for invalid configurations

## Best Practices

### Configuration File Organization
1. **Use YAML for readability**: YAML is more human-readable than JSON
2. **Include comments**: Document complex parameters with comments
3. **Organize logically**: Group related parameters together
4. **Use consistent naming**: Follow snake_case or camelCase consistently

### Parameter Management
1. **Use meaningful names**: Choose descriptive parameter names
2. **Document units**: Always specify units in comments
3. **Provide ranges**: Document valid ranges for parameters
4. **Include examples**: Provide example values in comments

### Version Control
1. **Track configuration changes**: Include configuration files in version control
2. **Use configuration templates**: Create templates for different scenarios
3. **Document breaking changes**: Note any configuration format changes
4. **Maintain backward compatibility**: Support older configuration formats when possible

### Testing
1. **Test configuration loading**: Verify all configuration files load correctly
2. **Test validation**: Ensure validation catches invalid configurations
3. **Test defaults**: Verify default values are applied correctly
4. **Test edge cases**: Test with minimal and maximal configurations

## Dependencies

- **PyYAML**: YAML file parsing and loading
- **JSON**: Built-in JSON support
- **Pathlib**: File path handling
- **Logging**: Error reporting and debugging