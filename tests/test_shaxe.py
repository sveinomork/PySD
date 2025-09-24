import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')

from pysd.sdmodel import SD_BASE
from pysd.statements import SHAXE,SHSEC

def test_shaxe_basic():
    """Test the SHAXE statement from main.py"""
    shaxe = SHAXE( pa="PLATE", x1=(1,0,0),x2=(0,1,0),x3=(0,0,1) )
    assert shaxe.input == "SHAXE PA=PLATE X1=1,0,0 X2=0,1,0 X3=0,0,1"


def test_shaxe_model():
    """Test the SHAXE statement using sd_model"""
    model=SD_BASE()
    model.add(SHSEC(pa="PLATE",elset=3,hs=(1,4)))
    model.add(SHAXE( pa="PLATE", x1=(1,0,0),x2=(0,1,0),x3=(0,0,1) ))
    assert model.shaxe[0].input == "SHAXE PA=PLATE X1=1,0,0 X2=0,1,0 X3=0,0,1"

