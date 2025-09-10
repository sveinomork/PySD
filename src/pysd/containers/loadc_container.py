"""
Specialized container for LOADC statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Any
from .base_container import StandardContainer

if TYPE_CHECKING:
    from ..statements.loadc import LOADC

class LoadcContainer(StandardContainer['LOADC']):
    """
    Container for LOADC statements using StandardContainer for O(1) operations.
    
    Features:
    - O(1) lookups by key (LOADC uses string keys)
    - Consistent interface with other containers
    - Specialized LOADC query methods
    - Container-level validation hooks
    """
    
    def get_by_key(self, key: str) -> Optional['LOADC']:
        """Get LOADC by key - alias for get_by_id()."""
        return self.get_by_id(key)
    
    def has_key(self, key: str) -> bool:
        """Check if LOADC with given key exists - alias for contains()."""
        return self.contains(key)
    
    def get_keys(self) -> List[str]:
        """Get all LOADC keys - legacy alias for get_all_ids()."""
        return [str(identifier) for identifier in self.get_all_ids()]
    
    def get_by_run_number(self, run_number: int) -> List['LOADC']:
        """Get all LOADC statements with a specific run number."""
        return [item for item in self if item.run_number == run_number]
    
    def get_by_olc(self, olc: int) -> Optional['LOADC']:
        """Get LOADC that contains a specific OLC value."""
        for item in self:
            if item.is_olc(olc):
                return item
        return None
    
    def get_by_alc(self, alc: int) -> Optional['LOADC']:
        """Get LOADC that contains a specific ALC value."""
        for item in self:
            if item.is_alc(alc):
                return item
        return None
    
    def validate_container(self, context=None) -> List[Any]:
        """Container-level validation for LOADC-specific rules."""
        issues = []
        
        # Check for OLC uniqueness across all LOADC items
        all_olcs = set()
        for item in self:
            for olc in item.get_olc_list():
                if olc in all_olcs:
                    issues.append({
                        'severity': 'error',
                        'code': 'LOADC_OLC_DUPLICATE',
                        'message': f'Duplicate OLC value {olc} found across LOADC items',
                        'location': f'LoadcContainer.{item.key}'
                    })
                all_olcs.add(olc)
        
        return issues
