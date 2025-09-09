from typing import List, Protocol, runtime_checkable, Self, Any, Union
from pydantic import BaseModel, Field, model_validator


@runtime_checkable
class HasID(Protocol):
    """Protocol for objects that have an ID field."""
    id: Union[int, str]  # Support both int and string IDs


class BaseContainer(BaseModel):
    """
    Base container for statement types with unique ID validation.
    
    This container ensures that all items have unique IDs and provides
    essential functionality for statement collections.
    
    Examples:
        # For BASCO statements
        basco_container = BascoContainer(items=[basco1, basco2])

        # For GRECO statements  
        greco_container = GrecoContainer(items=[greco1, greco2])
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
        """Get an item by ID."""
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
    
    def __len__(self) -> int:
        """Return the number of items in the container."""
        return len(self.items)
    
    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        return self.items[index]