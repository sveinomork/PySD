from src.pysd.statements import BASCO, LoadCase
def test_basco_basic():
    """Test basic BASCO with single load case"""
    basco = BASCO(
        id=1010,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=1100, lc_fact=1.0)
        ]
    )
    assert basco.input == "BASCO ID=1010 LF=1.0 OLC=1100"