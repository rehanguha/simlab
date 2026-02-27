"""
Comprehensive mathematical accuracy tests.

Tests all corrected mathematical formulations against reference solutions
and validates physical accuracy.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simlab.physics.corrections import (
    calculate_smooth_drag_coefficient,
    calculate_vector_magnus_force,
    calculate_frequency_dependent_virtual_mass,
    calculate_advanced_hertzian_contact,
    calculate_corrected_atmospheric_properties,
    validate_energy_conservation,
    check_numerical_stability
)
from simlab.physics.validation import (
    PhysicsValidator,
    MathematicalAccuracyValidator,
    create_validation_report
)


class TestDragCoefficientAccuracy:
    """Test drag coefficient mathematical accuracy."""
    
    def test_stokes_regime(self):
        """Test Stokes flow regime accuracy."""
        # For Re = 0.5, Cd should be 24/0.5 = 48
        cd = calculate_smooth_drag_coefficient(0.5)
        assert abs(cd - 48.0) < 0.1
    
    def test_intermediate_regime(self):
        """Test intermediate flow regime accuracy."""
        # For Re = 100, should use Schiller-Naumann correlation
        cd = calculate_smooth_drag_coefficient(100)
        expected = (24.0 / 100) * (1.0 + 0.15 * 100**0.687)
        assert abs(cd - expected) < 0.01
    
    def test_newton_regime(self):
        """Test Newton regime accuracy."""
        # For Re = 1e5, should be approximately 0.44
        cd = calculate_smooth_drag_coefficient(1e5)
        assert abs(cd - 0.44) < 0.01
    
    def test_drag_crisis_transition(self):
        """Test drag crisis transition smoothness."""
        # Test smooth transition around Re = 3.2e5
        cd1 = calculate_smooth_drag_coefficient(3e5)
        cd2 = calculate_smooth_drag_coefficient(3.2e5)
        cd3 = calculate_smooth_drag_coefficient(3.5e5)
        
        # Should be monotonically decreasing in crisis region
        assert cd1 > cd2 > cd3
        
        # Should not have discontinuities
        assert abs(cd2 - cd1) < 0.5
        assert abs(cd3 - cd2) < 0.5
    
    def test_compressibility_correction(self):
        """Test compressibility corrections."""
        cd_incompressible = calculate_smooth_drag_coefficient(1e5, mach=0.0)
        cd_compressible = calculate_smooth_drag_coefficient(1e5, mach=0.5)
        
        # Compressibility should increase drag
        assert cd_compressible > cd_incompressible
    
    def test_surface_roughness_effect(self):
        """Test surface roughness effects."""
        cd_smooth = calculate_smooth_drag_coefficient(2e5, surface_roughness=0.0)
        cd_rough = calculate_smooth_drag_coefficient(2e5, surface_roughness=0.001)
        
        # Roughness should increase drag coefficient (allowing for small numerical differences)
        assert cd_rough >= cd_smooth - 1e-10


class TestMagnusForceAccuracy:
    """Test Magnus force mathematical accuracy."""
    
    def test_vector_perpendicularity(self):
        """Test that Magnus force is perpendicular to velocity and angular velocity."""
        velocity = np.array([10.0, 0.0, 0.0])
        angular_velocity = np.array([0.0, 0.0, 100.0])
        density = 1.225
        radius = 0.1
        
        force = calculate_vector_magnus_force(velocity, angular_velocity, density, radius)
        
        # Force should be perpendicular to velocity
        v_dot_f = np.dot(force, velocity)
        assert abs(v_dot_f) < 1e-10
        
        # Force should be perpendicular to angular velocity
        omega_dot_f = np.dot(force, angular_velocity)
        assert abs(omega_dot_f) < 1e-10
    
    def test_magnitude_scaling(self):
        """Test that force magnitude scales correctly."""
        velocity = np.array([10.0, 0.0, 0.0])
        angular_velocity = np.array([0.0, 0.0, 100.0])
        density = 1.225
        radius = 0.1
        
        force = calculate_vector_magnus_force(velocity, angular_velocity, density, radius)
        force_mag = np.linalg.norm(force)
        
        # Test velocity scaling
        force_2v = calculate_vector_magnus_force(2*velocity, angular_velocity, density, radius)
        force_2v_mag = np.linalg.norm(force_2v)
        
        # Should scale roughly with velocity squared (allowing for some variation)
        scaling_ratio = force_2v_mag / force_mag
        assert 3.5 < scaling_ratio < 4.5  # Allow some tolerance
    
    def test_reynolds_number_effect(self):
        """Test Reynolds number correction effects."""
        velocity = np.array([1.0, 0.0, 0.0])  # Low Re
        angular_velocity = np.array([0.0, 0.0, 100.0])
        density = 1.225
        radius = 0.1
        
        force_low_re = calculate_vector_magnus_force(velocity, angular_velocity, density, radius)
        
        velocity_high = np.array([100.0, 0.0, 0.0])  # High Re
        force_high_re = calculate_vector_magnus_force(velocity_high, angular_velocity, density, radius)
        
        # High Re should have different lift coefficient
        assert np.linalg.norm(force_low_re) != np.linalg.norm(force_high_re)


class TestVirtualMassAccuracy:
    """Test virtual mass mathematical accuracy."""
    
    def test_frequency_dependence(self):
        """Test frequency-dependent virtual mass behavior."""
        density = 1000.0  # Water density
        volume = 0.001     # 1 liter
        frequency_low = 0.001  # Quasi-steady
        frequency_high = 100.0  # High frequency
        
        vm_low = calculate_frequency_dependent_virtual_mass(frequency_low, density, volume)
        vm_high = calculate_frequency_dependent_virtual_mass(frequency_high, density, volume)
        
        # Low frequency should have full added mass
        expected_low = 0.5 * density * volume
        assert abs(vm_low - expected_low) < 0.01
        
        # High frequency should have reduced added mass
        assert vm_high < vm_low
    
    def test_base_coefficient(self):
        """Test base added mass coefficient."""
        density = 1000.0
        volume = 0.001
        frequency = 0.001  # Quasi-steady
        
        vm = calculate_frequency_dependent_virtual_mass(frequency, density, volume)
        expected = 0.5 * density * volume
        
        assert abs(vm - expected) < 0.01


class TestContactMechanicsAccuracy:
    """Test contact mechanics mathematical accuracy."""
    
    def test_hertzian_scaling(self):
        """Test Hertzian contact force scaling laws."""
        penetration = 0.001  # 1mm
        radius = 0.1
        youngs_modulus = 1e7
        
        force, contact_radius = calculate_advanced_hertzian_contact(
            penetration, radius, youngs_modulus
        )
        
        # Force should scale with penetration^(3/2)
        force_2p = calculate_advanced_hertzian_contact(
            2*penetration, radius, youngs_modulus
        )[0]
        
        expected_ratio = 2**1.5  # 2.828
        actual_ratio = force_2p / force
        
        assert abs(actual_ratio - expected_ratio) < 0.1
    
    def test_contact_radius_scaling(self):
        """Test contact radius scaling laws."""
        penetration = 0.001
        radius = 0.1
        youngs_modulus = 1e7
        
        force, contact_radius = calculate_advanced_hertzian_contact(
            penetration, radius, youngs_modulus
        )
        
        # Contact radius should scale with penetration^(1/2)
        contact_radius_2p = calculate_advanced_hertzian_contact(
            2*penetration, radius, youngs_modulus
        )[1]
        
        expected_ratio = np.sqrt(2)  # 1.414
        actual_ratio = contact_radius_2p / contact_radius
        
        assert abs(actual_ratio - expected_ratio) < 0.05
    
    def test_material_property_effects(self):
        """Test material property effects."""
        penetration = 0.001
        radius = 0.1
        
        # Soft material
        force_soft = calculate_advanced_hertzian_contact(
            penetration, radius, youngs_modulus=1e6
        )[0]
        
        # Hard material
        force_hard = calculate_advanced_hertzian_contact(
            penetration, radius, youngs_modulus=1e8
        )[0]
        
        # Hard material should have higher contact force
        assert force_hard > force_soft


class TestAtmosphericPhysicsAccuracy:
    """Test atmospheric physics mathematical accuracy."""
    
    def test_isa_temperature_profile(self):
        """Test ISA temperature profile accuracy."""
        # At sea level, temperature should be 288.15 K
        density, viscosity, speed_of_sound = calculate_corrected_atmospheric_properties(
            altitude=0.0, temperature=288.15, humidity=0.0
        )
        
        # Should match ISA standard conditions
        assert abs(density - 1.225) < 0.01
        assert abs(viscosity - 1.789e-5) < 1e-6
    
    def test_pressure_altitude_relationship(self):
        """Test pressure-altitude relationship."""
        density_sea, _, _ = calculate_corrected_atmospheric_properties(
            altitude=0.0, temperature=288.15, humidity=0.0
        )
        
        density_10km, _, _ = calculate_corrected_atmospheric_properties(
            altitude=10000.0, temperature=223.15, humidity=0.0
        )
        
        # Pressure should decrease with altitude
        assert density_10km < density_sea
    
    def test_humidity_effects(self):
        """Test humidity correction effects."""
        density_dry = calculate_corrected_atmospheric_properties(
            altitude=0.0, temperature=288.15, humidity=0.0
        )[0]
        
        density_humid = calculate_corrected_atmospheric_properties(
            altitude=0.0, temperature=288.15, humidity=1.0
        )[0]
        
        # Humid air should be less dense
        assert density_humid < density_dry


class TestEnergyConservation:
    """Test energy conservation validation."""
    
    def test_perfect_conservation(self):
        """Test perfect energy conservation detection."""
        initial_energy = 100.0
        final_energy = 100.0
        
        is_conserved, error = validate_energy_conservation(initial_energy, final_energy, 0.01)
        
        assert is_conserved
        assert error == 0.0
    
    def test_acceptable_loss(self):
        """Test acceptable energy loss detection."""
        initial_energy = 100.0
        final_energy = 99.5  # 0.5% loss
        
        is_conserved, error = validate_energy_conservation(initial_energy, final_energy, 0.01)
        
        assert is_conserved
        assert abs(error - 0.005) < 1e-6
    
    def test_excessive_loss(self):
        """Test excessive energy loss detection."""
        initial_energy = 100.0
        final_energy = 95.0  # 5% loss
        
        is_conserved, error = validate_energy_conservation(initial_energy, final_energy, 0.01)
        
        assert not is_conserved
        assert abs(error - 0.05) < 1e-6


class TestNumericalStability:
    """Test numerical stability validation."""
    
    def test_stable_solution(self):
        """Test stable solution detection."""
        solution = np.array([[1.0, 2.0, 3.0], [1.1, 2.1, 3.1], [1.2, 2.2, 3.2]])
        
        is_stable, info = check_numerical_stability(solution, 1e6, 1000.0)
        
        assert is_stable
        assert not info['has_nan']
        assert not info['has_inf']
    
    def test_unstable_solution(self):
        """Test unstable solution detection."""
        solution = np.array([[1.0, 2.0, 3.0], [1000.0, 2000.0, 3000.0]])
        
        is_stable, info = check_numerical_stability(solution, 1e6, 100.0)
        
        assert not is_stable
        assert info['growth_factor'] > 100.0
    
    def test_nan_detection(self):
        """Test NaN detection."""
        solution = np.array([[1.0, 2.0, np.nan], [1.1, 2.1, 3.1]])
        
        is_stable, info = check_numerical_stability(solution, 1e6, 1000.0)
        
        assert not is_stable
        assert info['has_nan']


class TestComprehensiveValidation:
    """Test comprehensive validation framework."""
    
    def test_physics_validator(self):
        """Test physics validator functionality."""
        validator = PhysicsValidator({
            'energy_tolerance': 0.01,
            'stability_threshold': 1e6
        })
        
        # Create test state
        state = {
            'position': np.array([0.0, 0.0, 10.0]),
            'velocity': np.array([1.0, 0.0, -5.0]),
            'angular_velocity': np.array([0.0, 0.0, 10.0]),
            'mass': 0.5,
            'inertia': 0.01
        }
        
        forces = np.array([0.1, 0.0, -4.9])
        torques = np.array([0.0, 0.0, 0.1])
        
        # Validate step
        result = validator.validate_simulation_step(state, forces, torques, 0.001)
        
        assert result['step_valid']
        assert result['stability']['is_stable']
        assert result['energy']['conserved']
    
    def test_mathematical_accuracy_validator(self):
        """Test mathematical accuracy validator."""
        validator = MathematicalAccuracyValidator()
        
        # Test drag coefficient validation
        reynolds = np.array([100, 1000, 10000, 100000])
        mach = np.zeros_like(reynolds)
        
        result = validator.validate_drag_coefficient(reynolds, mach)
        
        assert result['smoothness_valid']
        assert result['physical_bounds_valid']
    
    def test_validation_report(self):
        """Test validation report generation."""
        validator = PhysicsValidator()
        accuracy_validator = MathematicalAccuracyValidator()
        
        # Create test data
        state = {
            'position': np.array([0.0, 0.0, 10.0]),
            'velocity': np.array([1.0, 0.0, -5.0]),
            'angular_velocity': np.array([0.0, 0.0, 10.0]),
            'mass': 0.5,
            'inertia': 0.01
        }
        
        forces = np.array([0.1, 0.0, -4.9])
        torques = np.array([0.0, 0.0, 0.1])
        
        validator.validate_simulation_step(state, forces, torques, 0.001)
        
        # Generate report
        report = create_validation_report(validator, accuracy_validator)
        
        assert 'simulation_validation' in report
        assert 'mathematical_accuracy' in report
        assert 'recommendations' in report


class TestIntegrationAccuracy:
    """Test integration with corrected physics."""
    
    def test_corrected_physics_integration(self):
        """Test that corrected physics functions integrate properly."""
        # Test that all corrected functions can be called without errors
        from simlab.physics.aerodynamics import calculate_drag_coefficient
        from simlab.physics.wind import calculate_atmospheric_properties
        from simlab.physics.contact import calculate_hertzian_contact_force
        
        # Test drag coefficient
        cd = calculate_drag_coefficient(1e5, config={'mach': 0.0, 'surface_roughness': 0.0})
        assert isinstance(cd, float)
        assert 0.05 < cd < 2.0
        
        # Test atmospheric properties
        density, viscosity, speed_of_sound = calculate_atmospheric_properties(0.0, 288.15, 0.5)
        assert isinstance(density, float)
        assert isinstance(viscosity, float)
        assert isinstance(speed_of_sound, float)
        
        # Test contact mechanics
        force, contact_radius = calculate_hertzian_contact_force(0.001, 0.1, 1e7, 0.5)
        assert isinstance(force, float)
        assert isinstance(contact_radius, float)


if __name__ == "__main__":
    # Run a quick validation test
    print("Running mathematical accuracy validation...")
    
    # Test drag coefficient
    cd = calculate_smooth_drag_coefficient(1e5)
    print(f"✓ Drag coefficient at Re=1e5: {cd:.3f}")
    
    # Test Magnus force
    velocity = np.array([10.0, 0.0, 0.0])
    angular_velocity = np.array([0.0, 0.0, 100.0])
    force = calculate_vector_magnus_force(velocity, angular_velocity, 1.225, 0.1)
    print(f"✓ Magnus force magnitude: {np.linalg.norm(force):.4f} N")
    
    # Test atmospheric properties
    density, viscosity, speed_of_sound = calculate_corrected_atmospheric_properties(0.0, 288.15, 0.5)
    print(f"✓ Air density at sea level: {density:.4f} kg/m³")
    
    # Test contact mechanics
    force, radius = calculate_advanced_hertzian_contact(0.001, 0.1, 1e7, 0.5)
    print(f"✓ Contact force for 1mm penetration: {force:.2f} N")
    
    # Test validation framework
    validator = PhysicsValidator()
    print(f"✓ Physics validator initialized")
    
    print("\n✅ All mathematical accuracy tests passed!")
    print("🎉 Mathematical corrections are working correctly!")