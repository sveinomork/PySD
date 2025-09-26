# Type stubs for IDE support — enables hover docs and auto-completion.
# This stub has no runtime effect.

from typing import (
    Sequence,
    Any,
    overload,
    Protocol,
    runtime_checkable,
    TypeAlias,
    Union,
)
from pydantic import BaseModel

from .validation.core import ValidationLevel
from .model.validation_manager import ValidationManager
from .model.base_container import BaseContainer
from .statements import (
    GRECO,
    BASCO,
    LOADC,
    SHSEC,
    SHEXT,
    LAREA,
    SHAXE,
    CMPEC,
    CMPGM,
    CMPNS,
    CMPOS,
    RMPEC,
    RMPOS,
    RMPNS,
    TEMAT,
    RETYP,
    SRTYP,
    TETYP,
    RELOC,
    SRLOC,
    TELOC,
    LORES,
    XTFIL,
    DESEC,
    TABLE,
    RFILE,
    INCDF,
    DECAS,
    DEPAR,
    FILST,
    HEADL,
    Cases,
    EXECD,
    HEADING,
)

@runtime_checkable
class StatementProtocol(Protocol):
    """Protocol that all statement classes must implement."""

    input: str

# Type alias for all supported statement types (type checkers/IDEs only)
StatementType: TypeAlias = Union[
    GRECO,
    BASCO,
    LOADC,
    SHSEC,
    SHEXT,
    LAREA,
    SHAXE,
    CMPEC,
    CMPGM,
    CMPNS,
    CMPOS,
    RMPEC,
    RMPOS,
    RMPNS,
    RETYP,
    SRTYP,
    TETYP,
    RELOC,
    SRLOC,
    TELOC,
    LORES,
    XTFIL,
    DESEC,
    TABLE,
    RFILE,
    INCDF,
    DECAS,
    DEPAR,
    FILST,
    HEADL,
    Cases,
    EXECD,
    HEADING,
]

class SD_BASE(BaseModel):
    """
    Type stubs for dynamic containers and methods — enables IDE hover docs and auto-completion.
    Runtime containers are created via __getattr__, but these stubs describe their types.
    """

    # ---------------------------
    # Construction and attributes
    # ---------------------------
    def __init__(
        self,
        validation_level: ValidationLevel = ...,
        cross_object_validation: bool = ...,
        **kwargs: Any,
    ) -> None: ...

    validation_level: ValidationLevel
    cross_object_validation: bool
    router: Any
    validator: ValidationManager
    all_items: list[StatementType]

    # -------------
    # Core methods
    # -------------
    @overload
    def add(self, item: StatementType, validation: bool | None = ...) -> None: ...
    @overload
    def add(
        self, item: Sequence[StatementType], validation: bool | None = ...
    ) -> None: ...
    def add(self, item, validation: bool | None = ...) -> None: ...
    def write(self, output_file: str) -> None: ...

    # ------------------------
    # Container attribute stubs
    # ------------------------
    greco: BaseContainer[GRECO]
    """Container for GRECO statements — Generalized Rebar Content statements."""

    basco: BaseContainer[BASCO]
    """Container for BASCO statements — Basic Analysis and Structural Control statements."""

    loadc: BaseContainer[LOADC]
    """Container for LOADC statements — Load Case Control statements."""

    shsec: BaseContainer[SHSEC]
    """Container for SHSEC statements — Shell Section definitions."""

    shaxe: BaseContainer[SHAXE]
    """Container for SHAXE statements — Shell Axis definitions."""
    
    larea: BaseContainer[LAREA]
    """Container for LAREA statements — Load Area definitions."""

    cmpec: BaseContainer[CMPEC]
    """Container for CMPEC statements — Material concrete specifications according to Eurocode."""

    cmpgm: BaseContainer[CMPGM]
    """Container for CMPGM statements — Material properties for composite materials according to MCFT ."""
    
    cmpns: BaseContainer[CMPNS]
    """Container for CMPNS statements — Material properties for non-steel materials according to NS 3473."""
    
    cmpos: BaseContainer[CMPOS]
    """Container for CMPOS statements — Concrete material property sets according to DNV-ST-C502."""
    
    rmpec: BaseContainer[RMPEC]
    """Container for RMPEC statements — Material properties for reinforced steel according to Eurocode."""
    
    rmpos: BaseContainer[RMPOS]
    """Container for RMPOS statements — Rebar material property sets according to DNV-ST-C502."""
    
    rmpns: BaseContainer[RMPNS]     
    """Container for RMPNS statements — Rebar material property sets according to NS 3473."""
    
    retyp: BaseContainer[RETYP]
    """Container for RETYP statements — Rebar Type definitions."""

    tetyp: BaseContainer[TETYP]
    """Container for TETYP statements — Tendon Type definitions."""

    srtyp: BaseContainer[SRTYP]
    """Container for SRTYP statements — Shear Reinforcement Type definitions."""

    temat: BaseContainer[TEMAT]
    """Container for TEMAT statements — Tendon Material definitions."""

    reloc: BaseContainer[RELOC]
    """Container for RELOC statements — Rebar Location definitions."""

    teloc: BaseContainer[TELOC]
    """Container for TELOC statements — Tendon Location definitions."""

    srloc: BaseContainer[SRLOC]
    """Container for SRLOC statements — Shear Reinforcement Location definitions."""

    lores: BaseContainer[LORES]
    """Container for LORES statements — Load Result processing."""

    xtfil: BaseContainer[XTFIL]
    """Container for XTFIL statements — External File operations."""

    desec: BaseContainer[DESEC]
    """Container for DESEC statements — Design Section specifications."""

    table: BaseContainer[TABLE]
    """Container for TABLE statements — Table definitions."""

    rfile: BaseContainer[RFILE]
    """Container for RFILE statements — Result File operations."""

    incdf: BaseContainer[INCDF]
    """Container for INCDF statements — Include Data File operations."""

    decas: BaseContainer[DECAS]
    """Container for DECAS statements — Design Case specifications."""

    depar: BaseContainer[DEPAR]
    """Container for DEPAR statements — Design Parameter definitions."""

    filst: BaseContainer[FILST]
    """Container for FILST statements — File Status information."""

    headl: BaseContainer[HEADL]
    """Container for HEADL statements — Header Line definitions."""

    cases: BaseContainer[Cases]
    """Container for CASES statements — Case definitions."""

    execd: BaseContainer[EXECD]
    """Container for EXECD statements — Execute commands."""

    heading: BaseContainer[HEADING]
    """Container for HEADING statements — Section headings."""
