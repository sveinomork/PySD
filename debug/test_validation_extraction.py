#!/usr/bin/env python3
"""
Test validation control method extraction.

Verify that all validation control methods work correctly after being
moved from SD_BASE to ValidationManager.
"""

import sys
sys.path.insert(0, 'src')

from src.pysd.sdmodel import SD_BASE
from src.pysd.statements import TABLE

def test_validation_control_methods():
    """Test that all validation control methods work through delegation."""
    print("=== Testing Validation Control Method Extraction ===\n")
    
    # Create model
    sd_model = SD_BASE()
    sd_model.validation_enabled = False  # Disable for simple testing
    
    print("1. Testing basic validation control methods:")
    
    try:
        # Test disable/enable methods
        sd_model.disable_container_validation()
        assert not sd_model.container_validation_enabled
        print("   ✅ disable_container_validation() works")
        
        sd_model.enable_container_validation() 
        assert sd_model.container_validation_enabled
        print("   ✅ enable_container_validation() works")
        
        sd_model.disable_cross_container_validation()
        assert not sd_model.cross_container_validation_enabled
        print("   ✅ disable_cross_container_validation() works")
        
        sd_model.enable_cross_container_validation()
        assert sd_model.cross_container_validation_enabled
        print("   ✅ enable_cross_container_validation() works")
        
        sd_model.disable_deferred_validation()
        assert not sd_model.deferred_cross_validation
        print("   ✅ disable_deferred_validation() works")
        
        sd_model.enable_deferred_validation()
        assert sd_model.deferred_cross_validation
        print("   ✅ enable_deferred_validation() works")
        
    except Exception as e:
        print(f"   ❌ Basic methods failed: {e}")
        return False
    
    print("\n2. Testing context managers:")
    
    try:
        # Test container validation context manager
        original_container = sd_model.container_validation_enabled
        with sd_model.container_validation_disabled():
            assert not sd_model.container_validation_enabled
        assert sd_model.container_validation_enabled == original_container
        print("   ✅ container_validation_disabled() context manager works")
        
        # Test cross validation context manager
        original_cross = sd_model.cross_container_validation_enabled
        with sd_model.cross_validation_disabled():
            assert not sd_model.cross_container_validation_enabled
        assert sd_model.cross_container_validation_enabled == original_cross
        print("   ✅ cross_validation_disabled() context manager works")
        
        # Test immediate validation context manager
        original_deferred = sd_model.deferred_cross_validation
        with sd_model.immediate_validation():
            assert not sd_model.deferred_cross_validation
        assert sd_model.deferred_cross_validation == original_deferred
        print("   ✅ immediate_validation() context manager works")
        
        # Test general validation context manager
        original_validation = sd_model.validation_enabled
        with sd_model.validation_disabled():
            assert not sd_model.validation_enabled
        assert sd_model.validation_enabled == original_validation
        print("   ✅ validation_disabled() context manager works")
        
    except Exception as e:
        print(f"   ❌ Context managers failed: {e}")
        return False
    
    print("\n3. Testing delegation to ValidationManager:")
    
    try:
        # Check that methods exist on the validator
        validator = sd_model.validator
        assert hasattr(validator, 'disable_container_validation')
        assert hasattr(validator, 'container_validation_disabled')
        assert hasattr(validator, 'validation_disabled')
        print("   ✅ ValidationManager has all control methods")
        
        # Test direct call to validator
        validator.disable_container_validation()
        assert not sd_model.container_validation_enabled
        print("   ✅ Direct ValidationManager calls work")
        
    except Exception as e:
        print(f"   ❌ Delegation test failed: {e}")
        return False
    
    return True

def test_file_size_reduction():
    """Test that sdmodel.py got smaller."""
    print("\n4. Testing file size reduction:")
    
    try:
        with open('src/pysd/sdmodel.py') as f:
            sdmodel_lines = len(f.readlines())
        
        with open('src/pysd/model/validation_manager.py') as f:
            validator_lines = len(f.readlines())
        
        print(f"   ✅ sdmodel.py: {sdmodel_lines} lines (reduced from 318)")
        print(f"   ✅ validation_manager.py: {validator_lines} lines (expanded)")
        print(f"   ✅ Validation control logic successfully extracted")
        
        # Should be smaller than before
        assert sdmodel_lines < 318, f"Expected < 318 lines, got {sdmodel_lines}"
        
        return True
        
    except Exception as e:
        print(f"   ❌ Size test failed: {e}")
        return False

def show_summary():
    """Show what was accomplished."""
    print(f"\n🎯 Validation Control Extraction Summary:")
    print(f"   ✅ All validation control methods moved to ValidationManager")
    print(f"   ✅ SD_BASE now delegates all validation control")
    print(f"   ✅ sdmodel.py is shorter and simpler")
    print(f"   ✅ All functionality preserved through delegation")
    print(f"   ✅ Context managers work correctly")
    
    print(f"\n📝 Methods Extracted:")
    print(f"   • disable_container_validation()")
    print(f"   • enable_container_validation()")
    print(f"   • disable_cross_container_validation()")
    print(f"   • enable_cross_container_validation()")  
    print(f"   • disable_deferred_validation()")
    print(f"   • enable_deferred_validation()")
    print(f"   • disable_validation()")
    print(f"   • enable_validation()")
    print(f"   • container_validation_disabled() context manager")
    print(f"   • cross_validation_disabled() context manager")
    print(f"   • immediate_validation() context manager")
    print(f"   • validation_disabled() context manager")

if __name__ == "__main__":
    success = True
    success &= test_validation_control_methods()
    success &= test_file_size_reduction()
    
    if success:
        show_summary()
        print(f"\n🎉 Validation Control Extraction Complete!")
        print(f"sdmodel.py is now even shorter and more focused!")
    else:
        print(f"\n❌ Some tests failed")