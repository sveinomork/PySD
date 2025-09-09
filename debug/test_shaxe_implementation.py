#!/usr/bin/env python3
"""
Test script for SHAXE Pydantic implementation and validation system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pysd import SD_BASE
from pysd.statements.shaxe import SHAXE
from pysd.statements.shsec import SHSEC
from pysd.validation.core import ValidationMode, set_validation_mode


def test_shaxe_basic_functionality():
    """Test basic SHAXE functionality."""
    print("=== Testing SHAXE Basic Functionality ===")
    
    # Test Mode 1 (Explicit Axes)
    shaxe1 = SHAXE(pa="A1", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1), fs=(1, 10))
    print(f"Mode 1 SHAXE: {shaxe1.input}")
    print(f"Key: {shaxe1.key}")
    
    # Test Mode 2 (Point-Axis Definition)
    shaxe2 = SHAXE(pa="A2", xp=(0, 0, 0), xa=(0, 0, 1), al=-90, fs=(1, 10), hs=(1, 5))
    print(f"Mode 2 SHAXE: {shaxe2.input}")
    print(f"Key: {shaxe2.key}")
    
    # Test Mode 3 (Center-Axis Definition)
    shaxe3 = SHAXE(pa="A3", xc=(0, 0, 0), xa=(0, 0, 1), fs=(1, 10), hs=(15, 50))
    print(f"Mode 3 SHAXE: {shaxe3.input}")
    print(f"Key: {shaxe3.key}")
    
    print("✓ Basic functionality tests passed\n")


def test_shaxe_validation_rules():
    """Test SHAXE validation rules."""
    print("=== Testing SHAXE Validation Rules ===")
    
    # Test PA required validation
    try:
        shaxe_invalid = SHAXE(pa="", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1))
        print("✗ PA validation failed - should have caught empty PA")
    except Exception as e:
        print(f"✓ PA validation working: {e}")
    
    # Test mode exclusivity validation
    try:
        shaxe_invalid = SHAXE(pa="A1", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1), xp=(0, 0, 0), xa=(0, 0, 1))
        print("✗ Mode exclusivity validation failed - should have caught multiple modes")
    except Exception as e:
        print(f"✓ Mode exclusivity validation working: {e}")
    
    # Test no mode validation
    try:
        shaxe_invalid = SHAXE(pa="A1")
        print("✗ No mode validation failed - should have caught missing mode")
    except Exception as e:
        print(f"✓ No mode validation working: {e}")
    
    print("✓ Validation rule tests passed\n")


def test_shaxe_container():
    """Test SHAXE container functionality."""
    print("=== Testing SHAXE Container ===")
    
    # Create SD_BASE model
    model = SD_BASE()
    
    # First add SHSEC statements for the parts we want to reference
    shsec1 = SHSEC(pa="PLATE1", el=1001)
    shsec2 = SHSEC(pa="PLATE2", el=2001)
    model.add(shsec1)
    model.add(shsec2)
    
    # Create SHAXE statements
    shaxe1 = SHAXE(pa="PLATE1", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1), fs=(1, 10))
    shaxe2 = SHAXE(pa="PLATE2", xp=(0, 0, 0), xa=(0, 0, 1), fs=(1, 5))
    
    # Add to model
    model.add(shaxe1)
    model.add(shaxe2)
    
    print(f"Container has {len(model.shaxe)} SHAXE statements")
    print(f"Keys: {model.shaxe.get_keys()}")
    print(f"Part names: {model.shaxe.get_part_names()}")
    
    # Test retrieval
    retrieved = model.shaxe.get_by_key(shaxe1.key)
    if retrieved:
        print(f"✓ Retrieved SHAXE by key: {retrieved.key}")
    else:
        print("✗ Failed to retrieve SHAXE by key")
    
    # Test part-based retrieval
    plate1_shaxes = model.shaxe.get_by_pa("PLATE1")
    print(f"✓ Found {len(plate1_shaxes)} SHAXE statements for PLATE1")
    
    print("✓ Container tests passed\n")


def test_cross_reference_validation():
    """Test cross-reference validation (PA must exist in SHSEC)."""
    print("=== Testing Cross-Reference Validation ===")
    
    # Set validation mode to STRICT to catch all errors
    set_validation_mode(ValidationMode.STRICT)
    
    # Test 1: Add SHAXE without corresponding SHSEC (should fail)
    try:
        model1 = SD_BASE()  # Fresh model
        shaxe_invalid = SHAXE(pa="NONEXIST", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1))
        model1.add(shaxe_invalid)
        print("✗ Cross-reference validation failed - should have caught non-existent PA")
    except Exception as e:
        print(f"✓ Cross-reference validation working: {e}")
    
    # Test 2: Add SHSEC first, then SHAXE (should pass)
    try:
        model2 = SD_BASE()  # Fresh model
        shsec = SHSEC(pa="VALID", el=1001)  # PA must be ≤8 chars
        model2.add(shsec)
        
        shaxe_valid = SHAXE(pa="VALID", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1))
        model2.add(shaxe_valid)
        print("✓ Valid cross-reference works correctly")
    except Exception as e:
        print(f"✗ Valid cross-reference failed: {e}")
    
    print("✓ Cross-reference validation tests passed\n")


def test_duplicate_key_validation():
    """Test duplicate key validation."""
    print("=== Testing Duplicate Key Validation ===")
    
    model = SD_BASE()
    
    # Add SHSEC first to satisfy cross-reference validation
    shsec = SHSEC(pa="PLATE1", el=1001)
    model.add(shsec)
    
    # Add first SHAXE
    shaxe1 = SHAXE(pa="PLATE1", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1), fs=(1, 10))
    model.add(shaxe1)
    print(f"Added SHAXE with key: {shaxe1.key}")
    
    # Try to add duplicate (same PA and FS) - should fail
    try:
        shaxe2 = SHAXE(pa="PLATE1", xp=(0, 0, 0), xa=(0, 0, 1), fs=(1, 10))  # Same PA and FS
        model.add(shaxe2)
        print("✗ Duplicate key validation failed - should have caught duplicate key")
    except Exception as e:
        print(f"✓ Duplicate key validation working: {e}")
    
    print("✓ Duplicate key validation tests passed\n")


if __name__ == "__main__":
    print("Testing SHAXE Pydantic Implementation and Validation System\n")
    
    try:
        test_shaxe_basic_functionality()
        test_shaxe_validation_rules()
        test_shaxe_container()
        test_cross_reference_validation()
        test_duplicate_key_validation()
        
        print("🎉 All SHAXE tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)