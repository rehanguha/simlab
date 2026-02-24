"""
Comprehensive tests for models.py module.
Tests all dataclasses: Params, Surface, Wind, SimulationResult.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind, SimulationResult


# =========================
# Params Tests
# =========================

class TestParamsDefaults:
    """Test Params dataclass default values."""
    
    def test_default_mass(self):
        """Test default mass value."""
        params = Params()
        assert params.mass == 0.5
    
    def test_default_radius(self):
        """Test default radius value."""
        params = Params()
        assert params.radius == 0.1
    
    def test_default_initial_velocity(self):
        """Test default initial velocity."""
        params = Params()
        assert params.v0 == 10.0
    
    def test_default_drop_angle(self):
        """Test default drop angle."""
        params = Params()
        assert params.drop_angle_deg == 45.0
    
    def test_default_azimuth(self):
        """Test default azimuth angle."""
        params = Params()
        assert params.azimuth_deg == 0.0
    
    def test_default_spin_rps(self):
        """Test default spin rate."""
        params = Params()
        assert params.spin_rps == 8.0
    
    def test_default_spin_axis(self):
        """Test default spin axis."""
        params = Params()
        assert params.spin_axis == (0.0, 0.0, 1.0)
    
    def test_default_gravity(self):
        """Test default gravity."""
        params = Params()
        assert params.g == 9.81
    
    def test_default_timestep(self):
        """Test default timestep."""
        params = Params()
        assert params.dt == 0.005
    
    def test_default_max_time(self):
        """Test default max time."""
        params = Params()
        assert params.t_max == 20.0
    
    def test_default_initial_position(self):
        """Test default initial position."""
        params = Params()
        assert params.x0 == 0.0
        assert params.y0 == 0.0
        assert params.z0 == 10.0
    
    def test_default_stop_thresholds(self):
        """Test default stop thresholds."""
        params = Params()
        assert params.stop_speed_threshold == 0.05
        assert params.stop_angular_threshold == 0.5
        assert params.stop_hold_time == 0.5
    
    def test_default_physics_flags(self):
        """Test default physics feature flags."""
        params = Params()
        assert params.buoyancy is True
        assert params.use_virtual_mass is True
        assert params.use_multi_regime_cd is True
        assert params.use_hertzian_contact is True
        assert params.adaptive_timestep is False
    
    def test_default_seed(self):
        """Test default random seed."""
        params = Params()
        assert params.seed == 42


class TestParamsCustomValues:
    """Test Params with custom values."""
    
    def test_custom_mass(self):
        """Test custom mass value."""
        params = Params(mass=2.5)
        assert params.mass == 2.5
    
    def test_custom_position(self):
        """Test custom initial position."""
        params = Params(x0=5.0, y0=3.0, z0=50.0)
        assert params.x0 == 5.0
        assert params.y0 == 3.0
        assert params.z0 == 50.0
    
    def test_custom_spin_axis(self):
        """Test custom spin axis."""
        params = Params(spin_axis=(1.0, 0.0, 0.0))
        assert params.spin_axis == (1.0, 0.0, 0.0)
    
    def test_custom_velocity_and_angles(self):
        """Test custom velocity and angles."""
        params = Params(v0=20.0, drop_angle_deg=60.0, azimuth_deg=45.0)
        assert params.v0 == 20.0
        assert params.drop_angle_deg == 60.0
        assert params.azimuth_deg == 45.0
    
    def test_custom_timestep_settings(self):
        """Test custom timestep settings."""
        params = Params(dt=0.001, t_max=30.0, adaptive_timestep=True)
        assert params.dt == 0.001
        assert params.t_max == 30.0
        assert params.adaptive_timestep is True


class TestParamsToDict:
    """Test Params serialization."""
    
    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        params = Params()
        d = params.to_dict()
        assert isinstance(d, dict)
    
    def test_to_dict_contains_all_fields(self):
        """Test that to_dict contains all expected fields."""
        params = Params()
        d = params.to_dict()
        
        expected_keys = [
            'mass', 'radius', 'v0', 'drop_angle_deg', 'azimuth_deg',
            'spin_rps', 'spin_axis', 'g', 'dt', 't_max',
            'x0', 'y0', 'z0', 'stop_speed_threshold', 'stop_angular_threshold',
            'stop_hold_time', 'buoyancy', 'seed', 'use_virtual_mass',
            'use_multi_regime_cd', 'use_hertzian_contact', 'adaptive_timestep'
        ]
        
        for key in expected_keys:
            assert key in d
    
    def test_to_dict_values_match(self):
        """Test that to_dict values match object attributes."""
        params = Params(mass=1.5, radius=0.2, v0=15.0)
        d = params.to_dict()
        
        assert d['mass'] == 1.5
        assert d['radius'] == 0.2
        assert d['v0'] == 15.0


# =========================
# Surface Tests
# =========================

class TestSurfaceDefaults:
    """Test Surface dataclass default values."""
    
    def test_default_elasticity(self):
        """Test default elasticity values."""
        surface = Surface()
        assert surface.elasticity_base == 0.70
        assert surface.elasticity_drop == 0.002
    
    def test_default_friction(self):
        """Test default friction coefficients."""
        surface = Surface()
        assert surface.friction_mu_s == 0.50
        assert surface.friction_mu_k == 0.35
    
    def test_default_dampness(self):
        """Test default dampness."""
        surface = Surface()
        assert surface.dampness == 0.10
    
    def test_default_geometry(self):
        """Test default surface geometry."""
        surface = Surface()
        assert surface.slope_x == 0.0
        assert surface.slope_y == 0.0
        assert surface.base_height == 0.0
        assert surface.rough_amp == 0.0
    
    def test_default_wetness(self):
        """Test default wetness."""
        surface = Surface()
        assert surface.wetness == 0.0


class TestSurfaceCustomValues:
    """Test Surface with custom values."""
    
    def test_custom_elasticity(self):
        """Test custom elasticity values."""
        surface = Surface(elasticity_base=0.9, elasticity_drop=0.001)
        assert surface.elasticity_base == 0.9
        assert surface.elasticity_drop == 0.001
    
    def test_custom_friction(self):
        """Test custom friction coefficients."""
        surface = Surface(friction_mu_s=0.8, friction_mu_k=0.6)
        assert surface.friction_mu_s == 0.8
        assert surface.friction_mu_k == 0.6
    
    def test_custom_slope(self):
        """Test custom surface slope."""
        surface = Surface(slope_x=0.1, slope_y=0.05)
        assert surface.slope_x == 0.1
        assert surface.slope_y == 0.05
    
    def test_custom_roughness(self):
        """Test custom surface roughness."""
        surface = Surface(rough_amp=0.05, rough_lambda_x=3.0)
        assert surface.rough_amp == 0.05
        assert surface.rough_lambda_x == 3.0
    
    def test_custom_wetness(self):
        """Test custom wetness."""
        surface = Surface(wetness=0.5)
        assert surface.wetness == 0.5


class TestSurfaceToDict:
    """Test Surface serialization."""
    
    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        surface = Surface()
        d = surface.to_dict()
        assert isinstance(d, dict)
    
    def test_to_dict_contains_all_fields(self):
        """Test that to_dict contains all expected fields."""
        surface = Surface()
        d = surface.to_dict()
        
        expected_keys = [
            'elasticity_base', 'elasticity_drop', 'friction_mu_s', 'friction_mu_k',
            'dampness', 'slope_x', 'slope_y', 'base_height', 'rough_amp',
            'rough_lambda_x', 'rough_lambda_y', 'wetness', 'surface_roughness',
            'contact_stiffness'
        ]
        
        for key in expected_keys:
            assert key in d
    
    def test_to_dict_values_match(self):
        """Test that to_dict values match object attributes."""
        surface = Surface(elasticity_base=0.85, friction_mu_s=0.7)
        d = surface.to_dict()
        
        assert d['elasticity_base'] == 0.85
        assert d['friction_mu_s'] == 0.7


# =========================
# Wind Tests
# =========================

class TestWindDefaults:
    """Test Wind dataclass default values."""
    
    def test_default_speed(self):
        """Test default wind speed."""
        wind = Wind()
        assert wind.ref_speed == 2.0
    
    def test_default_height(self):
        """Test default reference height."""
        wind = Wind()
        assert wind.ref_height == 10.0
    
    def test_default_shear(self):
        """Test default wind shear alpha."""
        wind = Wind()
        assert wind.shear_alpha == 0.12
    
    def test_default_direction(self):
        """Test default wind direction."""
        wind = Wind()
        assert wind.direction_deg == 0.0
    
    def test_default_gust_parameters(self):
        """Test default gust parameters."""
        wind = Wind()
        assert wind.gust_tau == 2.0
        assert wind.gust_sigma == 1.0
    
    def test_default_humidity(self):
        """Test default humidity."""
        wind = Wind()
        assert wind.humidity_pct == 50.0


class TestWindCustomValues:
    """Test Wind with custom values."""
    
    def test_custom_speed_and_height(self):
        """Test custom wind speed and height."""
        wind = Wind(ref_speed=5.0, ref_height=20.0)
        assert wind.ref_speed == 5.0
        assert wind.ref_height == 20.0
    
    def test_custom_direction(self):
        """Test custom wind direction."""
        wind = Wind(direction_deg=90.0)
        assert wind.direction_deg == 90.0
    
    def test_custom_gust_parameters(self):
        """Test custom gust parameters."""
        wind = Wind(gust_tau=1.0, gust_sigma=2.0)
        assert wind.gust_tau == 1.0
        assert wind.gust_sigma == 2.0
    
    def test_custom_humidity(self):
        """Test custom humidity."""
        wind = Wind(humidity_pct=80.0)
        assert wind.humidity_pct == 80.0
    
    def test_no_wind(self):
        """Test zero wind conditions."""
        wind = Wind(ref_speed=0.0, gust_sigma=0.0)
        assert wind.ref_speed == 0.0
        assert wind.gust_sigma == 0.0


class TestWindToDict:
    """Test Wind serialization."""
    
    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        wind = Wind()
        d = wind.to_dict()
        assert isinstance(d, dict)
    
    def test_to_dict_contains_all_fields(self):
        """Test that to_dict contains all expected fields."""
        wind = Wind()
        d = wind.to_dict()
        
        expected_keys = [
            'ref_speed', 'ref_height', 'shear_alpha', 'direction_deg',
            'gust_tau', 'gust_sigma', 'humidity_pct'
        ]
        
        for key in expected_keys:
            assert key in d
    
    def test_to_dict_values_match(self):
        """Test that to_dict values match object attributes."""
        wind = Wind(ref_speed=8.0, direction_deg=180.0)
        d = wind.to_dict()
        
        assert d['ref_speed'] == 8.0
        assert d['direction_deg'] == 180.0


# =========================
# SimulationResult Tests
# =========================

class TestSimulationResult:
    """Test SimulationResult dataclass."""
    
    def test_simulation_result_creation(self, default_params, default_surface, default_wind):
        """Test creating a SimulationResult."""
        import pandas as pd
        
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Z': [10.0, 9.0, 8.0]
        })
        
        result = SimulationResult(
            df=df,
            params=default_params,
            surface=default_surface,
            wind=default_wind
        )
        
        assert result.df is df
        assert result.params is default_params
        assert result.surface is default_surface
        assert result.wind is default_wind
    
    def test_simulation_result_defaults(self, default_params, default_surface, default_wind):
        """Test SimulationResult default values."""
        import pandas as pd
        
        df = pd.DataFrame()
        result = SimulationResult(
            df=df,
            params=default_params,
            surface=default_surface,
            wind=default_wind
        )
        
        assert result.stability_ok is True
        assert result.energy_ok is True
        assert result.max_energy_gain_pct == 0.0
        assert result.compute_time_ms == 0.0
    
    def test_get_metadata(self, default_params, default_surface, default_wind):
        """Test get_metadata method."""
        import pandas as pd
        
        df = pd.DataFrame()
        result = SimulationResult(
            df=df,
            params=default_params,
            surface=default_surface,
            wind=default_wind,
            stability_ok=True,
            energy_ok=True,
            max_energy_gain_pct=1.5,
            compute_time_ms=123.45
        )
        
        metadata = result.get_metadata()
        
        assert isinstance(metadata, dict)
        assert 'mass' in metadata  # From params
        assert 'surface' in metadata
        assert 'wind' in metadata
        assert metadata['stability_ok'] is True
        assert metadata['energy_ok'] is True
        assert metadata['max_energy_gain_pct'] == 1.5
        assert metadata['compute_time_ms'] == 123.45
    
    def test_get_metadata_contains_all_params(self, default_params, default_surface, default_wind):
        """Test that get_metadata contains all parameter fields."""
        import pandas as pd
        
        df = pd.DataFrame()
        result = SimulationResult(
            df=df,
            params=default_params,
            surface=default_surface,
            wind=default_wind
        )
        
        metadata = result.get_metadata()
        
        # Check params fields are at top level
        assert 'mass' in metadata
        assert 'radius' in metadata
        assert 'v0' in metadata
        assert 'g' in metadata
        assert 'dt' in metadata
        
        # Check nested objects
        assert 'elasticity_base' in metadata['surface']
        assert 'ref_speed' in metadata['wind']


# =========================
# Dataclass Immutability Tests
# =========================

class TestDataclassBehavior:
    """Test dataclass behavior and edge cases."""
    
    def test_params_equality(self):
        """Test Params equality comparison."""
        params1 = Params(mass=1.0, radius=0.1)
        params2 = Params(mass=1.0, radius=0.1)
        params3 = Params(mass=1.0, radius=0.2)
        
        assert params1 == params2
        assert params1 != params3
    
    def test_surface_equality(self):
        """Test Surface equality comparison."""
        surface1 = Surface(elasticity_base=0.8)
        surface2 = Surface(elasticity_base=0.8)
        surface3 = Surface(elasticity_base=0.9)
        
        assert surface1 == surface2
        assert surface1 != surface3
    
    def test_wind_equality(self):
        """Test Wind equality comparison."""
        wind1 = Wind(ref_speed=5.0)
        wind2 = Wind(ref_speed=5.0)
        wind3 = Wind(ref_speed=3.0)
        
        assert wind1 == wind2
        assert wind1 != wind3
    
    def test_params_repr(self):
        """Test Params string representation."""
        params = Params(mass=1.0)
        repr_str = repr(params)
        
        assert 'Params' in repr_str
        assert 'mass=1.0' in repr_str
    
    def test_spin_axis_tuple(self):
        """Test that spin_axis is stored as tuple."""
        params = Params(spin_axis=(1.0, 0.0, 0.0))
        
        assert isinstance(params.spin_axis, tuple)
        assert len(params.spin_axis) == 3