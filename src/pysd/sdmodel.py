from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import contextmanager
from typing import List, Union, Protocol, runtime_checkable, Sequence, Optional

# Import all statement types for runtime use
from .statements.rfile import RFILE
from .statements.shaxe import SHAXE
from .statements.desec import DESEC
from. statements.cmpec import CMPEC
from .statements.loadc import LOADC
from .statements.lores import LORES
from .statements.basco import BASCO
from .statements.greco import GRECO
from .statements.filst import FILST
from .statements.retyp import RETYP
from. statements.reloc import RELOC
from .statements.decas import DECAS
from .statements.table import TABLE
from .statements.incdf import INCDF
from .statements.execd import EXECD
from .statements.shsec import SHSEC
from .statements.rmpec import RMPEC
from .statements.xtfil import XTFIL
from .statements.headl import HEADL
from .statements.depar import DEPAR


# Define a protocol that all statement classes implement
@runtime_checkable
class StatementProtocol(Protocol):
    """Protocol that all statement classes must implement."""
    input: str  # All statements have an input string

# Type alias for all supported statement types using the protocol
StatementType = Union[
    RFILE, SHAXE, DESEC, CMPEC, LOADC, LORES, BASCO, GRECO, 
    FILST, RETYP, RELOC, DECAS, TABLE, INCDF, EXECD, SHSEC, 
    RMPEC, XTFIL, HEADL
]



@dataclass
class SD_BASE():
    # Maintain order of all items
    _all_items: List[StatementType] = field(default_factory=list)  # type: ignore[misc]
   
    # Collections for type-specific access  
    rfile: List[RFILE] = field(default_factory=list)  # type: ignore[misc]
    incdf: List[INCDF] = field(default_factory=list)  # type: ignore[misc]
    headl: List[HEADL] = field(default_factory=list)  # type: ignore[misc]
    shaxe: dict[str, SHAXE] = field(default_factory=dict)  # type: ignore[misc] # key is PA_FS_HS
    shsec: dict[str, SHSEC] = field(default_factory=dict)  # type: ignore[misc] # key is based on pa and sections
    xtfil: dict[str, XTFIL] = field(default_factory=dict)  # type: ignore[misc] # key is FN_PA_FS_HS
  
    filst: List[FILST] = field(default_factory=list)  # type: ignore[misc]
    desec: dict[str, DESEC] = field(default_factory=dict)  # type: ignore[misc]
    greco: dict[str, GRECO] = field(default_factory=dict)  # type: ignore[misc]
    loadc: dict[str, LOADC] = field(default_factory=dict)  # type: ignore[misc] # key is string key
    lores: List[LORES] = field(default_factory=list)  # type: ignore[misc]
    table: List[TABLE] = field(default_factory=list)  # type: ignore[misc]
    execd: List[EXECD] = field(default_factory=list)  # type: ignore[misc]
    decas: List[DECAS] = field(default_factory=list)  # type: ignore[misc] # DECAS objects are uniquely identified by their input
    cmpec: dict[int, CMPEC] = field(default_factory=dict)  # type: ignore[misc] # key is numeric id
    rmpec: dict[int, RMPEC] = field(default_factory=dict)  # type: ignore[misc] # key is numeric id
    basco: dict[int, BASCO] = field(default_factory=dict)  # type: ignore[misc] # key is numeric id
    retyp: dict[int, RETYP] = field(default_factory=dict)  # type: ignore[misc] # key is numeric id
   
    reloc: dict[str, RELOC] = field(default_factory=dict)  # type: ignore[misc] # key is string id
    depar: Optional[DEPAR] = None  # Global design parameters - single instance
    


    def add(self, item: Union[StatementType, Sequence[StatementType]]) -> None:
        """
        Adds a model component or a list of components to the appropriate collection.

        If 'item' is a list, this method will be called for each element in the list.

        Components are stored both in type-specific collections and in a master list
        that maintains the order in which they were added.

        Args:
            item: The component to add, or a list of components.
        """
        if isinstance(item, list):
            for sub_item in item:
                self.add(sub_item)
            return

        # Add to type-specific collection
        if isinstance(item, RFILE):
            self.rfile.append(item)
        elif isinstance(item, HEADL):
            self.headl.append(item)
        elif isinstance(item, FILST):
            self.filst.append(item)
        elif isinstance(item, SHSEC):
            self.shsec[item.input] = item
        elif isinstance(item, SHAXE):
            self.shaxe[item.key] = item
        elif isinstance(item, XTFIL):
            self.xtfil[item.key] = item
        elif isinstance(item, DESEC):
            self.desec[item.pa] = item
        elif isinstance(item, GRECO):
            if item.id is not None:
                self.greco[item.id] = item
            else:
                raise ValueError("GRECO item must have a non-None id to be stored in SD_BASE")
        elif isinstance(item, LOADC):
            self.loadc[item.key] = item
        elif isinstance(item, LORES):
            self.lores.append(item)
        elif isinstance(item, DECAS):
            self.decas.append(item)
        elif isinstance(item, TABLE):
            self.table.append(item)
        elif isinstance(item, INCDF):
            self.incdf.append(item)
        elif isinstance(item, EXECD):
            self.execd.append(item)
        elif isinstance(item, BASCO):
            self.basco[item.id] = item
        elif isinstance(item, RETYP):
            self.retyp[item.id] = item
        elif isinstance(item, RELOC):
            self.reloc[item.id] = item
        elif isinstance(item, CMPEC):
            if item.id is not None:
                self.cmpec[item.id] = item
            else:
                raise ValueError("CMPEC item must have a non-None id to be stored in SD_BASE")
        elif isinstance(item, RMPEC):  # type: ignore[misc]
            if item.id is not None:
                self.rmpec[item.id] = item
            else:
                raise ValueError("RMPEC item must have a non-None id to be stored in SD_BASE")
        
        
        else:  
            raise TypeError(f"Unsupported type for add(): {type(item).__name__}")
        
        # Add to the master list to maintain order
        # Handle EXECD specially - always add it at the end
        if isinstance(item, EXECD):
            # Remove any existing EXECD items
            self._all_items = [x for x in self._all_items if not isinstance(x, EXECD)]
        
        # Add the item to the master list
        self._all_items.append(item)
    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str):
        """
        A context manager to create and write an SD_BASE model to a file.

        Yields an SD_BASE instance to be populated. Upon exiting the
        context, the contents are written to the specified file.

        Usage:
            with SD_BASE.create_writer("output.dat") as sd:
                # For dictionary-based components (using keys)
                shaxe_obj = SHAXE(pa="part1", fs=(1,10))
                sd.add(shaxe_obj)  # Added using its generated key
                
                # For list-based components
                sd.add(FILST(...))  # Appended to list
                
                # For components with numeric ids
                basco_obj = BASCO(id=1, ...)
                sd.add(basco_obj)  # Added using its id
        """
        sd_model = cls()
        try:
            yield sd_model
        finally:
            with open(output_file, "w", encoding="utf-8") as f:
                # Write all components in the order they were added
                # EXECD statements are automatically handled at the end
                for item in sd_model._all_items:
                    f.write(item.input + "\n")
              


    
