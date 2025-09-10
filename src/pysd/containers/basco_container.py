"""
Specialized container for BASCO statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Any
from .base_container import StandardContainer

if TYPE_CHECKING:
    from ..statements.basco import BASCO

class BascoContainer(StandardContainer['BASCO']):
    """
    Container for BASCO statements using StandardContainer for O(1) operations.
    
    Features:
    - O(1) lookups by ID
    - Consistent interface with other containers
    - Batch operations with validation
    - Container-level validation hooks
    """
    
    def has_id(self, id_value: int) -> bool:
        """Check if BASCO with given ID exists - alias for contains()."""
        return self.contains(id_value)
    
    def get_ids(self) -> List[int]:
        """Get all BASCO IDs as integers - legacy alias for get_all_ids()."""
        return [int(identifier) for identifier in self.get_all_ids()]
    
    def validate_container(self, context=None) -> List[Any]:
        """Container-level validation for BASCO-specific rules."""
        issues = []
        
        # Example: Check for reasonable number of BASCOs
        if len(self) > 1000:
            issues.append({
                'severity': 'warning',
                'code': 'BASCO_CONTAINER_SIZE',
                'message': f'Container has {len(self)} BASCO items, consider optimization',
                'location': 'BascoContainer'
            })
        
        return issues
