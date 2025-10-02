from pysd.statements import DECAS, CaseBuilder, BASCO, LoadCase, LOADC
from pysd.sdmodel import SD_BASE
from pysd.statements.greco import GRECO
from pysd.validation.core import ValidationLevel
from pysd.model.model_writer import ModelWriter


def test_decas_bas_validation():
    """Test that DECAS validates the bas parameter exists and works correctly"""
    # Create SDModel with immediate validation enabled
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    model.add(LOADC(run_number=1, alc=1, olc=110))
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=110)]))

    # Now create DECAS that references the existing bas - validation=True enables immediate validation
    decas = DECAS(ls="ULS", bas=101)
    model.add(decas, validation=True)  # New API: immediate validation

    # Test that the validation works - bas 101 exists so this should pass
    assert decas.input == "DECAS LS=ULS BAS=101"


def test_decas_bas_validation_with_greco():
    """Test that DECAS validates the bas and greco parameter exists and works correctly"""
    # Create SDModel with immediate validation enabled
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    model.add(LOADC(run_number=1, alc=1, olc=110))
    model.add(
        LOADC(run_number=2, alc=(2, 7), olc=(101, 106))
    )  # Use run_number=2 to avoid duplicate
    for i in range(6):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    model.add(GRECO(id="A", bas=[101, 106]))

    model.add(
        BASCO(id=201, load_cases=[LoadCase(lc_type="ELC", lc_numb=110, lc_fact=1.5)])
    )  # Another BASCO to ensure no false positives

    # Now create DECAS that references the existing bas - with immediate validation
    decas = DECAS(ls="ULS", bas=101, greco="A")
    model.add(decas, validation=True)  # New API: immediate validation

    # Test that the validation works - bas 101 exists so this should pass
    assert decas.input == "DECAS LS=ULS BAS=101:A"


def test_decas_validation_error():
    """Test that DECAS raises an error when the bas parameter does not exist"""
    import pytest
    import os

    # Create SDModel and add basic load cases first
    output_file = "tests/test_output/test_decas_validation_error.mdl"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # The validation error should be raised when the context exits (during finalization)
    with pytest.raises(
        ValueError,
        match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]",
    ):
        with ModelWriter.create_writer(output_file) as model:
            model.validator.enable_validation()

            model.add(LOADC(run_number=1, alc=1, olc=110))
            model.add(BASCO(id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=110)]))

            # Now create DECAS that references a non-existing bas
            decas = DECAS(ls="ULS", bas=999)  # 999 does not exist
            model.add(decas)

            # The validation error will be raised when the context manager exits


def test_decas_validation_error_immediate():
    """Test that DECAS raises immediate validation error with new API when the bas parameter does not exist"""
    import pytest

    # Create SDModel with immediate validation
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    model.add(LOADC(run_number=1, alc=1, olc=110))
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=110)]))

    # Now create DECAS that references a non-existing bas - should fail immediately
    decas = DECAS(ls="ULS", bas=999)  # 999 does not exist

    with pytest.raises(
        ValueError,
        match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]",
    ):
        model.add(
            decas, validation=True
        )  # New API: immediate validation should fail here


def test_decas_tuple():
    """Test the DECAS statement using tuple and greco"""
    decas = DECAS(ls="ULS", bas=(101, 102), greco="A")
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"


def test_decas_string():
    """Test the DECAS statement using string"""
    decas = DECAS(ls="ULS", bas="101-102:A")
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"


def test_decas_list_tuple():
    """Test the DECAS statement list containing tuples"""
    decas = DECAS(ls="ULS", bas=[(101, 102)], greco="A")
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"


# def test_decas_list_int():
#  TDOO  Fix this test so that it works
#     """Test the DECAS statement list containing tuples"""
#     decas = DECAS(ls='ULS', bas=[101,102], greco='A')
#     assert decas.input == "DECAS LS=ULS BAS=101-102:A"


def test_decas_case_buider():
    """Test the DECAS statement using the CaseBuilder"""
    cases = CaseBuilder().add(101, 102).add_greco("A")
    decas = DECAS(ls="ULS", bas=cases)
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"


def test_decas_only_int_no_greco():
    """Test the DECAS statement list containing tuples"""
    decas = DECAS(ls="ULS", bas=101)
    assert decas.input == "DECAS LS=ULS BAS=101"

def test_decas_ilc():
    """Test DECAS with ILC parameter"""
    pass  # TODO: Add test implementation


def test_validate_decas_model_greco_not_found():
    """Test that DECAS model validation catches missing GRECO references"""
    import pytest
    
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC and BASCO
    model.add(LOADC(run_number=1, alc=(1, 6), olc=(101, 106)))
    for i in range(6):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create DECAS with GRECO reference but don't define the GRECO - should fail
    decas = DECAS(ls="ULS", bas=(101, 106), greco="B")
    
    with pytest.raises(ValueError, match=r"(?s)DECAS_GRECO_NOT_FOUND.*GRECO 'B' not found"):
        model.add(decas, validation=True)


def test_validate_decas_model_greco_found():
    """Test that DECAS model validation passes when GRECO exists"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC and BASCO
    model.add(LOADC(run_number=1, alc=(1, 6), olc=(101, 106)))
    for i in range(6):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Add GRECO
    model.add(GRECO(id="B", bas=[101, 106]))

    # Create DECAS with GRECO reference - should pass
    decas = DECAS(ls="ULS", bas=(101, 106), greco="B")
    model.add(decas, validation=True)
    
    assert decas.input == "DECAS LS=ULS BAS=101-106:B"


def test_validate_decas_model_multiple_greco_refs():
    """Test that DECAS model validation handles checking for GRECO that doesn't exist"""
    import pytest
    
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC and BASCO
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))
    for i in range(10):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Add only GRECO A, not B
    model.add(GRECO(id="A", bas=[101, 105]))

    # Create first DECAS with GRECO A - should pass
    decas1 = DECAS(ls="ULS", bas=(101, 105), greco="A")
    model.add(decas1, validation=True)
    
    # Create second DECAS with GRECO B which doesn't exist - should fail
    decas2 = DECAS(ls="SLS", bas=(106, 110), greco="B")
    
    with pytest.raises(ValueError, match=r"(?s)DECAS_GRECO_NOT_FOUND.*GRECO 'B' not found"):
        model.add(decas2, validation=True)


def test_validate_decas_model_load_case_range():
    """Test that DECAS model validation validates load case ranges"""
    import pytest
    
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=(1, 5), olc=(101, 105)))
    
    # Add only some BASCO statements (101-103)
    for i in range(3):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create DECAS that references 101-105, but only 101-103 have BASCO
    decas = DECAS(ls="ULS", bas=(101, 105))
    
    with pytest.raises(ValueError, match=r"(?s)DECAS_LOAD_CASES_NOT_FOUND.*104.*105"):
        model.add(decas, validation=True)


def test_validate_decas_model_single_load_case():
    """Test that DECAS model validation validates single load case reference"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=1, olc=101))
    
    # Add BASCO for load case 101
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=101)]))

    # Create DECAS that references single load case - should pass
    decas = DECAS(ls="ULS", bas=101)
    model.add(decas, validation=True)
    
    assert decas.input == "DECAS LS=ULS BAS=101"


def test_validate_decas_model_string_format_validation():
    """Test that DECAS model validation works with string format"""
    import pytest
    
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))
    
    # Add BASCO for 101-105 only
    for i in range(5):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create DECAS with string format referencing missing load cases
    decas = DECAS(ls="ULS", bas="101-110")
    
    with pytest.raises(ValueError, match=r"(?s)DECAS_LOAD_CASES_NOT_FOUND"):
        model.add(decas, validation=True)


def test_validate_decas_model_all_load_cases_present():
    """Test that DECAS model validation passes when all load cases exist"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))
    
    # Add all BASCO statements
    for i in range(10):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )

    # Create DECAS that references all load cases - should pass
    decas = DECAS(ls="ULS", bas=(101, 110))
    model.add(decas, validation=True)
    
    assert decas.input == "DECAS LS=ULS BAS=101-110"


def test_validate_decas_model_greco_with_complete_setup():
    """Test complete DECAS validation with GRECO, LOADC, and BASCO"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=(1, 6), olc=(101, 106)))
    model.add(LOADC(run_number=2, alc=(7, 12), olc=(201, 206)))
    
    # Add BASCO statements
    for i in range(6):
        model.add(
            BASCO(id=101 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=101 + i)])
        )
    for i in range(6):
        model.add(
            BASCO(id=201 + i, load_cases=[LoadCase(lc_type="OLC", lc_numb=201 + i)])
        )

    # Add GRECO statements
    model.add(GRECO(id="A", bas=[101, 106]))
    model.add(GRECO(id="B", bas=[201, 206]))

    # Create multiple DECAS statements - all should pass
    decas1 = DECAS(ls="ULS", bas=(101, 106), greco="A")
    model.add(decas1, validation=True)
    
    decas2 = DECAS(ls="SLS", bas=(201, 206), greco="B")
    model.add(decas2, validation=True)
    
    assert decas1.input == "DECAS LS=ULS BAS=101-106:A"
    assert decas2.input == "DECAS LS=SLS BAS=201-206:B"


def test_validate_decas_model_mixed_load_case_formats():
    """Test DECAS validation with mixed load case formats (single + range)"""
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC
    model.add(LOADC(run_number=1, alc=(1, 10), olc=(101, 110)))
    
    # Add BASCO for specific cases
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type="OLC", lc_numb=101)]))
    model.add(BASCO(id=105, load_cases=[LoadCase(lc_type="OLC", lc_numb=105)]))
    model.add(BASCO(id=110, load_cases=[LoadCase(lc_type="OLC", lc_numb=110)]))

    # Create DECAS with single value - should pass
    decas = DECAS(ls="ULS", bas=101)
    model.add(decas, validation=True)
    
    assert decas.input == "DECAS LS=ULS BAS=101"


def test_validate_decas_model_no_basco_at_all():
    """Test that DECAS validation fails when no BASCO statements exist"""
    import pytest
    
    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )

    # Add LOADC but no BASCO
    model.add(LOADC(run_number=1, alc=1, olc=101))

    # Create DECAS - should fail because no BASCO exists
    decas = DECAS(ls="ULS", bas=101)
    
    with pytest.raises(ValueError, match=r"(?s)DECAS_LOAD_CASES_NOT_FOUND.*101"):
        model.add(decas, validation=True)
