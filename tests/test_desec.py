import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import DESEC

def test_desec_from_main_py():
    """Test the DESEC statements from main.py"""
    desec1 = DESEC(pa="VEGG_2")
    assert desec1.input == "DESEC PA=VEGG_2"

    desec2 = DESEC(pa="PLATE")
    assert desec2.input == "DESEC PA=PLATE"
