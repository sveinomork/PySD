from __future__ import annotations

from typing import Any, TYPE_CHECKING, Protocol, Union, TypeAlias, runtime_checkable


@runtime_checkable
class StatementProtocol(Protocol):
    """Protocol that all statement classes must implement."""
    input: str  # All statements have an input string


# Runtime: keep it light to avoid Pydantic schema issues with Protocols
StatementType: TypeAlias = Any

if TYPE_CHECKING:
    # Import all statement types for type hints (only for IDE/mypy)
    from .statements import (
        GRECO, BASCO, LOADC, SHSEC, SHAXE, CMPEC, RMPEC, RETYP, SRTYP, RELOC,
        LORES, XTFIL, DESEC, TABLE, RFILE, INCDF, DECAS, DEPAR, FILST, HEADL,
        Cases, EXECD, HEADING,
    )

    # Provide the full Union for rich IDE support (type checkers only)
    StatementType: TypeAlias = Union[
        GRECO, BASCO, LOADC, SHSEC, SHAXE, CMPEC, RMPEC, RETYP, SRTYP, RELOC,
        LORES, XTFIL, DESEC, TABLE, RFILE, INCDF, DECAS, DEPAR, FILST, HEADL,
        Cases, EXECD, HEADING,
    ]
