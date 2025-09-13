import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import EXECD

def test_execd_from_main_py():
    """Test the EXECD statement from main.py"""
    execd = EXECD(dm='V')
    assert execd.input == "EXECD DM=V"
