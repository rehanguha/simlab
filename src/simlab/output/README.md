# Output Module

This directory contains the output management system for SimLab, responsible for generating, organizing, and saving simulation results in various formats.

## Overview

The output module provides a comprehensive system for saving simulation results in multiple formats including CSV data files, JSON summaries, interactive HTML reports, static plots, and animated GIFs. It handles file organization, naming conventions, and format-specific optimizations.

## Module Structure

```
output/
├── __init__.py      # Module exports and public API
├── manager.py       # Output file management and organization
└── result.py        # Result object with plotting and analysis capabilities
```

## Output Formats

### CSV Data Files
- **Purpose**: Complete trajectory data with all calculated physics parameters
- **Content**: Time, position, velocity, acceleration, physics parameters
- **Format**: Comma-separated values with headers
- **Use Case**: Data analysis, external processing, long-term storage

**Example CSV Header:**
```csv
Time,X,Y,Z,Vx,Vy,Vz,Speed,OmegaZ,AirDensity,Reynolds,Cd,Mach
```

### JSON Summary
- **Purpose**: Machine-readable summary and configuration
- **Content**: Simulation summary, configuration, metadata, statistics
- **Format**: JSON with structured data
- **Use Case**: Programmatic access, configuration storage, metadata

**Example JSON Structure:**
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

### HTML Reports
- **Purpose**: Interactive visualization and analysis
- **Content**: 2D/3D plots, parameter visualization, summary statistics
- **Format**: Self-contained HTML with Plotly.js
- **Use Case**: Presentation, interactive analysis, sharing results

**Features:**
- Interactive 2D and 3D trajectory plots
- Velocity and height over time
- Physics parameter visualization
- Summary statistics with rich formatting
- Responsive design for different screen sizes

### Static Plots (PNG)
- **Purpose**: Publication-ready static visualizations
- **Content**: Trajectory, velocity components, physics parameters
- **Format**: High-resolution PNG images
- **Use Case**: Publications, presentations, documentation

**Plot Types:**
- Trajectory visualization (2D and 3D)
- Velocity components over time
- Physics parameters analysis
- Energy conservation plots
- Stability analysis plots

### Animated GIFs
- **Purpose**: Dynamic visualization of simulation progress
- **Content**: Time-lapse animation of object trajectory
- **Format**: Animated GIF with configurable frame rate
- **Use Case**: Demonstrations, presentations, analysis

## Output File Organization

### Default Directory Structure
When running simulations, outputs are organized as:
```
outputs/
├── data.csv              # Full trajectory data
├── summary.json          # Results summary
├── report.html           # Interactive HTML report
├── plots/                # Static matplotlib plots
│   ├── trajectory.png
│   ├── velocity.png
│   ├── physics.png
│   └── energy.png
└── animation.gif         # Trajectory animation
```

### Custom Output Directory
You can specify a custom output directory:
```python
result = simlab.run_simulation(
    config_path="config.json",
    output_dir="./my_results"
)
```

This creates:
```
my_results/
├── data.csv
├── summary.json
├── report.html
├── plots/
│   ├── trajectory.png
│   ├── velocity.png
│   └── physics.png
└── animation.gif
```

## Usage Examples

### Basic Output Generation
```python
import simlab

# Run simulation with default output
result = simlab.run_simulation(config_path="config.json")

# Access output files
output_files = result['output_files']
print(f"CSV data: {output_files['data']}")
print(f"HTML report: {output_files['html']}")
print(f"JSON summary: {output_files['json']}")
```

### Custom Output Configuration
```python
# Specify custom output directory
result = simlab.run_simulation(
    config_path="config.json",
    output_dir="./custom_results"
)

# Generate specific output formats
result = simlab.run_simulation(
    config_path="config.json",
    output_formats=["csv", "json", "html"]
)
```

### Programmatic Output Access
```python
# Access result data
data = result['data']           # Pandas DataFrame
summary = result['summary']     # Dictionary
config = result['config']       # Configuration used

# Access plotting capabilities
result_obj = result['result_object']
result_obj.plot_trajectory()
result_obj.plot_velocity()
result_obj.plot_physics()
```

## Output Manager (`manager.py`)

The output manager handles file operations and organization:

### Key Functions
```python
from simlab.output.manager import save_simulation_results

# Save all output formats
output_files = save_simulation_results(
    data=data,
    summary=summary,
    config=config,
    output_dir="./results",
    formats=["csv", "json", "html", "png", "gif"]
)
```

### File Naming Conventions
- **Data files**: `data.csv`
- **Summary files**: `summary.json`
- **Reports**: `report.html`
- **Plots**: `trajectory.png`, `velocity.png`, `physics.png`
- **Animations**: `animation.gif`

### Directory Management
- Creates output directories automatically
- Handles file overwriting with user confirmation
- Organizes plots in subdirectories
- Maintains consistent file naming

## Result Object (`result.py`)

The result object provides advanced plotting and analysis capabilities:

### Plotting Methods
```python
from simlab.output.result import SimulationResult

# Create result object
result = SimulationResult(data, summary, config)

# Generate plots
result.plot_trajectory()        # 2D and 3D trajectory
result.plot_velocity()          # Velocity components
result.plot_physics()           # Physics parameters
result.plot_energy()            # Energy conservation
result.plot_stability()         # Stability analysis

# Save plots
result.save_plots("./plots/")
```

### Analysis Methods
```python
# Get detailed statistics
stats = result.get_detailed_statistics()

# Check energy conservation
energy_conserved = result.check_energy_conservation()

# Analyze stability
stability_info = result.analyze_stability()

# Get flight characteristics
flight_info = result.get_flight_characteristics()
```

### Interactive Features
- **Zoom and Pan**: Interactive plot navigation
- **Data Points**: Hover information for data points
- **Legend Control**: Toggle different data series
- **Export Options**: Export plots in various formats

## Configuration Integration

Output settings can be configured in the simulation configuration:

```json
{
  "output": {
    "format": ["csv", "json", "html", "png", "gif"],
    "directory": "./results",
    "filename": "simulation_results",
    "overwrite": false,
    "compression": true,
    "precision": 6,
    "plot_style": "publication",
    "animation_fps": 30
  }
}
```

## Performance Considerations

### Large Dataset Handling
- **Memory Management**: Efficient handling of large trajectory datasets
- **Streaming**: CSV output supports streaming for memory efficiency
- **Plot Optimization**: Plot generation optimized for large datasets

### File I/O Optimization
- **Batch Operations**: Minimize file system operations
- **Compression**: Optional compression for large files
- **Parallel Processing**: Parallel generation of multiple output formats

### Plot Performance
- **Vector Graphics**: High-quality vector plots for publication
- **Interactive Optimization**: Optimized interactive plots for large datasets
- **Caching**: Cache expensive calculations for repeated plotting

## Error Handling

### File System Errors
- **Permission Issues**: Handle read/write permission problems
- **Disk Space**: Check available disk space before writing
- **Path Validation**: Validate output paths and create directories

### Format-Specific Errors
- **CSV Encoding**: Handle special characters in CSV output
- **JSON Serialization**: Handle complex data types in JSON
- **Plot Generation**: Handle plotting errors gracefully
- **Animation Creation**: Handle animation generation failures

### Recovery Strategies
- **Partial Output**: Generate available formats even if some fail
- **Error Logging**: Detailed error logging for debugging
- **User Feedback**: Clear error messages with suggestions

## Dependencies

- **Pandas**: CSV data handling and export
- **Matplotlib**: Static plot generation
- **Plotly**: Interactive HTML reports
- **ImageIO**: GIF animation creation
- **NumPy**: Data processing and analysis
- **JSON**: JSON serialization and formatting

## Best Practices

### Output Organization
1. **Consistent Naming**: Use consistent file naming conventions
2. **Directory Structure**: Organize outputs in logical directory structure
3. **Version Control**: Include output metadata for reproducibility
4. **Backup Strategy**: Implement backup for important results

### Performance Optimization
1. **Selective Output**: Generate only needed output formats
2. **Compression**: Use compression for large datasets
3. **Parallel Processing**: Generate multiple formats in parallel
4. **Memory Management**: Handle large datasets efficiently

### Quality Assurance
1. **Validation**: Validate output files after generation
2. **Testing**: Test output generation with various configurations
3. **Documentation**: Document output format specifications
4. **Compatibility**: Ensure output compatibility with external tools