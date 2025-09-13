
from pysd.statements import DECAS, CaseBuilder, BASCO, LoadCase, LOADC
from pysd.sdmodel import SD_BASE
from pysd.statements.greco import GRECO
from pysd.validation.core import ValidationLevel

def test_decas_bas_validation():
    """Test that DECAS validates the bas parameter exists and works correctly"""
    # Create SDModel with immediate validation enabled
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    
    model.add(LOADC(run_number=1,alc=1,olc=110))
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
    
    # Now create DECAS that references the existing bas - validation=True enables immediate validation
    decas = DECAS(ls='ULS', bas=101)
    model.add(decas, validation=True)  # New API: immediate validation
    
    # Test that the validation works - bas 101 exists so this should pass
    assert decas.input == "DECAS LS=ULS BAS=101"


def test_decas_bas_validation_with_greco():
    """Test that DECAS validates the bas and greco parameter exists and works correctly"""
    # Create SDModel with immediate validation enabled
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    
    model.add(LOADC(run_number=1,alc=1,olc=110))
    model.add(LOADC(run_number=2,alc=(2,7),olc=(101,106)))  # Use run_number=2 to avoid duplicate
    for i in range(6):
        model.add(BASCO(id=101+i, load_cases=[LoadCase(lc_type='OLC', lc_numb=101+i)]))

    model.add(GRECO(id='A', bas=[101,106]))

    model.add(BASCO(id=201, load_cases=[LoadCase(lc_type='ELC', lc_numb=110,lc_fact=1.5)]))  # Another BASCO to ensure no false positives
    
    # Now create DECAS that references the existing bas - with immediate validation
    decas = DECAS(ls='ULS', bas=101, greco='A')
    model.add(decas, validation=True)  # New API: immediate validation
    
    # Test that the validation works - bas 101 exists so this should pass
    assert decas.input == "DECAS LS=ULS BAS=101:A"

def test_decas_validation_error():
    """Test that DECAS raises an error when the bas parameter does not exist"""
    import pytest
    
    # Create SDModel and add basic load cases first
    output_file = "tests/test_output/test_decas_validation_error.mdl"
    
    # The validation error should be raised when the context exits (during finalization)
    with pytest.raises(ValueError, match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]"):
        with SD_BASE.create_writer(output_file) as model:
            model.validation_enabled = True

            model.add(LOADC(run_number=1,alc=1,olc=110))
            model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))

            # Now create DECAS that references a non-existing bas
            decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
            model.add(decas)
            
            # The validation error will be raised when the context manager exits


def test_decas_validation_error_immediate():
    """Test that DECAS raises immediate validation error with new API when the bas parameter does not exist"""
    import pytest
    
    # Create SDModel with immediate validation
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    
    model.add(LOADC(run_number=1,alc=1,olc=110))
    model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))

    # Now create DECAS that references a non-existing bas - should fail immediately
    decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
    
    with pytest.raises(ValueError, match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]"):
        model.add(decas, validation=True)  # New API: immediate validation should fail here


def test_decas_tuple():
    """Test the DECAS statement using tuple and greco"""
    decas = DECAS(ls='ULS', bas=(101,102), greco='A')
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"

def test_decas_string():
    """Test the DECAS statement using string"""
    decas = DECAS(ls='ULS', bas="101-102:A")
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"

def test_decas_list_tuple():
    """Test the DECAS statement list containing tuples"""
    decas = DECAS(ls='ULS', bas=[(101,102)], greco='A')
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"

# def test_decas_list_int():
#  TDOO  Fix this test so that it works
#     """Test the DECAS statement list containing tuples"""
#     decas = DECAS(ls='ULS', bas=[101,102], greco='A')
#     assert decas.input == "DECAS LS=ULS BAS=101-102:A"


def test_decas_case_buider():
    """Test the DECAS statement using the CaseBuilder"""
    cases = CaseBuilder().add(101,102).add_greco('A')
    decas = DECAS(ls='ULS', bas=cases)
    assert decas.input == "DECAS LS=ULS BAS=101-102:A"

def test_decas_only_int_no_greco():
    """Test the DECAS statement list containing tuples"""
    decas = DECAS(ls='ULS', bas=101)
    assert decas.input == "DECAS LS=ULS BAS=101"
