"""
StatementRouter - Simple routing logic extracted from SD_BASE.

This module handles all statement routing using a registry pattern,
eliminating the massive if/elif chains from sdmodel.py.

Focus: Make adding new statements require only 1 line change.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Type
from collections import defaultdict

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE, StatementType

class StatementRouter:
    """
    Simple statement router using registry pattern.
    
    Goal: Eliminate the 50+ line _route_item() and 40+ line _add_batch() 
    methods from SD_BASE and replace with a single registry.
    """
    
    def __init__(self, model: 'SD_BASE'):
        self.model = model
        self._routing_registry = self._build_routing_registry()
    
    def _build_routing_registry(self) -> Dict[Type, str]:
        """
        Build the routing registry - single source of truth for all statement routing.
        
        Adding a new statement type only requires adding one line here!
        """
        # Import statements here to avoid circular imports
        # Use relative imports to match the test import pattern
        from ..statements.greco import GRECO
        from ..statements.basco import BASCO
        from ..statements.loadc import LOADC
        from ..statements.shsec import SHSEC
        from ..statements.shaxe import SHAXE
        from ..statements.cmpec import CMPEC
        from ..statements.rmpec import RMPEC
        from ..statements.retyp import RETYP
        from ..statements.reloc import RELOC
        from ..statements.lores import LORES
        from ..statements.xtfil import XTFIL
        from ..statements.desec import DESEC
        from ..statements.table import TABLE
        from ..statements.rfile import RFILE
        from ..statements.incdf import INCDF
        from ..statements.decas import DECAS
        from ..statements.depar import DEPAR
        from ..statements.filst import FILST
        from ..statements.headl import HEADL
        from ..statements.cases import Cases
        from ..statements.statement_heading import HEADING
        from ..statements.execd import EXECD
        
        # Single source of truth for all routing
        return {
            # Container-based routing
            GRECO: 'greco',
            BASCO: 'basco', 
            LOADC: 'loadc',
            SHSEC: 'shsec',
            SHAXE: 'shaxe',
            CMPEC: 'cmpec',
            RMPEC: 'rmpec',
            RETYP: 'retyp',
            RELOC: 'reloc',
            LORES: 'lores',
            XTFIL: 'xtfil',
            DESEC: 'desec',
            TABLE: 'table',
            RFILE: 'rfile',
            INCDF: 'incdf',
            DECAS: 'decas',
            DEPAR: 'depar',
            FILST: 'filst',
            HEADL: 'headl',
            Cases: 'cases',
            
            # List-based routing (special handling)
            HEADING: '_heading_list',
            EXECD: '_execd_list',
        }
    
    def route_item(self, item: 'StatementType') -> None:
        """
        Route a single item to its appropriate container/collection.
        
        Replaces the 50+ line _route_item method from SD_BASE.
        """
        item_type = type(item)
        container_name = self._routing_registry.get(item_type)
        
        if container_name is None:
            raise TypeError(f"Unsupported statement type: {item_type.__name__}")
        
        # Handle special cases for list-based storage
        if container_name.startswith('_'):
            self._route_to_list(item, container_name)
        else:
            # Standard container routing
            self._route_to_container(item, container_name)
    
    def _route_to_container(self, item: 'StatementType', container_name: str) -> None:
        """Route item to a BaseContainer."""
        container = getattr(self.model, container_name)
        container.add(item)
    
    def _route_to_list(self, item: 'StatementType', list_name: str) -> None:
        """Route item to a list (for HEADING and EXECD)."""
        # Remove the '_' prefix and '_list' suffix to get the actual field name
        field_name = list_name[1:-5]  # '_heading_list' -> 'heading'
        
        # Special handling for EXECD (remove existing ones)
        if field_name == 'execd':
            # Remove any existing EXECD items from all_items
            from ..statements.execd import EXECD
            self.model.all_items = [x for x in self.model.all_items if not isinstance(x, EXECD)]
        
        # Add to the appropriate list
        target_list = getattr(self.model, field_name)
        target_list.append(item)
    
    def route_batch(self, items: List['StatementType']) -> None:
        """
        Route multiple items with optimized batch processing.
        
        Replaces the 40+ line _add_batch method from SD_BASE.
        """
        # Group items by type for batch processing
        grouped_items = defaultdict(list)
        for item in items:
            item_type = type(item)
            grouped_items[item_type].append(item)
        
        # Process each group
        for item_type, type_items in grouped_items.items():
            container_name = self._routing_registry.get(item_type)
            
            if container_name is None:
                raise TypeError(f"Unsupported statement type: {item_type.__name__}")
            
            # Handle special cases
            if container_name.startswith('_'):
                # For list-based items, route individually (no batch support)
                for item in type_items:
                    self._route_to_list(item, container_name)
            else:
                # Use container's batch method if available
                container = getattr(self.model, container_name)
                if hasattr(container, 'add_batch'):
                    container.add_batch(type_items)
                else:
                    # Fallback to individual adds
                    for item in type_items:
                        container.add(item)
    
    def get_supported_types(self) -> List[Type]:
        """Get list of all supported statement types."""
        return list(self._routing_registry.keys())
    
    def is_supported_type(self, item_type: Type) -> bool:
        """Check if a statement type is supported."""
        return item_type in self._routing_registry
    
    def get_container_name(self, item_type: Type) -> str:
        """Get container name for a statement type."""
        return self._routing_registry.get(item_type, "")
    
    @classmethod
    def register_statement_type(cls, statement_type: Type, container_name: str) -> None:
        """
        Register a new statement type (for future extensibility).
        
        This would allow registering new types without modifying this file.
        """
        # This is a placeholder for future enhancement
        # Currently, types must be added to _build_routing_registry()
        pass