"""
Pytest fixtures for ball drop simulation tests.
"""

import pytest
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.core import run_simulation


# =========================
# Basic Fixtures
# =========================

@pytest.fixture
def default_config():
    """Standard simulation configuration for testing."""
    return {
        "scenario": "drop",
        "ball": {
            "mass": 0.5,
            "radius": 0.1,
            "spin_rps": 8.0
        },
        "position": {
            "z0": 10.0,
            "x0": 0.0,
            "y0": 0.0
        },
        "wind": {
            "humidity_pct": 50.0
        },
        "simulation": {
            "g": 9.81,
            "dt": 0.005,
            "t_max": 10.0,
            "seed": 42
        }
    }


@pytest.fixture
def no_spin_config(default_config):
    """Configuration with no spin."""
    config = default_config.copy()
    config["ball"]["spin_rps"] = 0.0
    return config


@pytest.fixture
def high_elasticity_config(default_config):
    """Configuration with high elasticity for bounce testing."""
    config = default_config.copy()
    config["surface"] = {
        "elasticity_base": 0.95,
        "elasticity_drop": 0.001
    }
    return config


@pytest.fixture
def low_elasticity_config(default_config):
    """Configuration with low elasticity for quick stop testing."""
    config = default_config.copy()
    config["surface"] = {
        "elasticity_base": 0.3,
        "elasticity_drop": 0.01
    }
    return config


@pytest.fixture
def sloped_surface_config(default_config):
    """Configuration with sloped surface for rolling tests."""
    config = default_config.copy()
    config["surface"] = {
        "elasticity_base": 0.5,
        "elasticity_drop": 0.002,
        "friction_mu_s": 0.6,
        "friction_mu_k": 0.4,
        "dampness": 0.1,
        "slope_x": 0.1,  # 10% slope in X direction
        "slope_y": 0.0,
        "base_height": 0.0
    }
    return config


@pytest.fixture
def no_wind_config(default_config):
    """Configuration with no wind."""
    config = default_config.copy()
    config["wind"] = {
        "humidity_pct": 50.0,
        "ref_speed": 0.0,
        "gust_sigma": 0.0
    }
    return config


@pytest.fixture
def simulation_result(default_config):
    """Pre-computed simulation result for testing."""
    return run_simulation(config_path=None, **default_config)


@pytest.fixture
def temp_output_dir():
    """Temporary directory for file output tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config_json(temp_output_dir):
    """Create a sample config JSON file for testing."""
    config_content = '''{
        "scenario": "drop",
        "ball": {
            "mass": 1.0,
            "radius": 0.15,
            "spin_rps": 5.0
        },
        "position": {
            "x0": 1.0,
            "y0": 2.0,
            "z0": 20.0
        },
        "wind": {
            "humidity_pct": 40.0,
            "ref_speed": 3.0,
            "ref_height": 15.0,
            "shear_alpha": 0.15,
            "direction_deg": 90.0,
            "gust_tau": 1.5,
            "gust_sigma": 0.5
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
    {"mass": 0.1, "radius": 0.05},   # Small ball
    {"mass": 0.5, "radius": 0.1},    # Medium ball
    {"mass": 2.0, "radius": 0.2},    # Large ball
])
def various_ball_configs(request):
    """Various ball configurations for testing."""
    config = {
        "scenario": "drop",
        "ball": request.param,
        "position": {"z0": 10.0},
        "wind": {"humidity_pct": 50.0},
        "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
    }
    return config


@pytest.fixture(params=[0.0, 5.0, 10.0, 20.0])
def various_initial_velocities(request):
    """Various initial velocities for testing."""
    config = {
        "scenario": "drop",
        "ball": {"mass": 0.5, "radius": 0.1, "spin_rps": 0.0},
        "position": {"z0": 10.0},
        "wind": {"humidity_pct": 50.0},
        "simulation": {"g": 9.81, "dt": 0.005, "t_max": 10.0}
    }
    return config
