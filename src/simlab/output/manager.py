"""
Output manager.

Handles saving simulation results to various formats including CSV, JSON, HTML, and plots.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class OutputManager:
    """Manages output file creation and organization."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize output manager.
        
        Args:
            output_dir (str): Output directory (auto-generated if None)
        """
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = Path(f"outputs/physimlab_{timestamp}")
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track created files
        self.output_files = {}
    
    def calculate_detailed_statistics(self, data: pd.DataFrame, config: Dict[str, Any]) -> dict:
        """Calculate comprehensive physics statistics from simulation data."""
        
        # Extract configuration parameters
        ball_config = config.get('ball', {})
        position_config = config.get('position', {})
        wind_config = config.get('wind', {})
        physics_config = config.get('simulation', {})
        
        # Physical parameters
        mass = ball_config.get('mass', 0.5)
        radius = ball_config.get('radius', 0.1)
        initial_height = position_config.get('z0', 100.0)
        
        # Environmental parameters
        humidity = wind_config.get('humidity_pct', 50.0) / 100.0
        temperature = 288.15  # Default ISA temperature
        
        # Calculate derived quantities
        data = data.copy()
        data["Speed"] = np.sqrt(data["vx"]**2 + data["vy"]**2 + data["vz"]**2)
        data["Z_bottom"] = data["z"] - radius
        data["Clearance"] = data["z"] - radius  # Assuming flat ground at z=0
        
        # Calculate air properties
        data["AirDensity"] = self._calculate_air_density(temperature, humidity)
        data["Mu"] = self._calculate_viscosity(temperature)
        data["SpeedOfSound"] = self._calculate_speed_of_sound(temperature)
        
        # Calculate Reynolds number and drag coefficient
        data["Re"] = self._calculate_reynolds_number(data["AirDensity"], data["Speed"], radius, data["Mu"])
        data["Cd"] = self._calculate_drag_coefficient(data["Re"])
        
        # Calculate Mach number
        data["Mach"] = data["Speed"] / data["SpeedOfSound"]
        
        # Calculate energy
        g = physics_config.get('g', 9.81)
        data["KineticEnergy"] = 0.5 * mass * data["Speed"]**2
        data["PotentialEnergy"] = mass * g * data["z"]
        data["TotalEnergy"] = data["KineticEnergy"] + data["PotentialEnergy"]
        
        # Calculate energy loss
        initial_energy = data["TotalEnergy"].iloc[0]
        final_energy = data["TotalEnergy"].iloc[-1]
        energy_loss = initial_energy - final_energy
        energy_loss_pct = (energy_loss / initial_energy) * 100 if initial_energy > 0 else 0
        
        # Basic statistics
        max_height = data["z"].max()
        total_distance = np.sqrt(
            (data["x"].iloc[-1] - data["x"].iloc[0])**2 + 
            (data["y"].iloc[-1] - data["y"].iloc[0])**2
        )
        flight_time = data["time"].iloc[-1]
        
        # Count bounces (simplified - when z is very small)
        bounce_count = 0
        z_values = data["z"]
        for i in range(1, len(z_values)):
            if z_values.iloc[i-1] > 0.001 and z_values.iloc[i] <= 0.001:
                bounce_count += 1
        
        # Stability check
        is_stable = True
        max_speed = data["Speed"].max()
        if max_speed > 1000:  # Arbitrary threshold for instability
            is_stable = False
        
        # Energy conservation check
        energy_conserved = True
        max_energy_gain = 0
        for i in range(1, len(data)):
            if data["TotalEnergy"].iloc[i] > data["TotalEnergy"].iloc[i-1]:
                gain = data["TotalEnergy"].iloc[i] - data["TotalEnergy"].iloc[i-1]
                max_energy_gain = max(max_energy_gain, gain)
        
        if max_energy_gain > initial_energy * 0.01:  # More than 1% energy gain
            energy_conserved = False
        
        return {
            "max_height": max_height,
            "total_distance": total_distance,
            "flight_time": flight_time,
            "max_speed": data["Speed"].max(),
            "max_mach": data["Mach"].max(),
            "max_reynolds": data["Re"].max(),
            "bounce_count": bounce_count,
            "timestep_count": len(data),
            "dt_min": data["time"].diff().min(),
            "dt_max": data["time"].diff().max(),
            "energy_loss": energy_loss,
            "energy_loss_pct": energy_loss_pct,
            "is_stable": is_stable,
            "energy_conserved": energy_conserved,
            "max_energy_gain": max_energy_gain,
            "max_energy_gain_pct": (max_energy_gain / initial_energy) * 100 if initial_energy > 0 else 0,
            "df": data
        }
    
    def _calculate_air_density(self, temperature: float, humidity: float) -> float:
        """Calculate air density with humidity correction."""
        # Basic density calculation (simplified)
        p0 = 101325  # Pa
        R_d = 287.058  # J/(kg*K)
        R_v = 461.495  # J/(kg*K)
        
        # Saturation vapor pressure (Buck equation)
        T_c = temperature - 273.15
        e_s = 611.21 * np.exp((18.678 - T_c/234.5) * T_c / (257.14 + T_c))
        e = e_s * humidity
        
        # Density calculation
        rho_dry = p0 / (R_d * temperature)
        rho_vapor = e / (R_v * temperature)
        
        return float(rho_dry + rho_vapor)
    
    def _calculate_viscosity(self, temperature: float) -> float:
        """Calculate dynamic viscosity using Sutherland's law."""
        mu_ref = 1.716e-5
        T_ref = 273.15
        S = 111
        
        return mu_ref * (temperature / T_ref)**1.5 * (T_ref + S) / (temperature + S)
    
    def _calculate_speed_of_sound(self, temperature: float) -> float:
        """Calculate speed of sound."""
        gamma = 1.4
        R = 287.058
        
        return np.sqrt(gamma * R * temperature)
    
    def _calculate_reynolds_number(self, density: float, speed: float, radius: float, viscosity: float) -> float:
        """Calculate Reynolds number."""
        if np.any(speed < 1e-6) or np.any(viscosity < 1e-6):
            return 0.0
        return 2 * radius * speed * density / viscosity
    
    def _calculate_drag_coefficient(self, reynolds: float) -> float:
        """Calculate drag coefficient using multi-regime correlation."""
        if np.any(reynolds <= 1):
            return 24 / reynolds
        elif np.any(reynolds <= 1000):
            return (24 / reynolds) * (1 + 0.15 * reynolds**0.687)
        else:
            return 0.44
    
    def save_data(self, data: pd.DataFrame) -> None:
        """Save simulation data to CSV."""
        csv_path = self.output_dir / "data.csv"
        data.to_csv(csv_path, index=False)
        self.output_files['data'] = str(csv_path)
    
    def save_summary(self, summary: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Save summary statistics and configuration to JSON."""
        summary_data = {
            'summary': summary,
            'config': config,
            'timestamp': datetime.now().isoformat()
        }
        
        json_path = self.output_dir / "summary.json"
        with open(json_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        self.output_files['summary'] = str(json_path)
    
    def save_plots(self, data: pd.DataFrame) -> None:
        """Save various plots."""
        plots_dir = self.output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Height vs Time
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data['time'], data['z'], 'b-', linewidth=2)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Height (m)')
        ax.set_title('Height vs Time')
        ax.grid(True, alpha=0.3)
        plt.savefig(plots_dir / 'height_vs_time.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Velocity vs Time
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data['time'], data['vx'], 'r-', label='Vx', linewidth=2)
        ax.plot(data['time'], data['vy'], 'g-', label='Vy', linewidth=2)
        ax.plot(data['time'], data['vz'], 'b-', label='Vz', linewidth=2)
        ax.plot(data['time'], data['speed'], 'k-', label='Speed', linewidth=2)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Velocity Components vs Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.savefig(plots_dir / 'velocity_vs_time.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2D Trajectory
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data['x'], data['z'], 'b-', linewidth=2)
        ax.set_xlabel('Horizontal Distance (m)')
        ax.set_ylabel('Height (m)')
        ax.set_title('2D Trajectory')
        ax.grid(True, alpha=0.3)
        plt.savefig(plots_dir / '2d_trajectory.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3D Trajectory
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(data['x'], data['y'], data['z'], 'b-', linewidth=2)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('3D Trajectory')
        plt.savefig(plots_dir / '3d_trajectory.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        self.output_files['plots'] = str(plots_dir)
    
    def save_html_report(self, data: pd.DataFrame, summary: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Save comprehensive interactive HTML report."""
        
        # Generate detailed HTML report
        html_content = self._generate_detailed_html_report(data, summary, config)
        
        # Save HTML
        html_path = self.output_dir / "report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.output_files['html'] = str(html_path)
    
    def _generate_detailed_html_report(self, data: pd.DataFrame, summary: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report with all sections."""
        
        # Calculate additional statistics
        stats = self.calculate_detailed_statistics(data, config)
        
        # Generate all plotly figures
        figures_html = self._generate_all_figures_html(data, stats)
        
        # Generate all tables HTML
        tables_html = self._generate_all_tables_html(summary, config, stats)
        
        # Generate CSS styles
        css_styles = self._get_report_css()
        
        # Generate JavaScript for interactivity
        js_scripts = self._get_report_javascript()
        
        # Combine all sections into complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>physimlab Simulation Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{css_styles}</style>
</head>
<body>
    <div class="container">
        {self._generate_header_html(config)}
        {tables_html}
        {figures_html}
        {js_scripts}
    </div>
</body>
</html>"""
        
        return html_content
    
    def _generate_header_html(self, config: Dict[str, Any]) -> str:
        """Generate report header with title and timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
        <div class="header">
            <h1>Ball Drop Simulation Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
        """
    
    def _generate_all_tables_html(self, summary: Dict[str, Any], config: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generate all HTML tables for the report."""
        return f"""
        {self._generate_summary_statistics_html(summary, stats)}
        {self._generate_simulation_status_html(summary, stats)}
        {self._generate_ball_parameters_html(config)}
        {self._generate_surface_properties_html(config)}
        {self._generate_wind_conditions_html(config)}
        {self._generate_physics_settings_html(config)}
        """
    
    def _generate_summary_statistics_html(self, summary: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generate Summary Statistics table."""
        return f"""
        <div class="section">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{summary.get('flight_time', 0):.3f}</div>
                    <div class="stat-label">Flight Time (s)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{summary.get('max_height', 0):.2f}</div>
                    <div class="stat-label">Max Height (m)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{summary.get('horizontal_range', 0):.2f}</div>
                    <div class="stat-label">Horizontal Distance (m)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{summary.get('max_velocity', 0):.2f}</div>
                    <div class="stat-label">Max Speed (m/s)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{summary.get('max_mach', 0):.4f}</div>
                    <div class="stat-label">Max Mach Number</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('max_reynolds', 0):.2e}</div>
                    <div class="stat-label">Max Reynolds Number</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{summary.get('ground_contacts', 0)}</div>
                    <div class="stat-label">Ground Contacts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{'{:.2f}'.format(stats.get('compute_time', 0))}</div>
                    <div class="stat-label">Compute Time (ms)</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_simulation_status_html(self, summary: Dict[str, Any], stats: Dict[str, Any]) -> str:
        """Generate Simulation Status table."""
        stability_status = "PASS" if stats.get('is_stable', True) else "FAIL"
        energy_status = "PASS" if stats.get('energy_conserved', True) else "FAIL"
        
        return f"""
        <div class="section">
            <h2>Simulation Status</h2>
            <table class="data-table">
                <tr><td>Numerical Stability</td><td class="status-{stability_status.lower()}">{stability_status}</td></tr>
                <tr><td>Energy Conservation</td><td class="status-{energy_status.lower()}">{energy_status}</td></tr>
                <tr><td>Max Energy Gain</td><td>{stats.get('max_energy_gain_pct', 0):.2f}%</td></tr>
                <tr><td>Time Steps</td><td>{stats.get('timestep_count', 0)}</td></tr>
                <tr><td>dt Range</td><td>{stats.get('dt_min', 0):.6f} - {stats.get('dt_max', 0):.6f} s</td></tr>
            </table>
        </div>
        """
    
    def _generate_ball_parameters_html(self, config: Dict[str, Any]) -> str:
        """Generate Ball Parameters table."""
        ball_config = config.get('ball', {})
        position_config = config.get('position', {})
        physics_config = config.get('simulation', {})
        
        return f"""
        <div class="section">
            <h2>Ball Parameters</h2>
            <table class="data-table">
                <tr><td>Mass</td><td>{ball_config.get('mass', 0):.4f} kg</td></tr>
                <tr><td>Radius</td><td>{ball_config.get('radius', 0):.4f} m</td></tr>
                <tr><td>Initial Velocity</td><td>{ball_config.get('initial_velocity', 0):.2f} m/s</td></tr>
                <tr><td>Drop Angle</td><td>{ball_config.get('drop_angle_deg', 0):.1f}°</td></tr>
                <tr><td>Azimuth</td><td>{ball_config.get('azimuth_deg', 0):.1f}°</td></tr>
                <tr><td>Initial Position (X, Y, Z)</td><td>({position_config.get('x0', 0):.2f}, {position_config.get('y0', 0):.2f}, {position_config.get('z0', 0):.2f}) m</td></tr>
                <tr><td>Spin Rate</td><td>{ball_config.get('spin_rps', 0):.1f} rps</td></tr>
                <tr><td>Spin Axis</td><td>({ball_config.get('spin_axis', [0,0,1])[0]:.1f}, {ball_config.get('spin_axis', [0,0,1])[1]:.1f}, {ball_config.get('spin_axis', [0,0,1])[2]:.1f})</td></tr>
                <tr><td>Gravity</td><td>{physics_config.get('g', 9.81):.4f} m/s²</td></tr>
            </table>
        </div>
        """
    
    def _generate_surface_properties_html(self, config: Dict[str, Any]) -> str:
        """Generate Surface Properties table."""
        surface_config = config.get('surface', {})
        
        return f"""
        <div class="section">
            <h2>Surface Properties</h2>
            <table class="data-table">
                <tr><td>Elasticity (Base)</td><td>{surface_config.get('elasticity_base', 0):.3f}</td></tr>
                <tr><td>Elasticity Drop</td><td>{surface_config.get('elasticity_drop', 0):.4f}</td></tr>
                <tr><td>Static Friction (μs)</td><td>{surface_config.get('friction_mu_s', 0):.3f}</td></tr>
                <tr><td>Kinetic Friction (μk)</td><td>{surface_config.get('friction_mu_k', 0):.3f}</td></tr>
                <tr><td>Dampness</td><td>{surface_config.get('dampness', 0):.2f}</td></tr>
                <tr><td>Wetness</td><td>{surface_config.get('wetness', 0):.2f}</td></tr>
                <tr><td>Base Height</td><td>{surface_config.get('base_height', 0):.2f} m</td></tr>
                <tr><td>Slope (X, Y)</td><td>({surface_config.get('slope_x', 0):.4f}, {surface_config.get('slope_y', 0):.4f})</td></tr>
                <tr><td>Surface Roughness</td><td>{surface_config.get('surface_roughness', 0):.4f} m</td></tr>
            </table>
        </div>
        """
    
    def _generate_wind_conditions_html(self, config: Dict[str, Any]) -> str:
        """Generate Wind Conditions table."""
        wind_config = config.get('wind', {})
        
        return f"""
        <div class="section">
            <h2>Wind Conditions</h2>
            <table class="data-table">
                <tr><td>Reference Speed</td><td>{wind_config.get('ref_speed', 0):.2f} m/s</td></tr>
                <tr><td>Reference Height</td><td>{wind_config.get('ref_height', 0):.1f} m</td></tr>
                <tr><td>Wind Direction</td><td>{wind_config.get('direction_deg', 0):.1f}°</td></tr>
                <tr><td>Shear Alpha</td><td>{wind_config.get('shear_alpha', 0):.3f}</td></tr>
                <tr><td>Gust Time Constant (τ)</td><td>{wind_config.get('gust_tau', 0):.2f} s</td></tr>
                <tr><td>Gust Intensity (σ)</td><td>{wind_config.get('gust_sigma', 0):.2f} m/s</td></tr>
                <tr><td>Humidity</td><td>{wind_config.get('humidity_pct', 0):.1f}%</td></tr>
            </table>
        </div>
        """
    
    def _generate_physics_settings_html(self, config: Dict[str, Any]) -> str:
        """Generate Physics Settings table."""
        sim_config = config.get('simulation', {})
        
        return f"""
        <div class="section">
            <h2>Physics Settings</h2>
            <table class="data-table">
                <tr><td>Buoyancy</td><td>{'Enabled' if sim_config.get('buoyancy', True) else 'Disabled'}</td></tr>
                <tr><td>Virtual Mass Effect</td><td>{'Enabled' if sim_config.get('use_virtual_mass', True) else 'Disabled'}</td></tr>
                <tr><td>Multi-Regime Drag</td><td>{'Enabled' if sim_config.get('use_multi_regime_cd', True) else 'Disabled'}</td></tr>
                <tr><td>Hertzian Contact Model</td><td>{'Enabled' if sim_config.get('use_hertzian_contact', True) else 'Disabled'}</td></tr>
                <tr><td>Adaptive Timestep</td><td>{'Enabled' if sim_config.get('adaptive_timestep', False) else 'Disabled'}</td></tr>
                <tr><td>Random Seed</td><td>{config.get('simulation', {}).get('seed', 42)}</td></tr>
            </table>
        </div>
        """
    
    def _generate_all_figures_html(self, data: pd.DataFrame, stats: Dict[str, Any]) -> str:
        """Generate all Plotly figures HTML."""
        return f"""
        {self._generate_3d_trajectory_html(data)}
        {self._generate_speed_clearance_html(data, stats)}
        {self._generate_aerodynamic_properties_html(data, stats)}
        """
    
    def _generate_3d_trajectory_html(self, data: pd.DataFrame) -> str:
        """Generate 3D trajectory plot."""
        fig = go.Figure(data=[go.Scatter3d(
            x=data['x'],
            y=data['y'],
            z=data['z'],
            mode='lines',
            line=dict(color='blue', width=4),
            name='Trajectory'
        )])
        
        fig.update_layout(
            title='3D Trajectory',
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=600,
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        return f"""
        <div class="section">
            <h2>3D Trajectory</h2>
            <div id="plot-3d" class="plot-container"></div>
            <script>
                Plotly.newPlot('plot-3d', {fig.to_json()});
            </script>
        </div>
        """
    
    def _generate_speed_clearance_html(self, data: pd.DataFrame, stats: Dict[str, Any]) -> str:
        """Generate Speed and Clearance vs Time plot."""
        # Calculate clearance (height - radius)
        radius = stats.get('df', data)['radius'].iloc[0] if 'radius' in stats.get('df', data).columns else 0.2
        clearance = data['z'] - radius
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Speed plot
        fig.add_trace(
            go.Scatter(x=data['time'], y=data['Speed'], name='Speed', line=dict(color='blue')),
            secondary_y=False,
        )
        
        # Clearance plot
        fig.add_trace(
            go.Scatter(x=data['time'], y=clearance, name='Clearance', line=dict(color='red')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time (s)")
        fig.update_yaxes(title_text="Speed (m/s)", secondary_y=False)
        fig.update_yaxes(title_text="Clearance (m)", secondary_y=True)
        
        fig.update_layout(
            title='Speed and Clearance vs Time',
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return f"""
        <div class="section">
            <h2>Speed and Clearance vs Time</h2>
            <div id="plot-speed-clearance" class="plot-container"></div>
            <script>
                Plotly.newPlot('plot-speed-clearance', {fig.to_json()});
            </script>
        </div>
        """
    
    def _generate_aerodynamic_properties_html(self, data: pd.DataFrame, stats: Dict[str, Any]) -> str:
        """Generate Aerodynamic Properties plot (Reynolds number and drag coefficient)."""
        df = stats.get('df', data)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Reynolds number plot
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['Re'], name='Reynolds Number', line=dict(color='green')),
            secondary_y=False,
        )
        
        # Drag coefficient plot
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['Cd'], name='Drag Coefficient', line=dict(color='orange')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time (s)")
        fig.update_yaxes(title_text="Reynolds Number", secondary_y=False)
        fig.update_yaxes(title_text="Drag Coefficient", secondary_y=True)
        
        fig.update_layout(
            title='Aerodynamic Properties',
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return f"""
        <div class="section">
            <h2>Aerodynamic Properties</h2>
            <div id="plot-aero" class="plot-container"></div>
            <script>
                Plotly.newPlot('plot-aero', {fig.to_json()});
            </script>
        </div>
        """
    
    def _get_report_css(self) -> str:
        """Get CSS styles for the report."""
        return """
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --bg-color: #f8f9fa;
            --text-color: #333;
            --card-bg: #ffffff;
            --border-color: #dee2e6;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: var(--card-bg);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            color: var(--primary-color);
            margin-bottom: 10px;
            font-size: 2.5rem;
        }
        
        .timestamp {
            color: var(--secondary-color);
            font-size: 1.1rem;
        }
        
        .section {
            background: var(--card-bg);
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
            font-size: 1.5rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--border-color);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--secondary-color);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 1rem;
        }
        
        .data-table th, .data-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .data-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .data-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-pass {
            color: var(--success-color);
            font-weight: bold;
        }
        
        .status-fail {
            color: var(--danger-color);
            font-weight: bold;
        }
        
        .plot-container {
            width: 100%;
            height: 600px;
            margin: 20px 0;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .section {
                padding: 15px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .plot-container {
                height: 400px;
            }
        }
        """
    
    def _get_report_javascript(self) -> str:
        """Get JavaScript for report interactivity."""
        return """
        <script>
        // Add any additional JavaScript for interactivity here
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize tooltips or other interactive elements
            console.log('physimlab Report loaded successfully');
        });
        </script>
        """
    
    def save_animation(self, data: pd.DataFrame) -> None:
        """Save animated GIF of the trajectory."""
        try:
            from PIL import Image
            import io
            
            frames = []
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create frames for animation
            for i in range(0, len(data), 10):  # Every 10th frame
                ax.clear()
                ax.plot(data['x'][:i+1], data['z'][:i+1], 'b-', linewidth=2, alpha=0.3)
                ax.plot(data['x'][i], data['z'][i], 'ro', markersize=8)
                ax.set_xlabel('Horizontal Distance (m)')
                ax.set_ylabel('Height (m)')
                ax.set_title(f'Trajectory Animation - t={data["time"][i]:.2f}s')
                ax.grid(True, alpha=0.3)
                ax.set_xlim(data['x'].min() - 1, data['x'].max() + 1)
                ax.set_ylim(data['z'].min() - 1, data['z'].max() + 1)
                
                # Save frame to buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100)
                buf.seek(0)
                frames.append(Image.open(buf))
            
            # Save as GIF
            gif_path = self.output_dir / "trajectory.gif"
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=100,
                loop=0
            )
            
            self.output_files['animation'] = str(gif_path)
            
        except ImportError:
            # PIL not available
            pass
    
    def save_comparison(self, comparison: Dict[str, Any], result1, result2) -> None:
        """Save comparison between two results."""
        comparison_data = {
            'comparison': comparison,
            'result1_summary': result1.summary,
            'result2_summary': result2.summary,
            'timestamp': datetime.now().isoformat()
        }
        
        comparison_path = self.output_dir / "comparison.json"
        with open(comparison_path, 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        self.output_files['comparison'] = str(comparison_path)
    
    def save_all(self, result) -> None:
        """
        Save all output files for a simulation result.
        
        Args:
            result: Simulation result object
        """
        # Calculate detailed statistics
        stats = self.calculate_detailed_statistics(result.data, result.config)
        
        # Save data
        self.save_data(stats["df"])
        
        # Save enhanced summary
        enhanced_summary = result.summary.copy()
        enhanced_summary.update({
            "max_speed": stats["max_speed"],
            "max_mach": stats["max_mach"],
            "max_reynolds": stats["max_reynolds"],
            "bounce_count": stats["bounce_count"],
            "energy_loss": stats["energy_loss"],
            "energy_loss_pct": stats["energy_loss_pct"],
            "is_stable": stats["is_stable"],
            "energy_conserved": stats["energy_conserved"],
            "max_energy_gain": stats["max_energy_gain"],
            "max_energy_gain_pct": stats["max_energy_gain_pct"],
        })
        
        self.save_summary(enhanced_summary, result.config)
        
        # Save plots
        self.save_plots(stats["df"])
        
        # Save HTML report
        self.save_html_report(stats["df"], enhanced_summary, result.config)
        
        # Save GIF animation
        self.save_animation(stats["df"])
    
    def get_output_files(self) -> Dict[str, str]:
        """Get dictionary of created output files."""
        return self.output_files.copy()
