import sys

sys.path.append("C:\\Users\\nx74\\Work\\programing\\PySD\\src")
from pysd.statements import FILST


def test_filst_simple():
    """Test the FILST statement from main.py"""
    filst = FILST(name="aquapod", vers="1.0", date="14.aug-2025", resp="som")
    print(filst.input)
    assert filst.input == "FILST NAME=aquapod VERS=1.0 DATE=14.aug-2025 RESP=som"


if __name__ == "__main__":
    test_filst_simple()
    print("All tests passed.")
