#!/usr/bin/env python3

from src.pysd.statements import DESEC, XTFIL, SHSEC
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def test_xtfil_validation():
    """Test XTFIL validation against DESEC."""
    print("Testing XTFIL validation...")
    
    # Set normal validation mode
    set_validation_mode(ValidationMode.NORMAL)
    
    # Create model
    sd_model = SD_BASE()
    
    # Add SHSEC for the part first (required by DESEC)
    sd_model.add(SHSEC(pa="PART1", ty="THICK", th=0.02, el=100))
    print("✓ Added SHSEC for PART1")
    
    # Add DESEC for existing parts
    sd_model.add(DESEC(pa="PART1"))
    print("✓ Added DESEC for PART1")
    
    # Add XTFIL for existing part (should work)
    sd_model.add(XTFIL(fn="test_file", pa="PART1", fs=(1,10), hs=(1,10)))
    print("✓ Added XTFIL for PART1 (should pass)")
    
    # Try to add XTFIL for non-existing part (should fail)
    try:
        sd_model.add(XTFIL(fn="test_file2", pa="PART2", fs=(1,10), hs=(1,10)))
        print("❌ XTFIL for PART2 incorrectly passed validation")
    except ValueError as e:
        print("✅ XTFIL for PART2 correctly failed validation:")
        print(f"   {e}")

if __name__ == "__main__":
    test_xtfil_validation()