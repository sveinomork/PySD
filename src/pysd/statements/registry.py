from __future__ import annotations
from typing import Dict, Type

STATEMENT_CLASSES: Dict[str, Type] = {}


def register_statement(cls: Type) -> Type:
    """
    Register a Statement class by its class name (e.g., 'GRECO' -> GRECO class).
    Called automatically by StatementBase.__init_subclass__.
    """
    STATEMENT_CLASSES[cls.__name__] = cls
    return cls
