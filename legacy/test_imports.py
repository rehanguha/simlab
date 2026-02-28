#!/usr/bin/env python3
"""
Test script to verify physimlab package imports work correctly.
"""

def test_basic_imports():
    """Test that all main modules can be imported."""
    print("Testing basic imports...")
    
    try:
        import physimlab
        print("✓ physimlab package imported successfully")
        print(f"  Version: {physimlab.__version__}")
        print(f"  Author: {physimlab.__author__}")
        print(f"  License: {physimlab.__license__}")
    except ImportError as e:
        print(f"✗ Failed to import physimlab: {e}")
        return False
    
    try:
        from physimlab import run_simulation
        print("✓ run_simulation function imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import run_simulation: {e}")
        return False
    
    try:
        from physimlab import batch_simulation
        print("✓ batch_simulation function imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import batch_simulation: {e}")
        return False
    
    try:
        from physimlab import compare_results
        print("✓ compare_results function imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import compare_results: {e}")
        return False
    
    return True

def test_submodule_imports():
    """Test that submodules can be imported."""
    print("\nTesting submodule imports...")
    
    modules_to_test = [
        'physimlab.config',
        'physimlab.physics',
        'physimlab.output',
        'physimlab.utils'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
            return False
    
    return True

def test_cli_import():
    """Test that CLI module can be imported."""
    print("\nTesting CLI import...")
    
    try:
        from physimlab.cli import app
        print("✓ CLI app imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CLI: {e}")
        return False
    
    return True

def test_core_imports():
    """Test that core simulation functions work."""
    print("\nTesting core simulation imports...")
    
    try:
        from physimlab.core import run_simulation
        print("✓ Core run_simulation imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core run_simulation: {e}")
        return False
    
    return True

def main():
    """Run all import tests."""
    print("physimlab Import Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test basic imports
    if not test_basic_imports():
        all_passed = False
    
    # Test submodule imports
    if not test_submodule_imports():
        all_passed = False
    
    # Test CLI import
    if not test_cli_import():
        all_passed = False
    
    # Test core imports
    if not test_core_imports():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All import tests passed!")
        return 0
    else:
        print("✗ Some import tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())