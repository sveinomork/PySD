"""
Test Cases construction to debug the tuple unpacking issue.
"""

from src.pysd.statements.cases import Cases

def test_cases_construction():
    """Test different Cases construction patterns."""
    
    print("=== Cases Construction Test ===\n")
    
    # Test 1: Valid constructions
    print("📋 Test 1: Valid constructions")
    try:
        # Single values
        cases1 = Cases(ranges=[211, 212, 213])
        print(f"   ✅ Single values: {cases1.to_list()}")
        
        # Simple range
        cases2 = Cases(ranges=[(211, 215)])
        print(f"   ✅ Simple range: {cases2.to_list()}")
        
        # Mixed - range and single value
        cases3 = Cases(ranges=[(211, 215), 218])
        print(f"   ✅ Mixed format: {cases3.to_list()}")
        
    except Exception as e:
        print(f"   ❌ Valid construction failed: {type(e).__name__}: {e}")
    
    # Test 2: Your current main.py format  
    print("\n📋 Test 2: Your main.py format")
    try:
        # This is the problematic line from main.py
        cases_main = Cases(ranges=[(211, 215), 218])
        print(f"   ✅ Main.py format works: {cases_main.to_list()}")
        
    except Exception as e:
        print(f"   ❌ Main.py format failed: {type(e).__name__}: {e}")
        print(f"      Error details: {str(e)}")
    
    # Test 3: Alternative correct formats
    print("\n📋 Test 3: Alternative correct formats")
    try:
        # Correct way to include 218
        cases_alt1 = Cases(ranges=[(211, 215), (218, 218)])  # 218 as single-item range
        print(f"   ✅ Alternative 1: {cases_alt1.to_list()}")
        
        cases_alt2 = Cases(ranges=[(211, 215), 218])  # 218 as single integer
        print(f"   ✅ Alternative 2: {cases_alt2.to_list()}")
        
    except Exception as e:
        print(f"   ❌ Alternative failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_cases_construction()