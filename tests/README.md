# Test Suite

This directory contains the comprehensive test suite for physimlab, ensuring the reliability and accuracy of the physics simulation library.

## Overview

The test suite is organized to validate all aspects of the physimlab library including physics calculations, numerical methods, configuration handling, output generation, and integration scenarios. Tests follow pytest conventions and include both unit tests and integration tests.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # pytest configuration and fixtures
├── sample_config.json             # Sample configuration for testing
├── test_config.json               # Configuration validation test data
├── test_config_loader.py          # Configuration loading and validation tests
├── test_integration.py            # Integration tests for complete workflows
├── test_mathematical_accuracy.py  # Mathematical precision and accuracy tests
├── test_models.py                 # Physics model tests
├── test_physics.py                # Basic physics calculation tests
├── test_physics_detailed.py       # Detailed physics domain tests
├── test_physics_complete.py       # Comprehensive physics system tests
├── test_reporting.py              # Output and reporting tests
├── test_simulation.py             # Main simulation engine tests
├── test_validation.py             # Physics validation and consistency tests
└── __pycache__/                   # Compiled test modules
```

## Test Categories

### Unit Tests
Test individual components and functions in isolation:

- **Physics Calculations**: Test individual physics functions
- **Configuration Loading**: Test configuration parsing and validation
- **Utility Functions**: Test helper functions and constants
- **Output Generation**: Test individual output format generators

### Integration Tests
Test the interaction between multiple components:

- **End-to-End Simulations**: Complete simulation workflows
- **Configuration Integration**: Configuration system with simulation engine
- **Output Pipeline**: Data flow from simulation to output files
- **Error Handling**: Error propagation and recovery

### Mathematical Accuracy Tests
Validate numerical precision and mathematical correctness:

- **Precision Tests**: Floating-point precision validation
- **Convergence Tests**: Numerical method convergence
- **Edge Cases**: Boundary condition handling
- **Performance Tests**: Computational efficiency validation

### Physics Validation Tests
Ensure physical correctness and consistency:

- **Conservation Laws**: Energy and momentum conservation
- **Physical Limits**: Realistic physical behavior
- **Unit Consistency**: Proper unit handling
- **Model Validation**: Physics model accuracy

## Test Configuration

### pytest Configuration
The test suite uses pytest with the following configuration:

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-config --strict-markers
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

### Test Fixtures
Common test fixtures are defined in `conftest.py`:

```python
import pytest
import numpy as np
from physimlab.config import load_config

@pytest.fixture
def sample_config():
    """Load sample configuration for testing"""
    return load_config("tests/sample_config.json")

@pytest.fixture
def physics_parameters():
    """Common physics parameters for testing"""
    return {
        'mass': 0.5,
        'radius': 0.1,
        'spin_rate': 8.0,
        'temperature': 288.15,
        'humidity': 0.5
    }

@pytest.fixture
def numerical_data():
    """Sample numerical data for testing"""
    return np.linspace(0, 10, 1000)
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_physics.py

# Run specific test function
pytest tests/test_physics.py::test_calculate_density
```

### Test Coverage
```bash
# Run tests with coverage
pytest --cov=physimlab --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/ --benchmark-only

# Run with performance profiling
pytest tests/ --profile-svg
```

### Mathematical Accuracy Testing
```bash
# Run mathematical precision tests
pytest tests/test_mathematical_accuracy.py -v

# Run with high precision validation
pytest tests/test_mathematical_accuracy.py --precision=1e-12
```

## Test Examples

### Physics Calculation Test
```python
import pytest
import numpy as np
from physimlab.physics import calculate_density, calculate_drag_coefficient

def test_calculate_density():
    """Test air density calculation"""
    # Standard conditions
    density = calculate_density(temperature=288.15, humidity=0.0)
    assert abs(density - 1.225) < 1e-6
    
    # High altitude
    density_high = calculate_density(temperature=250.0, humidity=0.0)
    assert density_high < density

def test_drag_coefficient_reynolds_dependency():
    """Test drag coefficient variation with Reynolds number"""
    reynolds_values = [1e3, 1e4, 1e5, 1e6]
    drag_coefficients = [calculate_drag_coefficient(re) for re in reynolds_values]
    
    # Drag coefficient should decrease with Reynolds number in certain ranges
    assert drag_coefficients[0] > drag_coefficients[-1]
```

### Configuration Test
```python
import pytest
from physimlab.config import load_config, validate_config

def test_config_loading():
    """Test configuration file loading"""
    config = load_config("tests/sample_config.json")
    
    assert 'scenario' in config
    assert 'object' in config
    assert 'environment' in config
    assert 'simulation' in config

def test_config_validation():
    """Test configuration validation"""
    config = {
        "scenario": "drop",
        "object": {"mass": 0.5, "radius": 0.1},
        "initial_height": 100
    }
    
    is_valid, errors = validate_config(config)
    assert is_valid
    assert len(errors) == 0
```

### Integration Test
```python
import pytest
from physimlab import run_simulation

def test_complete_simulation_workflow(sample_config):
    """Test complete simulation workflow"""
    result = run_simulation(config_path="tests/sample_config.json")
    
    # Check result structure
    assert 'summary' in result
    assert 'data' in result
    assert 'output_files' in result
    
    # Check summary values
    summary = result['summary']
    assert summary['flight_time'] > 0
    assert summary['max_height'] > 0
    assert summary['horizontal_range'] >= 0
    
    # Check data structure
    data = result['data']
    assert len(data) > 0
    assert 'Time' in data.columns
    assert 'X' in data.columns
    assert 'Y' in data.columns
```

## Test Data

### Sample Configuration Files
- **sample_config.json**: Basic configuration for unit tests
- **test_config.json**: Configuration with various parameter combinations
- **edge_case_config.json**: Configuration for edge case testing

### Test Data Sets
- **physics_test_data.csv**: Reference data for physics calculations
- **integration_test_data.json**: Expected results for integration tests
- **performance_benchmark_data.json**: Performance test parameters

## Continuous Integration

### GitHub Actions Integration
Tests are automatically run on every commit and pull request:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest
    - name: Run coverage
      run: pytest --cov=physimlab --cov-report=xml
```

### Test Requirements
```txt
# requirements-test.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-benchmark>=4.0.0
pytest-mock>=3.0.0
hypothesis>=6.0.0
```

## Test Best Practices

### Test Organization
1. **Clear Naming**: Use descriptive test function names
2. **Single Responsibility**: Each test should test one specific behavior
3. **Isolation**: Tests should not depend on each other
4. **Setup/Teardown**: Use fixtures for common setup and cleanup

### Test Quality
1. **Edge Cases**: Test boundary conditions and edge cases
2. **Error Conditions**: Test error handling and validation
3. **Performance**: Include performance regression tests
4. **Documentation**: Document complex test scenarios

### Mathematical Testing
1. **Precision**: Use appropriate tolerance for floating-point comparisons
2. **Reference Data**: Compare against known reference solutions
3. **Convergence**: Test numerical method convergence
4. **Consistency**: Verify mathematical relationships and constraints

### Physics Testing
1. **Unit Tests**: Test individual physics functions
2. **Integration Tests**: Test physics system integration
3. **Validation Tests**: Verify physical correctness
4. **Regression Tests**: Prevent physics calculation regressions

## Debugging Tests

### Running Specific Tests
```bash
# Run single test with detailed output
pytest tests/test_physics.py::test_calculate_density -v -s

# Run tests in a specific class
pytest tests/test_physics.py::PhysicsTests -v

# Run tests matching pattern
pytest -k "drag" -v
```

### Debug Mode
```bash
# Run with Python debugger
pytest --pdb tests/test_physics.py

# Run with traceback for all failures
pytest --tb=long tests/test_physics.py
```

### Performance Debugging
```bash
# Profile test execution
pytest --profile tests/test_integration.py

# Memory profiling
pytest --memray tests/test_physics.py
```

## Test Maintenance

### Regular Updates
1. **Review Test Coverage**: Ensure new features have adequate test coverage
2. **Update Reference Data**: Update expected results when physics models change
3. **Performance Monitoring**: Monitor test execution time for performance regressions
4. **Dependency Updates**: Keep test dependencies up to date

### Test Refactoring
1. **Remove Duplicates**: Eliminate duplicate test code
2. **Improve Readability**: Make tests easy to understand and maintain
3. **Optimize Performance**: Remove slow tests or optimize them
4. **Update Fixtures**: Keep test fixtures current and efficient

## Dependencies

- **pytest**: Test framework and runner
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance benchmarking
- **pytest-mock**: Mocking framework
- **hypothesis**: Property-based testing
- **numpy**: Numerical testing and array operations
- **pandas**: Data frame testing
- **matplotlib**: Plot testing (if applicable)