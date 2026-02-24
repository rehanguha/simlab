# SimLab - Physics Simulation Laboratory

[![PyPI version](https://badge.fury.io/py/simlab.svg)](https://badge.fury.io/py/simlab)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/pypi/pyversions/simlab.svg)](https://pypi.org/project/simlab/)
[![Downloads](https://pepy.tech/badge/simlab)](https://pepy.tech/project/simlab)

**SimLab** is a comprehensive physics simulation package for ball drop experiments with advanced aerodynamics, Magnus effect, and ground interaction physics.

## 🚀 Features

### 📊 Advanced Physics
- **Aerodynamics**: Drag force, Reynolds number, Mach number calculations
- **Magnus Effect**: Spin-induced lift forces for realistic ball behavior
- **Thermodynamics**: Temperature and humidity effects on air properties
- **Ground Physics**: Elastic collisions with configurable surface properties
- **Wind Effects**: Crosswind and turbulence simulation

### 🎯 Multiple Scenarios
- **Ball Drop**: Standard drop simulation with bounce physics
- **Wind Tunnel**: Aerodynamics testing with controlled airflow
- **Terminal Velocity**: Free fall with drag force analysis
- **Projectile Motion**: Trajectory simulation with air resistance

### 📈 Rich Output
- **CSV Data**: Full trajectory data with all physics parameters
- **Interactive HTML**: Plotly-powered reports with 3D visualization
- **Animated GIFs**: Real-time trajectory animations
- **High-Quality Plots**: Publication-ready static plots
- **JSON Summary**: Machine-readable results and configuration

### 🐍 Python Library
```python
import simlab

# Simple usage
result = simlab.run()
print(f"Flight time: {result.summary['flight_time']:.2f} s")

# Advanced usage
from simlab.scenarios import Drop
from simlab.objects import Sphere

ball = Sphere(mass=0.5, radius=0.1, spin_rate=8.0)
drop = Drop(object=ball, initial_height=100.0)
result = drop.run()

# Plotting
result.plot_height()
result.plot_trajectory_3d()
result.save("./output")
```

### 🖥️ Command Line Interface
```bash
# Basic usage
$ simlab run
$ simlab run --config config.yaml

# Advanced usage
$ simlab run --scenario drop --height 100 --mass 0.5
$ simlab batch --param mass 0.1 0.5 1.0
$ simlab compare result1 result2

# Information
$ simlab list
$ simlab info drop
$ simlab version
```

## 📦 Installation

### PyPI (Recommended)
```bash
pip install simlab
```

### Development Version
```bash
pip install git+https://github.com/rehanguha/SimLab.git
```

### From Source
```bash
git clone https://github.com/rehanguha/SimLab.git
cd SimLab
pip install -e .
```

## 🎮 Quick Start

### 1. Basic Simulation
```bash
# Run with default configuration
simlab run

# Run with custom configuration
simlab run --config my_config.json
```

### 2. Python API
```python
import simlab

# Run simulation with defaults
result = simlab.run()

# Access results
print(f"Flight time: {result.summary['flight_time']:.2f} seconds")
print(f"Max height: {result.summary['max_height']:.2f} meters")
print(f"Horizontal range: {result.summary['horizontal_range']:.2f} meters")

# Save outputs
result.save("./my_results")
```

### 3. Configuration File
Create a `config.json` file:
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
  }
}
```

## 📋 CLI Reference

### `simlab run`
Run a simulation with specified configuration.

```bash
simlab run [OPTIONS]
```

**Options:**
- `--config, -c`: Configuration file path (default: config.json)
- `--output, -o`: Output directory (auto-generated if not specified)
- `--quiet, -q`: Minimal output
- `--verbose, -v`: Verbose output
- `--scenario, -s`: Scenario type
- `--height, -h`: Initial height (m)
- `--mass, -m`: Mass (kg)
- `--radius, -r`: Radius (m)
- `--spin`: Spin rate (rev/s)

### `simlab batch`
Run batch simulations with parameter sweep.

```bash
simlab batch --config CONFIG --param PARAM [PARAM ...]
```

**Parameters format:** `name min max steps`
Example: `mass 0.1 0.5 5` (5 values from 0.1 to 0.5)

### `simlab compare`
Compare two simulation results.

```bash
simlab compare RESULT1 RESULT2
```

### `simlab list`
List available scenarios.

### `simlab info`
Show information about a scenario.

```bash
simlab info [SCENARIO]
```

### `simlab version`
Show version information.

### `simlab init`
Initialize a new SimLab project.

```bash
simlab init NAME --output DIR --scenario SCENARIO
```

## 🔬 Physics Models

### Aerodynamics
- **Air Density**: Ideal gas law with humidity effects
- **Viscosity**: Sutherland's formula for temperature dependence
- **Speed of Sound**: Temperature-dependent calculation
- **Reynolds Number**: Flow regime characterization
- **Drag Coefficient**: Reynolds number-dependent model
- **Magnus Force**: Spin-induced lift calculation

### Mechanics
- **Gravity**: Altitude-dependent gravitational acceleration
- **Terminal Velocity**: Drag vs. gravity equilibrium
- **Spin Decay**: Air resistance effects on rotation

### Environment
- **Temperature Effects**: On air density, viscosity, and speed of sound
- **Humidity Effects**: On air density calculations
- **Wind Effects**: Crosswind and relative velocity calculations

## 📊 Output Formats

### CSV Data
Full trajectory data with all calculated physics parameters:
```csv
Time,X,Y,Z,Vx,Vy,Vz,Speed,OmegaZ,AirDensity,Reynolds,Cd,Mach
0.000,0.035,0.000,100.035,7.071,0.001,7.022,9.965,50.206,1.209,234928,0.160,0.026
...
```

### JSON Summary
Machine-readable summary and configuration:
```json
{
  "summary": {
    "flight_time": 19.995,
    "max_height": 102.56,
    "horizontal_range": 45.77,
    "max_velocity": 42.90,
    "ground_contacts": 6,
    "max_mach": 0.126,
    "is_stable": true,
    "energy_conserved": true
  },
  "config": { ... },
  "timestamp": "2026-02-24T16:51:32"
}
```

### HTML Report
Interactive Plotly report with:
- 2D and 3D trajectory plots
- Velocity and height over time
- Physics parameter visualization
- Summary statistics

### Animated GIF
Real-time trajectory animation with:
- Ball position with trail
- Velocity vector visualization
- Ground contact highlights
- Real-time statistics overlay

## 🏗️ Package Structure

```
simlab/
├── cli.py              # Typer CLI interface
├── core.py             # Main simulation engine
├── physics/            # Physics calculations
│   ├── aerodynamics.py # Drag, lift, air properties
│   └── mechanics.py    # Gravity, motion, collisions
├── config/             # Configuration handling
│   └── loader.py       # JSON/YAML loading and validation
├── output/             # Output management
│   ├── manager.py      # File saving and organization
│   └── result.py       # Result object with plotting
├── utils/              # Utilities and constants
│   ├── constants.py    # Physical constants
│   └── helpers.py      # Formatting functions
└── __init__.py         # Package entry point
```

## 🧪 Testing

Run the test suite:
```bash
pip install simlab[dev]
pytest
```

Run with coverage:
```bash
pytest --cov=simlab --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

**SimLab** is licensed under the [Apache License 2.0](LICENSE).

```
Copyright 2026 Rehan Guha

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 🙏 Acknowledgments

- **NumPy**: Numerical computations
- **Pandas**: Data handling and CSV export
- **Matplotlib**: Static plotting
- **Plotly**: Interactive visualization
- **Typer**: CLI interface
- **Rich**: Beautiful terminal output

## 📞 Support

For questions, bug reports, or feature requests:

- **GitHub Issues**: [https://github.com/rehanguha/SimLab/issues](https://github.com/rehanguha/SimLab/issues)
- **Documentation**: [GitHub README](https://github.com/rehanguha/SimLab/blob/main/README.md)

## 🏷️ Keywords

physics simulation, aerodynamics, ball drop, Magnus effect, terminal velocity, projectile motion, scientific computing, Python package, CLI tool, data visualization