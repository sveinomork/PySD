#!/usr/bin/env python3
"""Debug Phase 3 parent model setup."""

import sys
sys.path.insert(0, 'src')

from src.pysd.sdmodel import SD_BASE

def debug_parent_setup():
    print("=== Debugging Parent Model Setup ===")
    
    sd_model = SD_BASE()
    
    # Check what containers exist
    containers = ['greco', 'basco', 'loadc', 'shsec', 'shaxe', 'cmpec', 'rmpec', 
                  'retyp', 'reloc', 'lores', 'xtfil', 'desec', 'table', 'rfile', 
                  'incdf', 'decas', 'depar', 'filst', 'headl', 'cases']
    
    for name in containers:
        container = getattr(sd_model, name, None)
        if container is not None:
            has_parent = hasattr(container, 'parent_model')
            parent_value = getattr(container, 'parent_model', None)
            parent_set = parent_value is sd_model
            print(f"{name}: has_parent_attr={has_parent}, parent_set={parent_set}, parent_value={type(parent_value).__name__ if parent_value else None}")
        else:
            print(f"{name}: NOT FOUND")

if __name__ == "__main__":
    debug_parent_setup()