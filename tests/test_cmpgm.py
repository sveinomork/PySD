from pysd.statements import CMPGM


def test_cmpgm_basic():
    """Basic CMPGM formatting with minimal fields."""
    s = CMPGM(id=1, gr="B30")
    assert s.input == "CMPGM ID=1 GR=B30"


def test_cmpgm_full():
    """Full CMPGM formatting with many fields."""
    s = CMPGM(
        id=2,
        gr="B40",
        epu=0.0035,
        ftc=2500.0,
        ags=0.03,
        mfu=1.4,
        mfa=1.1,
        mfs=1.0,
        sp=5,
        la=10,
        pa="VEGG",
        fs=(1, 20),
        hs=(1, 10),
    )
    expected = (
        "CMPGM ID=2 GR=B40 EPU=0.0035 FTC=2500 AGS=0.03 "
        "MFU=1.4 MFA=1.1 MFS=1 SP=5 LA=10 PA=VEGG FS=1-20 HS=1-10"
    )
    assert s.input == expected
