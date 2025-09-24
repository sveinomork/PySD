import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import RFILE
import os
import tempfile

def test_rfile_simple():
    """Test the RFILE statement from main.py"""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "R1.SIN")
        with open(file_path, "w") as f:
            f.write("dummy content")

        rfile = RFILE(
            pre=tmpdir,
            fnm="R1",
            suf="SIN",
            typ="SHE",
        )
        assert rfile.input == f'RFILE PRE={tmpdir} FNM=R1 SUF=SIN TYP=SHE'