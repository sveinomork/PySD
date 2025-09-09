#!/usr/bin/env python3
"""
Test script to verify SHAXE integration with main.py components.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pysd import SD_BASE
from pysd.statements.shaxe import SHAXE
from pysd.statements.shsec import SHSEC
from pysd.validation.core import ValidationMode, set_validation_mode
from pysd.helpers import create_axes_based_on_3_points_in_plane
from shapely.geometry import Point


def test_shaxe_with_main_components():
    """Test SHAXE with components similar to main.py"""
    print("=== Testing SHAXE with Main.py Components ===")
    
    # Set validation mode
    set_validation_mode(ValidationMode.STRICT)
    
    # Create model
    sd_model = SD_BASE()
    
    # Points similar to main.py
    p1 = Point(-4.9, -2.2, -1.05)
    p2 = Point(0.0, -1.6, -1.05)
    p3 = Point(4.9, -2.2, -1.05)
    p4 = Point(-4.9, -2.2, 0.85)
    p8 = Point(0.0, -1.6, 0.85)
    p9 = Point(-4.614273, -2.16501302, -0.95)
    p10 = Point(4.614273, -2.16501302, -0.95)
    
    def _shaxe_base_point(part: str, p1: Point, p2: Point, p3: Point) -> SHAXE:
        """Helper function from main.py"""
        v1, v2, v3 = create_axes_based_on_3_points_in_plane(p1, p2, p3)
        return SHAXE(pa=part, x1=v1, x2=v2, x3=v3, hs=(1, 4))
    
    # Test 1: Add SHSEC statements first
    print("Adding SHSEC statements...")
    sd_model.add(SHSEC(pa="PLATE", elset=3, hs=(1, 4)))
    sd_model.add(SHSEC(pa="VEGG_2", elset=2, hs=(1, 4)))
    sd_model.add(SHSEC(pa="VEGG_3", elset=3, hs=(5, 8)))
    
    # Test 2: Add SHAXE statements (should work)
    print("Adding SHAXE statements...")
    sd_model.add(SHAXE(pa="PLATE", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, 1)))
    sd_model.add(_shaxe_base_point("VEGG_2", p2, p10, p8))
    sd_model.add(_shaxe_base_point("VEGG_3", p2, p9, p8))
    
    print(f"✓ Successfully added {len(sd_model.shaxe)} SHAXE statements")
    print(f"✓ SHAXE keys: {sd_model.shaxe.get_keys()}")
    print(f"✓ SHAXE part names: {sd_model.shaxe.get_part_names()}")
    
    # Test 3: Test input string generation
    print("\\nGenerated SHAXE strings:")
    for shaxe in sd_model.shaxe:
        print(f"  {shaxe.input}")
    
    print("✓ SHAXE integration with main.py components successful\\n")


def test_shaxe_coordinate_calculation():
    """Test SHAXE with coordinate-based axis calculation"""
    print("=== Testing SHAXE Coordinate-Based Axes ===")
    
    # Create model
    sd_model = SD_BASE()
    
    # Add required SHSEC
    sd_model.add(SHSEC(pa="WALL1", elset=1))
    
    # Test different coordinate-based configurations
    p1 = Point(0, 0, 0)
    p2 = Point(1, 0, 0)
    p3 = Point(0, 1, 0)
    
    # Calculate axes from points
    v1, v2, v3 = create_axes_based_on_3_points_in_plane(p1, p2, p3)
    
    # Create SHAXE with calculated axes
    shaxe_calc = SHAXE(pa="WALL1", x1=v1, x2=v2, x3=v3)
    sd_model.add(shaxe_calc)
    
    print(f"✓ Calculated axes from points:")
    print(f"  X1: {v1}")
    print(f"  X2: {v2}")
    print(f"  X3: {v3}")
    print(f"  Generated: {shaxe_calc.input}")
    
    print("✓ Coordinate-based SHAXE test successful\\n")


if __name__ == "__main__":
    print("Testing SHAXE Integration with Main.py Components\\n")
    
    try:
        test_shaxe_with_main_components()
        test_shaxe_coordinate_calculation()
        
        print("🎉 All SHAXE integration tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)