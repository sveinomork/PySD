"""
Specialized container for BASCO statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.basco import BASCO

class BascoContainer(BaseContainer):
    """
    Container for BASCO statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for BASCO statements.
    """
    
    def add_batch(self, items: List['BASCO']) -> None:
        """Add multiple BASCO items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_id(self, id_value: int) -> Optional['BASCO']:
        """Get BASCO by ID (override to handle int IDs)."""
        for item in self.items:
            if int(item.id) == id_value:
                return item
        return None
    
    def has_id(self, id_value: int) -> bool:
        """Check if BASCO with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[int]:
        """Get all BASCO IDs as integers."""
        return [int(item.id) for item in self.items]