#!/usr/bin/env python3

from src.pysd.statements import DESEC, XTFIL, SHSEC, TABLE
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def test_table_validation():
    """Test TABLE validation against DESEC."""
    print("Testing TABLE validation...")
    
    # Set strict validation mode
    set_validation_mode(ValidationMode.STRICT)
    
    # Create model
    sd_model = SD_BASE()
    
    # Add SHSEC for the parts first (required by DESEC)
    sd_model.add(SHSEC(pa="VEGG_2", elset=2, hs=(1,4)))
    sd_model.add(SHSEC(pa="PLATE", elset=3, hs=(1,4)))
    print("✓ Added SHSEC for VEGG_2 and PLATE")
    
    # Add DESEC for existing parts
    sd_model.add(DESEC(pa="VEGG_2"))
    sd_model.add(DESEC(pa="PLATE"))
    print("✓ Added DESEC for VEGG_2 and PLATE")
    
    # Add XTFIL for existing parts (should work)
    sd_model.add(XTFIL(fn="AquaPod_09", pa="VEGG_2", fs=(1,9999), hs=(1,99)))
    sd_model.add(XTFIL(fn="AquaPod_09", pa="PLATE", fs=(1,9999), hs=(1,99)))
    print("✓ Added XTFIL for VEGG_2 and PLATE (should pass)")
    
    # Add TABLE for existing part (should work)
    sd_model.add(TABLE(tab="DR", pa="PLATE", fs=1, hs=1))
    print("✓ Added TABLE for PLATE (should pass)")
    
    # Try to add TABLE for non-existing part (should fail)
    try:
        sd_model.add(TABLE(tab="DR", pa="VEGG", fs=1, hs=1))
        print("❌ TABLE for VEGG incorrectly passed validation")
    except ValueError as e:
        print("✅ TABLE for VEGG correctly failed validation:")
        print(f"   {e}")

if __name__ == "__main__":
    test_table_validation()