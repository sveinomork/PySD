"""
Debug LOADC validation to find the exact tuple unpacking issue.
"""

from src.pysd.statements import LOADC
from src.pysd.validation import set_validation_mode, ValidationMode

def debug_loadc_validation():
    """Debug LOADC validation to find tuple unpacking issue."""
    
    print("=== LOADC Validation Debug ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    # Test individual LOADC statements that might cause issues
    test_cases = [
        ("LOADC with run_number and tuples", {"run_number": 1, "alc": (1,6), "olc": (101,106)}),
        ("LOADC with table=True", {"table": True}),
        ("LOADC with pri=True", {"pri": True}),
    ]
    
    for description, kwargs in test_cases:
        print(f"📋 Testing: {description}")
        print(f"   Args: {kwargs}")
        
        try:
            loadc = LOADC(**kwargs)
            print(f"   ✅ LOADC created successfully")
            print(f"   ALC: {loadc.alc} (type: {type(loadc.alc)})")
            print(f"   OLC: {loadc.olc} (type: {type(loadc.olc)})")
            
            # Check what the validation will see
            if hasattr(loadc.alc, 'to_list'):
                print(f"   ALC.to_list(): {loadc.alc.to_list()}")
            if hasattr(loadc.olc, 'to_list'):
                print(f"   OLC.to_list(): {loadc.olc.to_list()}")
                
        except Exception as e:
            print(f"   ❌ LOADC creation failed: {type(e).__name__}: {e}")
        
        print()

if __name__ == "__main__":
    debug_loadc_validation()