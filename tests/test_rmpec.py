import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RMPEC

def test_rmpec_simple():
    """Test the RMPEC statement from main.py"""
    rmpec = RMPEC(id=1, gr=500)
   
    assert rmpec.input == "RMPEC ID=1 GR=500"

def test_rmpec_detailed():
    """Test the RMPEC statement with all parameters"""
    rmpec = RMPEC(
        id=2, gr="600", esk=200000, fyk=500000,fsk=400000, den=7850,mfu=1.15,
        epu=0.3, mfa=1.10, epa=0.010, mfs=1.00, eps=0.002)
       
   
    print(rmpec.input)
    expected_input = (
        "RMPEC ID=2 GR=600 ESK=200000 FYK=500000 FSK=400000 DEN=7850 "
        "MFU=1.15 EPU=0.3 MFA=1.1 EPA=0.01 MFS=1 EPS=0.002"
    )
    print(expected_input)
    assert rmpec.input == expected_input

if __name__ == "__main__":
    test_rmpec_simple()
    test_rmpec_detailed()

    print("All tests passed.")