"""
Specialized container for GRECO statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.greco import GRECO

class GrecoContainer(BaseContainer):
    """
    Container for GRECO statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for GRECO statements.
    """
    
    def add_batch(self, items: List['GRECO']) -> None:
        """Add multiple GRECO items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_id(self, id_value: str) -> Optional['GRECO']:
        """Get GRECO by ID (override to handle string IDs)."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
    
    def has_id(self, id_value: str) -> bool:
        """Check if GRECO with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[str]:
        """Get all GRECO IDs."""
        return [item.id for item in self.items]