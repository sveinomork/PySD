"""
Simple test script to verify the new simplified API works correctly.
"""

from src.pysd.statements import DECAS, BASCO, LoadCase, LOADC
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation.core import ValidationLevel

def test_successful_api():
    print("Testing new simplified API - successful case...")
    
    # NEW SIMPLIFIED API: No context managers
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    print(f"Created model with validation_level='{model.validation_level}', cross_object_validation={model.cross_object_validation}")
    
    # Add statements with immediate validation
    model.add(LOADC(run_number=1, alc=1, olc=110))
    print("Added LOADC statement")
    
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
    print("Added BASCO statement")
    
    # Add DECAS with immediate validation - should work
    decas = DECAS(ls='ULS', bas=101)
    model.add(decas, validation=True)  # Immediate validation
    print(f"Added DECAS statement with immediate validation: {decas.input}")
    
    # Write to file using simple API
    output_file = "test_successful_api.inp"
    model.write(output_file)
    print(f"✅ Model written to {output_file}")
    
    print("✅ New API test completed successfully!")

def test_validation_error():
    print("\nTesting validation error handling...")
    
    # Create a separate model for testing validation errors
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    
    model.add(LOADC(run_number=1, alc=1, olc=110))
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
    
    # Test validation error with immediate feedback
    try:
        bad_decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
        model.add(bad_decas, validation=True)  # Should fail immediately
        print("❌ Expected validation error was not caught")
    except ValueError as e:
        print(f"✅ Immediate validation caught error: {str(e)[:80]}...")
        print("   Validation failed as expected!")

def test_disabled_validation():
    print("\nTesting disabled validation level...")
    
    # Create model with disabled validation
    model = SD_BASE(validation_level=ValidationLevel.DISABLED)
    print(f"Created model with validation_level='{model.validation_level}'")
    
    # Should be able to add invalid statements without error
    model.add(LOADC(run_number=1, alc=1, olc=110))
    # No BASCO defined - this should not raise an error
    decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
    model.add(decas, validation=True)  # Should not fail with disabled validation
    
    print(f"Added DECAS with invalid reference: {decas.input}")
    
    # Write to file
    output_file = "test_disabled_validation.inp"
    model.write(output_file)
    print(f"✅ Model with disabled validation written to {output_file}")

if __name__ == "__main__":
    test_successful_api()
    test_validation_error()
    test_disabled_validation()
    print("\n🎉 All API tests completed!")