import sys

sys.path.append("C:\\Users\\som\\coding\\PySD\\src")
from pysd.statements import CMPEC


def test_cmpec_basic():
    """Test the CMPEC statement from main.py"""
    cmpec = CMPEC(id=1, gr="B35")
    assert cmpec.input == "CMPEC ID=1 GR=B35"


def test_cmpec_full():
    """Test the CMPEC statement with all parameters"""
    cmpec = CMPEC(
        id=2,
        gr="B40",
        rh=1250.0,
        fck=40000.0,
        ecm=30000.0,
        fcn=35000.0,
        ftm=3000.0,
        acc=0.9,
        exp=0.3,
        ec2=2000.0,
        ecu=0.0035,
        mfu=1.4,
        mfa=1.1,
        mfs=1.0,
        k1c=0.16,
        k1t=0.32,
        k2=0.14,
        cot=2.6,
        tsp=120,
        tsd=1.1,
        la=10,
        pa="VEGG",
        fs=(1, 20),
        hs=(1, 10),
    )

    expected_input = (
        "CMPEC ID=2 GR=B40 RH=1250 FCK=40000 ECM=30000 FCN=35000 "
        "FTM=3000 ACC=0.9 EXP=0.3 EC2=2000 ECU=0.0035 MFU=1.4 MFA=1.1 "
        "MFS=1 K1C=0.16 K1T=0.32 K2=0.14 COT=2.6 TSP=120 TSD=1.1 "
        "LA=10 PA=VEGG FS=1-20 HS=1-10"
    )

    assert cmpec.input == expected_input


if __name__ == "__main__":
    test_cmpec_basic()
    test_cmpec_full()
    print("All tests passed.")
