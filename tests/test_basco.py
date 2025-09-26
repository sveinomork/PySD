import pytest
from pysd.sdmodel import SD_BASE
from pysd.statements import BASCO, LoadCase, LOADC
from pysd import ValidationLevel
from pysd.statements.greco import GRECO


def test_basco_basic():
    """Test basic BASCO with single load case"""
    basco = BASCO(
        id=1010, load_cases=[LoadCase(lc_type="OLC", lc_numb=1100, lc_fact=1.0)]
    )
    assert basco.input == "BASCO ID=1010 LF=1.0 OLC=1100"


def test_basco_multiple_load_cases():
    """Test the first BASCO statement from the loop in main.py"""
    load_cases = [
        LoadCase(lc_type="OLC", lc_numb=201, lc_fact=1),
        LoadCase(lc_type="ELC", lc_numb=202, lc_fact=1),
    ]
    basco = BASCO(id=211, load_cases=load_cases)
    assert basco.input == "BASCO ID=211 LF=1.0 OLC=201 LF=1.0 ELC=202"


def test_basco_connected_sdbase_fails(
    validity_level=ValidationLevel.NORMAL, cross_object_validation=True
):
    """Test BASCO connected to SD_BASE model"""
    model = SD_BASE()

    basco = BASCO(
        id=1001,
        load_cases=[
            LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0),
            LoadCase(lc_type="ELC", lc_numb=102, lc_fact=1.5),
        ],
    )
    # This should FAIL with cross-validation error
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(basco, validation=True)  # Immediate validation


def test_basco_connected_sdbase_succeeds(
    validity_level=ValidationLevel.NORMAL, cross_object_validation=True
):
    """Test BASCO connected to SD_BASE model"""
    model = SD_BASE()

    model.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))
    model.add(LOADC(run_number=2, alc=(11, 16), olc=(201, 206)))
    for i in range(6):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=201 + i)])
        )
    model.add(GRECO(id="A", bas=[201, 206]))

    basco = BASCO(
        id=1001,
        load_cases=[
            LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0),
            LoadCase(lc_type="ELC", lc_numb=102, lc_fact=1.5),
        ],
    )
    model.add(basco, validation=True)  # Immediate validation

    assert basco.input == "BASCO ID=1001 LF=1.0 OLC=101 LF=1.5 ELC=102"


def test_basco_connected_sdbase_failure_due_to_greco(
    validity_level=ValidationLevel.NORMAL, cross_object_validation=True
):
    """Test BASCO with ELC reference fails when no GRECO is defined"""
    model = SD_BASE()

    # Add LOADC statements with OLC references
    model.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))
    model.add(LOADC(run_number=2, alc=(11, 16), olc=(201, 206)))

    # Add BASCO statements for the OLC references
    for i in range(6):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=201 + i)])
        )

    # Create BASCO with ELC reference but no GRECO defined - this should fail
    basco = BASCO(
        id=1001,
        load_cases=[
            LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0),
            LoadCase(
                lc_type="ELC", lc_numb=102, lc_fact=1.5
            ),  # ELC without GRECO should fail
        ],
    )

    # This should FAIL because ELC 102 requires a GRECO statement
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(basco, validation=True)  # Immediate validation
