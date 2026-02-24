"""
Configuration loader for ball drop simulation.
Loads parameters from JSON file and creates model objects.
"""

import json
from typing import Tuple
from models import Params, Surface, Wind


class ConfigLoader:
    """Load and parse simulation configuration from JSON file."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration loader.
        
        Parameters:
            config_path: Path to JSON configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load JSON configuration file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_params(self) -> Params:
        """Create Params object from configuration."""
        ball = self.config.get('ball', {})
        position = self.config.get('position', {})
        sim = self.config.get('simulation', {})
        
        spin_axis = ball.get('spin_axis', [0.0, 0.0, 1.0])
        
        return Params(
            g=sim.get('g', 9.81),
            mass=ball.get('mass', 0.5),
            radius=ball.get('radius', 0.1),
            v0=ball.get('initial_velocity', 10.0),
            drop_angle_deg=ball.get('drop_angle_deg', 45.0),
            azimuth_deg=ball.get('azimuth_deg', 0.0),
            spin_rps=ball.get('spin_rps', 8.0),
            spin_axis=(spin_axis[0], spin_axis[1], spin_axis[2]),
            c_spin_decay=sim.get('c_spin_decay', 0.05),
            c_spin_aero=sim.get('c_spin_aero', 0.02),
            dt=sim.get('dt', 0.005),
            t_max=sim.get('t_max', 20.0),
            z0=position.get('z0', 10.0),
            x0=position.get('x0', 0.0),
            y0=position.get('y0', 0.0),
            stop_speed_threshold=sim.get('stop_speed_threshold', 0.05),
            stop_angular_threshold=sim.get('stop_angular_threshold', 0.5),
            stop_hold_time=sim.get('stop_hold_time', 0.5),
            buoyancy=sim.get('buoyancy', True),
            seed=sim.get('seed', 42),
            use_virtual_mass=sim.get('use_virtual_mass', True),
            use_multi_regime_cd=sim.get('use_multi_regime_cd', True),
            use_hertzian_contact=sim.get('use_hertzian_contact', True),
            adaptive_timestep=sim.get('adaptive_timestep', False),
            rtol=sim.get('rtol', 1e-4),
            atol=sim.get('atol', 1e-6),
            min_dt=sim.get('min_dt', 1e-5),
            max_dt=sim.get('max_dt', 0.05)
        )
    
    def get_surface(self) -> Surface:
        """Create Surface object from configuration."""
        surf = self.config.get('surface', {})
        
        return Surface(
            elasticity_base=surf.get('elasticity_base', 0.70),
            elasticity_drop=surf.get('elasticity_drop', 0.002),
            friction_mu_s=surf.get('friction_mu_s', 0.50),
            friction_mu_k=surf.get('friction_mu_k', 0.35),
            dampness=surf.get('dampness', 0.10),
            slope_x=surf.get('slope_x', 0.0),
            slope_y=surf.get('slope_y', 0.0),
            base_height=surf.get('base_height', 0.0),
            rough_amp=surf.get('rough_amp', 0.0),
            rough_lambda_x=surf.get('rough_lambda_x', 5.0),
            wetness=surf.get('wetness', 0.0),
            surface_roughness=surf.get('surface_roughness', 0.0),
            contact_stiffness=surf.get('contact_stiffness', 1e7)
        )
    
    def get_wind(self) -> Wind:
        """Create Wind object from configuration."""
        w = self.config.get('wind', {})
        
        return Wind(
            ref_speed=w.get('ref_speed', 2.0),
            ref_height=w.get('ref_height', 10.0),
            shear_alpha=w.get('shear_alpha', 0.12),
            direction_deg=w.get('direction_deg', 0.0),
            gust_tau=w.get('gust_tau', 2.0),
            gust_sigma=w.get('gust_sigma', 1.0),
            humidity_pct=w.get('humidity_pct', 50.0)
        )
    
    def get_output_settings(self) -> dict:
        """Get output file settings."""
        output = self.config.get('output', {})
        return {
            'run_name': output.get('run_name', 'simulation'),
            'output_dir': output.get('output_dir', 'outputs'),
            'csv_file': output.get('csv_file', 'ball_drop_data_table.csv'),
            'plot_file': output.get('plot_file', 'ball_drop_2d_graph.png'),
            'html_file': output.get('html_file', 'ball_drop_report.html'),
            'generate_video': output.get('generate_video', True),
            'video_fps': output.get('video_fps', 30),
            'verbose': output.get('verbose', True)
        }


def load_config(config_path: str = "config.json") -> Tuple[Params, Surface, Wind, dict]:
    """
    Load all configuration from JSON file.
    
    Parameters:
        config_path: Path to JSON configuration file
    
    Returns:
        Tuple of (Params, Surface, Wind, output_settings)
    """
    loader = ConfigLoader(config_path)
    return (
        loader.get_params(),
        loader.get_surface(),
        loader.get_wind(),
        loader.get_output_settings()
    )