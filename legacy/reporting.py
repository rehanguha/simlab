"""
Reporting module for ball drop simulation.
Generates CSV exports, 2D plots, interactive HTML reports, and animated GIFs.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import plotly.graph_objects as go
from typing import Optional
import time
import os

from models import SimulationResult, Params, Surface, Wind


def calculate_statistics(result: SimulationResult) -> dict:
    """Calculate summary statistics from simulation result."""
    df = result.df
    params = result.params
    R = params.radius
    
    # Derived quantities
    df = df.copy()
    df["Speed"] = np.sqrt(df["Vx"]**2 + df["Vy"]**2 + df["Vz"]**2)
    df["Z_bottom"] = df["Z"] - R
    df["Clearance"] = df["Z"] - df["Z_ground"] - R
    
    # Basic statistics
    max_height = df["Z"].max()
    total_distance = np.sqrt(
        (df["X"].iloc[-1] - df["X"].iloc[0])**2 + 
        (df["Y"].iloc[-1] - df["Y"].iloc[0])**2
    )
    flight_time = df["Time"].iloc[-1]
    
    # Count bounces
    bounce_count = 0
    clearance = df["Clearance"].values
    for i in range(1, len(clearance)):
        if clearance[i-1] < 0.005 and clearance[i] >= 0.005:
            bounce_count += 1
    
    return {
        "max_height": max_height,
        "total_distance": total_distance,
        "flight_time": flight_time,
        "max_speed": df["Speed"].max(),
        "max_mach": df["Mach"].max(),
        "max_reynolds": df["Re"].max(),
        "bounce_count": bounce_count,
        "timestep_count": len(df),
        "dt_min": df["Dt_actual"].min(),
        "dt_max": df["Dt_actual"].max(),
        "df": df
    }


def export_csv(result: SimulationResult, filename: str = "ball_drop_data_table.csv") -> str:
    """Export simulation data to CSV file."""
    stats = calculate_statistics(result)
    df = stats["df"]
    df.to_csv(filename, index=False)
    return filename


def generate_2d_plot(result: SimulationResult, filename: str = "ball_drop_2d_graph.png") -> str:
    """Generate 2D trajectory plot."""
    stats = calculate_statistics(result)
    df = stats["df"]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)
    
    ax1.plot(df["X"], df["Z_bottom"], label="Ball bottom (Z - R)", lw=2, color="royalblue")
    ax1.plot(df["X"], df["Z_ground"], label="Ground", color="brown", alpha=0.9)
    ax1.set_ylabel("Height (m)")
    ax1.set_title("Ball Trajectory")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.plot(df["X"], df["Clearance"], label="Clearance", color="darkgreen")
    ax2.axhline(0, color="k", lw=1, alpha=0.6)
    ax2.set_xlabel("X (m)")
    ax2.set_ylabel("Clearance (m)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    
    return filename


def generate_html_report(result: SimulationResult, filename: str = "ball_drop_report.html") -> str:
    """Generate simple HTML report for researchers with minimal CSS and white background."""
    stats = calculate_statistics(result)
    df = stats["df"]
    params = result.params
    surface = result.surface
    wind = result.wind
    
    # Generate HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ball Drop Simulation Report</title>
    <script src="https://cdn.plot.ly/plotly-3.3.1.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #ffffff;
            color: #333333;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ 
            color: #000000; 
            border-bottom: 2px solid #333333; 
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{ 
            color: #000000; 
            border-bottom: 1px solid #cccccc;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        .section {{ margin-bottom: 30px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-bottom: 20px;
        }}
        th, td {{ 
            border: 1px solid #dddddd; 
            padding: 8px 12px; 
            text-align: left; 
        }}
        th {{ background-color: #f5f5f5; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-box {{
            border: 1px solid #dddddd;
            padding: 15px;
            text-align: center;
        }}
        .stat-box .value {{ font-size: 1.5em; font-weight: bold; color: #000000; }}
        .stat-box .label {{ font-size: 0.9em; color: #666666; }}
        .status-ok {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
        .chart {{ width: 100%; height: 500px; margin: 20px 0; }}
        .timestamp {{ color: #666666; font-size: 0.9em; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Ball Drop Simulation Report</h1>
        <p class="timestamp">Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value">{stats["flight_time"]:.3f}</div>
                    <div class="label">Flight Time (s)</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["max_height"]:.2f}</div>
                    <div class="label">Max Height (m)</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["total_distance"]:.2f}</div>
                    <div class="label">Horizontal Distance (m)</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["max_speed"]:.2f}</div>
                    <div class="label">Max Speed (m/s)</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["max_mach"]:.4f}</div>
                    <div class="label">Max Mach Number</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["max_reynolds"]:.2e}</div>
                    <div class="label">Max Reynolds Number</div>
                </div>
                <div class="stat-box">
                    <div class="value">{stats["bounce_count"]}</div>
                    <div class="label">Ground Contacts</div>
                </div>
                <div class="stat-box">
                    <div class="value">{result.compute_time_ms:.2f}</div>
                    <div class="label">Compute Time (ms)</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Simulation Status</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Numerical Stability</td><td class="{'status-ok' if result.stability_ok else 'status-error'}">{'PASS' if result.stability_ok else 'FAIL'}</td></tr>
                <tr><td>Energy Conservation</td><td class="{'status-ok' if result.energy_ok else 'status-warning'}">{'PASS' if result.energy_ok else 'WARNING'}</td></tr>
                <tr><td>Max Energy Gain</td><td>{result.max_energy_gain_pct:.2f}%</td></tr>
                <tr><td>Time Steps</td><td>{stats["timestep_count"]}</td></tr>
                <tr><td>dt Range</td><td>{stats["dt_min"]:.6f} - {stats["dt_max"]:.6f} s</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Ball Parameters</h2>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Mass</td><td>{params.mass:.4f} kg</td></tr>
                <tr><td>Radius</td><td>{params.radius:.4f} m</td></tr>
                <tr><td>Initial Velocity</td><td>{params.v0:.2f} m/s</td></tr>
                <tr><td>Drop Angle</td><td>{params.drop_angle_deg:.1f}°</td></tr>
                <tr><td>Azimuth</td><td>{params.azimuth_deg:.1f}°</td></tr>
                <tr><td>Initial Position (X, Y, Z)</td><td>({params.x0:.2f}, {params.y0:.2f}, {params.z0:.2f}) m</td></tr>
                <tr><td>Spin Rate</td><td>{params.spin_rps:.1f} rps</td></tr>
                <tr><td>Spin Axis</td><td>({params.spin_axis[0]:.1f}, {params.spin_axis[1]:.1f}, {params.spin_axis[2]:.1f})</td></tr>
                <tr><td>Gravity</td><td>{params.g:.4f} m/s²</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Surface Properties</h2>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Elasticity (Base)</td><td>{surface.elasticity_base:.3f}</td></tr>
                <tr><td>Elasticity Drop</td><td>{surface.elasticity_drop:.4f}</td></tr>
                <tr><td>Static Friction (μs)</td><td>{surface.friction_mu_s:.3f}</td></tr>
                <tr><td>Kinetic Friction (μk)</td><td>{surface.friction_mu_k:.3f}</td></tr>
                <tr><td>Dampness</td><td>{surface.dampness:.2f}</td></tr>
                <tr><td>Wetness</td><td>{surface.wetness:.2f}</td></tr>
                <tr><td>Base Height</td><td>{surface.base_height:.2f} m</td></tr>
                <tr><td>Slope (X, Y)</td><td>({surface.slope_x:.4f}, {surface.slope_y:.4f})</td></tr>
                <tr><td>Surface Roughness</td><td>{surface.surface_roughness:.4f} m</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Wind Conditions</h2>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Reference Speed</td><td>{wind.ref_speed:.2f} m/s</td></tr>
                <tr><td>Reference Height</td><td>{wind.ref_height:.1f} m</td></tr>
                <tr><td>Wind Direction</td><td>{wind.direction_deg:.1f}°</td></tr>
                <tr><td>Shear Alpha</td><td>{wind.shear_alpha:.3f}</td></tr>
                <tr><td>Gust Time Constant (τ)</td><td>{wind.gust_tau:.2f} s</td></tr>
                <tr><td>Gust Intensity (σ)</td><td>{wind.gust_sigma:.2f} m/s</td></tr>
                <tr><td>Humidity</td><td>{wind.humidity_pct:.1f}%</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Physics Settings</h2>
            <table>
                <tr><th>Feature</th><th>Status</th></tr>
                <tr><td>Buoyancy</td><td>{"Enabled" if params.buoyancy else "Disabled"}</td></tr>
                <tr><td>Virtual Mass Effect</td><td>{"Enabled" if params.use_virtual_mass else "Disabled"}</td></tr>
                <tr><td>Multi-Regime Drag</td><td>{"Enabled" if params.use_multi_regime_cd else "Disabled"}</td></tr>
                <tr><td>Hertzian Contact Model</td><td>{"Enabled" if params.use_hertzian_contact else "Disabled"}</td></tr>
                <tr><td>Adaptive Timestep</td><td>{"Enabled" if params.adaptive_timestep else "Disabled"}</td></tr>
                <tr><td>Random Seed</td><td>{params.seed}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>3D Trajectory</h2>
            <div class="chart" id="plot3d"></div>
        </div>
        
        <div class="section">
            <h2>Speed and Clearance vs Time</h2>
            <div class="chart" id="plot2d"></div>
        </div>
        
        <div class="section">
            <h2>Aerodynamic Properties</h2>
            <div class="chart" id="plotAero"></div>
        </div>
    </div>
    
    <script>
    // 3D Trajectory Plot
    Plotly.newPlot('plot3d', [{{
        x: {df["X"].tolist()},
        y: {df["Y"].tolist()},
        z: {df["Z"].tolist()},
        type: 'scatter3d',
        mode: 'lines',
        line: {{ 
            color: {df["Speed"].tolist()}, 
            colorscale: 'Viridis', 
            width: 4,
            colorbar: {{ title: 'Speed (m/s)' }}
        }},
        name: 'Trajectory'
    }}, {{
        x: [{df["X"].iloc[0]}], 
        y: [{df["Y"].iloc[0]}], 
        z: [{df["Z"].iloc[0]}],
        type: 'scatter3d', 
        mode: 'markers',
        marker: {{ size: 8, color: 'green' }}, 
        name: 'Start'
    }}, {{
        x: [{df["X"].iloc[-1]}], 
        y: [{df["Y"].iloc[-1]}], 
        z: [{df["Z"].iloc[-1]}],
        type: 'scatter3d', 
        mode: 'markers',
        marker: {{ size: 8, color: 'red' }}, 
        name: 'End'
    }}], {{
        title: '3D Ball Trajectory',
        scene: {{ 
            xaxis: {{ title: 'X (m)' }}, 
            yaxis: {{ title: 'Y (m)' }}, 
            zaxis: {{ title: 'Z (m)' }}
        }},
        margin: {{ l: 0, r: 0, b: 0, t: 40 }}
    }});
    
    // 2D Speed and Clearance Plot
    Plotly.newPlot('plot2d', [{{
        x: {df["Time"].tolist()},
        y: {df["Speed"].tolist()},
        type: 'scatter', 
        mode: 'lines', 
        name: 'Speed (m/s)',
        line: {{ color: '#1f77b4' }}
    }}, {{
        x: {df["Time"].tolist()},
        y: {df["Clearance"].tolist()},
        type: 'scatter', 
        mode: 'lines', 
        name: 'Clearance (m)',
        line: {{ color: '#2ca02c' }},
        yaxis: 'y2'
    }}], {{
        title: 'Speed and Ground Clearance vs Time',
        xaxis: {{ title: 'Time (s)' }},
        yaxis: {{ title: 'Speed (m/s)' }},
        yaxis2: {{ title: 'Clearance (m)', side: 'right', overlaying: 'y' }},
        legend: {{ x: 0.02, y: 0.98 }},
        margin: {{ l: 60, r: 60, b: 40, t: 40 }}
    }});
    
    // Aerodynamic Properties Plot
    Plotly.newPlot('plotAero', [{{
        x: {df["Time"].tolist()},
        y: {df["Re"].tolist()},
        type: 'scatter', 
        mode: 'lines', 
        name: 'Reynolds Number',
        line: {{ color: '#ff7f0e' }}
    }}, {{
        x: {df["Time"].tolist()},
        y: {df["Cd"].tolist()},
        type: 'scatter', 
        mode: 'lines', 
        name: 'Drag Coefficient',
        line: {{ color: '#d62728' }},
        yaxis: 'y2'
    }}], {{
        title: 'Reynolds Number and Drag Coefficient vs Time',
        xaxis: {{ title: 'Time (s)' }},
        yaxis: {{ title: 'Reynolds Number' }},
        yaxis2: {{ title: 'Drag Coefficient', side: 'right', overlaying: 'y' }},
        legend: {{ x: 0.02, y: 0.98 }},
        margin: {{ l: 60, r: 60, b: 40, t: 40 }}
    }});
    </script>
</body>
</html>'''
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return filename


def generate_trajectory_gif(result: SimulationResult, 
                            filename: str = "ball_drop_trajectory.gif",
                            fps: int = 30) -> str:
    """
    Generate animated GIF of the ball trajectory.
    
    Parameters:
        result: SimulationResult containing trajectory data
        filename: Output GIF filename
        fps: Frames per second for the animation
    
    Returns:
        Path to the generated GIF file
    """
    stats = calculate_statistics(result)
    df = stats["df"]
    params = result.params
    R = params.radius
    
    # Downsample for reasonable animation length (max ~300 frames)
    total_frames = min(300, len(df))
    skip = max(1, len(df) // total_frames)
    df_anim = df.iloc[::skip].reset_index(drop=True)
    
    # Create figure with 3D projection
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Calculate axis limits
    x_margin = (df["X"].max() - df["X"].min()) * 0.1 + 1
    y_margin = (df["Y"].max() - df["Y"].min()) * 0.1 + 1
    z_margin = (df["Z"].max() - df["Z"].min()) * 0.1 + 1
    
    x_min, x_max = df["X"].min() - x_margin, df["X"].max() + x_margin
    y_min, y_max = df["Y"].min() - y_margin, df["Y"].max() + y_margin
    z_min, z_max = 0, df["Z"].max() + z_margin
    
    # Create ground mesh
    x_ground = np.linspace(x_min, x_max, 20)
    y_ground = np.linspace(y_min, y_max, 20)
    X_ground, Y_ground = np.meshgrid(x_ground, y_ground)
    
    def init():
        ax.clear()
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Ball Trajectory Animation')
        return []
    
    def animate(frame):
        ax.clear()
        
        # Set axis limits and labels
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_zlim(z_min, z_max)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        
        # Draw ground surface
        Z_ground = np.full_like(X_ground, df["Z_ground"].iloc[0])
        ax.plot_surface(X_ground, Y_ground, Z_ground, alpha=0.3, color='brown')
        
        # Draw trajectory trail (all points up to current frame)
        trail_x = df_anim["X"].iloc[:frame+1].values
        trail_y = df_anim["Y"].iloc[:frame+1].values
        trail_z = df_anim["Z"].iloc[:frame+1].values
        ax.plot(trail_x, trail_y, trail_z, 'b-', alpha=0.5, linewidth=1, label='Trajectory')
        
        # Draw current ball position
        current_x = df_anim["X"].iloc[frame]
        current_y = df_anim["Y"].iloc[frame]
        current_z = df_anim["Z"].iloc[frame]
        ax.scatter([current_x], [current_y], [current_z], 
                   c='red', s=100, marker='o', label='Ball')
        
        # Draw start and end markers
        ax.scatter([df_anim["X"].iloc[0]], [df_anim["Y"].iloc[0]], [df_anim["Z"].iloc[0]], 
                   c='green', s=50, marker='^', label='Start')
        if frame == len(df_anim) - 1:
            ax.scatter([df_anim["X"].iloc[-1]], [df_anim["Y"].iloc[-1]], [df_anim["Z"].iloc[-1]], 
                       c='darkred', s=50, marker='v', label='End')
        
        # Add time and height info
        current_time = df_anim["Time"].iloc[frame]
        current_speed = df_anim["Speed"].iloc[frame]
        ax.set_title(f'Ball Trajectory\nTime: {current_time:.2f}s | Height: {current_z:.1f}m | Speed: {current_speed:.1f}m/s')
        
        ax.legend(loc='upper left')
        
        return []
    
    # Create animation
    anim = FuncAnimation(fig, animate, init_func=init, 
                         frames=len(df_anim), interval=1000//fps, blit=False)
    
    # Save as GIF
    writer = PillowWriter(fps=fps)
    anim.save(filename, writer=writer)
    plt.close()
    
    return filename


def generate_all_reports(result: SimulationResult, 
                         csv_file: str = "ball_drop_data_table.csv",
                         plot_file: str = "ball_drop_2d_graph.png",
                         html_file: str = "ball_drop_report.html",
                         generate_video: bool = True,
                         video_fps: int = 30) -> dict:
    """Generate all report files including optional animated GIF."""
    files = {
        "csv": export_csv(result, csv_file),
        "plot": generate_2d_plot(result, plot_file),
        "html": generate_html_report(result, html_file)
    }
    
    # Generate animated GIF if requested
    if generate_video:
        # Derive GIF filename from the plot file path
        gif_file = os.path.join(
            os.path.dirname(plot_file),
            "ball_drop_trajectory.gif"
        )
        try:
            files["gif"] = generate_trajectory_gif(result, gif_file, video_fps)
        except Exception as e:
            print(f"Warning: Could not generate GIF: {e}")
    
    return files
