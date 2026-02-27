# SimLab Test Configuration Files

This directory contains configuration files for testing SimLab with known behaviors and scenarios that are easy to understand and verify.

## Test Scenarios

### 1. No-Wind Bounce Test (`config_no_wind_bounce.json`)
**Purpose**: Test basic physics - ball dropped from height bounces at same spot
**Key Features**:
- Zero wind conditions
- Simple vertical bouncing
- No horizontal movement expected
- Perfect for testing collision physics

**Expected Behavior**:
- Horizontal range: ~0.0 meters
- Multiple bounces with decreasing height
- Simple harmonic-like motion in vertical direction only

### 2. Vacuum Drop Test (`config_vacuum_drop.json`)
**Purpose**: Test gravity-only physics with no air resistance
**Key Features**:
- No aerodynamic effects (buoyancy=false, drag disabled)
- Perfect parabolic motion
- Easy to verify with basic physics equations

**Expected Behavior**:
- Impact time: 3.19 seconds (sqrt(2h/g))
- Impact velocity: 31.3 m/s (gt)
- Perfect parabola: z = z0 - 0.5 * g * t²

### 3. High Wind Test (`config_high_wind.json`)
**Purpose**: Test wind effects on trajectory
**Key Features**:
- Strong crosswind (15 m/s)
- Visible horizontal displacement
- Demonstrates wind physics clearly

**Expected Behavior**:
- Horizontal range: 10-20 meters
- Curved trajectory with horizontal drift
- Wind direction: 90 degrees (positive x-direction)

### 4. Spin Effect Test (`config_spin_effect.json`)
**Purpose**: Test Magnus effect from ball spin
**Key Features**:
- High spin rate (12 rev/s)
- Side spin to show curve
- Demonstrates aerodynamic forces

**Expected Behavior**:
- Lateral deflection due to Magnus force
- Curved trajectory perpendicular to spin axis
- Visible lateral movement even with no wind

### 5. Terminal Velocity Test (`config_terminal_velocity.json`)
**Purpose**: Test when drag equals gravity
**Key Features**:
- High drop height (1000m)
- Heavy ball (2kg)
- Shows velocity plateau

**Expected Behavior**:
- Velocity increases then plateaus at terminal velocity
- Time to terminal: 5-10 seconds
- No ground collision (simulation runs without hitting ground)

### 6. Multi-Bounce Test (`config_multi_bounce.json`)
**Purpose**: Test repeated collisions
**Key Features**:
- Multiple bounces with energy loss
- Shows damping effects
- Tests contact physics

**Expected Behavior**:
- 5-10 bounces before stopping
- Each bounce loses ~30% energy
- Exponential decay in bounce height

### 7. Temperature Effect Test (`config_temperature_effect.json`)
**Purpose**: Test how air density affects drag
**Key Features**:
- Elevated temperature (300K / 27°C)
- Shows density variations
- Demonstrates thermodynamic effects

**Expected Behavior**:
- Lower air density reduces drag
- Longer flight time compared to standard temperature
- Air density lower than standard sea level density

### 8. Validation Test Suite (`config_validation_suite.json`)
**Purpose**: Comprehensive test with known expected results
**Key Features**:
- Simple parameters for manual verification
- Short simulation time
- All physics effects enabled

**Expected Behavior**:
- Impact time: 1.01 seconds (sqrt(2*5/9.81))
- Impact velocity: 9.90 m/s (9.81*1.01)
- Easy to verify with hand calculations

## Usage

To run a specific test:

```bash
# Run with SimLab CLI
python -m simlab run configs/config_no_wind_bounce.json

# Or using the core module
python -c "from simlab.core import run_simulation; run_simulation('configs/config_vacuum_drop.json')"
```

## Validation

Each config includes `test_expectations` with:
- Description of expected behavior
- Quantitative predictions where possible
- Key physics principles being tested

## Creating New Tests

When creating new test configurations:

1. **Clear naming**: Use descriptive names like `config_[scenario]_[purpose].json`
2. **Documentation**: Include a `description` field
3. **Expectations**: Add `test_expectations` with expected behavior
4. **Simplicity**: Use simple parameters that are easy to verify
5. **Isolation**: Test one physics effect at a time when possible

## Physics Principles Tested

- **Gravity**: Basic free fall motion
- **Aerodynamics**: Drag, lift, and Magnus effects
- **Collision**: Bouncing and energy loss
- **Thermodynamics**: Temperature effects on air density
- **Wind**: Atmospheric effects on trajectory
- **Numerical Methods**: Integration accuracy and stability

## Expected Output Files

Each test generates:
- `*_data.csv`: Time series data
- `*_plot.png`: Trajectory visualization
- `*_report.html`: Detailed analysis report

## Troubleshooting

If a test doesn't behave as expected:
1. Check the `test_expectations` for the specific scenario
2. Verify the physics parameters in the config
3. Compare with manual calculations for simple cases
4. Check the generated reports for detailed analysis