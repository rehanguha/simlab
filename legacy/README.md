# Legacy Code

This directory contains legacy code and previous implementations that are no longer actively maintained but may be useful for reference or historical purposes.

## Overview

The legacy directory preserves older versions of physimlab components, experimental implementations, and code that has been superseded by newer, more efficient implementations. This code is provided for reference, comparison, and potential future use.

## Legacy Files

### Core Legacy Files

#### `ball_simulation.py`
- **Purpose**: Original ball simulation implementation
- **Status**: Superseded by current physics engine
- **Features**: Basic physics calculations, simple integration
- **Use Case**: Reference for original implementation approach
- **Dependencies**: Basic Python libraries

#### `simulation.py`
- **Purpose**: Legacy simulation engine
- **Status**: Replaced by modular simulation architecture
- **Features**: Monolithic simulation approach
- **Use Case**: Understanding evolution of simulation design
- **Dependencies**: NumPy, basic physics calculations

#### `physics.py`
- **Purpose**: Original physics calculations
- **Status**: Superseded by modular physics system
- **Features**: Basic aerodynamics, mechanics, integration
- **Use Case**: Reference for physics model development
- **Dependencies**: NumPy, mathematical functions

### Configuration and Models

#### `config_loader.py`
- **Purpose**: Legacy configuration loading system
- **Status**: Replaced by enhanced configuration system
- **Features**: Basic JSON configuration loading
- **Use Case**: Reference for configuration evolution
- **Dependencies**: JSON, file handling

#### `models.py`
- **Purpose**: Original physics model definitions
- **Status**: Superseded by current model system
- **Features**: Basic physics model classes
- **Use Case**: Understanding model architecture evolution
- **Dependencies**: Physics calculations

### Output and Reporting

#### `reporting.py`
- **Purpose**: Legacy reporting and output generation
- **Status**: Replaced by comprehensive output system
- **Features**: Basic CSV output, simple plotting
- **Use Case**: Reference for output system development
- **Dependencies**: Matplotlib, Pandas

#### `validation.py`
- **Purpose**: Original validation and testing framework
- **Status**: Superseded by pytest-based testing
- **Features**: Basic validation functions
- **Use Case**: Reference for testing approach evolution
- **Dependencies**: Testing utilities

### Utility and Test Files

#### `test_imports.py`
- **Purpose**: Import testing for legacy modules
- **Status**: Development/testing utility
- **Features**: Import validation, dependency checking
- **Use Case**: Ensuring legacy code imports correctly
- **Dependencies**: Legacy modules

#### `sample_config.json`
- **Purpose**: Sample configuration for legacy system
- **Status**: Compatible with legacy config_loader.py
- **Features**: Basic configuration example
- **Use Case**: Testing legacy configuration loading
- **Dependencies**: None (configuration file)

## Migration Notes

### From Legacy to Current System

#### Physics Calculations
**Legacy Approach:**
```python
# ball_simulation.py - monolithic physics
def simulate_ball_drop(mass, radius, height):
    # Combined physics calculations
    pass
```

**Current Approach:**
```python
# Modular physics system
from physimlab.physics import calculate_density, calculate_drag_coefficient
from physimlab.physics.numerical import AdaptiveRK45
```

#### Configuration System
**Legacy Approach:**
```python
# config_loader.py - basic JSON loading
config = json.load(open('config.json'))
```

**Current Approach:**
```python
# Enhanced configuration system
from physimlab.config import load_config, validate_config
config = load_config('config.json', validate=True)
```

#### Output Generation
**Legacy Approach:**
```python
# reporting.py - basic output
def generate_report(data):
    # Simple CSV and plot generation
    pass
```

**Current Approach:**
```python
# Comprehensive output system
from physimlab.output import save_simulation_results
output_files = save_simulation_results(data, summary, config, formats=['csv', 'json', 'html'])
```

## Using Legacy Code

### Reference and Comparison
Legacy code is primarily useful for:

1. **Understanding Evolution**: See how the system has developed
2. **Algorithm Comparison**: Compare old vs. new implementations
3. **Debugging Reference**: Use as reference when debugging current system
4. **Educational Purposes**: Learn from simpler, more straightforward implementations

### Running Legacy Code
```python
# Import legacy modules (if needed for reference)
import sys
sys.path.append('legacy')

# Example usage (for reference only)
from legacy.ball_simulation import simulate_ball_drop
from legacy.config_loader import load_legacy_config
```

### Compatibility Notes
- **Python Version**: Legacy code may require older Python versions
- **Dependencies**: May use older versions of libraries
- **API Changes**: Function signatures may differ from current system
- **Performance**: Legacy implementations may be less optimized

## Code Quality and Maintenance

### Current Status
- **No Active Development**: Legacy code is not actively maintained
- **No Bug Fixes**: Issues in legacy code will not be fixed
- **No Security Updates**: Security vulnerabilities will not be addressed
- **Reference Only**: Use only for reference and comparison

### Recommendations
1. **Use Current System**: Always prefer the current physimlab implementation
2. **Reference Only**: Use legacy code only for understanding or comparison
3. **No Production Use**: Do not use legacy code in production systems
4. **Documentation**: Refer to current documentation for up-to-date information

## Historical Context

### Development Timeline
- **Phase 1**: Initial implementation (`ball_simulation.py`, `simulation.py`)
- **Phase 2**: Modular physics (`physics.py`, `models.py`)
- **Phase 3**: Configuration system (`config_loader.py`)
- **Phase 4**: Output and reporting (`reporting.py`, `validation.py`)
- **Phase 5**: Current system (modular, comprehensive, tested)

### Design Evolution
1. **Monolithic to Modular**: From single files to organized modules
2. **Simple to Complex**: Basic physics to advanced models
3. **Manual to Automated**: Manual configuration to validation systems
4. **Basic to Comprehensive**: Simple output to multiple formats

## Future Considerations

### Potential Uses
- **Educational Examples**: Teaching physics simulation concepts
- **Algorithm Research**: Comparing different implementation approaches
- **Historical Reference**: Understanding project evolution
- **Backup Implementations**: Fallback implementations if needed

### Deprecation Timeline
- **Phase 1**: Legacy code marked as deprecated
- **Phase 2**: Documentation updated to reference current system
- **Phase 3**: Legacy code preserved for reference only
- **Phase 4**: Potential removal in major version updates (with notice)

## Dependencies

### Legacy Dependencies
- **Python 3.7+**: Minimum Python version for legacy code
- **NumPy**: For mathematical calculations
- **Matplotlib**: For basic plotting (legacy reporting)
- **Pandas**: For data handling (legacy reporting)
- **JSON**: For configuration loading

### Compatibility Notes
- **Library Versions**: May require specific older versions
- **API Changes**: Some library APIs may have changed
- **Performance**: May not be optimized for current hardware

## Contributing to Legacy Code

### General Policy
- **No New Features**: Legacy code will not receive new features
- **No Bug Fixes**: Bugs in legacy code will not be fixed
- **Documentation Only**: Only documentation updates may be accepted
- **Reference Preservation**: Changes only to preserve reference value

### When to Update Legacy Code
1. **Documentation**: Updating comments or docstrings
2. **Compatibility**: Minor updates for Python version compatibility
3. **Security**: Critical security fixes only
4. **Reference Value**: Improvements that enhance reference value

## Getting Help

### For Current System
- **Documentation**: See `docs/` directory for current documentation
- **Issues**: Report issues on GitHub for current system
- **Support**: Use current system support channels

### For Legacy Code
- **Reference Only**: Use legacy code for reference and comparison
- **No Support**: Legacy code is not supported
- **Community**: May be discussed in community forums for educational purposes

## Conclusion

The legacy directory preserves the history and evolution of physimlab. While this code is no longer actively maintained, it provides valuable insights into the development process and can serve as a reference for understanding the current system's design decisions and improvements.