import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RMPEC

def test_rmpec_from_main_py():
    """Test the RMPEC statement from main.py"""
    rmpec = RMPEC(id=1, gr=500)
    assert rmpec.input == "RMPEC ID=1 GR=500.0"