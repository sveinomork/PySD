"""
Specialized container for DESEC statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.desec import DESEC

class DesecContainer(BaseContainer):
    """
    Container for DESEC statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for DESEC statements.
    """
    
    def add_batch(self, items: List['DESEC']) -> None:
        """Add multiple DESEC items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_part(self, part_name: str) -> List['DESEC']:
        """Get all DESEC statements for a specific structural part."""
        return [item for item in self.items if item.pa == part_name]
    
    def get_parts(self) -> List[str]:
        """Get all unique structural part names."""
        return list({item.pa for item in self.items})
    
    def has_part(self, part_name: str) -> bool:
        """Check if a structural part has DESEC definitions."""
        return len(self.get_by_part(part_name)) > 0
    
    def get_with_thickness(self) -> List['DESEC']:
        """Get all DESEC statements with non-zero thickness."""
        return [item for item in self.items if item.th != 0.0]
    
    def get_with_coordinates(self) -> List['DESEC']:
        """Get all DESEC statements with non-zero coordinates."""
        return [item for item in self.items 
                if item.x != 0.0 or item.y != 0.0 or item.z != 0.0]
    
    def get_with_gradients(self) -> List['DESEC']:
        """Get all DESEC statements with thickness gradients."""
        return [item for item in self.items 
                if item.t11 != 0.0 or item.t12 != 0.0 or item.t21 != 0.0 or item.t22 != 0.0]
    
    def get_by_section_range(self, fs_range: tuple = None, hs_range: tuple = None) -> List['DESEC']:
        """Get DESEC statements by section range criteria."""
        result = []
        for item in self.items:
            if fs_range and item.fs and isinstance(item.fs, tuple):
                if not (fs_range[0] <= item.fs[0] and item.fs[1] <= fs_range[1]):
                    continue
            if hs_range and item.hs and isinstance(item.hs, tuple):
                if not (hs_range[0] <= item.hs[0] and item.hs[1] <= hs_range[1]):
                    continue
            result.append(item)
        return result