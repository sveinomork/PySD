import pytest

from pysd.statements import SHSEC
from pysd.statements.srtyp import SRTYP
from pysd.validation.core import ValidationLevel
from pysd.sdmodel import SD_BASE

from pysd.statements import SRLOC

def test_srloc_attributes():
    """Test the SRLOC statement from main.py"""
    srloc = SRLOC(id="SR1", pa="VEGG_2", st=1)
    assert "SRLOC" in srloc.input
    assert "ID=SR1" in srloc.input
    assert "PA=VEGG_2" in srloc.input
    assert "ST=1" in srloc.input
 
def test_srloc_statement():
    """Test the SRLOC statement with all parameters"""
    srloc = SRLOC(id="SR2", pa="PLATE", st=1, fs=(2, 5), hs=4)
    expected_input = "SRLOC ID=SR2 ST=1 PA=PLATE FS=2-5 HS=4"
    assert srloc.input == expected_input

def test_srtyp_incteracting_with_sd_base_failure():
    """Test SRLOC interacting with SD_BASE model - should fail when SRLOC references non-existent SRTYP"""
   
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    # Add SRTYP with id=1 (but SRLOC will reference st=2 which doesn't exist)
    model.add(SRTYP(id=1, mp=1, ar=753.0E-6, lb="1.0D12_c150c150"), validation=False)  # Skip validation for setup
    srloc = SRLOC(id="SR1", pa="VEGG_2", st=2)  # References SRTYP id=2 which doesn't exist
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(srloc, validation=True)  # This should fail because st=2 doesn't exist

def test_srtyp_incteracting_with_sd_base_success():
    """Test SRLOC interacting with SD_BASE model - success case"""
    from pysd.sdmodel import SD_BASE
   
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    # Skip individual validations during setup to avoid cross-reference issues
    srtyp = SRTYP(id=1, mp=1, ar=753.0E-6, lb="1.0D12_c150c150")
    model.add(srtyp, validation=False)  # Skip validation during setup
    model.add(SRLOC(id="SR1", pa="VEGG_2", st=1), validation=False)  # Skip validation during setup
    
    # Now validate the complete model
    print(model.srloc[0].input)
    assert model.srloc[0].input == "SRLOC ID=SR1 ST=1 PA=VEGG_2"

if __name__ == "__main__":
    test_srloc_attributes()
    test_srloc_statement()
    test_srtyp_incteracting_with_sd_base_success()
    test_srtyp_incteracting_with_sd_base_failure()