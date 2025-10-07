"""Validation rules module - imports all rule files to register them."""

# Import all validation rule files to ensure they're registered
from . import greco_rules
from . import basco_rules
from . import loadc_rules
from . import cases_rules
from . import shsec_rules
from . import rfile_rules
from . import incdf_rules  # FILST rules
from . import shaxe_rules
from . import cmpec_rules
from . import rmpec_rules
from . import retyp_rules
from . import reloc_rules
from . import lores_rules
from . import xtfil_rules
from . import desec_rules
from . import table_rules
from . import decas_rules
from . import srtyp_rules
from . import tetyp_rules
from . import temat_rules

__all__ = [
    "greco_rules",
    "basco_rules",
    "loadc_rules",
    "cases_rules",
    "shsec_rules",
    "rfile_rules",
    "incdf_rules",
    "shaxe_rules",
    "cmpec_rules",
    "rmpec_rules",
    "retyp_rules",
    "reloc_rules",
    "lores_rules",
    "xtfil_rules",
    "desec_rules",
    "table_rules",
    "decas_rules",
    "srtyp_rules",
    "tetyp_rules",
    "temat_rules",
]
