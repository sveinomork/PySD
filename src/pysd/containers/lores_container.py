"""
Specialized container for LORES statements.
"""

from __future__ import annotations
from typing import List, Optional, Literal, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.lores import LORES

class LoresContainer(BaseContainer):
    """
    Container for LORES statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for LORES statements.
    """
    
    def add_batch(self, items: List['LORES']) -> None:
        """Add multiple LORES items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_lc(self, lc: int) -> List['LORES']:
        """Get all LORES statements for a specific load case."""
        return [item for item in self.items if item.lc == lc]
    
    def get_by_part(self, part: Literal['REAL', 'IMAG']) -> List['LORES']:
        """Get all LORES statements for a specific part (REAL or IMAG)."""
        return [item for item in self.items if item.part == part]
    
    def get_manual_definitions(self) -> List['LORES']:
        """Get all manually defined LORES statements (with lc and part)."""
        return [item for item in self.items if item.lc is not None and item.part is not None]
    
    def get_sin_statements(self) -> List['LORES']:
        """Get all SIN file generation statements."""
        return [item for item in self.items if item.sin]
    
    def get_print_statements(self) -> List['LORES']:
        """Get all print/list statements (PRI=OLC or PRI=ALC)."""
        return [item for item in self.items if item.pri_olc or item.pri_alc]
    
    def get_load_cases(self) -> List[int]:
        """Get all unique load case numbers."""
        load_cases = {item.lc for item in self.items if item.lc is not None}
        return sorted(list(load_cases))
    
    def has_sin_generation(self) -> bool:
        """Check if any LORES statement uses SIN file generation."""
        return any(item.sin for item in self.items)
    
    def has_print_commands(self) -> bool:
        """Check if any LORES statement has print commands."""
        return any(item.pri_olc or item.pri_alc for item in self.items)