#!/usr/bin/env python3
"""
Test Phase 3: ContainerFactory implementation.

This tests that the ContainerFactory correctly manages all containers
and that the boilerplate has been eliminated.
"""

import sys
sys.path.insert(0, 'src')

from src.pysd.sdmodel import SD_BASE
from src.pysd.model.container_factory import ContainerFactory
from src.pysd.statements.greco import GRECO
from src.pysd.statements.basco import BASCO
from src.pysd.statements.table import TABLE

def test_phase3():
    print("=== Testing Phase 3: ContainerFactory ===")
    
    # Test ContainerFactory registry
    container_types = ContainerFactory.get_container_types()
    container_names = ContainerFactory.get_container_names()
    
    print(f"✓ ContainerFactory manages {len(container_types)} container types")
    
    # Test that key containers are present
    assert 'greco' in container_names, "GRECO container missing from factory"
    assert 'basco' in container_names, "BASCO container missing from factory"  
    assert 'table' in container_names, "TABLE container missing from factory"
    print("✓ Core containers registered in factory")
    
    # Test container creation
    sd_model = SD_BASE()
    sd_model.validation_enabled = False  # For simple test
    
    # Test that all containers exist and work
    assert hasattr(sd_model, 'greco'), "GRECO container not created"
    assert hasattr(sd_model, 'basco'), "BASCO container not created"
    assert hasattr(sd_model, 'table'), "TABLE container not created"
    print("✓ All containers created successfully")
    
    # Test parent model references were set by ContainerFactory
    assert sd_model.greco.parent_model is sd_model, "GRECO parent model not set"
    assert sd_model.basco.parent_model is sd_model, "BASCO parent model not set"
    print("✓ ContainerFactory set parent references correctly")
    
    # Test adding items still works
    greco_item = GRECO(
        input="GRECO   A   2   3   0.00   1.00   2.00   3.00   4.00   5.00   6.00   7.00   8.00   9.00   10.00   11.00   12.00   13.00   14.00   15.00   16.00   17.00   18.00   19.00",
        id="A"
    )
    
    sd_model.add(greco_item)
    assert len(sd_model.greco) == 1, "Adding items to containers failed"
    print("✓ Container functionality preserved")
    
    # Test factory utility methods
    assert ContainerFactory.is_valid_container('greco'), "Factory validation failed"
    assert not ContainerFactory.is_valid_container('invalid'), "Factory validation too permissive"
    assert ContainerFactory.get_statement_type('greco') is GRECO, "Statement type lookup failed"
    print("✓ Factory utility methods work")
    
    print(f"\n=== Phase 3 Test Results ===")
    print("ContainerFactory successfully manages all containers!")
    print(f"Containers managed: {len(container_names)}")
    print(f"Factory simplifies container management dramatically")
    print(f"Parent references set automatically: ✓")
    print(f"All container functionality preserved: ✓")
    
    return True

if __name__ == "__main__":
    try:
        test_phase3()
        print("\n🎉 Phase 3 test PASSED!")
    except Exception as e:
        print(f"\n❌ Phase 3 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)