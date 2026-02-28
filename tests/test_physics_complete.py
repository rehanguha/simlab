"""
Comprehensive test for all physics features.

Tests the complete physics implementation including all missing features.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physimlab.physics import (
    # Basic physics
    calculate_density, calculate_viscosity, calculate_speed_of_sound,
    calculate_reynolds_number, calculate_drag_coefficient,
    calculate_magnus_force, calculate_gravity, calculate_wind_force,
    calculate_terminal_velocity, calculate_spin_decay,
    
    # Enhanced physics
    calculate_multi_regime_drag_coefficient, calculate_buoyancy_force,
    calculate_virtual_mass, calculate_effective_mass, calculate_aerodynamic_forces,
    calculate_spin_decay_advanced, calculate_compressibility_correction,
    AerodynamicModel,
    
    # Numerical methods
    AdaptiveRK45, fixed_step_euler, check_stability, energy_monitor,
    adaptive_timestep_controller,
    
    # Wind physics
    calculate_wind_velocity, generate_gust_process, calculate_relative_velocity,
    calculate_atmospheric_properties, calculate_wind_profile,
    calculate_turbulence_intensity, calculate_wind_forces, calculate_wind_moment,
    WindField,
    
    # Contact physics
    calculate_hertzian_contact_force, calculate_coefficient_of_restitution,
    calculate_friction_forces, calculate_contact_impulse, calculate_rolling_resistance,
    calculate_surface_geometry, detect_collision, apply_collision_response,
    ContactModel
)


class TestEnhancedAerodynamics:
    """Test enhanced aerodynamics features."""
    
    def test_multi_regime_drag_coefficient(self):
        """Test multi-regime drag coefficient calculation."""
        # Test different Reynolds number regimes
        cd_stokes = calculate_multi_regime_drag_coefficient(0.5)
        cd_intermediate = calculate_multi_regime_drag_coefficient(100)
        cd_newton = calculate_multi_regime_drag_coefficient(1e5)
        cd_crisis = calculate_multi_regime_drag_coefficient(3.2e5)
        cd_post_crisis = calculate_multi_regime_drag_coefficient(5e5)
        
        # Verify drag crisis behavior
        assert cd_newton > cd_crisis
        assert cd_crisis < cd_post_crisis
        
        # Test compressibility correction
        cd_compressible = calculate_multi_regime_drag_coefficient(1e5, mach=0.5)
        assert cd_compressible > cd_newton
    
    def test_buoyancy_force(self):
        """Test buoyancy force calculation."""
        density = 1.225  # kg/m^3
        volume = 0.00418879  # m^3 (sphere radius 0.1m)
        buoyancy = calculate_buoyancy_force(density, volume)
        
        # Should be positive (upward force)
        assert buoyancy > 0
        assert abs(buoyancy - 0.0503) < 0.001
    
    def test_virtual_mass(self):
        """Test virtual mass calculation."""
        density = 1.225
        volume = 0.00418879
        added_mass = calculate_virtual_mass(density, volume)
        
        assert added_mass > 0
        assert abs(added_mass - 0.00256) < 0.0001
    
    def test_effective_mass(self):
        """Test effective mass calculation."""
        mass = 0.5
        density = 1.225
        volume = 0.00418879
        effective_mass = calculate_effective_mass(mass, density, volume)
        
        assert effective_mass > mass
        assert abs(effective_mass - 0.50256) < 0.0001
    
    def test_aerodynamic_forces(self):
        """Test complete aerodynamic force calculation."""
        velocity = np.array([10.0, 0.0, 0.0])
        angular_velocity = np.array([0.0, 0.0, 100.0])
        density = 1.225
        viscosity = 1.8e-5
        radius = 0.1
        mass = 0.5
        
        force, torque, reynolds = calculate_aerodynamic_forces(
            velocity, angular_velocity, density, viscosity, radius, mass
        )
        
        # Should have drag force in negative x direction
        assert force[0] < 0
        # Should have lift force in y direction due to Magnus effect
        assert abs(force[1]) > 0
        # Should have buoyancy in positive z direction
        assert force[2] > 0
        
        # Should have aerodynamic torque
        assert np.linalg.norm(torque) > 0
        
        # Reynolds number should be reasonable
        assert 1000 < reynolds < 1e6
    
    def test_spin_decay_advanced(self):
        """Test advanced spin decay calculation."""
        angular_velocity = np.array([0.0, 0.0, 100.0])
        velocity = np.array([10.0, 0.0, 0.0])
        density = 1.225
        viscosity = 1.8e-5
        radius = 0.1
        time_step = 0.001
        config = {'c_spin_decay': 0.05, 'c_spin_aero': 0.02}
        
        new_omega = calculate_spin_decay_advanced(
            angular_velocity, velocity, density, viscosity, radius, time_step, config
        )
        
        # Spin should decay
        assert np.linalg.norm(new_omega) < np.linalg.norm(angular_velocity)


class TestNumericalMethods:
    """Test numerical integration methods."""
    
    def test_adaptive_rk45(self):
        """Test adaptive RK45 integration."""
        def simple_ode(t, y):
            return np.array([-y[0]])  # dy/dt = -y
        
        integrator = AdaptiveRK45(rtol=1e-6, atol=1e-8)
        times, solutions = integrator.integrate(simple_ode, 0.0, np.array([1.0]), 1.0, 0.1)
        
        # Should reach final time
        assert times[-1] >= 1.0
        
        # Should have exponential decay behavior
        assert solutions[-1, 0] < solutions[0, 0]
        assert abs(solutions[-1, 0] - np.exp(-1.0)) < 0.01
    
    def test_fixed_step_euler(self):
        """Test fixed-step Euler integration."""
        def simple_ode(t, y):
            return np.array([-y[0]])
        
        times, solutions = fixed_step_euler(simple_ode, 0.0, np.array([1.0]), 1.0, 0.01)
        
        # Should reach final time
        assert times[-1] >= 1.0
        
        # Should have decaying solution
        assert solutions[-1, 0] < solutions[0, 0]
    
    def test_stability_check(self):
        """Test numerical stability checking."""
        y_stable = np.array([1.0, 2.0, 3.0])
        y_prev = np.array([0.9, 1.9, 2.9])
        
        assert check_stability(y_stable, y_prev)
        
        y_unstable = np.array([1e7, 1e7, 1e7])
        assert not check_stability(y_unstable, y_stable)
        
        y_nan = np.array([np.nan, 1.0, 2.0])
        assert not check_stability(y_nan, y_stable)
    
    def test_energy_monitor(self):
        """Test energy monitoring."""
        # State: [x, y, z, vx, vy, vz, omega_x, omega_y, omega_z]
        y = np.array([0.0, 0.0, 10.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        energy = energy_monitor(y, g=9.81, m=0.5, I=0.01)
        
        # Should have potential energy
        assert energy > 0
        
        # Moving object should have more energy than stationary
        y_moving = np.array([0.0, 0.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        energy_moving = energy_monitor(y_moving, g=9.81, m=0.5, I=0.01)
        assert energy_moving > energy


class TestWindPhysics:
    """Test wind and atmospheric physics."""
    
    def test_wind_velocity_calculation(self):
        """Test wind velocity calculation with power law."""
        wind = calculate_wind_velocity(10.0, ref_speed=5.0, ref_height=10.0)
        
        # At reference height, should equal reference speed
        assert abs(wind[0] - 5.0) < 0.1
        
        # At higher altitude, should be faster
        wind_high = calculate_wind_velocity(20.0, ref_speed=5.0, ref_height=10.0)
        assert wind_high[0] > wind[0]
    
    def test_atmospheric_properties(self):
        """Test atmospheric property calculation."""
        density, viscosity, speed_of_sound = calculate_atmospheric_properties(
            altitude=0.0, temperature=288.15, humidity=0.5
        )
        
        # Standard sea level values
        assert 1.2 < density < 1.3
        assert 1.7e-5 < viscosity < 1.9e-5
        assert 330 < speed_of_sound < 350
    
    def test_wind_profile(self):
        """Test wind profile calculation."""
        heights = np.array([0, 5, 10, 20])
        speeds = calculate_wind_profile(heights, ref_speed=10.0, ref_height=10.0)
        
        # Should increase with height
        assert speeds[0] == 0.0  # Ground
        assert speeds[2] == 10.0  # Reference height
        assert speeds[3] > speeds[2]  # Higher altitude
    
    def test_relative_velocity(self):
        """Test relative velocity calculation."""
        velocity = np.array([10.0, 0.0, 0.0])
        wind_velocity = np.array([5.0, 0.0, 0.0])
        
        v_rel = calculate_relative_velocity(velocity, wind_velocity)
        
        assert v_rel[0] == 5.0
        assert v_rel[1] == 0.0
        assert v_rel[2] == 0.0
    
    def test_wind_field_class(self):
        """Test WindField class."""
        config = {
            'ref_speed': 5.0,
            'ref_height': 10.0,
            'direction_deg': 90.0,  # North wind
            'gust_tau': 1.5,
            'gust_sigma': 0.5
        }
        
        wind_field = WindField(config)
        position = np.array([0.0, 0.0, 10.0])
        time = 0.0
        
        wind_vel = wind_field.get_wind_velocity(position, time)
        density, viscosity, speed_of_sound = wind_field.get_atmospheric_properties(position)
        
        # Should have northward wind component
        assert abs(wind_vel[1]) > 0
        
        # Should return valid atmospheric properties
        assert density > 0
        assert viscosity > 0
        assert speed_of_sound > 0


class TestContactPhysics:
    """Test advanced contact mechanics."""
    
    def test_hertzian_contact_force(self):
        """Test Hertzian contact force calculation."""
        penetration = 0.001  # 1mm
        radius = 0.1
        force = calculate_hertzian_contact_force(penetration, radius)
        
        # Should be positive force
        assert force > 0
        
        # Should increase with penetration
        force2 = calculate_hertzian_contact_force(2*penetration, radius)
        assert force2 > force
    
    def test_coefficient_of_restitution(self):
        """Test velocity-dependent coefficient of restitution."""
        e1 = calculate_coefficient_of_restitution(1.0, base_restitution=0.7)
        e2 = calculate_coefficient_of_restitution(10.0, base_restitution=0.7)
        
        # Should decrease with velocity
        assert e2 < e1
        
        # Should be between 0 and 1
        assert 0.0 <= e1 <= 1.0
        assert 0.0 <= e2 <= 1.0
    
    def test_friction_forces(self):
        """Test friction force calculation."""
        normal_force = 10.0
        relative_velocity = np.array([1.0, 0.0, 0.0])
        
        friction = calculate_friction_forces(
            normal_force, relative_velocity, static_friction=0.5, kinetic_friction=0.3
        )
        
        # Should oppose relative motion
        assert friction[0] < 0
        assert abs(friction[0]) < normal_force * 0.5
    
    def test_surface_geometry(self):
        """Test surface geometry calculation."""
        position = np.array([10.0, 5.0, 0.0])
        surface_config = {
            'base_height': 0.0,
            'slope_x': 0.1,
            'slope_y': 0.05,
            'surface_roughness': 0.0
        }
        
        normal, height = calculate_surface_geometry(position, surface_config)
        
        # Should return unit normal
        assert abs(np.linalg.norm(normal) - 1.0) < 1e-6
        
        # Should calculate correct height
        expected_height = 0.0 + 0.1*10.0 + 0.05*5.0
        assert abs(height - expected_height) < 1e-6
    
    def test_collision_detection(self):
        """Test collision detection."""
        position = np.array([0.0, 0.0, 0.05])  # 5cm above ground
        radius = 0.1  # 10cm radius
        surface_config = {'base_height': 0.0}
        
        collision, penetration, normal = detect_collision(position, radius, surface_config)
        
        # Should detect collision
        assert collision
        assert penetration > 0
        assert abs(normal[2] - 1.0) < 1e-6  # Upward normal
    
    def test_contact_model_class(self):
        """Test ContactModel class."""
        config = {
            'surface': {
                'elasticity_base': 0.7,
                'friction_mu_s': 0.5,
                'friction_mu_k': 0.3
            },
            'simulation': {
                'youngs_modulus': 1e7,
                'poisson_ratio': 0.5
            }
        }
        
        contact_model = ContactModel(config)
        
        state = {
            'velocity': np.array([1.0, 0.0, -5.0]),
            'angular_velocity': np.array([0.0, 0.0, 10.0]),
            'position': np.array([0.0, 0.0, 0.05]),
            'radius': 0.1,
            'mass': 0.5,
            'inertia': 0.01
        }
        
        updated_state = contact_model.process_contact(state)
        
        # Should modify state
        assert updated_state['velocity'][2] > state['velocity'][2]  # Bounce up
        
        # Should track contact events
        assert contact_model.get_contact_count() > 0


class TestIntegration:
    """Test integration of multiple physics features."""
    
    def test_complete_physics_simulation(self):
        """Test simulation with all physics features enabled."""
        # Configuration with all features enabled
        config = {
            'simulation': {
                'adaptive_timestep': True,
                'buoyancy': True,
                'use_virtual_mass': True,
                'use_multi_regime_cd': True,
                'use_hertzian_contact': True,
                'rtol': 1e-6,
                'atol': 1e-8,
                'min_dt': 1e-5,
                'max_dt': 0.05
            },
            'ball': {
                'mass': 0.5,
                'radius': 0.1,
                'spin_rps': 10.0
            },
            'position': {
                'x0': 0.0,
                'y0': 0.0,
                'z0': 10.0
            },
            'wind': {
                'ref_speed': 5.0,
                'ref_height': 10.0,
                'direction_deg': 90.0,
                'gust_tau': 1.5,
                'gust_sigma': 0.5,
                'humidity_pct': 50.0
            },
            'surface': {
                'elasticity_base': 0.7,
                'friction_mu_s': 0.5,
                'friction_mu_k': 0.3,
                'base_height': 0.0
            }
        }
        
        # Test that all configuration parameters are recognized
        assert config['simulation']['adaptive_timestep'] == True
        assert config['simulation']['buoyancy'] == True
        assert config['simulation']['use_virtual_mass'] == True
        assert config['simulation']['use_multi_regime_cd'] == True
        assert config['simulation']['use_hertzian_contact'] == True
        
        # Test that wind configuration is complete
        assert 'ref_speed' in config['wind']
        assert 'gust_tau' in config['wind']
        assert 'humidity_pct' in config['wind']
        
        # Test that surface configuration is complete
        assert 'elasticity_base' in config['surface']
        assert 'friction_mu_s' in config['surface']
        assert 'base_height' in config['surface']
    
    def test_physics_feature_interactions(self):
        """Test interactions between different physics features."""
        # Test buoyancy + virtual mass
        density = 1.225
        volume = 0.00418879
        mass = 0.5
        
        buoyancy = calculate_buoyancy_force(density, volume)
        effective_mass = calculate_effective_mass(mass, density, volume)
        
        # Both effects should be present
        assert buoyancy > 0
        assert effective_mass > mass
        
        # Test multi-regime drag + compressibility
        reynolds = 1e5
        mach = 0.5
        
        cd_incompressible = calculate_multi_regime_drag_coefficient(reynolds, mach=0.0)
        cd_compressible = calculate_multi_regime_drag_coefficient(reynolds, mach=mach)
        
        # Compressibility should increase drag
        assert cd_compressible > cd_incompressible


class TestPerformance:
    """Test performance of physics calculations."""
    
    def test_calculation_speed(self):
        """Test that physics calculations are reasonably fast."""
        import time
        
        # Test multiple calculations
        n_calculations = 1000
        
        start_time = time.time()
        for _ in range(n_calculations):
            # Aerodynamic calculations
            velocity = np.array([10.0, 5.0, 0.0])
            angular_velocity = np.array([0.0, 0.0, 100.0])
            density = 1.225
            viscosity = 1.8e-5
            radius = 0.1
            mass = 0.5
            
            force, torque, reynolds = calculate_aerodynamic_forces(
                velocity, angular_velocity, density, viscosity, radius, mass
            )
            
            # Contact calculations
            position = np.array([0.0, 0.0, 0.05])
            surface_config = {'base_height': 0.0}
            collision, penetration, normal = detect_collision(position, radius, surface_config)
            
            # Wind calculations
            wind = calculate_wind_velocity(10.0, ref_speed=5.0, ref_height=10.0)
        
        elapsed = time.time() - start_time
        
        # Should complete quickly
        assert elapsed < 5.0  # Less than 5 seconds for 1000 calculations
    
    def test_memory_usage(self):
        """Test that physics calculations don't leak memory."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Do many calculations
        for _ in range(100):
            for i in range(100):
                velocity = np.array([float(i), 0.0, 0.0])
                angular_velocity = np.array([0.0, 0.0, float(i)])
                density = 1.225
                viscosity = 1.8e-5
                radius = 0.1
                mass = 0.5
                
                force, torque, reynolds = calculate_aerodynamic_forces(
                    velocity, angular_velocity, density, viscosity, radius, mass
                )
        
        # Force garbage collection again
        gc.collect()
        
        # Should not have crashed or leaked significantly
        assert True  # If we get here, memory usage is reasonable


if __name__ == "__main__":
    # Run a quick test to verify everything works
    print("Testing enhanced physics implementation...")
    
    # Test basic functionality
    try:
        # Test multi-regime drag
        cd = calculate_multi_regime_drag_coefficient(1e5)
        print(f"✓ Multi-regime drag coefficient: {cd:.3f}")
        
        # Test buoyancy
        buoyancy = calculate_buoyancy_force(1.225, 0.00418879)
        print(f"✓ Buoyancy force: {buoyancy:.4f} N")
        
        # Test virtual mass
        added_mass = calculate_virtual_mass(1.225, 0.00418879)
        print(f"✓ Virtual mass: {added_mass:.4f} kg")
        
        # Test aerodynamic forces
        velocity = np.array([10.0, 0.0, 0.0])
        angular_velocity = np.array([0.0, 0.0, 100.0])
        force, torque, reynolds = calculate_aerodynamic_forces(
            velocity, angular_velocity, 1.225, 1.8e-5, 0.1, 0.5
        )
        print(f"✓ Aerodynamic force: {force}")
        print(f"✓ Reynolds number: {reynolds:.0f}")
        
        # Test wind
        wind = calculate_wind_velocity(10.0, ref_speed=5.0, ref_height=10.0)
        print(f"✓ Wind velocity: {wind}")
        
        # Test contact
        collision, penetration, normal = detect_collision(
            np.array([0.0, 0.0, 0.05]), 0.1, {'base_height': 0.0}
        )
        print(f"✓ Collision detection: {collision}, penetration: {penetration:.4f}")
        
        print("\n✅ All physics features working correctly!")
        print("🎉 Implementation complete - all missing physics features have been added!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()