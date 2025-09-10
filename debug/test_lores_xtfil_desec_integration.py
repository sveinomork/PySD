#!/usr/bin/env python3
"""
Test script to verify LORES, XTFIL, and DESEC integration with Pydantic, containers, and validation
"""

from src.pysd.sdmodel import SD_BASE
from src.pysd.statements.lores import LORES
from src.pysd.statements.xtfil import XTFIL
from src.pysd.statements.desec import DESEC

def test_lores_integration():
    """Test LORES Pydantic model and container integration"""
    print("\n=== Testing LORES Integration ===")
    
    # Create SD_BASE model
    sd_model = SD_BASE()
    
    # Create LORES instances
    lores1 = LORES(
        lc=1,
        part="REAL",
        resultants=[100.5, 200.3, 50.1]
    )
    
    lores2 = LORES(
        lc=2,
        part="IMAG",
        resultants=[150.2, 75.8]
    )
    
    # Add to model
    sd_model.add(lores1)
    sd_model.add(lores2)
    
    # Test validation
    validation_result = sd_model.validate_integrity()
    print(f"LORES validation result: {validation_result}")
    
    # Test summary
    summary = sd_model.get_validation_summary()
    print(f"LORES count in summary: {summary['containers']['lores']}")
    
    # Test input string generation
    print(f"LORES1 input string: {lores1.build_input_string()}")
    print(f"LORES2 input string: {lores2.build_input_string()}")
    
    return sd_model

def test_xtfil_integration():
    """Test XTFIL Pydantic model and container integration"""
    print("\n=== Testing XTFIL Integration ===")
    
    # Create SD_BASE model
    sd_model = SD_BASE()
    
    # Create XTFIL instances
    xtfil1 = XTFIL(
        fn="plot1.plt",
        pa="DECK1",
        plot_items=["AX", "FH"]
    )
    
    xtfil2 = XTFIL(
        fn="plot2.plt",
        pa="DECK2",
        plot_items=["DF", "PF"],
        peak_value_only=True
    )
    
    # Add to model
    sd_model.add(xtfil1)
    sd_model.add(xtfil2)
    
    # Test validation
    validation_result = sd_model.validate_integrity()
    print(f"XTFIL validation result: {validation_result}")
    
    # Test summary
    summary = sd_model.get_validation_summary()
    print(f"XTFIL count in summary: {summary['containers']['xtfil']}")
    
    # Test input string generation
    print(f"XTFIL1 input string: {xtfil1.build_input_string()}")
    print(f"XTFIL2 input string: {xtfil2.build_input_string()}")
    
    return sd_model

def test_desec_integration():
    """Test DESEC Pydantic model and container integration"""
    print("\n=== Testing DESEC Integration ===")
    
    # Create SD_BASE model
    sd_model = SD_BASE()
    
    # Create DESEC instances
    desec1 = DESEC(
        pa="PART1",
        th=0.25
    )
    
    desec2 = DESEC(
        pa="PART2",
        th=0.30,
        fs=5,
        hs=(1, 10)
    )
    
    # Add to model
    sd_model.add(desec1)
    sd_model.add(desec2)
    
    # Test validation
    validation_result = sd_model.validate_integrity()
    print(f"DESEC validation result: {validation_result}")
    
    # Test summary
    summary = sd_model.get_validation_summary()
    print(f"DESEC count in summary: {summary['containers']['desec']}")
    
    # Test input string generation
    print(f"DESEC1 input string: {desec1.build_input_string()}")
    print(f"DESEC2 input string: {desec2.build_input_string()}")
    
    return sd_model

def test_combined_integration():
    """Test all three types together"""
    print("\n=== Testing Combined Integration ===")
    
    # Create SD_BASE model
    sd_model = SD_BASE()
    
    # Create instances of all three types
    lores = LORES(
        lc=1,
        part="REAL",
        resultants=[100.5, 200.3]
    )
    
    xtfil = XTFIL(
        fn="combined.plt",
        pa="COMBINED",
        plot_items=["AX"]
    )
    
    desec = DESEC(
        pa="COMBINED",
        th=0.20
    )
    
    # Add all to model
    sd_model.add(lores)
    sd_model.add(xtfil)
    sd_model.add(desec)
    
    # Test validation
    validation_result = sd_model.validate_integrity()
    print(f"Combined validation result: {validation_result}")
    
    # Test summary
    summary = sd_model.get_validation_summary()
    print("Combined summary:")
    print(f"  LORES: {summary['containers']['lores']}")
    print(f"  XTFIL: {summary['containers']['xtfil']}")
    print(f"  DESEC: {summary['containers']['desec']}")
    print(f"  Total items: {summary['total_items']}")
    
    # Test batch operations
    batch_items = [
        LORES(lc=2, part="IMAG", resultants=[150.2, 75.8]),
        XTFIL(fn="batch.plt", pa="BATCH", plot_items=["DF"]),
        DESEC(pa="BATCH", th=0.15)
    ]
    
    sd_model.add(batch_items)
    
    # Test final summary
    final_summary = sd_model.get_validation_summary()
    print("Final summary after batch:")
    print(f"  LORES: {final_summary['containers']['lores']}")
    print(f"  XTFIL: {final_summary['containers']['xtfil']}")
    print(f"  DESEC: {final_summary['containers']['desec']}")
    print(f"  Total items: {final_summary['total_items']}")
    
    return sd_model

if __name__ == "__main__":
    print("Testing LORES, XTFIL, and DESEC integration with Pydantic, containers, and validation")
    
    try:
        # Test individual integrations
        lores_model = test_lores_integration()
        xtfil_model = test_xtfil_integration()
        desec_model = test_desec_integration()
        
        # Test combined integration
        combined_model = test_combined_integration()
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"\n=== Test failed with error: {e} ===")
        import traceback
        traceback.print_exc()