#!/usr/bin/env python3
"""
Test script to debug DESEC implementation issues
"""

from src.pysd.statements.desec import DESEC
from src.pysd.sdmodel import SD_BASE

def test_desec_creation():
    """Test DESEC creation and string generation"""
    print("Testing DESEC creation...")
    
    # Test basic DESEC creation
    try:
        desec1 = DESEC(pa="VEGG_2")
        print(f"✓ DESEC created: {desec1}")
        print(f"  ID: {desec1.id}")
        print(f"  Input string: '{desec1.input}'")
        print(f"  Build input: '{desec1.build_input_string()}'")
        
        desec2 = DESEC(pa="PLATE") 
        print(f"✓ DESEC created: {desec2}")
        print(f"  ID: {desec2.id}")
        print(f"  Input string: '{desec2.input}'")
        print(f"  Build input: '{desec2.build_input_string()}'")
        
    except Exception as e:
        print(f"❌ Error creating DESEC: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return [desec1, desec2]

def test_desec_in_model():
    """Test DESEC in SD_BASE model"""
    print("\nTesting DESEC in SD_BASE...")
    
    model = SD_BASE()
    
    try:
        desec_items = test_desec_creation()
        if desec_items:
            model.add(desec_items)
            
            print(f"Model has {len(model.desec)} DESEC items")
            print(f"Model has {len(model.all_items)} total items")
            
            # Check if items have proper string representations
            for i, item in enumerate(model.all_items):
                print(f"Item {i}: {type(item).__name__} -> '{str(item)}'")
                
            return model
    except Exception as e:
        print(f"❌ Error adding DESEC to model: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def test_desec_writing():
    """Test DESEC writing to file"""
    print("\nTesting DESEC writing to file...")
    
    output_file = "test_desec_output.inp"
    
    try:
        with SD_BASE.create_writer(output_file) as model:
            model.add(DESEC(pa="TESTPART"))
        
        # Read the file to check content
        with open(output_file, 'r') as f:
            content = f.read()
            print(f"File content:\n{content}")
            
        if "DESEC" in content:
            print("✅ DESEC was written to file!")
        else:
            print("❌ DESEC was NOT written to file!")
            
    except Exception as e:
        print(f"❌ Error writing DESEC: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_desec_creation()
    test_desec_in_model() 
    test_desec_writing()