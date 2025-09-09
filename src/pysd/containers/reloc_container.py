"""
Specialized container for RELOC statements.
"""

from __future__ import annotations
from typing import List, Optional, Union, Tuple, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.reloc import RELOC

class RelocContainer(BaseContainer):
    """
    Container for RELOC statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for RELOC statements.
    """
    
    def add_batch(self, items: List['RELOC']) -> None:
        """Add multiple RELOC items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_id(self, id_value: str) -> Optional['RELOC']:
        """Get RELOC by ID."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
    
    def has_id(self, id_value: str) -> bool:
        """Check if RELOC with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[str]:
        """Get all RELOC IDs."""
        return [item.id for item in self.items]
    
    def get_by_rebar_type(self, rt_id: int) -> List['RELOC']:
        """Get all RELOC statements referencing a specific rebar type."""
        result = []
        for item in self.items:
            if isinstance(item.rt, tuple):
                # Range of rebar types
                if rt_id >= item.rt[0] and rt_id <= item.rt[1]:
                    result.append(item)
            else:
                # Single rebar type
                if item.rt == rt_id:
                    result.append(item)
        return result
    
    def get_referenced_rebar_types(self) -> List[int]:
        """Get all unique rebar type IDs referenced by RELOC statements."""
        rebar_types = set()
        for item in self.items:
            if isinstance(item.rt, tuple):
                # Add all IDs in range
                for rt_id in range(item.rt[0], item.rt[1] + 1):
                    rebar_types.add(rt_id)
            else:
                rebar_types.add(item.rt)
        return sorted(list(rebar_types))
    
    def get_by_face(self, face: int) -> List['RELOC']:
        """Get all RELOC statements for a specific shell face.
        
        Args:
            face: 0=center, 1=face1, 2=face2
        """
        return [item for item in self.items if item.fa == face]
    
    def get_by_part(self, part_name: str) -> List['RELOC']:
        """Get all RELOC statements for a specific part."""
        return [item for item in self.items if item.pa == part_name]
    
    def get_by_location_area(self, la_id: int) -> List['RELOC']:
        """Get all RELOC statements for a specific location area."""
        return [item for item in self.items if item.la == la_id]
