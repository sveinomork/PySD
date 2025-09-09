"""
Specialized container for LOADC statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.loadc import LOADC

class LoadcContainer(BaseContainer):
    """
    Container for LOADC statements.
    
    Note: LOADC uses 'key' instead of 'id' for identification.
    All validation is now handled by the rule system.
    This container provides specialized accessor methods for LOADC statements.
    """
    
    def add_batch(self, items: List['LOADC']) -> None:
        """Add multiple LOADC items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_key(self, key: str) -> Optional['LOADC']:
        """Get LOADC by key (LOADC uses string keys, not IDs)."""
        for item in self.items:
            if item.key == key:
                return item
        return None
    
    def has_key(self, key: str) -> bool:
        """Check if LOADC with given key exists."""
        return self.get_by_key(key) is not None
    
    def get_keys(self) -> List[str]:
        """Get all LOADC keys."""
        return [item.key for item in self.items]
    
    def get_by_run_number(self, run_number: int) -> List['LOADC']:
        """Get all LOADC statements with a specific run number."""
        return [item for item in self.items if item.run_number == run_number]
    
    def get_by_olc(self, olc: int) -> Optional['LOADC']:
        """Get LOADC that contains a specific OLC value."""
        for item in self.items:
            if item.is_olc(olc):
                return item
        return None
    
    def get_by_alc(self, alc: int) -> Optional['LOADC']:
        """Get LOADC that contains a specific ALC value."""
        for item in self.items:
            if item.is_alc(alc):
                return item
        return None