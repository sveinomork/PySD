import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.sdmodel import SD_BASE
from pysd.statements import BASCO, LoadCase
def test_basco_basic():
    """Test basic BASCO with single load case"""
    basco = BASCO(
        id=1010,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=1100, lc_fact=1.0)
        ]
    )
    assert basco.input == "BASCO ID=1010 LF=1.0 OLC=1100"

def test_basco_multiple_load_cases():
    """Test the first BASCO statement from the loop in main.py"""
    load_cases = [LoadCase(lc_type='OLC', lc_numb=201, lc_fact=1),
                  LoadCase(lc_type='ELC', lc_numb=202, lc_fact=1),
                  ]
    basco = BASCO(id=211, load_cases=load_cases)
    assert basco.input == "BASCO ID=211 LF=1.0 OLC=201 LF=1.0 ELC=202"

def test_basco_connected_sdbase():
    """Test BASCO connected to SD_BASE model"""
    with SD_BASE.create_writer(output_file) as model:
        basco = BASCO(
            id=1001,
            load_cases=[
                LoadCase(lc_type='OLC', lc_numb=101, lc_fact=1.0),
                LoadCase(lc_type='ELC', lc_numb=102, lc_fact=1.5)
            ]
        )
        model.add(basco)
    assert basco.input == "BASCO ID=1001 LF=1.0 OLC=101 LF=1.5 ELC=102"
    