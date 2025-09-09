"""
Specialized container for RMPEC statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.rmpec import RMPEC

class RmpecContainer(BaseContainer):
    """
    Container for RMPEC statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for RMPEC statements.
    """
    
    def add_batch(self, items: List['RMPEC']) -> None:
        """Add multiple RMPEC items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_id(self, id_value: int) -> Optional['RMPEC']:
        """Get RMPEC by ID."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
    
    def has_id(self, id_value: int) -> bool:
        """Check if RMPEC with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[int]:
        """Get all RMPEC IDs."""
        return [item.id for item in self.items]
    
    def get_by_grade(self, grade: float) -> List['RMPEC']:
        """Get all RMPEC statements with a specific steel grade."""
        return [item for item in self.items if item.gr == grade]
    
    def get_grades(self) -> List[float]:
        """Get all unique steel grades."""
        return list(set(item.gr for item in self.items if item.gr is not None))