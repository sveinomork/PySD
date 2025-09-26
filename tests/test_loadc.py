
from pysd.statements import LOADC
from pysd.sdmodel import SD_BASE


def test_loadc():
    """Test the LOADC statements from main.py"""
    loadc1 = LOADC(run_number=1, alc=(1,7), olc=(101,107))
    assert loadc1.input == "LOADC RN=1 ALC=1-7 OLC=101-107"

def test_loadc_with_comment():
    loadc1 = LOADC(run_number=1, alc=(1,6), olc=(201,206),comment="Equilibrium load case")
    assert loadc1.input == "LOADC RN=1 ALC=1-6 OLC=201-206 % Equilibrium load case"

def test_loadc_table_and_pri():
    loadc2 = LOADC(table=True)
    assert loadc2.input == "LOADC TAB="

    loadc3 = LOADC(pri=True)
    assert loadc3.input == "LOADC PRI="

def test_loadc_in_model():
    """Test LOADC in a full model context."""
    sd_model = SD_BASE()
    loadc1 = LOADC(run_number=1, alc=(1,6), olc=(201,206))
    sd_model.add(loadc1)
    loadc2 = LOADC(run_number=1, alc=(11,16), olc=(101,106))
    sd_model.add(loadc2)
    loadc3 = LOADC(table=True)
    sd_model.add(loadc3)
    loadc4 = LOADC(pri=True)
    sd_model.add(loadc4)
    print(sd_model.loadc[0].input)

    assert sd_model.loadc[0].input == "LOADC RN=1 ALC=1-6 OLC=201-206"
    assert sd_model.loadc[1].input == "LOADC RN=1 ALC=11-16 OLC=101-106"
    assert sd_model.loadc[2].input == "LOADC TAB="
    assert sd_model.loadc[3].input == "LOADC PRI="

