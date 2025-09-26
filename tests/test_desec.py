import pytest

from pysd.statements.shsec import SHSEC

from pysd.statements import DESEC
from pysd.sdmodel import SD_BASE


def test_desec_simple():
    """Test the DESEC statements simple"""
    desec1 = DESEC(pa="VEGG_2")
    assert desec1.input == "DESEC PA=VEGG_2"

    desec2 = DESEC(pa="PLATE")
    assert desec2.input == "DESEC PA=PLATE"


def test_desec_model():
    """Test the DESEC statements from model,including cross-validation with SHSEC"""
    sd_model = SD_BASE()
    sd_model.add(SHSEC(pa="PLATE", elset=3, hs=(1, 4)))

    desec1 = DESEC(pa="PLATE", hs=(1, 4), fs=(1, 2))
    sd_model.add(desec1)
    assert desec1.input == "DESEC PA=PLATE HS=1-4 FS=1-2"


def test_desec_model_failure():
    """Test the DESEC statements failure due to cross-validation with SHSEC"""
    sd_model = SD_BASE()
    sd_model.add(SHSEC(pa="PLATE2", elset=3, hs=(1, 4)))

    desec1 = DESEC(pa="PLATE", hs=(1, 4), fs=(1, 2))
    with pytest.raises(ValueError, match=r"Model validation failed"):
        sd_model.add(desec1)


if __name__ == "__main__":
    test_desec_simple()
    test_desec_model()
