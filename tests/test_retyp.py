import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RETYP

def test_retyp_from_main_py():
    """Test the RETYP statements from main.py"""
    retyp1 = RETYP(id=1, mp=1, ar=753.0E-6 , c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150")
    assert "RETYP" in retyp1.input
    assert "ID=1" in retyp1.input
    assert "MP=1" in retyp1.input
    assert "AR=0.000753" in retyp1.input
    assert "C2=0.055" in retyp1.input
    assert "TH=0.014" in retyp1.input
    assert "DI=0.012" in retyp1.input
    assert "NR=1" in retyp1.input
    assert "LB=1.0D12_c150" in retyp1.input

    retyp2 = RETYP(id=2, mp=1, ar=753.0E-6 , os=0.0, th=0.014, di=0.012, nr=1, lb="1.0D12_c150")
    assert "RETYP" in retyp2.input
    assert "ID=2" in retyp2.input
    assert "MP=1" in retyp2.input
    assert "AR=0.000753" in retyp2.input
    assert "OS=0" in retyp2.input
    assert "TH=0.014" in retyp2.input
    assert "DI=0.012" in retyp2.input
    assert "NR=1" in retyp2.input
    assert "LB=1.0D12_c150" in retyp2.input