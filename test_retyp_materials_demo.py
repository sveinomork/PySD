"""
Demo script showing that RETYP validation now accepts materials from RMPEC, RMPNS, or RMPOS.
"""

from pysd.sdmodel import SD_BASE
from pysd import ValidationLevel
from pysd.statements import RETYP
from pysd.statements.rmpec import RMPEC
from pysd.statements.rmpns import RMPNS
from pysd.statements.rmpos import RMPOS


def test_with_rmpec():
    """RETYP should validate successfully when material is in RMPEC"""
    print("\n1. Testing RETYP with RMPEC material...")
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    
    # Add material to RMPEC
    model.add(RMPEC(id=100, gr="500"), validation=True)
    
    # Add RETYP referencing that material - should succeed
    retyp = RETYP(id=1, mp=100, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1)
    model.add(retyp, validation=True)
    print(f"   ✓ Success! RETYP {retyp.id} validated with material {retyp.mp} from RMPEC")


def test_with_rmpns():
    """RETYP should validate successfully when material is in RMPNS"""
    print("\n2. Testing RETYP with RMPNS material...")
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    
    # Add material to RMPNS
    model.add(RMPNS(id=200, fc=30.0), validation=True)
    
    # Add RETYP referencing that material - should succeed
    retyp = RETYP(id=2, mp=200, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1)
    model.add(retyp, validation=True)
    print(f"   ✓ Success! RETYP {retyp.id} validated with material {retyp.mp} from RMPNS")


def test_with_rmpos():
    """RETYP should validate successfully when material is in RMPOS"""
    print("\n3. Testing RETYP with RMPOS material...")
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    
    # Add material to RMPOS
    model.add(RMPOS(id=300, fy=500.0), validation=True)
    
    # Add RETYP referencing that material - should succeed
    retyp = RETYP(id=3, mp=300, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1)
    model.add(retyp, validation=True)
    print(f"   ✓ Success! RETYP {retyp.id} validated with material {retyp.mp} from RMPOS")


def test_material_not_found():
    """RETYP should fail validation when material is not in any container"""
    print("\n4. Testing RETYP with missing material (should fail)...")
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    
    # Don't add any materials
    
    # Try to add RETYP with non-existent material - should fail
    retyp = RETYP(id=4, mp=999, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1)
    try:
        model.add(retyp, validation=True)
        print("   ✗ Failed - should have raised validation error!")
    except ValueError as e:
        if "not found in RMPEC, RMPNS, or RMPOS" in str(e):
            print(f"   ✓ Correctly rejected - material 999 not found in any container")
        else:
            print(f"   ✗ Failed with unexpected error: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("RETYP Material Validation Demo")
    print("=" * 70)
    print("\nTesting that RETYP accepts materials from any of:")
    print("  - RMPEC (Eurocode material properties)")
    print("  - RMPNS (NS material properties)")
    print("  - RMPOS (Other standard material properties)")
    
    test_with_rmpec()
    test_with_rmpns()
    test_with_rmpos()
    test_material_not_found()
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
