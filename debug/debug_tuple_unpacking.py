"""
Focused debug script to identify the exact source of the tuple unpacking error.
"""

from src.pysd.statements import BASCO, GRECO, LoadCase, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def debug_tuple_unpacking():
    """Debug the exact source of tuple unpacking error."""
    
    print("=== Tuple Unpacking Debug ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    print("📋 Step 1: Test Cases creation")
    try:
        bas_cases = Cases(ranges=[(211, 215), 218])
        print(f"   ✅ Cases created: {bas_cases.to_list()}")
    except Exception as e:
        print(f"   ❌ Cases creation failed: {type(e).__name__}: {e}")
        return
    
    print("\n📋 Step 2: Test GRECO creation")
    try:
        greco_test = GRECO(id='A', bas=bas_cases)
        print(f"   ✅ GRECO created with BAS: {greco_test.bas.to_list()}")
    except Exception as e:
        print(f"   ❌ GRECO creation failed: {type(e).__name__}: {e}")
        return
        
    print("\n📋 Step 3: Test adding to empty SD_BASE")
    try:
        with SD_BASE.create_writer("debug_empty.inp") as sd_model:
            sd_model.add(greco_test)
            print("   ✅ GRECO added to empty model (should fail validation)")
    except Exception as e:
        print(f"   ❌ Empty model test failed: {type(e).__name__}: {e}")
        print(f"      Error: {str(e)[:200]}...")
    
    print("\n📋 Step 4: Test adding BASCO first, then GRECO")
    try:
        with SD_BASE.create_writer("debug_basco.inp") as sd_model:
            # Add some BASCO items (but not 218)
            for i in range(6):  # Creates 211-216
                basco_id = 211 + i
                basco = BASCO(id=basco_id, load_cases=[LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)])
                sd_model.add(basco)
                print(f"      Added BASCO {basco_id}")
            
            print(f"      Available BASCO IDs: {sd_model.basco.get_ids()}")
            
            # Now add GRECO (this should trigger the missing BAS 218 error)
            sd_model.add(greco_test)
            print("   ❌ GRECO added successfully (unexpected!)")
            
    except Exception as e:
        print(f"   ✅ BASCO+GRECO test caught error: {type(e).__name__}")
        print(f"      Error: {str(e)[:200]}...")
        
        # Try to identify the exact location of the tuple unpacking error
        import traceback
        print(f"\n      Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_tuple_unpacking()