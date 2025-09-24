import pytest

from pysd.sdmodel import SD_BASE
from pysd import ValidationLevel

from pysd.statements.rmpec import RMPEC

from pysd.statements import SRTYP

def test_srtyp_parameters():
    """Test the SRTYP statements basic"""
    srtyp1 = SRTYP(id=1, mp=1, ar=753.0E-6 , c2=0.055, nr=1, lb="1.0D12_c150")
    assert "SRTYP" in srtyp1.input
    assert "ID=1" in srtyp1.input
    assert "MP=1" in srtyp1.input
    assert "AR=0.000753" in srtyp1.input
    assert "C2=0.055" in srtyp1.input
    assert "NR=1" in srtyp1.input
    assert "LB=1.0D12_c150" in srtyp1.input


def test_srtyp_method1():
    """Test the SRTYP statements Method 1 (area input)"""
    srtyp1 = SRTYP(id=1, mp=1, ar=2094e-6)
    assert srtyp1.input == "SRTYP ID=1 MP=1 AR=0.002094"

def test_srtyp_method2():
    """Test the SRTYP statements Method 2 (count and diameter input)"""
    srtyp2 = SRTYP(id=2, mp=1, nr=2, di=12.0, c1=0.150, c2=0.150)
    print(srtyp2.input)
    assert srtyp2.input == "SRTYP ID=2 MP=1 DI=12 NR=2 C1=0.15 C2=0.15"

def test_srtyp_incteracting_with_sd_base_failure():
    """Test RETYP interacting with SD_BASE model"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel

    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    model.add(RMPEC(id=1, fyk=500.0E6, fsk=600.0E6), validation=True)  # Immediate validation
    srtyp = SRTYP(id=1, mp=2, ar=753.0E-6 ,  lb="1.0D12_c150c150")
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(srtyp, validation=True)  # Immediate validation

def test_srtyp_incteracting_with_sd_base_success():
    """Test SRTYP interacting with SD_BASE model"""
    

    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    model.add(RMPEC(id=1, fyk=500.0E6, fsk=600.0E6), validation=True)  # Immediate validation
    srtyp = SRTYP(id=1, mp=1, ar=753.0E-6 ,  lb="1.0D12_c150c150")
    model.add(srtyp, validation=True)
    print(model.srtyp[0].input)
    assert model.srtyp[0].input == "SRTYP ID=1 MP=1 AR=0.000753 LB=1.0D12_c150c150"


if __name__ == "__main__":
    #test_srtyp_parameters()
    #test_srtyp_method1()
    #test_srtyp_method2()
  
    test_srtyp_incteracting_with_sd_base_success()
    print("All tests passed.")

    