import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import LORES

def test_lores_simple():
    """Test the LORES statements from main.py"""
    lores1 = LORES(pri_alc=True)
    assert lores1.input == "LORES PRI=ALC"

    lores2 = LORES(sin=True)
    assert lores2.input == "LORES SIN="
