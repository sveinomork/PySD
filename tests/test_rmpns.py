from pysd.statements import RMPNS


def test_rmpns_basic():
    s = RMPNS(id=1, gr=500)
    assert s.input == "RMPNS ID=1 GR=500"


def test_rmpns_full():
    s = RMPNS(
        id=2,
        gr=500,
        esk=200e6,
        fyk=500e3,
        fsk=600e3,
        den=7850,
        mfu=1.15,
        epu=0.01,
        mfa=1.0,
        epa=0.01,
        mfs=1.0,
        eps=0.01,
        mff=1.1,
        ccf=1.0,
    )
    expected = (
        "RMPNS ID=2 GR=500 ESK=200000000 FYK=500000 FSK=600000 DEN=7850 "
        "MFU=1.15 EPU=0.01 MFA=1 EPA=0.01 MFS=1 EPS=0.01 MFF=1.1 CCF=1"
    )
    assert s.input == expected
