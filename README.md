# Ball Drop Simulation

A high-fidelity physics simulation for ball drop/launch scenarios with realistic aerodynamics, wind effects, and ground contact mechanics.

## Features

### Phase 1: Enhanced Physics
- **Multi-regime drag coefficient**: Stokes, Schiller-Naumann, Newton, and post-crisis regimes
- **Magnus effect**: Mehta correlation with aerodynamic spin decay torque
- **Air properties**: Humidity-corrected density and viscosity with Mach number effects
- **Hertzian contact model**: Velocity-dependent coefficient of restitution
- **Virtual mass effect**: Added mass for accelerating spheres in fluid

### Phase 2: Robustness & Numerical Methods
- **Input validation**: Physical bounds checking for all parameters
- **Adaptive timestep**: RK45 Dormand-Prince with error control
- **Stability checks**: NaN/Inf detection, energy monitoring, penetration resolution

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install numpy pandas matplotlib plotly numba
```

### Basic Usage

**Using default configuration:**
```bash
python ball_simulation.py
```

**Using custom configuration:**
```bash
python ball_simulation.py my_config.json
```

## Configuration File

Edit `config.json` to customize simulation parameters without modifying code:

```json
{
    "ball": {
        "mass": 10.0,
        "radius": 0.2,
        "initial_velocity": 10.0,
        "drop_angle_deg": 45.0,
        "spin_rps": 8.0
    },
    "surface": {
        "elasticity_base": 0.75,
        "friction_mu_s": 0.55,
        "wetness": 0.2
    },
    "wind": {
        "ref_speed": 2.5,
        "humidity_pct": 60.0
    }
}
```

### Parameter Sections

| Section | Description |
|---------|-------------|
| `ball` | Ball physical properties (mass, radius, velocity, spin) |
| `position` | Initial position coordinates (x0, y0, z0) |
| `surface` | Ground surface properties (elasticity, friction, wetness) |
| `wind` | Wind conditions (speed, direction, gusts, humidity) |
| `simulation` | Simulation settings (timestep, duration, physics options) |
| `output` | Output file paths and verbosity |

## Output Files

After running, the simulation generates:

| File | Description |
|------|-------------|
| `ball_drop_data_table.csv` | Raw simulation data (time series) |
| `ball_drop_2d_graph.png` | 2D trajectory plot |
| `ball_drop_report.html` | Interactive HTML report with charts |

## Project Structure

```
ball/
├── ball_simulation.py   # Main entry point
├── config.json          # Configuration file
├── config_loader.py     # Configuration loader
├── physics.py           # Physics constants & functions
├── models.py            # Data classes (Params, Surface, Wind)
├── simulation.py        # Core simulation engine
├── validation.py        # Input validation
├── reporting.py         # Report generation
└── docs/
    ├── MATHEMATICAL_DERIVATIONS.md
    └── REFERENCES.md
```

## Usage in Python

```python
from config_loader import load_config
from ball_simulation import run_simulation

# Load configuration
params, surface, wind, output = load_config("config.json")

# Run simulation
result = run_simulation(params, surface, wind)

# Access results
print(f"Max height: {result['statistics']['max_height']:.2f} m")
print(f"Flight time: {result['statistics']['flight_time']:.2f} s")
```

## References

See `docs/REFERENCES.md` for scientific references and `docs/MATHEMATICAL_DERIVATIONS.md` for detailed derivations of the physics models.

## License

MIT License