"""
Specialized container for XTFIL statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer

if TYPE_CHECKING:
    from ..statements.xtfil import XTFIL

class XtfilContainer(BaseContainer):
    """
    Container for XTFIL statements.
    
    Note: All validation is now handled by the rule system.
    This container provides specialized accessor methods for XTFIL statements.
    """
    
    def add_batch(self, items: List['XTFIL']) -> None:
        """Add multiple XTFIL items with batch validation."""
        for item in items:
            self.add(item)
    
    def get_by_filename(self, filename: str) -> Optional['XTFIL']:
        """Get XTFIL by filename."""
        for item in self.items:
            if item.fn == filename:
                return item
        return None
    
    def get_by_part(self, part_name: str) -> List['XTFIL']:
        """Get all XTFIL statements for a specific structural part."""
        return [item for item in self.items if item.pa == part_name]
    
    def get_by_key(self, key: str) -> Optional['XTFIL']:
        """Get XTFIL by its generated key."""
        for item in self.items:
            if hasattr(item, 'key') and item.key == key:
                return item
        return None
    
    def get_filenames(self) -> List[str]:
        """Get all unique filenames."""
        return list({item.fn for item in self.items})
    
    def get_parts(self) -> List[str]:
        """Get all unique structural part names."""
        return list({item.pa for item in self.items})
    
    def get_by_plot_item(self, plot_item: str) -> List['XTFIL']:
        """Get all XTFIL statements that include a specific plot item."""
        return [item for item in self.items if plot_item in item.plot_items]
    
    def get_peak_value_plots(self) -> List['XTFIL']:
        """Get all XTFIL statements with peak value only flag."""
        return [item for item in self.items if item.peak_value_only]
    
    def has_filename(self, filename: str) -> bool:
        """Check if a filename exists in the container."""
        return self.get_by_filename(filename) is not None
    
    def has_part(self, part_name: str) -> bool:
        """Check if a structural part has XTFIL definitions."""
        return len(self.get_by_part(part_name)) > 0