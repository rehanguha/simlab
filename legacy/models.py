"""
Data models for ball drop simulation parameters.
"""

from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Any


@dataclass
class Surface:
    """Surface properties for ground contact model."""
    elasticity_base: float = 0.70
    elasticity_drop: float = 0.002
    friction_mu_s: float = 0.50
    friction_mu_k: float = 0.35
    dampness: float = 0.10
    slope_x: float = 0.0
    slope_y: float = 0.0
    base_height: float = 0.0
    rough_amp: float = 0.0
    rough_lambda_x: float = 5.0
    rough_lambda_y: float = 5.0
    wetness: float = 0.0
    surface_roughness: float = 0.0
    contact_stiffness: float = 1e7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Wind:
    """Wind conditions for simulation."""
    ref_speed: float = 2.0
    ref_height: float = 10.0
    shear_alpha: float = 0.12
    direction_deg: float = 0.0
    gust_tau: float = 2.0
    gust_sigma: float = 1.0
    humidity_pct: float = 50.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Params:
    """Simulation parameters."""
    g: float = 9.81
    mass: float = 0.5
    radius: float = 0.1
    v0: float = 10.0
    drop_angle_deg: float = 45.0
    azimuth_deg: float = 0.0
    spin_rps: float = 8.0
    spin_axis: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    c_spin_decay: float = 0.05
    c_spin_aero: float = 0.02
    dt: float = 0.005
    t_max: float = 20.0
    z0: float = 10.0
    x0: float = 0.0
    y0: float = 0.0
    stop_speed_threshold: float = 0.05
    stop_angular_threshold: float = 0.5
    stop_hold_time: float = 0.5
    buoyancy: bool = True
    seed: int = 42
    use_virtual_mass: bool = True
    use_multi_regime_cd: bool = True
    use_hertzian_contact: bool = True
    adaptive_timestep: bool = False
    rtol: float = 1e-4
    atol: float = 1e-6
    min_dt: float = 1e-5
    max_dt: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SimulationResult:
    """Container for simulation results and metadata."""
    df: Any  # pandas DataFrame
    params: Params
    surface: Surface
    wind: Wind
    stability_ok: bool = True
    energy_ok: bool = True
    max_energy_gain_pct: float = 0.0
    compute_time_ms: float = 0.0

    def get_metadata(self) -> Dict[str, Any]:
        """Get complete metadata dictionary."""
        return {
            **self.params.to_dict(),
            "surface": self.surface.to_dict(),
            "wind": self.wind.to_dict(),
            "stability_ok": self.stability_ok,
            "energy_ok": self.energy_ok,
            "max_energy_gain_pct": self.max_energy_gain_pct,
            "compute_time_ms": self.compute_time_ms
        }