import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import GRECO, Cases

def test_greco_simple():
    """Test the GRECO statement from main.py"""
    greco = GRECO(
        id='A',
        bas=Cases(ranges=[(211, 216)])
    )
    assert greco.input == "GRECO ID=A BAS=211-216"