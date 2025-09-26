import pytest

from pysd.sdmodel import SD_BASE
from pysd import ValidationLevel

from pysd.statements.temat import TEMAT

# from pysd.sdmodel import SD_BASE
from pysd import ValidationLevel
from pysd.statements import TETYP


def test_tetyp_parameters():
    """Test the TETYP statements basic"""
    tetyp1 = TETYP(id=1, mp=1, ar=753.0e-6, eo=0.055, os=10)
    assert "TETYP" in tetyp1.input
    assert "ID=1" in tetyp1.input
    assert "MP=1" in tetyp1.input
    assert "AR=0.000753" in tetyp1.input
    assert "EO=0.055" in tetyp1.input
    assert "OS=10" in tetyp1.input


def test_tetyp_method1():
    """Test the TETYP statements Method 1 (area input)"""
    tetyp1 = TETYP(id=1, mp=1, ar=2094e-6)
    assert tetyp1.input == "TETYP ID=1 MP=1 AR=0.002094"


def test_tetyp_incteracting_with_sd_base_failure():
    """Test TETYP interacting with SD_BASE model"""

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    model.add(
        TEMAT(id=1, fsy=500.0e6, esk=600.0e6), validation=True
    )  # Immediate validation
    tetyp = TETYP(id=1, mp=2, ar=753.0e-6)
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(tetyp, validation=True)  # Immediate validation


def test_tetyp_incteracting_with_sd_base_success():
    """Test TETYP interacting with SD_BASE model"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    model.add(
        TEMAT(id=1, fsy=500.0e6, esk=600.0e6), validation=True
    )  # Immediate validation
    tetyp = TETYP(id=1, mp=1, ar=753.0e-6)
    model.add(tetyp, validation=True)
    print(model.tetyp[0].input)
    assert model.tetyp[0].input == "TETYP ID=1 MP=1 AR=0.000753"


if __name__ == "__main__":
    # test_srtyp_parameters()
    # test_srtyp_method1()
    # test_srtyp_method2()
    test_tetyp_incteracting_with_sd_base_failure()

    print("All tests passed.")
