import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import CMPEC

def test_cmpec_from_main_py():
    """Test the CMPEC statement from main.py"""
    cmpec = CMPEC(id=1, gr="B35")
    assert cmpec.input == "CMPEC ID=1 GR=B35"