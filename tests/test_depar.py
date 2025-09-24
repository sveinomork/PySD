import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import DEPAR

def test_depar_simple():
    """Test the DEPAR statement from main.py"""
    depar = DEPAR(
        n_lay=10,
        d_sig=10.0,
        d_cod="NS"
    )
    print(depar.input)
    assert depar.input == "DEPAR N_LAY=10 D_SIG=10 D_COD=NS"

if __name__ == "__main__":
    test_depar_simple()
    print("All tests passed.")