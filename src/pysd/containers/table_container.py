"""
Specialized container for TABLE statements.
"""

from __future__ import annotations
from typing import List, Optional, Literal, Union, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.table import TABLE, TabType, UrType

class TableContainer(BaseContainer):
    """
    Container for TABLE statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for TABLE statements.
    """
    
    def add_batch(self, items: List['TABLE']) -> None:
        """Add multiple TABLE items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_tab_type(self, tab_type: 'TabType') -> List['TABLE']:
        """Get all TABLE statements for a specific TAB type."""
        return [item for item in self.items if item.tab == tab_type]
    
    def get_by_ur_type(self, ur_type: 'UrType') -> List['TABLE']:
        """Get all TABLE statements for a specific UR type."""
        return [item for item in self.items if item.ur == ur_type]
    
    def get_by_part(self, pa: str) -> List['TABLE']:
        """Get all TABLE statements for a specific structural part."""
        return [item for item in self.items if item.pa == pa]
    
    def get_tab_statements(self) -> List['TABLE']:
        """Get all TAB mode statements."""
        return [item for item in self.items if item.tab is not None]
    
    def get_ur_statements(self) -> List['TABLE']:
        """Get all UR mode statements."""
        return [item for item in self.items if item.ur is not None]
    
    def get_by_limit_state(self, ls: Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']) -> List['TABLE']:
        """Get all TABLE statements for a specific limit state."""
        return [item for item in self.items if item.ls == ls]
    
    def get_with_file_output(self) -> List['TABLE']:
        """Get all TABLE statements with file output redirection."""
        return [item for item in self.items if item.of is not None or item.nf is not None]
    
    def get_with_threshold(self, min_threshold: Optional[float] = None) -> List['TABLE']:
        """Get all UR statements with threshold values, optionally filtered by minimum."""
        tables = [item for item in self.items if item.tv is not None]
        if min_threshold is not None:
            tables = [item for item in tables if item.tv >= min_threshold]
        return tables
    
    def get_section_filtered(self) -> List['TABLE']:
        """Get all TABLE statements with section filtering (fs or hs)."""
        return [item for item in self.items if item.fs is not None or item.hs is not None]
    
    def get_load_case_filtered(self) -> List['TABLE']:
        """Get all TABLE statements with load case filtering."""
        return [item for item in self.items 
                if any([item.ilc, item.olc, item.elc, item.bas, item.pha])]
    
    def get_unique_tab_types(self) -> List['TabType']:
        """Get all unique TAB types used."""
        tab_types = {item.tab for item in self.items if item.tab is not None}
        return sorted(list(tab_types))
    
    def get_unique_ur_types(self) -> List['UrType']:
        """Get all unique UR types used."""
        ur_types = {item.ur for item in self.items if item.ur is not None}
        return sorted(list(ur_types))
    
    def get_unique_parts(self) -> List[str]:
        """Get all unique structural parts referenced."""
        parts = {item.pa for item in self.items if item.pa is not None}
        return sorted(list(parts))
    
    def has_output_redirection(self) -> bool:
        """Check if any TABLE statement uses output redirection."""
        return any(item.of is not None or item.nf is not None for item in self.items)
    
    def get_max_threshold(self) -> Optional[float]:
        """Get the maximum threshold value used in UR statements."""
        thresholds = [item.tv for item in self.items if item.tv is not None]
        return max(thresholds) if thresholds else None