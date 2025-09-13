#!/usr/bin/env python3
"""Debug what fields exist on SD_BASE."""

import sys
sys.path.insert(0, 'src')

from src.pysd.sdmodel import SD_BASE

def debug_fields():
    print("=== Debugging SD_BASE Fields ===")
    
    sd_model = SD_BASE()
    
    # Get all attributes
    all_attrs = dir(sd_model)
    
    # Filter to likely container names
    container_attrs = [attr for attr in all_attrs if not attr.startswith('_') and not callable(getattr(sd_model, attr))]
    
    print("All non-private, non-callable attributes:")
    for attr in sorted(container_attrs):
        value = getattr(sd_model, attr)
        print(f"  {attr}: {type(value).__name__}")
    
    # Check model fields
    print(f"\nModel fields: {list(sd_model.model_fields.keys())}")

if __name__ == "__main__":
    debug_fields()