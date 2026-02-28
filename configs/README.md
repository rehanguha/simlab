# Configuration Examples

This directory contains example configuration files and generated reports for various simulation scenarios in SimLab.

## Overview

The configs directory provides a collection of configuration files that demonstrate different simulation scenarios, parameter combinations, and use cases. Each configuration file is paired with generated reports showing the simulation results.

## Configuration Files

### Basic Simulation Configurations

#### `config_no_wind_bounce.json`
- **Scenario**: Ball drop with multiple bounces
- **Features**: No wind effects, multiple ground contacts
- **Use Case**: Testing bounce physics and energy conservation
- **Parameters**: Standard atmospheric conditions, elastic collisions

#### `config_vacuum_drop.json`
- **Scenario**: Free fall in vacuum (no air resistance)
- **Features**: Zero air density, pure gravitational acceleration
- **Use Case**: Testing basic mechanics without aerodynamic effects
- **Parameters**: Vacuum conditions, no drag or lift forces

#### `config_terminal_velocity.json`
- **Scenario**: Object reaching terminal velocity
- **Features**: Drag force equilibrium with gravity
- **Use Case**: Testing drag calculations and terminal velocity physics
- **Parameters**: High drop height, realistic drag coefficients

### Advanced Physics Configurations

#### `config_high_wind.json`
- **Scenario**: Ball drop with strong wind effects
- **Features**: High wind speed, significant lateral displacement
- **Use Case**: Testing wind force calculations and trajectory effects
- **Parameters**: Wind speed of 20 m/s, crosswind effects

#### `config_spin_effect.json`
- **Scenario**: Spinning object with Magnus effect
- **Features**: Spin-induced lift forces, curved trajectory
- **Use Case**: Testing Magnus effect and rotational dynamics
- **Parameters**: High spin rate (8 rad/s), lift force calculations

#### `config_temperature_effect.json`
- **Scenario**: Temperature-dependent air properties
- **Features**: Variable temperature affecting air density and viscosity
- **Use Case**: Testing thermodynamic effects on aerodynamics
- **Parameters**: Temperature variations, ISA atmospheric model

#### `config_multi_bounce.json`
- **Scenario**: Multiple bounces with energy loss
- **Features**: Inelastic collisions, friction effects
- **Use Case**: Testing contact physics and energy dissipation
- **Parameters**: Low restitution coefficient, surface friction

### Validation and Testing Configurations

#### `config_validation_suite.json`
- **Scenario**: Comprehensive validation test
- **Features**: Multiple physics effects combined
- **Use Case**: System validation and regression testing
- **Parameters**: Complex parameter combinations, edge cases

## Generated Reports

Each configuration file has a corresponding HTML report showing the simulation results:

### Report Structure
```
configs/
├── config_[scenario].json           # Configuration file
├── [scenario]_report.html          # Interactive HTML report
├── plots/                          # Static plot images
│   ├── trajectory.png
│   ├── velocity.png
│   ├── physics.png
│   └── energy.png
└── data.csv                       # Raw simulation data
```

### Report Features
- **Interactive Plots**: Plotly-powered 2D and 3D visualizations
- **Summary Statistics**: Flight time, max height, range, velocities
- **Physics Analysis**: Drag coefficient, Reynolds number, Mach number
- **Energy Analysis**: Kinetic and potential energy over time
- **Stability Information**: Integration stability and error analysis

## Using Configuration Files

### Basic Usage
```bash
# Run simulation with specific configuration
simlab run --config configs/config_high_wind.json

# Run with custom output directory
simlab run --config configs/config_spin_effect.json --output ./my_results
```

### Python API Usage
```python
import simlab

# Load and run configuration
result = simlab.run_simulation(
    config_path="configs/config_terminal_velocity.json",
    output_dir="./terminal_velocity_results"
)

# Access results
summary = result['summary']
print(f"Terminal velocity: {summary['max_velocity']:.2f} m/s")
```

### Configuration Customization
You can modify existing configurations or create new ones:

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
    "humidity": 0.5,
    "wind_speed": 10.0,
    "wind_direction": 90
  },
  "simulation": {
    "time_step": 0.001,
    "max_time": 30.0,
    "tolerance": 1e-6
  }
}
```

## Configuration Guidelines

### Parameter Selection

#### Object Properties
- **Mass**: Typical range 0.01-10 kg for most applications
- **Radius**: Typical range 0.01-1.0 m for spherical objects
- **Spin Rate**: 0-50 rad/s for most realistic scenarios

#### Environment Settings
- **Temperature**: 250-320 K for atmospheric conditions
- **Humidity**: 0.0-1.0 (0-100% relative humidity)
- **Wind Speed**: 0-30 m/s for most applications
- **Wind Direction**: 0-360 degrees

#### Simulation Parameters
- **Time Step**: 0.0001-0.01 s for accuracy vs. performance
- **Max Time**: 1-100 s depending on scenario
- **Tolerance**: 1e-8-1e-4 for integration accuracy

### Best Practices

#### File Organization
1. **Descriptive Names**: Use clear, descriptive configuration file names
2. **Comments**: Add comments to complex configurations
3. **Version Control**: Track configuration changes in version control
4. **Backup**: Keep backup copies of working configurations

#### Parameter Validation
1. **Physical Realism**: Ensure parameters represent realistic physical conditions
2. **Unit Consistency**: Always use SI units (kg, m, s, K)
3. **Range Checking**: Validate parameters are within reasonable ranges
4. **Dependency Checking**: Ensure dependent parameters are consistent

#### Testing Strategy
1. **Start Simple**: Begin with basic configurations and add complexity gradually
2. **Compare Results**: Compare results between similar configurations
3. **Edge Cases**: Test with extreme parameter values
4. **Validation**: Validate results against known solutions when possible

## Creating New Configurations

### Template Configuration
Use this template as a starting point for new configurations:

```json
{
  "scenario": "drop",
  "object": {
    "type": "sphere",
    "mass": 0.5,
    "radius": 0.1,
    "spin_rate": 0.0,
    "material": {
      "density": 1000.0,
      "youngs_modulus": 1e9,
      "poisson_ratio": 0.3
    }
  },
  "initial_height": 100.0,
  "environment": {
    "gravity": 9.81,
    "temperature": 288.15,
    "humidity": 0.5,
    "pressure": 101325.0,
    "wind_speed": 0.0,
    "wind_direction": 0.0
  },
  "simulation": {
    "time_step": 0.001,
    "max_time": 30.0,
    "tolerance": 1e-6,
    "method": "adaptive",
    "adaptive": true
  },
  "output": {
    "format": ["csv", "json", "html", "png", "gif"],
    "directory": "./results",
    "filename": "simulation_results",
    "overwrite": false
  }
}
```

### Custom Scenarios
For custom scenarios, extend the configuration:

```json
{
  "scenario": "custom",
  "custom_parameters": {
    "parameter1": 1.0,
    "parameter2": 2.0
  },
  "object": {
    "type": "custom_shape",
    "custom_geometry": {
      "shape": "ellipsoid",
      "dimensions": [0.1, 0.1, 0.2]
    }
  }
}
```

## Troubleshooting

### Common Issues

#### Simulation Fails to Run
- **Check File Format**: Ensure JSON/YAML syntax is correct
- **Validate Parameters**: Check that all required parameters are present
- **File Permissions**: Ensure configuration file is readable

#### Unexpected Results
- **Parameter Values**: Verify parameter values are realistic
- **Units**: Check that all parameters use correct units
- **Physics Models**: Ensure appropriate physics models are enabled

#### Performance Issues
- **Time Step**: Increase time step for faster simulation
- **Max Time**: Reduce simulation time if not needed
- **Output Formats**: Generate only needed output formats

### Debugging Configurations
1. **Start with Examples**: Use working configurations as templates
2. **Incremental Changes**: Make small changes and test incrementally
3. **Validation**: Use configuration validation tools
4. **Logging**: Enable verbose logging for debugging

## Dependencies

- **SimLab Library**: Core simulation engine
- **JSON/YAML Parser**: For configuration file parsing
- **Validation Schema**: For configuration validation
- **Report Generator**: For HTML report generation