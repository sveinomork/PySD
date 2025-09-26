#!/usr/bin/env python3
"""
Test script to see what parts are defined in SHSEC
"""

from pysd.statements.shext import SHSEC
from src.pysd.statements.reloc import RELOC
from src.pysd.sdmodel import SD_BASE

def test_part_validation():
    """Test part validation"""
    print("Testing part validation...")
    
    model = SD_BASE()
    
    # Add SHSEC statements like in main.py
    model.add(SHSEC(pa="PLATE", elset=3, hs=(1,4)))
    
    vegg = [2,3,4,5,6,7,8,9]
    for counter, set_number in enumerate(vegg):
        model.add(SHSEC(pa=f"VEGG_{set_number}", elset=set_number, hs=(1+4*counter, 4+4*counter)))
    
    print("Defined SHSEC parts:")
    for item in model.all_items:
        if hasattr(item, '__class__') and item.__class__.__name__ == 'SHSEC':
            print(f"  - {item.pa}")
    
    # Try to add invalid RELOC
    try:
        model.add(RELOC(id="X11", pa="VEGG", rt=1, fa=1, al=0))
    except ValueError as e:
        print(f"\n✅ Validation caught error: {e}")
    
    # Try to add valid RELOC  
    try:
        model.add(RELOC(id="X11", pa="VEGG_2", rt=1, fa=1, al=0))
        print("✅ Valid RELOC accepted")
    except ValueError as e:
        print(f"❌ Valid RELOC rejected: {e}")

if __name__ == "__main__":
    test_part_validation()