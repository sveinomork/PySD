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
        Build routing registry from ContainerFactory - eliminates duplication!
        
        Adding a new statement now only requires updating ContainerFactory.
        No more maintaining two separate registries!
        """
        from .container_factory import ContainerFactory
        
        # Get routing registry from ContainerFactory unified registry
        return ContainerFactory.get_routing_registry()
    
    def route_item(self, item: 'StatementType') -> None:
        """
        Route a single item to its appropriate container.
        
        Much simpler now - ALL statements go to containers!
        Replaces the 50+ line _route_item method from SD_BASE.
        """
        item_type = type(item)
        container_name = self._routing_registry.get(item_type)
        
        if container_name is None:
            raise TypeError(f"Unsupported statement type: {item_type.__name__}")
        
        # Simple container routing for ALL statements - no special cases!
        container = getattr(self.model, container_name)
        container.add(item)
    
    def route_batch(self, items: List['StatementType']) -> None:
        """
        Route multiple items with optimized batch processing.
        
        Much simpler now - ALL statements go to containers!
        Replaces the 40+ line _add_batch method from SD_BASE.
        """
        # Group items by type for batch processing
        grouped_items = defaultdict(list)
        for item in items:
            item_type = type(item)
            grouped_items[item_type].append(item)
        
        # Process each group - simple container routing for all
        for item_type, type_items in grouped_items.items():
            container_name = self._routing_registry.get(item_type)
            
            if container_name is None:
                raise TypeError(f"Unsupported statement type: {item_type.__name__}")
            
            # Use container's batch method if available, otherwise individual adds
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