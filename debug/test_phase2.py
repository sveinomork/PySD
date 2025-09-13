#!/usr/bin/env python3
"""
Test script for Phase 2: StatementRouter functionality.

This tests that the routing logic has been successfully extracted
and that adding statements still works correctly.
"""

import sys
sys.path.insert(0, 'src')

from src.pysd.sdmodel import SD_BASE
from src.pysd.statements.greco import GRECO
from src.pysd.statements.basco import BASCO
from src.pysd.statements.statement_heading import HEADING
from src.pysd.validation.core import ValidationMode

def test_phase2():
    print("=== Testing Phase 2: StatementRouter ===")
    
    # Create model with validation disabled for testing
    sd_model = SD_BASE()
    sd_model.validation_enabled = False
    
    # Check that router was initialized
    assert hasattr(sd_model, 'router'), "StatementRouter not initialized"
    print("✓ StatementRouter initialized")
    
    # Test single item routing
    greco_item = GRECO(
        input="GRECO   A   2   3   0.00   1.00   2.00   3.00   4.00   5.00   6.00   7.00   8.00   9.00   10.00   11.00   12.00   13.00   14.00   15.00   16.00   17.00   18.00   19.00",
        id="A"
    )
    
    sd_model.add(greco_item)
    assert len(sd_model.greco) == 1, "Single item routing failed"
    assert sd_model.greco.get_by_id("A") is not None, "Item not found by ID"
    print("✓ Single item routing works")
    
    # Test batch routing with HEADING (simple statement)
    heading_items = [
        HEADING(input="HEADING   This is a test heading"),
    ]
    
    sd_model.add(heading_items)
    assert len(sd_model.heading) == 1, f"Batch routing failed: expected 1, got {len(sd_model.heading)}"
    print("✓ Batch routing works")
    
    # Test routing registry
    router = sd_model.router
    supported_types = router.get_supported_types()
    assert GRECO in supported_types, "GRECO not in routing registry"
    assert HEADING in supported_types, "HEADING not in routing registry"
    print(f"✓ Router supports {len(supported_types)} statement types")
    
    # Test container name lookup
    assert router.get_container_name(GRECO) == 'greco', "Wrong container name for GRECO"
    assert router.get_container_name(HEADING) == '_heading_list', "Wrong container name for HEADING"
    print("✓ Container name lookup works")
    
    # Test that all_items is maintained
    assert len(sd_model.all_items) == 2, f"all_items count wrong: {len(sd_model.all_items)} (expected 2: 1 GRECO + 1 HEADING)"
    print("✓ all_items list maintained correctly")
    
    print("\n=== Phase 2 Test Results ===")
    print("StatementRouter successfully replaces routing logic!")
    print(f"GRECO container: {len(sd_model.greco)} items")
    print(f"HEADING list: {len(sd_model.heading)} items") 
    print(f"Total items: {len(sd_model.all_items)}")
    print(f"Supported statement types: {len(supported_types)}")
    
    return True

if __name__ == "__main__":
    try:
        test_phase2()
        print("\n🎉 Phase 2 test PASSED!")
    except Exception as e:
        print(f"\n❌ Phase 2 test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)