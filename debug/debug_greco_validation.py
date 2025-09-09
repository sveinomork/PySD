"""
Debug script to test GRECO BAS cross-reference validation.
"""

from src.pysd.statements import BASCO, GRECO, LoadCase, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def debug_greco_validation():
    """Debug GRECO BAS cross-reference validation."""
    
    print("=== GRECO BAS Cross-Reference Validation Debug ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    with SD_BASE.create_writer("debug_greco.inp") as sd_model:
        
        print("📋 Step 1: Adding BASCO statements (211-216)")
        # Add BASCO statements 211-216 (note: range(6) creates 6 items)
        for i in range(6):
            basco_id = 211 + i
            load_cases = [LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)]
            basco = BASCO(id=basco_id, load_cases=load_cases)
            sd_model.add(basco)
            print(f"   Added BASCO {basco_id}")
        
        print(f"\n📋 Step 2: Current BASCO IDs in model: {sd_model.basco.get_ids()}")
        
        print("\n📋 Step 3: Trying to add GRECO with BAS=(211,215),218")
        try:
            greco_support = GRECO(
                id='A',
                bas=Cases(ranges=[(211, 215), 218])
            )
            print(f"   GRECO BAS list: {greco_support.bas.to_list()}")
            
            # This should trigger validation error for missing BAS 218
            sd_model.add(greco_support)
            print("   ✅ GRECO added successfully (unexpected!)")
            
        except Exception as e:
            print(f"   ❌ GRECO validation caught error: {type(e).__name__}")
            print(f"      Error: {str(e)}")
        
        print(f"\n📋 Step 4: Final model summary")
        summary = sd_model.get_validation_summary()
        print(f"   Total items: {summary['total_items']}")
        print(f"   BASCO count: {summary['containers']['basco']}")
        print(f"   Has errors: {summary['has_errors']}")
        print(f"   Has warnings: {summary['has_warnings']}")
        
        # Manual validation check
        print(f"\n📋 Step 5: Manual cross-reference check")
        basco_ids = sd_model.basco.get_ids()
        greco_bas_list = [218]  # The problematic reference
        
        print(f"   Available BASCO IDs: {basco_ids}")
        print(f"   GRECO BAS references: {greco_bas_list}")
        
        missing_refs = [bas_id for bas_id in greco_bas_list if bas_id not in basco_ids]
        print(f"   Missing BAS references: {missing_refs}")
        
        if missing_refs:
            print(f"   ❌ Missing references detected: {missing_refs}")
        else:
            print(f"   ✅ All references valid")

if __name__ == "__main__":
    debug_greco_validation()