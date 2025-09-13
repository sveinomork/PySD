import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RELOC

def test_reloc_from_main_py():
    """Test the RELOC statement from main.py"""
    reloc = RELOC(id="X12", pa="VEGG_2", rt=1, fa=1, al=0)
    assert "RELOC" in reloc.input
    assert "ID=X12" in reloc.input
    assert "PA=VEGG_2" in reloc.input
    assert "RT=1" in reloc.input
    assert "FA=1" in reloc.input
    assert "AL=0.0" not in reloc.input