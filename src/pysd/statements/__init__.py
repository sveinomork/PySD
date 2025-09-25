"""
ShellDesign statements module
"""

# Import all statement classes

from .cases import Cases, CaseBuilder,normalize_cases
from .basco import BASCO, LoadCase
from .greco import GRECO
from .headl import HEADL
from .desec import DESEC
from .shaxe import SHAXE
from .execd import EXECD
from .filst import FILST
from .loadc import LOADC
from .shsec import SHSEC
from .xtfil import XTFIL
from .decas import DECAS
from .table import TABLE
from .incdf import INCDF
from .retyp import RETYP 
from .srtyp import SRTYP
from .tetyp import TETYP
from .reloc import RELOC
from .srloc import SRLOC
from .teloc import TELOC
from .cmpec import CMPEC
from .rmpec import RMPEC 
from .temat import TEMAT 
from .lores import LORES
from .rfile import RFILE
from .depar import DEPAR
from .statement_heading import HEADING
#from ..statement_config import ALL_STATEMENTS


       
# ... importer alle andre statements

__all__ = [
    # BASCO related
    "BASCO", 
    "LoadCase",
    
    # Cases related
    "Cases",
    "CaseBuilder", 
    "normalize_cases",
    
    # Individual statements
    "LOADC",
    "GRECO", 
    "HEADL",
    "DESEC",
    "SHAXE",
    "EXECD",
    "FILST",
    "SHSEC",
    "XTFIL",
    "DECAS",
    "TABLE",
    "INCDF",
    "RELOC",
    "SRLOC",
    "TELOC",
    "CMPEC",
    "RMPEC",
    "TEMAT",
    "LORES",
    "RETYP",
    "SRTYP",
    "TETYP",
    "RFILE",
    "DEPAR",
    "HEADING"
]

def __getattr__(name: str):
    # Helpful message if a contributor forgets to add a new class to __all__
    if name not in __all__:
        raise AttributeError(
            f"pysd.statements has no attribute {name!r}. "
            f"If you added a new statement, import it in pysd.statements.__init__ and add it to __all__."
        )
    raise  # Let normal AttributeError propagate if Python got here by mistake