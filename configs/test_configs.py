#!/usr/bin/env python3
"""
Test script to validate all configuration files work with SimLab.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_loading():
    """Test that all config files can be loaded successfully."""
    print("Testing configuration file loading...")
    
    configs_dir = Path(__file__).parent
    config_files = list(configs_dir.glob("config_*.json"))
    
    if not config_files:
        print("❌ No configuration files found!")
        return False
    
    print(f"Found {len(config_files)} configuration files:")
    
    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Basic validation
            required_sections = ['scenario', 'ball', 'position', 'wind', 'simulation', 'output']
            missing_sections = [section for section in required_sections if section not in config]
            
            if missing_sections:
                print(f"  ❌ {config_file.name}: Missing sections: {missing_sections}")
                continue
            
            # Validate ball properties
            ball = config['ball']
            if ball['mass'] <= 0 or ball['radius'] <= 0:
                print(f"  ❌ {config_file.name}: Invalid ball properties")
                continue
            
            # Validate position
            position = config['position']
            if position['z0'] <= 0:
                print(f"  ❌ {config_file.name}: Invalid initial height")
                continue
            
            print(f"  ✅ {config_file.name}: Valid configuration")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ {config_file.name}: Invalid JSON - {e}")
        except Exception as e:
            print(f"  ❌ {config_file.name}: Error - {e}")
    
    return True

def test_simulation_import():
    """Test that SimLab can be imported and basic functions work."""
    print("\nTesting SimLab import...")
    
    try:
        from simlab.core import run_simulation, ConfigLoader
        print("  ✅ SimLab core modules imported successfully")
        
        # Test config loader
        loader = ConfigLoader()
        print("  ✅ ConfigLoader instantiated successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_sample_simulation():
    """Test running a simple simulation with one of the configs."""
    print("\nTesting sample simulation...")
    
    try:
        from simlab.core import run_simulation
        
        # Use the validation suite config for a quick test
        config_path = Path(__file__).parent / "config_validation_suite.json"
        
        if not config_path.exists():
            print("  ❌ Validation suite config not found")
            return False
        
        print(f"  🔄 Running simulation with {config_path.name}...")
        
        # Run a quick test simulation
        result = run_simulation(
            config_path=str(config_path),
            output_dir="test_output"
        )
        
        print("  ✅ Simulation completed successfully")
        print(f"     Flight time: {result['summary']['flight_time']:.2f} seconds")
        print(f"     Max height: {result['summary']['max_height']:.2f} meters")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Simulation failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 SimLab Configuration Test Suite")
    print("=" * 40)
    
    # Test 1: Config loading
    config_test = test_config_loading()
    
    # Test 2: SimLab import
    import_test = test_simulation_import()
    
    # Test 3: Sample simulation (only if imports work)
    simulation_test = True
    if import_test:
        simulation_test = test_sample_simulation()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"  Config Loading: {'✅ PASS' if config_test else '❌ FAIL'}")
    print(f"  SimLab Import: {'✅ PASS' if import_test else '❌ FAIL'}")
    print(f"  Sample Simulation: {'✅ PASS' if simulation_test else '❌ FAIL'}")
    
    if all([config_test, import_test, simulation_test]):
        print("\n🎉 All tests passed! Configuration files are ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())