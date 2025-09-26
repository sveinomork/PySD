from pysd.statements import LAREA


def test_larea_section_ranges_basic():
    # Example: LAREA(id=1, pa="BASE", fs=(1,24), hs=(5,15))
    s = LAREA(id=1, pa="BASE", fs=(1, 24), hs=(5, 15))
    # FS/HS keep hyphen for 2-tuples
    assert "PA=BASE" in s.input
    assert "FS=1-24" in s.input
    assert "HS=5-15" in s.input


def test_larea_coordinate_box_with_commas():
    # Example: LAREA(id=2, pa="BASE", xr=(2,30), yr=(7,8), al=30)
    s = LAREA(id=2, pa="BASE", xr=(2, 30), yr=(7, 8), al=30)
    # XR/YR use commas for 2-tuples (field-specific override)
    assert "PA=BASE" in s.input
    assert "XR=2,30" in s.input
    assert "YR=7,8" in s.input
    # float_precision=1 with trailing zeros stripped => "30" (no trailing dot)
    assert "AL=30" in s.input


def test_larea_pri_mode_prints_only_pri_flag():
    # PRI mode prints only the statement and PRI flag
    s = LAREA(id=3, pa="BASE", pri=True)
    assert s.input == "LAREA PRI="

