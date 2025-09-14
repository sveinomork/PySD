#!/usr/bin/env python3
"""Simple test to check validation execution without external dependencies"""

import sys
import os

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test the validation rule directly
print("Testing BASCO validation rule execution...")

try:
    from pysd.statements.basco import BASCO, LoadCase
    from pysd.validation.core import ValidationContext, ValidationIssue
    from pysd.validation.rules.basco_rules import validate_olc_references_exist
    
    # Create a mock full model
    class MockModel:
        def __init__(self):
            self.loadc = []  # Empty LOADC container
    
    # Create test data
    mock_model = MockModel()
    test_basco = BASCO(
        id=1001,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=101, lc_fact=1.0),
            LoadCase(lc_type='OLC', lc_numb=102, lc_fact=1.5)
        ]
    )
    
    context = ValidationContext(
        current_object=test_basco,
        full_model=mock_model
    )
    
    # Call the validation rule directly
    print("Calling validate_olc_references_exist...")
    issues = validate_olc_references_exist(test_basco, context)
    
    print(f"Found {len(issues)} validation issues:")
    for issue in issues:
        print(f"  - {issue.severity}: {issue.message}")
    
    if not issues:
        print("ERROR: Expected validation issues but none were found!")
    else:
        print("SUCCESS: Validation rule found expected issues!")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()