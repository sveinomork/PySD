from typing import List, Protocol, runtime_checkable, Self, Any, Union, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, model_validator
from abc import ABC, abstractmethod

# Type alias for identifier types
IdType = Union[int, str]
T = TypeVar('T')

@runtime_checkable
class Identifiable(Protocol):
    """Protocol for objects with consistent identifier access."""
    
    @property
    def identifier(self) -> IdType:
        """Get the unique identifier for this object."""
        ...

@runtime_checkable
class HasID(Protocol):
    """Legacy protocol for objects that have an ID field."""
    id: Union[int, str]  # Support both int and string IDs


class StandardContainer(BaseModel):
    """
    Standardized container with consistent interface and O(1) lookups.
    
    Features:
    - O(1) lookups via internal dictionary
    - Insertion order preservation
    - Consistent identifier protocol
    - Batch operations
    - Container-level validation hooks
    
    Examples:
        container = StandardContainer[BASCO]()
        container.add(basco_item)
        found = container.get_by_id(101)
    """
    items_dict: dict[IdType, T] = Field(default_factory=dict, exclude=True, description="Internal dictionary for O(1) lookups")
    insertion_order: List[IdType] = Field(default_factory=list, exclude=True, description="Order of item insertion")
    
    def add(self, item: Any) -> None:
        """Add an item to the container with duplicate checking."""
        if not isinstance(item, Identifiable):
            raise TypeError(f"Item must implement Identifiable protocol, got {type(item)}")
        
        identifier = item.identifier
        if identifier in self.items_dict:
            raise ValueError(f"Item with identifier {identifier} already exists")
        
        self.items_dict[identifier] = item
        self.insertion_order.append(identifier)
    
    def add_batch(self, items: List[Any]) -> None:
        """Add multiple items efficiently with batch validation."""
        # Pre-validate all items to avoid partial additions
        identifiers = []
        for item in items:
            if not isinstance(item, Identifiable):
                raise TypeError(f"Item must implement Identifiable protocol, got {type(item)}")
            
            identifier = item.identifier
            if identifier in self.items_dict:
                raise ValueError(f"Item with identifier {identifier} already exists")
            
            # Check for duplicates within the batch itself
            if identifier in identifiers:
                raise ValueError(f"Duplicate identifier {identifier} in batch")
            
            identifiers.append(identifier)
        
        # All validation passed, now add all items
        for item in items:
            identifier = item.identifier
            self.items_dict[identifier] = item
            self.insertion_order.append(identifier)
    
    def get_by_id(self, identifier: IdType) -> Optional[Any]:
        """Get an item by identifier - O(1) lookup."""
        return self.items_dict.get(identifier)
    
    def contains(self, identifier: IdType) -> bool:
        """Check if container contains an item with the given identifier - O(1)."""
        return identifier in self.items_dict
    
    def get_all_ids(self) -> List[IdType]:
        """Get all identifiers in insertion order."""
        return self.insertion_order.copy()
    
    def remove(self, identifier: IdType) -> Optional[Any]:
        """Remove and return item by identifier."""
        item = self.items_dict.pop(identifier, None)
        if item is not None:
            self.insertion_order.remove(identifier)
        return item
    
    def update(self, item: Any) -> None:
        """Update an existing item (must have same identifier)."""
        if not isinstance(item, Identifiable):
            raise TypeError(f"Item must implement Identifiable protocol")
        
        identifier = item.identifier
        if identifier not in self.items_dict:
            raise KeyError(f"Item with identifier {identifier} does not exist")
        
        self.items_dict[identifier] = item
    
    def validate_container(self, context=None) -> List[Any]:
        """Hook for container-level validation rules."""
        # Override in subclasses for specific validation
        return []
    
    def __len__(self) -> int:
        """Return the number of items in the container."""
        return len(self.items_dict)
    
    def __iter__(self):
        """Iterate over items in insertion order."""
        for identifier in self.insertion_order:
            yield self.items_dict[identifier]
    
    def __getitem__(self, index: int) -> Any:
        """Get item by insertion index."""
        identifier = self.insertion_order[index]
        return self.items_dict[identifier]
    
    def __contains__(self, identifier: IdType) -> bool:
        """Support 'in' operator."""
        return identifier in self.items_dict
    
    @property
    def items(self) -> List[Any]:
        """Compatibility property for accessing items as a list."""
        return [self.items_dict[identifier] for identifier in self.insertion_order]

class BaseContainer(BaseModel):
    """
    Legacy base container for backward compatibility.
    
    This container ensures that all items have unique IDs and provides
    essential functionality for statement collections.
    
    DEPRECATED: Use StandardContainer for new implementations.
    """
    items: List[Any] = Field(default_factory=list, description="List of items with unique IDs")
    
    @model_validator(mode='after')
    def validate_unique_ids(self) -> Self:
        """Ensure all item IDs are unique."""
        seen_ids: set[Union[int, str]] = set()
        for item in self.items:
            # Support both 'id' and 'key' fields for identification
            item_id = getattr(item, 'id', None) or getattr(item, 'key', None)
            if item_id and item_id in seen_ids:
                raise ValueError(f"Duplicate ID found: {item_id}")
            if item_id:
                seen_ids.add(item_id)
        return self
    
    def add(self, item: Any) -> None:
        """Add an item to the container, checking for duplicate IDs."""
        item_id = getattr(item, 'id', None) or getattr(item, 'key', None)
        for existing in self.items:
            existing_id = getattr(existing, 'id', None) or getattr(existing, 'key', None)
            if existing_id == item_id:
                raise ValueError(f"Item with ID {item_id} already exists")
        self.items.append(item)
    
    def get_by_id(self, id_value: Union[int, str]) -> Any:
        """Get an item by ID - O(n) linear search."""
        for item in self.items:
            item_id = getattr(item, 'id', None) or getattr(item, 'key', None)
            if item_id == id_value:
                return item
        return None
    
    def get_ids(self) -> List[Union[int, str]]:
        """Get a list of all IDs in the container."""
        ids = []
        for item in self.items:
            item_id = getattr(item, 'id', None) or getattr(item, 'key', None)
            if item_id:
                ids.append(item_id)
        return ids
    
    def get_all_ids(self) -> List[Union[int, str]]:
        """Alias for get_ids() for interface consistency."""
        return self.get_ids()
    
    def contains(self, id_value: Union[int, str]) -> bool:
        """Check if container contains an item with the given ID."""
        return self.get_by_id(id_value) is not None
    
    def __len__(self) -> int:
        """Return the number of items in the container."""
        return len(self.items)
    
    def __iter__(self):
        """Allow iteration over items in the container."""
        return iter(self.items)
    
    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        return self.items[index]