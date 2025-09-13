import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import LOADC

def test_loadc():
    """Test the LOADC statements from main.py"""
    loadc1 = LOADC(run_number=1, alc=(1,7), olc=(101,107))
    assert loadc1.input == "LOADC RN=1 LC=1-7,101-107"

def test_loadc_table_and_pri():
    loadc2 = LOADC(table=True)
    assert loadc2.input == "LOADC TAB="

    loadc3 = LOADC(pri=True)
    assert loadc3.input == "LOADC PRI="