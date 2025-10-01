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


def test_validate_olc_references_exist_success():
    """Test that OLC validation passes when LOADC contains the referenced OLC"""
    model = SD_BASE()

    # Add LOADC with OLC 101
    model.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))

    # Create BASCO referencing OLC 101 - should succeed
    basco = BASCO(
        id=1001, load_cases=[LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0)]
    )

    model.add(basco, validation=True)  # Should not raise
    assert model.basco[0].id == 1001


def test_validate_olc_references_exist_failure():
    """Test that OLC validation fails when LOADC does not contain the referenced OLC"""
    model = SD_BASE()

    # Add LOADC with OLC 101-102
    model.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))

    # Create BASCO referencing non-existent OLC 999 - should fail
    basco = BASCO(
        id=1001, load_cases=[LoadCase(lc_type="OLC", lc_numb=999, lc_fact=1.0)]
    )

    with pytest.raises(ValueError, match=r"(?s)Model validation failed.*999"):
        model.add(basco, validation=True)


def test_validate_no_circular_bas_references_simple():
    """Test detection of simple circular BAS reference (A -> B -> A)"""
    model = SD_BASE()

    # Add LOADC for the OLC references
    model.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))

    # Create BASCO 101 referencing OLC
    basco1 = BASCO(
        id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco1, validation=True)

    # Create BASCO 102 referencing BAS 101
    basco2 = BASCO(
        id=102, load_cases=[LoadCase(lc_type="BAS", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco2, validation=True)

    # Try to create BASCO 101 that references BAS 102 - creates circular reference
    # This would modify existing BASCO 101 to add a BAS reference to 102
    # Instead, let's create BASCO 103 that references 102, and then 104 that references 103 and 102
    basco3 = BASCO(
        id=103,
        load_cases=[
            LoadCase(lc_type="BAS", lc_numb=102, lc_fact=1.0),
            LoadCase(lc_type="BAS", lc_numb=103, lc_fact=1.0),  # Self-reference = cycle
        ],
    )

    with pytest.raises(ValueError, match=r"(?s)Model validation failed.*Circular"):
        model.add(basco3, validation=True)


def test_validate_no_circular_bas_references_complex():
    """Test detection of complex circular BAS reference (A -> B -> C -> A)"""
    model = SD_BASE()

    # Add LOADC for the OLC references
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))

    # Create chain: 101 -> 102 -> 103 -> 101 (circular)
    basco1 = BASCO(
        id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco1, validation=True)

    basco2 = BASCO(
        id=102, load_cases=[LoadCase(lc_type="BAS", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco2, validation=True)

    basco3 = BASCO(
        id=103, load_cases=[LoadCase(lc_type="BAS", lc_numb=102, lc_fact=1.0)]
    )
    model.add(basco3, validation=True)

    # Now try to add BASCO that creates cycle: 104 references 103, then update 101 to reference 104
    basco4 = BASCO(
        id=104, load_cases=[LoadCase(lc_type="BAS", lc_numb=103, lc_fact=1.0)]
    )
    model.add(basco4, validation=True)

    # Create the circular reference: 105 references both 104 and 105 (self-cycle)
    basco5 = BASCO(
        id=105,
        load_cases=[
            LoadCase(lc_type="BAS", lc_numb=104, lc_fact=1.0),
            LoadCase(lc_type="BAS", lc_numb=105, lc_fact=0.5),  # Self-reference
        ],
    )

    with pytest.raises(ValueError, match=r"(?s)Model validation failed.*Circular"):
        model.add(basco5, validation=True)


def test_validate_no_circular_bas_references_valid_chain():
    """Test that valid non-circular BAS reference chain is accepted"""
    model = SD_BASE()

    # Add LOADC for the OLC references
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))

    # Create valid chain: 101 (OLC) <- 102 (BAS) <- 103 (BAS) <- 104 (BAS)
    basco1 = BASCO(
        id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco1, validation=True)

    basco2 = BASCO(
        id=102, load_cases=[LoadCase(lc_type="BAS", lc_numb=101, lc_fact=1.0)]
    )
    model.add(basco2, validation=True)

    basco3 = BASCO(
        id=103, load_cases=[LoadCase(lc_type="BAS", lc_numb=102, lc_fact=1.0)]
    )
    model.add(basco3, validation=True)

    basco4 = BASCO(
        id=104, load_cases=[LoadCase(lc_type="BAS", lc_numb=103, lc_fact=1.0)]
    )
    model.add(basco4, validation=True)  # Should not raise

    # Verify all were added
    assert len(list(model.basco.items)) == 4
    assert model.basco[0].id == 101
    assert model.basco[3].id == 104
