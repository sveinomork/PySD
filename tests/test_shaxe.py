import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import SHAXE

def test_shaxe_from_main_py():
    """Test the SHAXE statement from main.py"""
    shaxe = SHAXE( pa="PLATE", x1=(1,0,0),x2=(0,1,0),x3=(0,0,1) )
    assert shaxe.input == "SHAXE PA=PLATE X1=1,0,0 X2=0,1,0 X3=0,0,1"
