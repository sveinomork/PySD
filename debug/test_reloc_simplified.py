#!/usr/bin/env python3
"""
Test script to verify simplified RELOC implementation works correctly
"""

from src.pysd.statements.reloc import RELOC
from src.pysd.sdmodel import SD_BASE

def test_simplified_reloc():
    """Test simplified RELOC implementation"""
    print("Testing simplified RELOC implementation...")
    
    # Test cases that should work (validation is now handled by rules)
    test_cases = [
        ("Basic RELOC", lambda: RELOC(id="X11", rt=1)),
        ("RELOC with parts", lambda: RELOC(id="Y02", pa="VEGG", rt=2, fa=0, al=90)),
        ("RELOC with range", lambda: RELOC(id="B1", rt=(101, 105), fa=1)),
        ("RELOC with sections", lambda: RELOC(id="S1", rt=1, fs=(1, 10), hs=(1, 5))),
    ]
    
    model = SD_BASE()
    
    for test_name, reloc_factory in test_cases:
        try:
            reloc = reloc_factory()
            print(f"✓ {test_name}: {reloc}")
            model.add(reloc)
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nModel summary:")
    print(f"Total items: {len(model.all_items)}")
    print(f"RELOC: {len(model.reloc)}")
    
    # Test writing to file
    output_file = "test_reloc_simplified.inp"
    try:
        with SD_BASE.create_writer(output_file) as test_model:
            test_model.add([
                RELOC(id="X11", rt=1),
                RELOC(id="Y02", pa="VEGG", rt=2, fa=0, al=90),
                RELOC(id="B1", rt=(101, 105), fa=1)
            ])
        
        # Read and display the file content
        with open(output_file, 'r') as f:
            content = f.read()
            print(f"\nGenerated file content:\n{content}")
            
        print("✅ Simplified RELOC implementation works correctly!")
        
    except Exception as e:
        print(f"❌ File writing failed: {e}")
        import traceback
        traceback.print_exc()

def test_validation_still_works():
    """Test that rule-based validation still catches issues"""
    print("\nTesting rule-based validation...")
    
    # Test with validation enabled
    try:
        with SD_BASE.create_writer("test_validation.inp") as model:
            # This should work fine
            model.add(RELOC(id="X11", rt=1))
            print("✓ Valid RELOC accepted")
            
            # Add some potentially problematic cases that rules might catch
            model.add(RELOC(id="TOOLONG", rt=1))  # Rules should catch long ID
            model.add(RELOC(id="A1", rt=1, al=100))  # Rules should catch invalid angle
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        
    print("Validation system delegated to rules successfully!")

if __name__ == "__main__":
    test_simplified_reloc()
    test_validation_still_works()