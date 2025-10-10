import pytest

from pysd.statements.rmpec import RMPEC

from pysd.statements import RETYP


def test_retyp_parameters():
    """Test the RETYP statements basic"""
    retyp1 = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )
    assert "RETYP" in retyp1.input
    assert "ID=1" in retyp1.input
    assert "MP=1" in retyp1.input
    assert "AR=0.000753" in retyp1.input
    assert "C2=0.055" in retyp1.input
    assert "TH=0.014" in retyp1.input
    assert "DI=0.012" in retyp1.input
    assert "NR=1" in retyp1.input
    assert "LB=1.0D12_c150" in retyp1.input

    retyp2 = RETYP(
        id=2, mp=1, ar=753.0e-6, os=0.0, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )
    assert "RETYP" in retyp2.input
    assert "ID=2" in retyp2.input
    assert "MP=1" in retyp2.input
    assert "AR=0.000753" in retyp2.input
    assert "OS=0" in retyp2.input
    assert "TH=0.014" in retyp2.input
    assert "DI=0.012" in retyp2.input
    assert "NR=1" in retyp2.input
    assert "LB=1.0D12_c150" in retyp2.input


def test_retyp_incteracting_with_sd_base_success():
    """Test RETYP interacting with SD_BASE model"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=False
    )
    retyp = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )

    model.add(retyp, validation=True)  # Immediate validation
    assert retyp.ar == 753.0e-6
    # assert retyp.input == "RETYP ID=1 MP=1 AR=0.000753 C2=0.055 TH=0.014 DI=0.012 NR=1 LB=1.0D12_c150"


def test_retyp_incteracting_with_sd_base_failure():
    """Test RETYP interacting with SD_BASE model"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    retyp = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )
    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(retyp, validation=True)  # Immediate validation


def test_retyp_add_rmpec_succuess():
    """Test RETYP interacting with SD_BASE model, adding RMPEC first to satisfy cross-validation"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    model.add(RMPEC(id=1, gr="500"), validation=True)  # Immediate validation
    retyp = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )
    print(retyp.input)
    model.add(retyp, validation=True)  # Immediate validation


def test_retyp_add_rmpec_failure():
    """Test RETYP interacting with SD_BASE model, adding RMPEC first to fail cross-validation"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    model.add(RMPEC(id=2, gr="500"), validation=True)  # Immediate validation
    retyp = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )

    with pytest.raises(ValueError, match=r"Model validation failed"):
        model.add(retyp, validation=True)  # Immediate validation


def test_retyp_add_rmpns_success():
    """Test RETYP interacting with SD_BASE model, adding RMPNS material to satisfy cross-validation"""
    from pysd.sdmodel import SD_BASE
    from pysd import ValidationLevel
    from pysd.statements.rmpns import RMPNS

    model = SD_BASE(
        validation_level=ValidationLevel.NORMAL, cross_object_validation=True
    )
    model.add(RMPNS(id=1, fc=30.0), validation=True)  # Add RMPNS material
    retyp = RETYP(
        id=1, mp=1, ar=753.0e-6, c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"
    )
    model.add(retyp, validation=True)  # Should succeed with RMPNS material
    assert retyp.mp == 1
    assert model.rmpns[0].id == 1


if __name__ == "__main__":
    test_retyp_add_rmpec_succuess()
