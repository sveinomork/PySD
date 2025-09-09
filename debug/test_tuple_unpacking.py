"""
Isolate the tuple unpacking issue to fix GRECO validation.
"""

from src.pysd.statements import LOADC, BASCO, GRECO, LoadCase, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def test_tuple_unpacking_issue():
    """Test to isolate the tuple unpacking issue."""
    
    print("=== Isolating Tuple Unpacking Issue ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    # Test 1: Just add individual LOADC statements (not as batch)
    print("📋 Test 1: Adding LOADC statements individually")
    try:
        with SD_BASE.create_writer("test1.inp") as sd_model:
            sd_model.add(LOADC(run_number=1, alc=(1,6), olc=(101,106)))
            sd_model.add(LOADC(table=True))
            sd_model.add(LOADC(pri=True))
            print("   ✅ Individual LOADC statements added successfully")
    except Exception as e:
        print(f"   ❌ Individual LOADC failed: {type(e).__name__}: {e}")
    
    # Test 2: Add LOADC as batch (like in main.py)
    print("\n📋 Test 2: Adding LOADC statements as batch")
    try:
        with SD_BASE.create_writer("test2.inp") as sd_model:
            loadc_list = [
                LOADC(run_number=1, alc=(1,6), olc=(101,106)),
                LOADC(table=True),
                LOADC(pri=True)
            ]
            sd_model.add(loadc_list)
            print("   ✅ Batch LOADC statements added successfully")
    except Exception as e:
        print(f"   ❌ Batch LOADC failed: {type(e).__name__}: {e}")
        print(f"      Error details: {str(e)[:200]}...")
    
    # Test 3: Add BASCO and then GRECO (the main issue)
    print("\n📋 Test 3: Adding BASCO + GRECO to trigger the validation")
    try:
        with SD_BASE.create_writer("test3.inp") as sd_model:
            # Add BASCO 211-216 (only 6, missing 218)
            for i in range(6):
                basco = BASCO(id=211+i, load_cases=[LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)])
                sd_model.add(basco)
            
            print(f"   Added BASCO IDs: {sd_model.basco.get_ids()}")
            
            # Try to add GRECO that references non-existent BAS 218 (should fail)
            greco = GRECO(id='A', bas=Cases(ranges=[(211, 215), 218]))
            print(f"   GRECO references BAS: {greco.bas.to_list()}")
            
            sd_model.add(greco)  # This SHOULD raise validation error
            print("   ❌ GRECO added successfully (THIS IS WRONG - should have failed!)")
            
    except ValueError as e:
        if "GRECO A references non-existent BAS 218" in str(e):
            print("   ✅ GRECO validation correctly caught missing BAS 218!")
        else:
            print(f"   ❌ GRECO failed with unexpected error: {e}")
    except Exception as e:
        print(f"   ❌ GRECO failed with unexpected error type: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_tuple_unpacking_issue()