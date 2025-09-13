import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import FILST

def test_filst_from_main_py():
    """Test the FILST statement from main.py"""
    filst = FILST(
        name="aquapod",
        vers="1.0",
        date="14.aug-2025",
        resp="som"
    )
    assert filst.input == "FILST NAME=aquapod VERS=1.0 DATE=14.aug-2025 RESP=som"