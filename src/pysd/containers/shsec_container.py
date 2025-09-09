"""
Specialized container for SHSEC statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.shsec import SHSEC

class ShsecContainer(BaseContainer):
    """
    Container for SHSEC statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for SHSEC statements.
    """
    
    def add_batch(self, items: List['SHSEC']) -> None:
        """Add multiple SHSEC items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_key(self, key: str) -> Optional['SHSEC']:
        """Get SHSEC by key (override to handle string keys)."""
        for item in self.items:
            if getattr(item, 'key', None) == key:
                return item
        return None
    
    def has_key(self, key: str) -> bool:
        """Check if SHSEC with given key exists."""
        return self.get_by_key(key) is not None
    
    def get_by_pa(self, pa: str) -> List['SHSEC']:
        """Get all SHSEC statements for a given part name."""
        return [item for item in self.items if item.pa == pa]
    
    def get_keys(self) -> List[str]:
        """Get all SHSEC keys."""
        return [getattr(item, 'key', '') for item in self.items if hasattr(item, 'key')]
    
    def get_part_names(self) -> List[str]:
        """Get all unique part names (PA values)."""
        return list(set(item.pa for item in self.items))