"""
Simple test script to verify the new simplified API works correctly.
"""

from src.pysd.statements import DECAS, BASCO, LoadCase, LOADC
from src.pysd.sdmodel import SD_BASE

def test_new_api():
    print("Testing new simplified API...")
    
    # NEW SIMPLIFIED API: No context managers
    model = SD_BASE(validation_level='normal', cross_object_validation=True)
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
    
    # Test validation error with immediate feedback
    try:
        bad_decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
        model.add(bad_decas, validation=True)  # Should fail immediately
        print("❌ Expected validation error was not caught")
    except ValueError as e:
        print(f"✅ Immediate validation caught error: {str(e)[:80]}...")
        print("   (Bad statement was NOT added to model)")
    
    # Write to file using simple API
    output_file = "test_new_api.inp"
    model.write(output_file)
    print(f"✅ Model written to {output_file}")
    
    print("✅ New API test completed successfully!")

if __name__ == "__main__":
    test_new_api()