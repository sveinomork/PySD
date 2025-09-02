"""
ShellDesign statements module
"""

# Import all statement classes
from .basco import BASCO, LoadCase, convert_to_only_olcs
from .cases import Cases, CaseBuilder,normalize_cases
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
from .reloc import RELOC
from .cmpec import CMPEC
from .rmpec import RMPEC  
from .lores import LORES
from .rfile import RFILE



       
# ... importer alle andre statements

__all__ = [
    # BASCO related
    "BASCO", 
    "LoadCase",
    "convert_to_only_olcs",
    
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
    "CMPEC",
    "RMPEC",
    "LORES",
    "RETYP",
    "RFILE"

    # ... alle andre
]