from pysd.statements import CMPOS


def test_cmpos_basic():
    s = CMPOS(id=1, gr="C35")
    assert s.input == "CMPOS ID=1 GR=C35"


def test_cmpos_full():
    s = CMPOS(
        id=2,
        gr="C45",
        rh=1250.0,
        fig=(1, 2),
        fcn=35000.0,
        ecn=30000.0,
        epu=0.0035,
        csd=0.9,
        tsp=120,
        tsd=1.1,
        ftk=3000.0,
        ftn=2500.0,
        ac1=0.85,
        ac2=0.75,
        mfu=1.4,
        mfa=1.1,
        mff=1.0,
        mfs=1.0,
        la=10,
        pa="VEGG",
        fs=(1, 20),
        hs=(1, 10),
    )
    expected = (
        "CMPOS ID=2 GR=C45 RH=1250 FIG=1-2 FCN=35000 ECN=30000 EPU=0.0035 "
        "CSD=0.9 TSP=120 TSD=1.1 FTK=3000 FTN=2500 AC1=0.85 AC2=0.75 "
        "MFU=1.4 MFA=1.1 MFF=1 MFS=1 LA=10 PA=VEGG FS=1-20 HS=1-10"
    )
    assert s.input == expected
