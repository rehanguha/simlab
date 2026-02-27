# Configuration Guide

This guide provides comprehensive information about configuring SimLab simulations, including all available parameters, their effects, and best practices for different simulation scenarios.

## Table of Contents

1. [Configuration File Structure](#configuration-file-structure)
2. [Core Configuration Sections](#core-configuration-sections)
3. [Physics Configuration](#physics-configuration)
4. [Advanced Configuration](#advanced-configuration)
5. [Scenario-Specific Configurations](#scenario-specific-configurations)
6. [Best Practices](#best-practices)
7. [Configuration Examples](#configuration-examples)

---

## Configuration File Structure

SimLab uses JSON or YAML configuration files to define simulation parameters. The configuration file structure is hierarchical and organized by functional areas.

### Basic Structure
```json
{
  "scenario": "drop",
  "ball": {
    "mass": 0.5,
    "radius": 0.1,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 100.0
  },
  "wind": {
    "humidity_pct": 50.0,
    "ref_speed": 2.0,
    "ref_height": 10.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 30.0
  }
}
```

### Required Sections
- **scenario**: Defines the simulation type
- **ball**: Object properties (mass, radius, spin)
- **position**: Initial position coordinates
- **simulation**: Core simulation parameters

### Optional Sections
- **wind**: Atmospheric and wind conditions
- **surface**: Ground surface properties
- **output**: Output configuration

---

## Core Configuration Sections

### Scenario Configuration
Defines the type of simulation to run.

**Available Scenarios:**
- `"drop"`: Standard ball drop with bounce physics
- `"wind-tunnel"`: Aerodynamics testing with controlled airflow
- `"terminal-velocity"`: Free fall analysis with drag force measurement
- `"projectile"`: Projectile motion with aerodynamic effects
- `"spin"`: Rotational dynamics analysis

**Example:**
```json
{
  "scenario": "drop"
}
```

### Ball Configuration
Defines the physical properties of the simulated object.

**Parameters:**
- `mass` (float): Object mass in kilograms (kg)
- `radius` (float): Object radius in meters (m)
- `spin_rps` (float): Initial spin rate in revolutions per second (rps)
- `spin_axis` (array): Spin axis direction [x, y, z] (optional, defaults to [0,0,1])

**Example:**
```json
{
  "ball": {
    "mass": 0.5,
    "radius": 0.1,
    "spin_rps": 10.0,
    "spin_axis": [0, 0, 1]
  }
}
```

**Typical Values:**
- **Tennis ball**: mass=0.057, radius=0.033
- **Baseball**: mass=0.145, radius=0.037
- **Basketball**: mass=0.624, radius=0.12
- **Golf ball**: mass=0.046, radius=0.021

### Position Configuration
Defines the initial position of the object.

**Parameters:**
- `x0` (float): Initial x-coordinate in meters (m)
- `y0` (float): Initial y-coordinate in meters (m)
- `z0` (float): Initial z-coordinate (height) in meters (m)

**Example:**
```json
{
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 100.0
  }
}
```

### Simulation Configuration
Core simulation parameters that control the numerical integration and physics behavior.

**Parameters:**
- `g` (float): Gravitational acceleration (m/s²), default: 9.81
- `dt` (float): Time step for numerical integration (s), default: 0.001
- `t_max` (float): Maximum simulation time (s), default: 30.0
- `rtol` (float): Relative tolerance for adaptive integration, default: 1e-6
- `atol` (float): Absolute tolerance for adaptive integration, default: 1e-8
- `min_dt` (float): Minimum adaptive timestep (s), default: 1e-5
- `max_dt` (float): Maximum adaptive timestep (s), default: 0.05

**Example:**
```json
{
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 30.0,
    "rtol": 1e-6,
    "atol": 1e-8
  }
}
```

---

## Physics Configuration

### Wind Configuration
Atmospheric and wind conditions that affect aerodynamic forces.

**Parameters:**
- `humidity_pct` (float): Relative humidity percentage (0-100), default: 50.0
- `ref_speed` (float): Reference wind speed at ref_height (m/s), default: 2.0
- `ref_height` (float): Reference height for wind speed (m), default: 10.0
- `shear_alpha` (float): Power law exponent for wind profile (0.12-0.16), default: 0.15
- `direction_deg` (float): Wind direction in degrees (0-360), default: 0.0
- `gust_tau` (float): Gust correlation time constant (s), default: 1.5
- `gust_sigma` (float): Gust intensity standard deviation (m/s), default: 0.5

**Example:**
```json
{
  "wind": {
    "humidity_pct": 50.0,
    "ref_speed": 10.0,
    "ref_height": 10.0,
    "shear_alpha": 0.14,
    "direction_deg": 90.0,
    "gust_tau": 2.0,
    "gust_sigma": 1.0
  }
}
```

**Wind Profile Formula:**
`w(z) = w_ref * (z/z_ref)^α`

### Surface Configuration
Ground surface properties that affect collision behavior.

**Parameters:**
- `elasticity_base` (float): Base coefficient of restitution (0-1), default: 0.7
- `elasticity_drop` (float): Velocity-dependent elasticity drop rate, default: 0.02
- `friction_mu_s` (float): Static friction coefficient (0-2), default: 0.5
- `friction_mu_k` (float): Kinetic friction coefficient (0-2), default: 0.3
- `dampness` (float): Surface dampness effect (0-1), default: 0.0
- `wetness` (float): Surface wetness effect (0-1), default: 0.0
- `base_height` (float): Ground surface height (m), default: 0.0
- `slope_x` (float): Surface slope in x-direction, default: 0.0
- `slope_y` (float): Surface slope in y-direction, default: 0.0
- `surface_roughness` (float): Surface roughness amplitude (m), default: 0.0
- `roughness_wavelength` (float): Surface roughness wavelength (m), default: 10.0

**Example:**
```json
{
  "surface": {
    "elasticity_base": 0.8,
    "friction_mu_s": 0.6,
    "friction_mu_k": 0.4,
    "surface_roughness": 0.002,
    "base_height": 0.0
  }
}
```

### Advanced Physics Configuration
Fine-grained control over physics models and numerical methods.

**Parameters:**
- `buoyancy` (boolean): Enable buoyancy forces, default: true
- `use_virtual_mass` (boolean): Enable virtual mass effects, default: true
- `use_multi_regime_cd` (boolean): Use advanced drag correlations, default: true
- `use_hertzian_contact` (boolean): Use Hertzian contact model, default: true
- `adaptive_timestep` (boolean): Use adaptive integration, default: false
- `c_spin_decay` (float): Spin decay coefficient, default: 0.05
- `c_spin_aero` (float): Aerodynamic spin effects coefficient, default: 0.02
- `compressibility_correction` (boolean): Enable compressibility effects, default: false
- `youngs_modulus` (float): Material Young's modulus (Pa), default: 1e7
- `poisson_ratio` (float): Material Poisson's ratio, default: 0.5

**Example:**
```json
{
  "simulation": {
    "buoyancy": true,
    "use_virtual_mass": true,
    "use_multi_regime_cd": true,
    "adaptive_timestep": true,
    "c_spin_decay": 0.05,
    "c_spin_aero": 0.02
  }
}
```

---

## Advanced Configuration

### Output Configuration
Controls the output files and their format.

**Parameters:**
- `run_name` (string): Name for the simulation run
- `output_dir` (string): Output directory path
- `csv_file` (string): CSV data file name
- `plot_file` (string): Static plot file name
- `html_file` (string): HTML report file name
- `animation_file` (string): Animation file name

**Example:**
```json
{
  "output": {
    "run_name": "high_wind_test",
    "output_dir": "outputs/high_wind",
    "csv_file": "high_wind_data.csv",
    "plot_file": "high_wind_plot.png",
    "html_file": "high_wind_report.html"
  }
}
```

### Test Expectations Configuration
Defines expected results for validation and testing.

**Parameters:**
- `description` (string): Description of the test scenario
- `expected_horizontal_range` (string): Expected horizontal range
- `expected_flight_time` (string): Expected flight time
- `expected_behavior` (string): Expected physical behavior
- `wind_direction` (string): Expected wind direction effects

**Example:**
```json
{
  "test_expectations": {
    "description": "High wind test - strong crosswind affects ball trajectory",
    "expected_horizontal_range": "10-20 meters",
    "expected_flight_time": "Slightly longer than vacuum due to lift/drag",
    "expected_behavior": "Curved trajectory with horizontal drift",
    "wind_direction": "90 degrees (positive x-direction)"
  }
}
```

---

## Scenario-Specific Configurations

### Ball Drop Scenario
Standard drop simulation with bounce physics.

**Recommended Configuration:**
```json
{
  "scenario": "drop",
  "ball": {
    "mass": 0.5,
    "radius": 0.1,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 100.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 30.0,
    "use_hertzian_contact": true,
    "adaptive_timestep": true
  }
}
```

### Wind Tunnel Scenario
Aerodynamics testing with controlled airflow.

**Recommended Configuration:**
```json
{
  "scenario": "wind-tunnel",
  "ball": {
    "mass": 0.1,
    "radius": 0.05,
    "spin_rps": 20.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 0.0
  },
  "wind": {
    "ref_speed": 20.0,
    "ref_height": 1.0,
    "gust_sigma": 0.0
  },
  "simulation": {
    "g": 0.0,
    "dt": 0.0001,
    "t_max": 5.0,
    "use_multi_regime_cd": true,
    "adaptive_timestep": true
  }
}
```

### Terminal Velocity Scenario
Free fall analysis with drag force measurement.

**Recommended Configuration:**
```json
{
  "scenario": "terminal-velocity",
  "ball": {
    "mass": 1.0,
    "radius": 0.05,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 500.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 60.0,
    "buoyancy": false,
    "use_virtual_mass": false,
    "stop_speed_threshold": 0.01
  }
}
```

### Projectile Motion Scenario
Projectile motion with aerodynamic effects.

**Recommended Configuration:**
```json
{
  "scenario": "projectile",
  "ball": {
    "mass": 0.2,
    "radius": 0.04,
    "spin_rps": 5.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 2.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 10.0,
    "use_multi_regime_cd": true,
    "adaptive_timestep": true
  }
}
```

### Spin Analysis Scenario
Rotational dynamics analysis.

**Recommended Configuration:**
```json
{
  "scenario": "spin",
  "ball": {
    "mass": 0.05,
    "radius": 0.03,
    "spin_rps": 50.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 10.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.0001,
    "t_max": 2.0,
    "c_spin_decay": 0.1,
    "c_spin_aero": 0.05,
    "use_hertzian_contact": false
  }
}
```

---

## Best Practices

### Configuration File Organization
1. **Use meaningful names**: Choose descriptive names for configuration files
2. **Group related parameters**: Keep related parameters together
3. **Add comments**: Use comments to explain non-obvious parameter choices
4. **Version control**: Keep configuration files in version control

### Parameter Selection
1. **Start simple**: Begin with basic configurations and add complexity gradually
2. **Use realistic values**: Base parameters on real-world measurements when possible
3. **Consider units**: Always use SI units (kg, m, s) unless otherwise specified
4. **Test sensitivity**: Test how results change with parameter variations

### Performance Optimization
1. **Adaptive timesteps**: Use adaptive integration for better performance
2. **Appropriate time steps**: Choose dt based on the fastest physical process
3. **Limit simulation time**: Set t_max to the minimum necessary duration
4. **Disable unused features**: Turn off physics features you don't need

### Validation and Testing
1. **Compare with known results**: Validate against analytical solutions when available
2. **Test convergence**: Verify results converge with smaller timesteps
3. **Check conservation**: Monitor energy and momentum conservation
4. **Use test expectations**: Define expected results for automated testing

---

## Configuration Examples

### Basic Ball Drop
```json
{
  "scenario": "drop",
  "description": "Basic ball drop simulation",
  "ball": {
    "mass": 0.5,
    "radius": 0.1,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 100.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 30.0
  },
  "output": {
    "run_name": "basic_drop",
    "output_dir": "outputs/basic_drop"
  }
}
```

### High Wind Conditions
```json
{
  "scenario": "drop",
  "description": "Ball drop with strong crosswind",
  "ball": {
    "mass": 0.4,
    "radius": 0.12,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 20.0
  },
  "wind": {
    "humidity_pct": 50.0,
    "ref_speed": 15.0,
    "ref_height": 10.0,
    "shear_alpha": 0.14,
    "direction_deg": 90.0,
    "gust_tau": 2.0,
    "gust_sigma": 2.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.002,
    "t_max": 8.0,
    "adaptive_timestep": true,
    "buoyancy": true,
    "use_virtual_mass": true,
    "use_multi_regime_cd": true
  },
  "output": {
    "run_name": "high_wind_test",
    "output_dir": "outputs/high_wind"
  },
  "test_expectations": {
    "description": "Ball should be significantly displaced horizontally by wind",
    "expected_horizontal_range": "10-20 meters",
    "expected_flight_time": "Slightly longer than vacuum due to lift/drag",
    "expected_behavior": "Curved trajectory with horizontal drift"
  }
}
```

### Terminal Velocity Analysis
```json
{
  "scenario": "terminal-velocity",
  "description": "Terminal velocity measurement",
  "ball": {
    "mass": 0.1,
    "radius": 0.025,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 200.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 30.0,
    "buoyancy": false,
    "use_virtual_mass": false,
    "use_multi_regime_cd": true,
    "stop_speed_threshold": 0.01,
    "stop_angular_threshold": 0.5
  },
  "output": {
    "run_name": "terminal_velocity",
    "output_dir": "outputs/terminal_velocity"
  },
  "test_expectations": {
    "description": "Object should reach terminal velocity and maintain constant speed",
    "expected_behavior": "Velocity should asymptotically approach terminal velocity"
  }
}
```

### Spin Effect Analysis
```json
{
  "scenario": "spin",
  "description": "Magnus effect and spin decay analysis",
  "ball": {
    "mass": 0.05,
    "radius": 0.03,
    "spin_rps": 100.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 5.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.0001,
    "t_max": 1.0,
    "c_spin_decay": 0.2,
    "c_spin_aero": 0.1,
    "use_hertzian_contact": false,
    "adaptive_timestep": true
  },
  "output": {
    "run_name": "spin_analysis",
    "output_dir": "outputs/spin_analysis"
  }
}
```

### Vacuum Drop (No Aerodynamics)
```json
{
  "scenario": "drop",
  "description": "Vacuum drop - no aerodynamic effects",
  "ball": {
    "mass": 0.5,
    "radius": 0.1,
    "spin_rps": 0.0
  },
  "position": {
    "x0": 0.0,
    "y0": 0.0,
    "z0": 100.0
  },
  "simulation": {
    "g": 9.81,
    "dt": 0.001,
    "t_max": 5.0,
    "buoyancy": false,
    "use_virtual_mass": false,
    "use_multi_regime_cd": false,
    "c_spin_decay": 0.0,
    "c_spin_aero": 0.0
  },
  "output": {
    "run_name": "vacuum_drop",
    "output_dir": "outputs/vacuum_drop"
  },
  "test_expectations": {
    "description": "Pure gravitational motion without air resistance",
    "expected_flight_time": "4.52 seconds (analytical: sqrt(2h/g))",
    "expected_max_velocity": "44.3 m/s (analytical: sqrt(2gh))"
  }
}
```

---

## Troubleshooting Common Issues

### Simulation Runs Too Slow
**Solutions:**
- Increase time step (`dt`)
- Reduce maximum simulation time (`t_max`)
- Disable adaptive integration if not needed
- Turn off unused physics features

### Simulation Results Unstable
**Solutions:**
- Decrease time step (`dt`)
- Enable adaptive integration
- Check for unrealistic parameter values
- Verify energy conservation

### Unexpected Physics Behavior
**Solutions:**
- Review physics configuration parameters
- Check units and parameter ranges
- Compare with known analytical solutions
- Enable detailed output for debugging

### Configuration File Errors
**Solutions:**
- Validate JSON/YAML syntax
- Check required parameters are present
- Verify parameter types and ranges
- Use configuration validation tools

This comprehensive configuration guide should help you create effective and accurate SimLab simulations for a wide variety of scenarios. Always test your configurations with simple cases before moving to complex simulations.