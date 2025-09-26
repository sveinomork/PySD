from pysd.statements import XTFIL


def test_xtfil_simple():
    """Test the XTFIL statements from main.py"""
    xtfil1 = XTFIL(fn="AquaPod_09", pa="VEGG_2", fs=(1, 9999), hs=(1, 99))
    print(xtfil1.input)
    assert xtfil1.input == "XTFIL FN=AquaPod_09 PA=VEGG_2 FS=1-9999 HS=1-99"

    xtfil2 = XTFIL(fn="AquaPod_09", pa="PLATE", fs=(1, 9999), hs=(1, 99))
    print(xtfil2.input)
    assert xtfil2.input == "XTFIL FN=AquaPod_09 PA=PLATE FS=1-9999 HS=1-99"
