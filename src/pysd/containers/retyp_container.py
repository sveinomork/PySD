"""
Specialized container for RETYP statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.retyp import RETYP

class RetypContainer(BaseContainer):
    """
    Container for RETYP statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for RETYP statements.
    """
    
    def add_batch(self, items: List['RETYP']) -> None:
        """Add multiple RETYP items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_id(self, id_value: int) -> Optional['RETYP']:
        """Get RETYP by ID."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
    
    def has_id(self, id_value: int) -> bool:
        """Check if RETYP with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[int]:
        """Get all RETYP IDs."""
        return [item.id for item in self.items]
    
    def get_by_material(self, mp_id: int) -> List['RETYP']:
        """Get all RETYP statements with a specific material property ID."""
        return [item for item in self.items if item.mp == mp_id]
    
    def get_materials(self) -> List[int]:
        """Get all unique material property IDs."""
        materials = {item.mp for item in self.items if item.mp is not None}
        return sorted(list(materials))
    
    def get_by_method(self, method: str) -> List['RETYP']:
        """Get RETYP statements by calculation method.
        
        Args:
            method: 'area' for Method 1 (direct area), 'count' for Method 2 (number + diameter)
        """
        if method == 'area':
            return [item for item in self.items if item.ar is not None]
        elif method == 'count':
            return [item for item in self.items if item.nr is not None and item.di is not None]
        else:
            raise ValueError("Method must be 'area' or 'count'")
