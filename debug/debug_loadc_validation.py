"""
Debug LOADC validation to find the tuple unpacking issue.
"""

from src.pysd.statements import LOADC
from src.pysd.validation import set_validation_mode, ValidationMode

def debug_loadc_validation():
    """Debug LOADC validation to find tuple unpacking issues."""
    
    print("=== LOADC Validation Debug ===\n")
    
    set_validation_mode(ValidationMode.STRICT)
    
    # Test the specific LOADC instances from main.py
    loadc_instances = [
        {"name": "Normal LOADC", "args": {"run_number": 1, "alc": (1,6), "olc": (101,106)}},
        {"name": "Table LOADC", "args": {"table": True}},
        {"name": "PRI LOADC", "args": {"pri": True}}
    ]
    
    for test_case in loadc_instances:
        print(f"📋 Testing {test_case['name']}")
        try:
            loadc = LOADC(**test_case['args'])
            print(f"   ✅ Created: {loadc}")
            
            # Check the field values
            print(f"      alc type: {type(loadc.alc)}, value: {loadc.alc}")
            print(f"      olc type: {type(loadc.olc)}, value: {loadc.olc}")
            
            # Test alc.to_list() if alc exists
            if loadc.alc:
                try:
                    alc_list = loadc.alc.to_list()
                    print(f"      alc.to_list(): {alc_list}")
                except Exception as e:
                    print(f"      ❌ alc.to_list() failed: {type(e).__name__}: {e}")
            
            # Test olc.to_list() if olc exists
            if loadc.olc:
                try:
                    if hasattr(loadc.olc, 'to_list'):
                        olc_list = loadc.olc.to_list()
                        print(f"      olc.to_list(): {olc_list}")
                    else:
                        print(f"      olc has no to_list() method")
                except Exception as e:
                    print(f"      ❌ olc.to_list() failed: {type(e).__name__}: {e}")
            
        except Exception as e:
            print(f"   ❌ Creation failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    debug_loadc_validation()