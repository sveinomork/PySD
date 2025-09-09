"""
Debug script to identify the exact source of the tuple/load_cases error.
"""

from src.pysd.statements import BASCO, LOADC, LoadCase
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def debug_basco_tuple_issue():
    """Debug the tuple/load_cases attribute error."""
    
    print("=== BASCO Tuple Issue Debug ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    try:
        with SD_BASE.create_writer("debug_basco.inp") as sd_model:
            
            print("📋 Step 1: Adding first LOADC")
            loadc = LOADC(run_number=1, alc=(1,6), olc=(101,106))
            sd_model.add(loadc)
            print("   ✅ LOADC added successfully")
            
            print("📋 Step 2: Adding first BASCO (this should trigger the error)")
            load_cases = [LoadCase(lc_type='OLC', lc_numb=201, lc_fact=1)]
            basco = BASCO(id=211, load_cases=load_cases)
            
            print(f"   BASCO object: {basco}")
            print(f"   BASCO id: {basco.id}")
            print(f"   BASCO load_cases: {basco.load_cases}")
            print(f"   BASCO load_cases type: {type(basco.load_cases)}")
            
            sd_model.add(basco)  # This should trigger the error
            print("   ✅ BASCO added successfully")
            
    except Exception as e:
        print(f"   ❌ Error occurred: {type(e).__name__}: {e}")
        
        # Print some debugging info
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_basco_tuple_issue()