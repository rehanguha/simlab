# physimlab Source Code

This directory contains the main physimlab physics simulation library source code.

## Overview

physimlab is a comprehensive physics simulation framework designed for scientific research and engineering analysis. The library provides advanced physics models for aerodynamics, mechanics, and numerical integration with support for various output formats.

## Package Structure

```
src/physimlab/
├── __init__.py          # Package entry point and public API
├── cli.py              # Typer-based command-line interface
├── core.py             # Main simulation engine and API functions
├── config/             # Configuration handling and validation
├── objects/            # Physical object definitions
├── output/             # Output management and reporting
├── physics/            # Physics calculations and models
└── utils/              # Utilities and constants
```

## Key Components

### Core Module (`core.py`)
- **Main Simulation Engine**: `run_simulation()` function for executing simulations
- **Batch Processing**: `batch_simulation()` for parameter sweeps and multiple runs
- **Result Comparison**: `compare_results()` for analyzing different simulation outcomes
- **Configuration Management**: Integration with configuration system

### CLI Module (`cli.py`)
- **Command-Line Interface**: Rich, user-friendly CLI using Typer
- **Subcommands**: `run`, `batch`, `compare`, `list`, `info`, `version`, `init`
- **Output Options**: Support for various output formats and verbosity levels
- **Error Handling**: Comprehensive error reporting and validation

### Physics Module (`physics/`)
- **Aerodynamics**: Drag, lift, Magnus effect, air properties
- **Mechanics**: Gravity, terminal velocity, spin decay
- **Numerical Methods**: Adaptive integration, stability monitoring
- **Wind Effects**: Atmospheric modeling, turbulence, gust effects
- **Contact Physics**: Collision detection, Hertzian contact, friction models

### Configuration Module (`config/`)
- **File Loading**: JSON and YAML configuration support
- **Validation**: Schema validation and error reporting
- **Defaults**: Default configuration values and overrides

### Output Module (`output/`)
- **File Management**: Organized output file handling
- **Result Objects**: Structured result data with plotting capabilities
- **Multiple Formats**: CSV, JSON, HTML, PNG, GIF outputs

### Utilities Module (`utils/`)
- **Constants**: Physical constants and mathematical values
- **Helpers**: Formatting functions and utility operations

## Usage Examples

### Basic Simulation
```python
import physimlab

# Run simulation with configuration file
result = physimlab.run_simulation(config_path="config.json")

# Access results
summary = result['summary']
data = result['data']
print(f"Flight time: {summary['flight_time']:.3f} seconds")
```

### Advanced Usage
```python
# Batch simulation with parameter sweep
results = physimlab.batch_simulation(
    config_path="config.json",
    parameters=[
        {"name": "mass", "min": 0.1, "max": 1.0, "steps": 5},
        {"name": "radius", "min": 0.05, "max": 0.2, "steps": 3}
    ]
)

# Compare results
comparison = physimlab.compare_results("./result1", "./result2")
```

### Command Line
```bash
# Run simulation
physimlab run --config config.json

# Batch processing
physimlab batch --config config.json --param mass 0.1 0.5 5

# Compare results
physimlab compare ./result1 ./result2
```

## Dependencies

- **NumPy**: Numerical computations and array operations
- **SciPy**: Scientific computing and numerical integration
- **Pandas**: Data handling and CSV export
- **Matplotlib**: Static plotting and visualization
- **Typer**: Command-line interface framework
- **PyYAML**: YAML configuration file support

## Development

### Adding New Physics Models
1. Create new module in `physics/` directory
2. Implement physics functions following existing patterns
3. Add exports to `physics/__init__.py`
4. Update documentation and tests

### Adding New Output Formats
1. Extend `output/manager.py` with new format support
2. Update `output/result.py` for format-specific methods
3. Add configuration options if needed
4. Update CLI help text and documentation

### Testing
Run the test suite:
```bash
cd /home/rehanguha/Documents/GitHub/physimlab
pytest tests/
```

Run with coverage:
```bash
pytest --cov=physimlab --cov-report=html
```

## Architecture Notes

- **Modular Design**: Each physics domain is separated into its own module
- **Configuration-Driven**: All parameters come from configuration files
- **Extensible**: Easy to add new physics models, output formats, and scenarios
- **Performance**: Optimized for scientific computing with NumPy arrays
- **Validation**: Comprehensive input validation and error reporting

## Integration Points

- **Configuration System**: All modules integrate with the configuration loader
- **Output System**: Physics calculations feed into output generation
- **CLI Interface**: All functionality is accessible via command line
- **Testing Framework**: Comprehensive test coverage for all components

## Best Practices

1. **Follow PEP 8**: Adhere to Python coding standards
2. **Type Hints**: Use type annotations for better code documentation
3. **Documentation**: Document all public functions and classes
4. **Testing**: Write tests for all new functionality
5. **Performance**: Use vectorized operations with NumPy where possible
6. **Error Handling**: Provide clear error messages and graceful degradation