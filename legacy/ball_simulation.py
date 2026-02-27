"""
Ball drop / launch simulation with realistic aerodynamics, wind, and ground contact.

This is the main entry point for the simulation. The codebase is organized into modules:
- physics.py: Physics constants and Numba-compiled functions
- models.py: Data classes for parameters (Params, Surface, Wind, SimulationResult)
- validation.py: Input validation and error handling
- simulation.py: Core simulation engine with RK45 adaptive timestep
- reporting.py: CSV export, plotting, and HTML report generation
- config_loader.py: Load configuration from JSON file

Usage:
    python ball_simulation.py                    # Use default config.json
    python ball_simulation.py my_config.json     # Use custom config file

Phase 1 Enhanced Physics:
- Multi-regime drag coefficient (Stokes, Schiller-Naumann, Newton, drag crisis)
- Mehta correlation for Magnus effect with spin decay torque
- Air properties with humidity correction and Mach number
- Hertzian contact model with velocity-dependent restitution
- Virtual mass effect for accelerating spheres

Phase 2 Robustness & Numerical Methods:
- Input validation with physical bounds checking
- Adaptive timestep (RK45 Dormand-Prince) with error control
- Stability checks: NaN/Inf detection, energy monitoring, penetration resolution
"""

import sys
import os
import time
from models import Params, Surface, Wind
from simulation import simulate_drop
from reporting import generate_all_reports, calculate_statistics
from config_loader import load_config, ConfigLoader


def run_simulation(params: Params, surface: Surface, wind: Wind, 
                   output_csv: str = "ball_drop_data_table.csv",
                   output_plot: str = "ball_drop_2d_graph.png",
                   output_html: str = "ball_drop_report.html",
                   verbose: bool = True,
                   generate_video: bool = True,
                   video_fps: int = 30,
                   output_dir: str = None) -> dict:
    """
    Run a complete ball drop simulation with reporting.
    
    Parameters:
        params: Simulation parameters (mass, radius, velocity, etc.)
        surface: Surface properties (elasticity, friction, etc.)
        wind: Wind conditions (speed, direction, gusts, etc.)
        output_csv: Path for CSV output file
        output_plot: Path for 2D plot image file
        output_html: Path for HTML report file
        verbose: If True, print simulation progress and results
        generate_video: If True, generate animated GIF of trajectory
        video_fps: Frames per second for video/GIF
        output_dir: Output directory path for all files
    
    Returns:
        Dictionary containing simulation results and file paths
    """
    if verbose:
        print("=" * 60)
        print("Ball Drop Simulation")
        print("=" * 60)
        print("\nPhase 1: Enhanced Physics Features")
        print("  - Multi-regime drag coefficient")
        print("  - Mehta Magnus correlation with aerodynamic torque")
        print("  - Humidity-corrected air properties + Mach number")
        print("  - Hertzian contact model")
        print("  - Virtual mass effect")
        print("\nPhase 2: Robustness & Numerical Methods")
        print("  - Input validation with physical bounds checking")
        print("  - Adaptive timestep (RK45 Dormand-Prince)")
        print("  - Stability checks: NaN/Inf, energy monitoring")
        print("=" * 60)
    
    # Run simulation
    result = simulate_drop(params, surface, wind)
    
    if verbose:
        print(f"\nSimulation completed in {result.compute_time_ms:.2f} ms ({len(result.df)} timesteps)")
        print(f"Stability: {'OK' if result.stability_ok else 'FAILED'}")
        print(f"Energy monitoring: {'OK' if result.energy_ok else 'WARNING - excess energy gain'}")
        print(f"Max energy gain: {result.max_energy_gain_pct:.2f}%")
    
    # Generate reports
    report_files = generate_all_reports(
        result, output_csv, output_plot, output_html,
        generate_video=generate_video,
        video_fps=video_fps
    )
    
    # Calculate statistics
    stats = calculate_statistics(result)
    
    if verbose:
        print("\n" + "=" * 50)
        print("SIMULATION SUMMARY")
        print("=" * 50)
        print(f"Flight time: {stats['flight_time']:.2f} s")
        print(f"Max height: {stats['max_height']:.2f} m")
        print(f"Horizontal distance: {stats['total_distance']:.2f} m")
        print(f"Max velocity: {stats['max_speed']:.2f} m/s")
        print(f"Max Mach number: {stats['max_mach']:.4f}")
        print(f"Max Reynolds number: {stats['max_reynolds']:.2e}")
        print(f"Ground contacts: {stats['bounce_count']}")
        print(f"Adaptive dt range: {stats['dt_min']:.6f} - {stats['dt_max']:.6f} s")
        print(f"\nOutput directory: {output_dir}")
        print(f"Files saved:")
        for file_type, file_path in report_files.items():
            print(f"  - {file_type}: {file_path}")
    
    return {
        "result": result,
        "statistics": stats,
        "files": report_files
    }


def run_from_config(config_path: str = "config.json") -> dict:
    """
    Run simulation using configuration from JSON file.
    
    Parameters:
        config_path: Path to JSON configuration file
    
    Returns:
        Dictionary containing simulation results and file paths
    """
    params, surface, wind, output_settings = load_config(config_path)
    
    # Create output directory with run name and timestamp
    run_name = output_settings.get('run_name', 'simulation')
    output_dir = output_settings.get('output_dir', 'outputs')
    timestamp = int(time.time())
    run_folder_name = f"{run_name}_{timestamp}"
    run_output_path = os.path.join(output_dir, run_folder_name)
    
    # Create the output directory
    os.makedirs(run_output_path, exist_ok=True)
    
    # Build full output paths
    output_csv = os.path.join(run_output_path, output_settings['csv_file'])
    output_plot = os.path.join(run_output_path, output_settings['plot_file'])
    output_html = os.path.join(run_output_path, output_settings['html_file'])
    generate_video = output_settings.get('generate_video', True)
    video_fps = output_settings.get('video_fps', 30)
    
    return run_simulation(
        params=params,
        surface=surface,
        wind=wind,
        output_csv=output_csv,
        output_plot=output_plot,
        output_html=output_html,
        verbose=output_settings['verbose'],
        generate_video=generate_video,
        video_fps=video_fps,
        output_dir=run_output_path
    )


# =========================
# Main Entry Point
# =========================

if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        print(f"Using configuration file: {config_path}")
    else:
        config_path = "config.json"
        print(f"Using default configuration file: {config_path}")
    
    # Run simulation
    output = run_from_config(config_path)