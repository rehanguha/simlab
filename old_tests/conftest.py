"""
Pytest fixtures for ball drop simulation tests.
"""

import pytest
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind
from simulation import simulate_drop


# =========================
# Basic Fixtures
# =========================

@pytest.fixture
def default_params():
    """Standard simulation parameters for testing."""
    return Params(
        mass=0.5,
        radius=0.1,
        v0=10.0,
        drop_angle_deg=45.0,
        azimuth_deg=0.0,
        spin_rps=8.0,
        spin_axis=(0.0, 0.0, 1.0),
        z0=10.0,
        x0=0.0,
        y0=0.0,
        dt=0.005,
        t_max=10.0,
        seed=42
    )


@pytest.fixture
def default_surface():
    """Standard surface properties for testing."""
    return Surface(
        elasticity_base=0.75,
        elasticity_drop=0.002,
        friction_mu_s=0.5,
        friction_mu_k=0.35,
        dampness=0.1,
        slope_x=0.0,
        slope_y=0.0,
        base_height=0.0,
        rough_amp=0.0,
        rough_lambda_x=5.0,
        wetness=0.0,
        surface_roughness=0.0
    )


@pytest.fixture
def default_wind():
    """Standard wind conditions for testing."""
    return Wind(
        ref_speed=2.0,
        ref_height=10.0,
        shear_alpha=0.12,
        direction_deg=0.0,
        gust_tau=2.0,
        gust_sigma=1.0,
        humidity_pct=50.0
    )


@pytest.fixture
def no_wind():
    """No wind conditions for testing."""
    return Wind(
        ref_speed=0.0,
        ref_height=10.0,
        shear_alpha=0.12,
        direction_deg=0.0,
        gust_tau=2.0,
        gust_sigma=0.0,
        humidity_pct=50.0
    )


@pytest.fixture
def no_spin_params(default_params):
    """Parameters with no spin."""
    params = default_params
    params.spin_rps = 0.0
    return params


@pytest.fixture
def high_elasticity_surface(default_surface):
    """Surface with high elasticity for bounce testing."""
    surface = default_surface
    surface.elasticity_base = 0.95
    surface.elasticity_drop = 0.001
    return surface


@pytest.fixture
def low_elasticity_surface(default_surface):
    """Surface with low elasticity for quick stop testing."""
    surface = default_surface
    surface.elasticity_base = 0.3
    surface.elasticity_drop = 0.01
    return surface


@pytest.fixture
def sloped_surface():
    """Sloped surface for rolling tests."""
    return Surface(
        elasticity_base=0.5,
        elasticity_drop=0.002,
        friction_mu_s=0.6,
        friction_mu_k=0.4,
        dampness=0.1,
        slope_x=0.1,  # 10% slope in X direction
        slope_y=0.0,
        base_height=0.0,
        rough_amp=0.0,
        rough_lambda_x=5.0,
        wetness=0.0,
        surface_roughness=0.0
    )


@pytest.fixture
def simulation_result(default_params, default_surface, default_wind):
    """Pre-computed simulation result for testing."""
    return simulate_drop(default_params, default_surface, default_wind)


@pytest.fixture
def temp_output_dir():
    """Temporary directory for file output tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config_json(temp_output_dir):
    """Create a sample config JSON file for testing."""
    config_content = '''{
        "ball": {
            "mass": 1.0,
            "radius": 0.15,
            "initial_velocity": 15.0,
            "drop_angle_deg": 30.0,
            "azimuth_deg": 45.0,
            "spin_rps": 5.0,
            "spin_axis": [1.0, 0.0, 0.0]
        },
        "position": {
            "x0": 1.0,
            "y0": 2.0,
            "z0": 20.0
        },
        "surface": {
            "elasticity_base": 0.8,
            "elasticity_drop": 0.001,
            "friction_mu_s": 0.6,
            "friction_mu_k": 0.4,
            "dampness": 0.05,
            "wetness": 0.1,
            "base_height": 0.5,
            "slope_x": 0.01,
            "slope_y": 0.02,
            "rough_amp": 0.01,
            "rough_lambda_x": 3.0,
            "surface_roughness": 0.0005
        },
        "wind": {
            "ref_speed": 3.0,
            "ref_height": 15.0,
            "shear_alpha": 0.15,
            "direction_deg": 90.0,
            "gust_tau": 1.5,
            "gust_sigma": 0.5,
            "humidity_pct": 40.0
        },
        "simulation": {
            "g": 9.81,
            "dt": 0.002,
            "t_max": 15.0,
            "seed": 123,
            "adaptive_timestep": false,
            "buoyancy": true,
            "use_virtual_mass": true,
            "use_multi_regime_cd": true,
            "use_hertzian_contact": true
        },
        "output": {
            "run_name": "test_run",
            "output_dir": "outputs",
            "csv_file": "test_data.csv",
            "plot_file": "test_plot.png",
            "html_file": "test_report.html"
        }
    }'''
    config_path = os.path.join(temp_output_dir, "test_config.json")
    with open(config_path, 'w') as f:
        f.write(config_content)
    return config_path


# =========================
# Parametrized Fixtures
# =========================

@pytest.fixture(params=[
    (0.1, 0.05),   # Small ball
    (0.5, 0.1),    # Medium ball
    (2.0, 0.2),    # Large ball
])
def various_ball_sizes(request):
    """Various ball masses and radii for testing."""
    mass, radius = request.param
    return Params(mass=mass, radius=radius, z0=10.0)


@pytest.fixture(params=[0.0, 45.0, 90.0])
def various_drop_angles(request):
    """Various drop angles for testing."""
    return Params(drop_angle_deg=request.param, z0=10.0)


@pytest.fixture(params=[0.0, 5.0, 10.0, 20.0])
def various_initial_velocities(request):
    """Various initial velocities for testing."""
    return Params(v0=request.param, z0=10.0)