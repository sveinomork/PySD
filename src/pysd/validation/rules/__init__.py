"""Validation rules module - imports all rule files to register them."""

# Import all validation rule files to ensure they're registered
from . import greco_rules
from . import basco_rules
from . import loadc_rules
from . import cases_rules
from . import shsec_rules
from . import rfile_rules
from . import rules_incdf  # FILST rules
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

__all__ = []