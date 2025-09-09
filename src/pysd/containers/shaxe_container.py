"""
Specialized container for SHAXE statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.shaxe import SHAXE

class ShaxeContainer(BaseContainer):
    """
    Container for SHAXE statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for SHAXE statements.
    """
    
    def add_batch(self, items: List['SHAXE']) -> None:
        """Add multiple SHAXE items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_key(self, key: str) -> Optional['SHAXE']:
        """Get SHAXE by key."""
        for item in self.items:
            if getattr(item, 'key', None) == key:
                return item
        return None
    
    def has_key(self, key: str) -> bool:
        """Check if SHAXE with given key exists."""
        return self.get_by_key(key) is not None
    
    def get_by_pa(self, pa: str) -> List['SHAXE']:
        """Get all SHAXE statements for a given part name."""
        return [item for item in self.items if item.pa == pa]
    
    def get_keys(self) -> List[str]:
        """Get all SHAXE keys."""
        return [getattr(item, 'key', '') for item in self.items if hasattr(item, 'key')]
    
    def get_part_names(self) -> List[str]:
        """Get all unique part names (PA values)."""
        return list(set(item.pa for item in self.items))
    
    def has_part(self, pa: str) -> bool:
        """Check if any SHAXE exists for the given part name."""
        return any(item.pa == pa for item in self.items)