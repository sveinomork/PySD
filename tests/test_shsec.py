import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import SHSEC

def test_shsec_from_basic_py():
    """Test the SHSEC basic.py"""
    shsec = SHSEC(pa="PLATE",elset=3,hs=(1,4))
    assert shsec.input == "SHSEC PA=PLATE ELSET=3 HS=1-4"


def test_shsec_more_params():
    """Test the SHSEC identifier property."""
    #SHSEC PA=BS-SHAFT SE=20001 EL=11216 XF=0,1,0 XH=1,0,0 FS=1-2 HS=2-25 NE=3 ET=LI
    shsec = SHSEC(pa="BS-SHAFT", se=20001, el=11216, xf=(0, 1, 0), xh=(1, 0, 0), fs=(1, 2), hs=(2, 25), ne=3, et="LI")
    
    assert str(shsec) == "SHSEC PA=BS-SHAFT SE=20001 EL=11216 XF=0.0,1.0,0.0 XH=1.0,0.0,0.0 FS=1-2 HS=2-25 NE=3 ET=LI"
                                         


if __name__ == "__main__":
    test_shsec_from_basic_py()
    test_shsec_more_params()