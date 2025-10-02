
from pysd.statements import GRECO, Cases, BASCO, LoadCase, LOADC
from pysd.sdmodel import SD_BASE
from pysd.validation.core import ValidationLevel
import pytest


def test_greco_simple():
    """Test the GRECO statement from main.py"""
    greco = GRECO(id="A", bas=Cases(ranges=[(211, 216)]))
    assert greco.input == "GRECO ID=A BAS=211-216"


def test_validate_elc_references_exist_success():
    """Test that ELC validation passes when LOADC contains the referenced OLC"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC with OLC 101-106
    model.add(LOADC(run_number=1, alc=(1, 6), olc=(101, 106)))
    
    # Add BASCO statements for the BAS references
    for i in range(6):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create GRECO with ELC references that exist as OLC - should succeed
    greco = GRECO(id="A", bas=Cases(ranges=[(201, 206)]), elc=Cases(ranges=[(101, 106)]))
    model.add(greco, validation=True)
    
    assert greco.input == "GRECO ID=A BAS=201-206 ELC=101-106"


def test_validate_elc_references_exist_failure():
    """Test that ELC validation fails when LOADC does not contain the referenced OLC"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC with OLC 101-103 only
    model.add(LOADC(run_number=1, alc=(1, 3), olc=(101, 103)))
    
    # Add BASCO statements
    for i in range(3):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create GRECO with ELC references that don't exist (104-106) - should fail
    greco = GRECO(id="A", bas=Cases(ranges=[(201, 203)]), elc=Cases(ranges=[(101, 106)]))
    
    with pytest.raises(ValueError, match=r"(?s)GRECO-ELC-REF-001.*ELC 104.*not found.*OLC.*LOADC"):
        model.add(greco, validation=True)


def test_validate_elc_references_exist_no_loadc():
    """Test that ELC validation fails when no LOADC container exists"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add BASCO statements without validation to avoid OLC reference errors
    for i in range(3):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="BAS", lc_numb=201 + i)]),
            validation=False  # Skip validation to avoid OLC checks
        )

    # Create GRECO with ELC references but no LOADC - should fail
    greco = GRECO(id="A", bas=Cases(ranges=[(201, 203)]), elc=Cases(ranges=[(101, 103)]))
    
    with pytest.raises(ValueError, match=r"(?s)GRECO-ELC-NO-CONTAINER.*no LOADC container exists"):
        model.add(greco, validation=True)
