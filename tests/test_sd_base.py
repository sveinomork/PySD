import pytest

from pysd import SD_BASE, ValidationLevel
from pysd.statements import (
    RETYP,
    SHSEC,
    DESEC,
    RFILE,
    LOADC,
)


def test_add_single_and_container_presence():
    m = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    r = RETYP(id=1, mp=1, ar=1e-3)
    # Disable cross-object validation here; we only test routing/container behavior
    m.add(r, validation=False)
    assert len(m.retyp) == 1
    assert m.retyp.contains(1)


def test_container_id_normalization():
    m = SD_BASE()
    # RETYP uses int id; normalization lets 1.0 match 1
    m.add(RETYP(id=1, mp=1, ar=1e-3), validation=False)
    assert m.retyp.contains(1.0)
    assert m.retyp.get_by_id("1") is not None


def test_duplicate_identifier_rejected():
    m = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    m.add(RETYP(id=1, mp=1, ar=1e-3), validation=False)
    with pytest.raises(ValueError):
        m.add(RETYP(id=1, mp=1, ar=2e-3), validation=False)  # same id should fail


def test_validation_immediate_vs_deferred(tmp_path):
    # Immediate validation raises when cross-ref invalid
    m1 = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    m1.add(SHSEC(pa="PLATE", elset=3, hs=(1, 4)))
    with pytest.raises(ValueError):
        m1.add(DESEC(pa="OTHER", hs=(1, 4), fs=(1, 2)), validation=True)

    # Deferred: add invalid, then final validation fails on write/finalize
    m2 = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    m2.add(SHSEC(pa="PLATE", elset=3, hs=(1, 4)))
    m2.add(DESEC(pa="OTHER", hs=(1, 4), fs=(1, 2)), validation=False)
    out = tmp_path / "model_invalid.inp"
    with pytest.raises(ValueError):
        # write triggers finalize/validation
        m2.write(str(out))


def test_validation_disabled_allows_invalid():
    m = SD_BASE(validation_level=ValidationLevel.DISABLED, cross_object_validation=False)
    # No matching SHSEC for DESEC, but validation disabled means it's accepted
    m.add(DESEC(pa="NO_MATCH", hs=(1, 4), fs=(1, 2)), validation=False)
    assert len(m.desec) == 1


def test_write_creates_file_and_contains_lines(tmp_path):
    m = SD_BASE()
    # Create a real file for RFILE validation to pass
    (tmp_path / "R1.SIN").write_text("", encoding="utf-8")
    m.add(RFILE(pre=str(tmp_path), fnm="R1", suf="SIN", typ="SHE"))
    m.add(LOADC(run_number=1, alc=(1, 2), olc=(101, 102)))
    out = tmp_path / "out.inp"
    m.write(str(out))
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "RFILE" in text and "LOADC" in text


def test_trailing_comment_auto_append():
    m = SD_BASE()
    s = LOADC(run_number=1, alc=(1, 2), olc=(101, 102), comment="Equilibrium load case")
    m.add(s)
    assert s.input.endswith("% Equilibrium load case")


def test_router_places_statement_in_correct_container(tmp_path):
    m = SD_BASE()
    (tmp_path / "R1.SIN").write_text("", encoding="utf-8")
    r = RFILE(pre=str(tmp_path), fnm="R1", suf="SIN", typ="SHE")
    m.add(r)
    assert len(m.rfile) == 1
    assert m.rfile.items[0] is r
