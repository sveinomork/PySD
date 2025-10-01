from pysd.sdmodel import SD_BASE
from pysd.statements import TEMAT, TETYP, RETYP, RMPEC
from pathlib import Path
#tests/test_integration.py
def test_full_model_lifecycle():
    """Test complete workflow."""
    model = SD_BASE()
    
    # Build model
    model.add(TEMAT(id=1, gr="B35"))
    model.add(TETYP(id=1, mp=1,ar=100))
    # ... etc
    
    # Validate
    model.finalize()

    # Write
    temp_file = "temp_model.txt"
    model.write(temp_file)
    
    # Read back
    assert Path(temp_file).exists()
    content = Path(temp_file).read_text()
    assert "TEMAT" in content
    
    # Cleanup
    Path(temp_file).unlink()