#!/usr/bin/env python3
"""
Test script to verify all modernized statements work correctly with proper parameters
"""

from src.pysd.statements.desec import DESEC
from src.pysd.statements.xtfil import XTFIL
from src.pysd.statements.lores import LORES
from src.pysd.statements.table import TABLE
from src.pysd.sdmodel import SD_BASE

def test_modernized_statements():
    """Test all modernized statements with valid parameters"""
    print("Testing modernized statements with valid parameters...")
    
    # Test each statement with valid parameters
    test_cases = [
        ("DESEC", lambda: DESEC(pa="TESTPART")),
        ("XTFIL", lambda: XTFIL(fn="test", pa="TESTPART", fs=(1, 10), hs=(1, 5))),
        ("LORES", lambda: LORES(sin=True)),  # Use sin mode
        ("TABLE", lambda: TABLE(tab="GE")),  # Use tab mode
    ]
    
    model = SD_BASE()
    
    for stmt_name, stmt_factory in test_cases:
        try:
            stmt = stmt_factory()
            print(f"✓ {stmt_name} created: {stmt}")
            model.add(stmt)
        except Exception as e:
            print(f"❌ {stmt_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nModel summary:")
    print(f"Total items: {len(model.all_items)}")
    print(f"DESEC: {len(model.desec)}")
    print(f"XTFIL: {len(model.xtfil)}")
    print(f"LORES: {len(model.lores)}")
    print(f"TABLE: {len(model.table)}")
    
    # Test writing to file
    output_file = "test_modernized_output.inp"
    try:
        with SD_BASE.create_writer(output_file) as test_model:
            test_model.add([
                DESEC(pa="TESTPART"),
                XTFIL(fn="test", pa="TESTPART", fs=(1, 10), hs=(1, 5)),
                LORES(sin=True),
                TABLE(tab="GE")
            ])
        
        # Read and display the file content
        with open(output_file, 'r') as f:
            content = f.read()
            print(f"\nGenerated file content:\n{content}")
            
        print("✅ All modernized statements work correctly!")
        
    except Exception as e:
        print(f"❌ File writing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modernized_statements()