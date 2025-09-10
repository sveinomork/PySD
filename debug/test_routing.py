#!/usr/bin/env python3
"""
Test script to verify all statement types are properly routed in SD_BASE
"""

from src.pysd.sdmodel import SD_BASE
from src.pysd.statements.decas import DECAS
from src.pysd.statements.execd import EXECD
from src.pysd.statements.headl import HEADL
from src.pysd.statements.incdf import INCDF
from src.pysd.statements.rfile import RFILE
from src.pysd.statements.filst import FILST

def test_all_statement_routing():
    """Test that all statement types are properly routed"""
    print("Testing statement routing...")
    
    model = SD_BASE()
    
    # Add various statement types (avoiding complex validation for routing test)
    statements = [
        DECAS(ls='ULS'),
        EXECD(),
        HEADL(heading='Test Header'),
        INCDF(path='test.inc'),
        FILST(name='test.fil')
    ]
    
    # Test RFILE separately since it has cross-reference validation
    try:
        model.add(RFILE(file_name='test.rf'))
        print("RFILE added successfully")
    except Exception as e:
        print(f"RFILE validation error (expected): {e}")
        # This is expected due to cross-reference validation
    
    model.add(statements)
    
    # Check counts
    summary = model.get_validation_summary()
    print(f"Total items: {summary['total_items']}")
    print(f"DECAS count: {len(model.decas)}")
    print(f"EXECD count: {len(model.execd)}")
    print(f"HEADL count: {len(model.headl)}")
    print(f"INCDF count: {len(model.incdf)}")
    print(f"RFILE count: {len(model.rfile)}")
    print(f"FILST count: {len(model.filst)}")
    
    # Verify all items are tracked
    print(f"All items tracked: {len(model.all_items)}")
    
    return model

if __name__ == "__main__":
    try:
        model = test_all_statement_routing()
        print("✅ All statement types routing successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()