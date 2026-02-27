"""
Comprehensive tests for validation.py module.
Tests input validation, bounds checking, and error handling.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Params, Surface, Wind
from validation import (
    validate_inputs,
    validate_inputs_or_raise,
    validate_dataframe,
    ValidationError
)


# =========================
# ValidationError Tests
# =========================

class TestValidationError:
    """Test custom ValidationError exception."""
    
    def test_validation_error_is_value_error(self):
        """Test that ValidationError is a subclass of ValueError."""
        assert issubclass(ValidationError, ValueError)
    
    def test_validation_error_message(self):
        """Test ValidationError message."""
        error = ValidationError("Test error message")
        assert "Test error message" in str(error)


# =========================
# Valid Input Tests
# =========================

class TestValidInputs:
    """Test that valid inputs pass validation."""
    
    def test_validate_inputs_valid_returns_empty_list(self):
        """Test that valid inputs return empty error list."""
        params = Params(mass=0.5, radius=0.1, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=50.0)
        
        errors = validate_inputs(params, surface, wind)
        assert errors == []
    
    def test_validate_inputs_or_raise_valid_no_exception(self):
        """Test that valid inputs don't raise exception."""
        params = Params(mass=0.5, radius=0.1, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=50.0)
        
        # Should not raise
        validate_inputs_or_raise(params, surface, wind)
    
    def test_validate_inputs_with_all_custom_valid_values(self):
        """Test validation with all custom valid values."""
        params = Params(
            mass=2.0,
            radius=0.15,
            v0=20.0,
            spin_rps=10.0,
            spin_axis=(1.0, 0.0, 0.0),
            z0=50.0,
            dt=0.001,
            t_max=30.0
        )
        surface = Surface(
            elasticity_base=0.9,
            friction_mu_s=0.8,
            friction_mu_k=0.6,
            base_height=1.0
        )
        wind = Wind(humidity_pct=75.0)
        
        errors = validate_inputs(params, surface, wind)
        assert errors == []


# =========================
# Mass Validation Tests
# =========================

class TestMassValidation:
    """Test mass parameter validation."""
    
    def test_negative_mass_fails(self):
        """Test that negative mass fails validation."""
        params = Params(mass=-0.5, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('mass' in e.lower() for e in errors)
    
    def test_zero_mass_fails(self):
        """Test that zero mass fails validation."""
        params = Params(mass=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('mass' in e.lower() for e in errors)
    
    def test_very_small_mass_passes(self):
        """Test that very small positive mass passes."""
        params = Params(mass=0.001, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('mass' not in e.lower() for e in errors)
    
    def test_large_mass_passes(self):
        """Test that large mass passes validation."""
        params = Params(mass=100.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('mass' not in e.lower() for e in errors)


# =========================
# Radius Validation Tests
# =========================

class TestRadiusValidation:
    """Test radius parameter validation."""
    
    def test_negative_radius_fails(self):
        """Test that negative radius fails validation."""
        params = Params(radius=-0.1, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('radius' in e.lower() for e in errors)
    
    def test_zero_radius_fails(self):
        """Test that zero radius fails validation."""
        params = Params(radius=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('radius' in e.lower() for e in errors)
    
    def test_very_small_radius_passes(self):
        """Test that very small positive radius passes."""
        params = Params(radius=0.001, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('radius' not in e.lower() for e in errors)


# =========================
# Velocity Validation Tests
# =========================

class TestVelocityValidation:
    """Test initial velocity validation."""
    
    def test_negative_velocity_fails(self):
        """Test that negative initial velocity fails."""
        params = Params(v0=-5.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('v0' in e.lower() or 'velocity' in e.lower() for e in errors)
    
    def test_zero_velocity_passes(self):
        """Test that zero initial velocity passes (free fall)."""
        params = Params(v0=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('v0' not in e.lower() and 'velocity' not in e.lower() for e in errors)
    
    def test_large_velocity_passes(self):
        """Test that large velocity passes."""
        params = Params(v0=100.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('v0' not in e.lower() for e in errors)


# =========================
# Spin Validation Tests
# =========================

class TestSpinValidation:
    """Test spin parameter validation."""
    
    def test_negative_spin_fails(self):
        """Test that negative spin rate fails."""
        params = Params(spin_rps=-5.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('spin' in e.lower() for e in errors)
    
    def test_zero_spin_passes(self):
        """Test that zero spin passes."""
        params = Params(spin_rps=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('spin' not in e.lower() for e in errors)
    
    def test_spin_with_zero_axis_fails(self):
        """Test that spin with zero axis fails."""
        params = Params(spin_rps=10.0, spin_axis=(0.0, 0.0, 0.0), z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('spin_axis' in e.lower() for e in errors)
    
    def test_spin_with_valid_axis_passes(self):
        """Test that spin with valid axis passes."""
        params = Params(spin_rps=10.0, spin_axis=(1.0, 0.0, 0.0), z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('spin_axis' not in e.lower() for e in errors)
    
    def test_zero_spin_with_zero_axis_passes(self):
        """Test that zero spin with zero axis passes."""
        params = Params(spin_rps=0.0, spin_axis=(0.0, 0.0, 0.0), z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('spin_axis' not in e.lower() for e in errors)


# =========================
# Position Validation Tests
# =========================

class TestPositionValidation:
    """Test initial position validation."""
    
    def test_z0_below_ground_fails(self):
        """Test that z0 below ground fails."""
        params = Params(z0=0.05, radius=0.1)  # z0 < radius
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert len(errors) > 0
        assert any('z0' in e.lower() for e in errors)
    
    def test_z0_at_ground_plus_radius_fails(self):
        """Test that z0 at ground + radius fails (must be >)."""
        params = Params(z0=0.1, radius=0.1)  # z0 == radius
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('z0' in e.lower() for e in errors)
    
    def test_z0_above_ground_passes(self):
        """Test that z0 above ground passes."""
        params = Params(z0=0.11, radius=0.1)  # z0 > radius
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('z0' not in e.lower() for e in errors)
    
    def test_z0_with_base_height(self):
        """Test z0 validation with non-zero base height."""
        params = Params(z0=5.0, radius=0.1)
        surface = Surface(base_height=5.0)  # Ground at 5m
        wind = Wind()
        
        # z0 = 5.0, base_height = 5.0, radius = 0.1
        # z0 must be > base_height + radius = 5.1
        errors = validate_inputs(params, surface, wind)
        assert any('z0' in e.lower() for e in errors)


# =========================
# Time Parameter Validation Tests
# =========================

class TestTimeValidation:
    """Test time parameter validation."""
    
    def test_negative_dt_fails(self):
        """Test that negative dt fails."""
        params = Params(dt=-0.01, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('dt' in e.lower() for e in errors)
    
    def test_zero_dt_fails(self):
        """Test that zero dt fails."""
        params = Params(dt=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('dt' in e.lower() for e in errors)
    
    def test_negative_t_max_fails(self):
        """Test that negative t_max fails."""
        params = Params(t_max=-1.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('t_max' in e.lower() for e in errors)
    
    def test_zero_t_max_fails(self):
        """Test that zero t_max fails."""
        params = Params(t_max=0.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('t_max' in e.lower() for e in errors)


# =========================
# Surface Validation Tests
# =========================

class TestSurfaceValidation:
    """Test surface parameter validation."""
    
    def test_elasticity_below_zero_fails(self):
        """Test that elasticity below 0 fails."""
        params = Params(z0=10.0)
        surface = Surface(elasticity_base=-0.1)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('elasticity' in e.lower() for e in errors)
    
    def test_elasticity_above_one_fails(self):
        """Test that elasticity above 1 fails."""
        params = Params(z0=10.0)
        surface = Surface(elasticity_base=1.5)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('elasticity' in e.lower() for e in errors)
    
    def test_elasticity_at_zero_passes(self):
        """Test that elasticity at 0 passes (perfectly inelastic)."""
        params = Params(z0=10.0)
        surface = Surface(elasticity_base=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('elasticity' not in e.lower() for e in errors)
    
    def test_elasticity_at_one_passes(self):
        """Test that elasticity at 1 passes (perfectly elastic)."""
        params = Params(z0=10.0)
        surface = Surface(elasticity_base=1.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert all('elasticity' not in e.lower() for e in errors)
    
    def test_friction_mu_s_below_zero_fails(self):
        """Test that static friction below 0 fails."""
        params = Params(z0=10.0)
        surface = Surface(friction_mu_s=-0.5)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('friction_mu_s' in e.lower() for e in errors)
    
    def test_friction_mu_s_above_two_fails(self):
        """Test that static friction above 2 fails."""
        params = Params(z0=10.0)
        surface = Surface(friction_mu_s=2.5)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('friction_mu_s' in e.lower() for e in errors)
    
    def test_friction_mu_k_below_zero_fails(self):
        """Test that kinetic friction below 0 fails."""
        params = Params(z0=10.0)
        surface = Surface(friction_mu_k=-0.5)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('friction_mu_k' in e.lower() for e in errors)
    
    def test_friction_mu_k_above_two_fails(self):
        """Test that kinetic friction above 2 fails."""
        params = Params(z0=10.0)
        surface = Surface(friction_mu_k=2.5)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        assert any('friction_mu_k' in e.lower() for e in errors)


# =========================
# Wind Validation Tests
# =========================

class TestWindValidation:
    """Test wind parameter validation."""
    
    def test_humidity_below_zero_fails(self):
        """Test that humidity below 0% fails."""
        params = Params(z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=-10.0)
        
        errors = validate_inputs(params, surface, wind)
        assert any('humidity' in e.lower() for e in errors)
    
    def test_humidity_above_100_fails(self):
        """Test that humidity above 100% fails."""
        params = Params(z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=110.0)
        
        errors = validate_inputs(params, surface, wind)
        assert any('humidity' in e.lower() for e in errors)
    
    def test_humidity_at_zero_passes(self):
        """Test that 0% humidity passes."""
        params = Params(z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=0.0)
        
        errors = validate_inputs(params, surface, wind)
        assert all('humidity' not in e.lower() for e in errors)
    
    def test_humidity_at_100_passes(self):
        """Test that 100% humidity passes."""
        params = Params(z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=100.0)
        
        errors = validate_inputs(params, surface, wind)
        assert all('humidity' not in e.lower() for e in errors)


# =========================
# validate_inputs_or_raise Tests
# =========================

class TestValidateInputsOrRaise:
    """Test validate_inputs_or_raise function."""
    
    def test_raises_validation_error(self):
        """Test that function raises ValidationError."""
        params = Params(mass=-1.0, z0=10.0)  # Invalid
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        with pytest.raises(ValidationError):
            validate_inputs_or_raise(params, surface, wind)
    
    def test_error_message_contains_all_errors(self):
        """Test that error message lists all errors."""
        params = Params(mass=-1.0, radius=-0.1, z0=10.0)  # Two invalid
        surface = Surface(elasticity_base=2.0)  # Invalid
        wind = Wind(humidity_pct=150.0)  # Invalid
        
        try:
            validate_inputs_or_raise(params, surface, wind)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            error_msg = str(e)
            # Should contain multiple error mentions
            assert 'mass' in error_msg.lower() or 'radius' in error_msg.lower()
    
    def test_no_error_for_valid_inputs(self):
        """Test that no error is raised for valid inputs."""
        params = Params(mass=0.5, radius=0.1, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind(humidity_pct=50.0)
        
        # Should not raise
        validate_inputs_or_raise(params, surface, wind)


# =========================
# DataFrame Validation Tests
# =========================

class TestValidateDataFrame:
    """Test DataFrame validation."""
    
    def test_valid_dataframe_passes(self):
        """Test that valid DataFrame passes."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [0.0, 2.0, 4.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0],
            'Ox': [0.0, 0.0, 0.0],
            'Oy': [0.0, 0.0, 0.0],
            'Oz': [50.0, 50.0, 50.0],
            'AirDensity': [1.225, 1.225, 1.225],
            'Mu': [1.8e-5, 1.8e-5, 1.8e-5],
            'Re': [1000.0, 2000.0, 3000.0],
            'Cd': [0.44, 0.44, 0.44],
            'WindX': [2.0, 2.0, 2.0],
            'WindY': [0.0, 0.0, 0.0],
            'WindZ': [0.0, 0.0, 0.0],
            'Z_ground': [0.0, 0.0, 0.0],
            'Mach': [0.03, 0.06, 0.09],
            'Dt_actual': [0.005, 0.005, 0.005]
        })
        
        errors = validate_dataframe(df)
        assert errors == []
    
    def test_missing_columns_detected(self):
        """Test that missing columns are detected."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1],
            'X': [0.0, 1.0],
            'Z': [10.0, 9.0]
            # Missing many required columns
        })
        
        errors = validate_dataframe(df)
        assert len(errors) > 0
        assert any('Missing' in e for e in errors)
    
    def test_nan_values_detected(self):
        """Test that NaN values are detected."""
        df = pd.DataFrame({
            'Time': [0.0, np.nan, 0.2],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [0.0, 2.0, 4.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0],
            'Ox': [0.0, 0.0, 0.0],
            'Oy': [0.0, 0.0, 0.0],
            'Oz': [50.0, 50.0, 50.0],
            'AirDensity': [1.225, 1.225, 1.225],
            'Mu': [1.8e-5, 1.8e-5, 1.8e-5],
            'Re': [1000.0, 2000.0, 3000.0],
            'Cd': [0.44, 0.44, 0.44],
            'WindX': [2.0, 2.0, 2.0],
            'WindY': [0.0, 0.0, 0.0],
            'WindZ': [0.0, 0.0, 0.0],
            'Z_ground': [0.0, 0.0, 0.0],
            'Mach': [0.03, 0.06, 0.09],
            'Dt_actual': [0.005, 0.005, 0.005]
        })
        
        errors = validate_dataframe(df)
        assert len(errors) > 0
        assert any('NaN' in e for e in errors)
    
    def test_inf_values_detected(self):
        """Test that Inf values are detected."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, np.inf],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [0.0, 2.0, 4.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0],
            'Ox': [0.0, 0.0, 0.0],
            'Oy': [0.0, 0.0, 0.0],
            'Oz': [50.0, 50.0, 50.0],
            'AirDensity': [1.225, 1.225, 1.225],
            'Mu': [1.8e-5, 1.8e-5, 1.8e-5],
            'Re': [1000.0, 2000.0, 3000.0],
            'Cd': [0.44, 0.44, 0.44],
            'WindX': [2.0, 2.0, 2.0],
            'WindY': [0.0, 0.0, 0.0],
            'WindZ': [0.0, 0.0, 0.0],
            'Z_ground': [0.0, 0.0, 0.0],
            'Mach': [0.03, 0.06, 0.09],
            'Dt_actual': [0.005, 0.005, 0.005]
        })
        
        errors = validate_dataframe(df)
        assert len(errors) > 0
        assert any('Inf' in e for e in errors)
    
    def test_negative_inf_detected(self):
        """Test that negative Inf values are detected."""
        df = pd.DataFrame({
            'Time': [0.0, 0.1, -np.inf],
            'X': [0.0, 1.0, 2.0],
            'Y': [0.0, 0.0, 0.0],
            'Z': [10.0, 9.0, 8.0],
            'Vx': [0.0, 2.0, 4.0],
            'Vy': [0.0, 0.0, 0.0],
            'Vz': [0.0, -1.0, -2.0],
            'Ox': [0.0, 0.0, 0.0],
            'Oy': [0.0, 0.0, 0.0],
            'Oz': [50.0, 50.0, 50.0],
            'AirDensity': [1.225, 1.225, 1.225],
            'Mu': [1.8e-5, 1.8e-5, 1.8e-5],
            'Re': [1000.0, 2000.0, 3000.0],
            'Cd': [0.44, 0.44, 0.44],
            'WindX': [2.0, 2.0, 2.0],
            'WindY': [0.0, 0.0, 0.0],
            'WindZ': [0.0, 0.0, 0.0],
            'Z_ground': [0.0, 0.0, 0.0],
            'Mach': [0.03, 0.06, 0.09],
            'Dt_actual': [0.005, 0.005, 0.005]
        })
        
        errors = validate_dataframe(df)
        assert len(errors) > 0
        assert any('Inf' in e for e in errors)


# =========================
# Multiple Errors Tests
# =========================

class TestMultipleErrors:
    """Test handling of multiple validation errors."""
    
    def test_multiple_errors_all_reported(self):
        """Test that all errors are reported."""
        params = Params(
            mass=-1.0,      # Invalid
            radius=-0.1,    # Invalid
            v0=-5.0,        # Invalid
            z0=0.0          # May be invalid depending on radius
        )
        surface = Surface(
            elasticity_base=2.0,    # Invalid
            friction_mu_s=3.0       # Invalid
        )
        wind = Wind(humidity_pct=150.0)  # Invalid
        
        errors = validate_inputs(params, surface, wind)
        
        # Should have multiple errors
        assert len(errors) >= 3
    
    def test_error_messages_are_descriptive(self):
        """Test that error messages are descriptive."""
        params = Params(mass=-1.0, z0=10.0)
        surface = Surface(base_height=0.0)
        wind = Wind()
        
        errors = validate_inputs(params, surface, wind)
        
        # Error should contain the invalid value
        assert '-1' in errors[0] or '-1.0' in errors[0]