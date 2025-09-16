import sys

from pysd.statements import SHSEC
from pysd.statements.rmpec import RMPEC
from pysd.validation.core import ValidationLevel
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RELOC

def test_reloc_attributes():
    """Test the RELOC statement from main.py"""
    reloc = RELOC(id="X12", pa="VEGG_2", rt=1, fa=1, al=0)
    assert "RELOC" in reloc.input
    assert "ID=X12" in reloc.input
    assert "PA=VEGG_2" in reloc.input
    assert "RT=1" in reloc.input
    assert "FA=1" in reloc.input
    assert "AL=0.0" not in reloc.input

def test_reloc_statement():
    """# Rebar in a specific section range:
    RELOC(id='X11', rt=(16101, 20101), fa=1, fs=(5, 10), hs=3)
    → 'RELOC ID=X11 RT=16101-20101 FA=1 FS=5-10 HS=3'
    """
    reloc = RELOC(id="X11", rt=(16101, 20101),al=0, fa=1, fs=(5, 10), hs=3)
    print(reloc.input)
    assert reloc.input == "RELOC ID=X11 RT=16101-20101 FA=1 FS=5-10 AL=0.0 HS=3"

def test_reloc_in_model():
    """Test RELOC in a full model context."""
    from pysd import SD_BASE
    from pysd.statements import RELOC, RETYP

    sd_model = SD_BASE(validation_level=ValidationLevel.NORMAL,cross_object_validation=True)
    sd_model.add(RMPEC(id=1,gr=500))
    sd_model.add(SHSEC(pa="PLATE",elset=3,hs=(1,4)))
    retyp1 = RETYP(id=1, mp=1, ar=753.0E-6 , c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150")
    retyp2 = RETYP(id=2, mp=1, ar=853.0E-6 , c2=0.055, th=0.014, di=0.012, nr=1, lb="1.1D12_c150")
    sd_model.add(retyp1)
    sd_model.add(retyp2)
    reloc = RELOC(id="X11", rt=(1, 2),al=0, fa=1,pa="PLATE", fs=(5, 10), hs=3)
    print(reloc.input)
    sd_model.add(reloc)
    assert sd_model.reloc[0].input == "RELOC ID=X11 RT=1-2 FA=1 AL=0 PA=PLATE FS=5-10 HS=3"

if __name__ == "__main__":
    #test_reloc_attributes()
    #test_reloc_statement()
    test_reloc_in_model()