"""
physimlab CLI - Command Line Interface

Typer-based CLI for running physics simulations with rich output formatting.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt
from typing import Optional, List
import json
import yaml
import sys
import os
from datetime import datetime
import subprocess

from .core import run_simulation, batch_simulation, compare_results
from . import __version__, __author__, __license__

app = typer.Typer(
    name="physimlab",
    help="Physics Simulation Laboratory - Ball Drop Simulation",
    add_completion=False,
    no_args_is_help=True
)

console = Console()

@app.command()
def run(
    config: str = typer.Option(..., "--config", "-c", help="Configuration file path (required)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run a ball drop simulation."""
    
    # Show header
    if not quiet:
        console.print(Panel.fit(
            f"[bold blue]physimlab v{__version__}[/bold blue]\n"
            f"[dim]Physics Simulation Laboratory[/dim]",
            border_style="blue"
        ))
    
    # Validate config file
    if not os.path.exists(config):
        console.print(f"[red]Error:[/red] Configuration file '{config}' not found")
        raise typer.Exit(1)
    
    # Load configuration
    try:
        with open(config, 'r') as f:
            if config.endswith('.yaml') or config.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load configuration: {e}")
        raise typer.Exit(1)
    
    # Note: Individual parameters are no longer supported - use config file only
    
    # Show configuration summary
    if not quiet:
        config_table = Table(title="Configuration", show_header=False, box=None)
        config_table.add_row("Scenario", config_data.get('scenario', 'drop'))
        config_table.add_row("Object", config_data.get('object', {}).get('type', 'sphere'))
        config_table.add_row("Mass", f"{config_data.get('ball', {}).get('mass', 0.5)} kg")
        config_table.add_row("Radius", f"{config_data.get('ball', {}).get('radius', 0.1)} m")
        config_table.add_row("Height", f"{config_data.get('position', {}).get('z0', 100)} m")
        if 'spin_rate' in config_data.get('object', {}):
            config_table.add_row("Spin", f"{config_data['object']['spin_rate']} rev/s")
        console.print(config_table)
    
    # Run simulation with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet
    ) as progress:
        task = progress.add_task("Running simulation...", total=100)
        
        try:
            result = run_simulation(config_path=config, output_dir=output)
            progress.update(task, completed=100)
        except Exception as e:
            console.print(f"[red]Error:[/red] Simulation failed: {e}")
            raise typer.Exit(1)
    
    # Show results
    if not quiet:
        summary = result['summary']
        config = result.get('config', {})
        
        # Enhanced results display matching HTML report format
        console.print(Panel.fit(
            "[bold blue]Simulation Results Summary[/bold blue]",
            border_style="blue"
        ))
        
        # Summary Statistics Section
        stats_table = Table(title="Summary Statistics", show_header=False, box=None)
        stats_table.add_row("Flight Time", f"[bold]{summary.get('flight_time', 0):.3f}[/bold] s")
        stats_table.add_row("Max Height", f"[bold]{summary.get('max_height', 0):.2f}[/bold] m")
        stats_table.add_row("Horizontal Distance", f"[bold]{summary.get('horizontal_range', 0):.2f}[/bold] m")
        stats_table.add_row("Max Speed", f"[bold]{summary.get('max_velocity', 0):.2f}[/bold] m/s")
        stats_table.add_row("Max Mach Number", f"[bold]{summary.get('max_mach', 0):.4f}[/bold]")
        
        # Get detailed statistics if available
        detailed_stats = result.get('detailed_stats', {})
        max_reynolds = detailed_stats.get('max_reynolds', summary.get('max_reynolds', 0))
        compute_time = detailed_stats.get('compute_time', 0)
        ground_contacts = summary.get('ground_contacts', 0)
        
        stats_table.add_row("Max Reynolds Number", f"[bold]{max_reynolds:.2e}[/bold]")
        stats_table.add_row("Ground Contacts", f"[bold]{ground_contacts}[/bold]")
        stats_table.add_row("Compute Time", f"[bold]{compute_time:.2f}[/bold] ms")
        
        console.print(stats_table)
        
        # Simulation Status Section
        status_table = Table(title="Simulation Status", show_header=False, box=None)
        
        # Stability status
        stability_status = "PASS" if detailed_stats.get('is_stable', summary.get('is_stable', True)) else "FAIL"
        stability_color = "green" if stability_status == "PASS" else "red"
        status_table.add_row("Numerical Stability", f"[{stability_color}]{stability_status}[/{stability_color}]")
        
        # Energy conservation status
        energy_status = "PASS" if detailed_stats.get('energy_conserved', summary.get('energy_conserved', True)) else "FAIL"
        energy_color = "green" if energy_status == "PASS" else "red"
        status_table.add_row("Energy Conservation", f"[{energy_color}]{energy_status}[/{energy_color}]")
        
        # Energy gain
        energy_gain_pct = detailed_stats.get('max_energy_gain_pct', 0)
        status_table.add_row("Max Energy Gain", f"{energy_gain_pct:.2f}%")
        
        # Time steps
        timestep_count = detailed_stats.get('timestep_count', len(result.get('data', [])))
        status_table.add_row("Time Steps", f"{timestep_count}")
        
        # dt range
        dt_min = detailed_stats.get('dt_min', 0)
        dt_max = detailed_stats.get('dt_max', 0)
        status_table.add_row("dt Range", f"{dt_min:.6f} - {dt_max:.6f} s")
        
        console.print(status_table)
        
        # Ball Parameters Section
        ball_config = config.get('ball', {})
        position_config = config.get('position', {})
        physics_config = config.get('simulation', {})
        
        ball_table = Table(title="Ball Parameters", show_header=False, box=None)
        ball_table.add_row("Mass", f"{ball_config.get('mass', 0):.4f} kg")
        ball_table.add_row("Radius", f"{ball_config.get('radius', 0):.4f} m")
        ball_table.add_row("Initial Velocity", f"{ball_config.get('initial_velocity', 0):.2f} m/s")
        ball_table.add_row("Drop Angle", f"{ball_config.get('drop_angle_deg', 0):.1f}°")
        ball_table.add_row("Azimuth", f"{ball_config.get('azimuth_deg', 0):.1f}°")
        ball_table.add_row("Initial Position", f"({position_config.get('x0', 0):.2f}, {position_config.get('y0', 0):.2f}, {position_config.get('z0', 0):.2f}) m")
        ball_table.add_row("Spin Rate", f"{ball_config.get('spin_rps', 0):.1f} rps")
        spin_axis = ball_config.get('spin_axis', [0,0,1])
        ball_table.add_row("Spin Axis", f"({spin_axis[0]:.1f}, {spin_axis[1]:.1f}, {spin_axis[2]:.1f})")
        ball_table.add_row("Gravity", f"{physics_config.get('g', 9.81):.4f} m/s²")
        
        console.print(ball_table)
        
        # Surface Properties Section
        surface_config = config.get('surface', {})
        
        surface_table = Table(title="Surface Properties", show_header=False, box=None)
        surface_table.add_row("Elasticity (Base)", f"{surface_config.get('elasticity_base', 0):.3f}")
        surface_table.add_row("Elasticity Drop", f"{surface_config.get('elasticity_drop', 0):.4f}")
        surface_table.add_row("Static Friction (μs)", f"{surface_config.get('friction_mu_s', 0):.3f}")
        surface_table.add_row("Kinetic Friction (μk)", f"{surface_config.get('friction_mu_k', 0):.3f}")
        surface_table.add_row("Dampness", f"{surface_config.get('dampness', 0):.2f}")
        surface_table.add_row("Wetness", f"{surface_config.get('wetness', 0):.2f}")
        surface_table.add_row("Base Height", f"{surface_config.get('base_height', 0):.2f} m")
        surface_table.add_row("Slope (X, Y)", f"({surface_config.get('slope_x', 0):.4f}, {surface_config.get('slope_y', 0):.4f})")
        surface_table.add_row("Surface Roughness", f"{surface_config.get('surface_roughness', 0):.4f} m")
        
        console.print(surface_table)
        
        # Wind Conditions Section
        wind_config = config.get('wind', {})
        
        wind_table = Table(title="Wind Conditions", show_header=False, box=None)
        wind_table.add_row("Reference Speed", f"{wind_config.get('ref_speed', 0):.2f} m/s")
        wind_table.add_row("Reference Height", f"{wind_config.get('ref_height', 0):.1f} m")
        wind_table.add_row("Wind Direction", f"{wind_config.get('direction_deg', 0):.1f}°")
        wind_table.add_row("Shear Alpha", f"{wind_config.get('shear_alpha', 0):.3f}")
        wind_table.add_row("Gust Time Constant (τ)", f"{wind_config.get('gust_tau', 0):.2f} s")
        wind_table.add_row("Gust Intensity (σ)", f"{wind_config.get('gust_sigma', 0):.2f} m/s")
        wind_table.add_row("Humidity", f"{wind_config.get('humidity_pct', 0):.1f}%")
        
        console.print(wind_table)
        
        # Physics Settings Section
        sim_config = config.get('simulation', {})
        
        physics_table = Table(title="Physics Settings", show_header=False, box=None)
        physics_table.add_row("Buoyancy", f"{'[green]Enabled[/green]' if sim_config.get('buoyancy', True) else '[red]Disabled[/red]'}")
        physics_table.add_row("Virtual Mass Effect", f"{'[green]Enabled[/green]' if sim_config.get('use_virtual_mass', True) else '[red]Disabled[/red]'}")
        physics_table.add_row("Multi-Regime Drag", f"{'[green]Enabled[/green]' if sim_config.get('use_multi_regime_cd', True) else '[red]Disabled[/red]'}")
        physics_table.add_row("Hertzian Contact Model", f"{'[green]Enabled[/green]' if sim_config.get('use_hertzian_contact', True) else '[red]Disabled[/red]'}")
        physics_table.add_row("Adaptive Timestep", f"{'[green]Enabled[/green]' if sim_config.get('adaptive_timestep', False) else '[red]Disabled[/red]'}")
        physics_table.add_row("Random Seed", f"{config.get('simulation', {}).get('seed', 42)}")
        
        console.print(physics_table)
        
        # Output files
        if 'output_files' in result:
            files_table = Table(title="Output Files", show_header=False, box=None)
            for file_type, file_path in result['output_files'].items():
                files_table.add_row(file_type.title(), file_path)
            console.print(files_table)
    
    else:
        # Quiet output
        summary = result['summary']
        detailed_stats = result.get('detailed_stats', {})
        
        console.print(
            f"✓ Completed: {summary.get('flight_time', 0):.3f}s flight, "
            f"{summary.get('max_height', 0):.2f}m max height, "
            f"{summary.get('horizontal_range', 0):.2f}m range, "
            f"{summary.get('max_velocity', 0):.2f}m/s max speed"
        )
        
        # Status indicators
        stability = "Stable" if detailed_stats.get('is_stable', summary.get('is_stable', True)) else "Unstable"
        energy = "Conserved" if detailed_stats.get('energy_conserved', summary.get('energy_conserved', True)) else "Lost"
        console.print(f"Status: {stability} | Energy: {energy}")
        
        if 'output_files' in result and 'data' in result['output_files']:
            console.print(f"Output: {result['output_files']['data']}")


@app.command()
def batch(
    config: str = typer.Option("config.json", "--config", "-c", help="Base configuration file"),
    param: List[str] = typer.Option(..., "--param", "-p", help="Parameter to vary: name min max steps"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
):
    """Run batch simulations with parameter sweep."""
    
    if not quiet:
        console.print(Panel.fit(
            f"[bold blue]physimlab Batch v{__version__}[/bold blue]\n"
            f"[dim]Parameter Sweep Simulation[/dim]",
            border_style="blue"
        ))
    
    # Parse parameters
    params = []
    for p in param:
        name, min_val, max_val, steps = p.split()
        params.append({
            'name': name,
            'min': float(min_val),
            'max': float(max_val),
            'steps': int(steps)
        })
    
    # Run batch simulation
    try:
        results = batch_simulation(config_path=config, parameters=params, output_dir=output)
        
        if not quiet:
            # Show comparison table
            comparison_table = Table(title="Batch Results", show_header=True, box=None)
            comparison_table.add_column("Run", style="cyan")
            for param in params:
                comparison_table.add_column(param['name'].title(), style="magenta")
            comparison_table.add_column("Flight Time", style="green")
            comparison_table.add_column("Max Height", style="yellow")
            comparison_table.add_column("Range", style="blue")
            
            for i, result in enumerate(results):
                summary = result['summary']
                row_data = [str(i+1)]
                for param in params:
                    row_data.append(f"{result['config'].get(param['name'], 'N/A')}")
                row_data.extend([
                    f"{summary['flight_time']:.3f}s",
                    f"{summary['max_height']:.2f}m",
                    f"{summary['horizontal_range']:.2f}m"
                ])
                comparison_table.add_row(*row_data)
            
            console.print(comparison_table)
            
            # Save comparison
            if output:
                comparison_file = os.path.join(output, "batch_comparison.csv")
                import pandas as pd
                df_data = []
                for result in results:
                    summary = result['summary']
                    row = result['config'].copy()
                    row.update({
                        'flight_time': summary['flight_time'],
                        'max_height': summary['max_height'],
                        'horizontal_range': summary['horizontal_range']
                    })
                    df_data.append(row)
                df = pd.DataFrame(df_data)
                df.to_csv(comparison_file, index=False)
                console.print(f"Comparison saved to: {comparison_file}")
        
        else:
            console.print(f"✓ Batch completed: {len(results)} runs")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] Batch simulation failed: {e}")
        raise typer.Exit(1)


@app.command()
def compare(
    result1: str = typer.Argument(..., help="First result directory"),
    result2: str = typer.Argument(..., help="Second result directory"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
):
    """Compare two simulation results."""
    
    try:
        comparison = compare_results(result1, result2, output_dir=output)
        
        if not quiet:
            console.print(Panel.fit(
                f"[bold blue]physimlab Compare v{__version__}[/bold blue]\n"
                f"[dim]Results Comparison[/dim]",
                border_style="blue"
            ))
            
            # Show comparison table
            comp_table = Table(title="Comparison", show_header=False, box=None)
            for key, value in comparison.items():
                comp_table.add_row(key.replace('_', ' ').title(), str(value))
            console.print(comp_table)
            
            if output:
                console.print(f"Comparison plots saved to: {output}")
        else:
            console.print("✓ Comparison completed")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] Comparison failed: {e}")
        raise typer.Exit(1)


@app.command()
def list():
    """List available scenarios."""
    scenarios = [
        ("drop", "Ball drop simulation with aerodynamics"),
        ("wind-tunnel", "Wind tunnel aerodynamics test"),
        ("terminal-velocity", "Terminal velocity measurement"),
        ("projectile", "Projectile motion with drag"),
    ]
    
    table = Table(title="Available Scenarios", show_header=True, box=None)
    table.add_column("Scenario", style="cyan")
    table.add_column("Description", style="magenta")
    
    for name, desc in scenarios:
        table.add_row(name, desc)
    
    console.print(table)


@app.command()
def info(scenario: str = typer.Argument("drop", help="Scenario to show information for")):
    """Show information about a scenario."""
    
    if scenario == "drop":
        info_text = """
# Ball Drop Scenario

Simulates a ball falling under gravity with air resistance, Magnus effect, and ground bounce physics.

## Parameters

- **--height**: Initial drop height (meters)
- **--mass**: Ball mass (kg)  
- **--radius**: Ball radius (meters)
- **--spin**: Initial spin rate (revolutions per second)
- **--wind-speed**: Wind speed (m/s)
- **--elasticity**: Surface elasticity (0-1)

## Example

```bash
physimlab run --config config.json
```

## Configuration File

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
  }
}
```
        """
    else:
        info_text = f"Scenario '{scenario}' not found. Available: drop, wind-tunnel, terminal-velocity, projectile"
    
    console.print(Markdown(info_text))


@app.command()
def version():
    """Show version information."""
    console.print(Panel(
        f"[bold]physimlab v{__version__}[/bold]\n"
        f"Author: {__author__}\n"
        f"License: {__license__}\n"
        f"Python: {sys.version.split()[0]}",
        title="Version Information",
        border_style="blue"
    ))


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory"),
    scenario: str = typer.Option("drop", "--scenario", "-s", help="Default scenario"),
):
    """Initialize a new physimlab project."""
    
    project_dir = os.path.join(output, name)
    
    if os.path.exists(project_dir):
        console.print(f"[red]Error:[/red] Directory '{project_dir}' already exists")
        raise typer.Exit(1)
    
    os.makedirs(project_dir, exist_ok=True)
    
    # Create example config
    config = {
        "scenario": scenario,
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
    
    config_file = os.path.join(project_dir, "config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create README
    readme = f"""# {name}

Physics simulation project created with physimlab.

## Quick Start

```bash
physimlab run --config config.json
```

## Configuration

Edit `config.json` to customize the simulation parameters.

## Output

Results will be saved to the `outputs/` directory.
"""
    
    readme_file = os.path.join(project_dir, "README.md")
    with open(readme_file, 'w') as f:
        f.write(readme)
    
    console.print(f"✓ Created project '{name}' in {project_dir}")
    console.print(f"  Config file: {config_file}")
    console.print(f"  README: {readme_file}")


if __name__ == "__main__":
    app()
