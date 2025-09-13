import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import SHSEC

def test_shsec_from_main_py():
    """Test the SHSEC statement from main.py"""
    shsec = SHSEC(pa="PLATE",elset=3,hs=(1,4))
    assert shsec.input == "SHSEC PA=PLATE ELSET=3 HS=1-4"