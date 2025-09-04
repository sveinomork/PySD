from typing import TypeVar, Generic, List, Protocol, runtime_checkable, Self, Any, Union
from pydantic import BaseModel, Field, model_validator


@runtime_checkable
class HasID(Protocol):
    """Protocol for objects that have an ID field."""
    id: Union[int, str]  # Support both int and string IDs


T = TypeVar('T', bound=HasID)


class BaseContainer(BaseModel, Generic[T]):
    """
    Generic container for statement types with unique ID validation.
    
    This container ensures that all items have unique IDs and provides
    list-like functionality for statement collections.
    
    Type Parameters:
        T: Any type that implements the HasID protocol (has an 'id' field)
    
    Examples:
        # For BASCO statements
        basco_container = GrecoContainer[BASCO](items=[basco1, basco2])

        # For GRECO statements
        greco_container = GrecoContainer[GRECO](items=[greco1, greco2])

        # For RETYP statements
        retyp_container = BaseContainer[RETYP](items=[retyp1, retyp2])
    """
    items: List[Any] = Field(default_factory=list, description="List of items with unique IDs")
    
    @model_validator(mode='after')
    def validate_unique_ids(self) -> Self:
        """Ensure all item IDs are unique."""
        seen_ids: set[int] = set()
        for item in self.items:
            if item.id in seen_ids:
                raise ValueError(f"Duplicate ID found: {item.id}")
            seen_ids.add(item.id)
        return self
    
    def add(self, item: Any) -> None:
        """Add an item to the container, checking for duplicate IDs."""
        if any(existing.id == item.id for existing in self.items):
            raise ValueError(f"Item with ID {item.id} already exists")
        self.items.append(item)
    
    def remove(self, id_value: Union[int, str]) -> Any:
        """Remove and return an item by ID."""
        for i, item in enumerate(self.items):
            if item.id == id_value:
                return self.items.pop(i)
        raise KeyError(f"No item found with ID: {id_value}")
    
    def get_by_id(self, id_value: Union[int, str]) -> Any:
        """Get an item by ID."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None  # Changed from raising KeyError to returning None for compatibility
    
    def has_id(self, id_value: Union[int, str]) -> bool:
        """Check if an item with the given ID exists."""
        return any(item.id == id_value for item in self.items)
    
    def get_ids(self) -> List[Union[int, str]]:
        """Get a list of all IDs in the container."""
        return [item.id for item in self.items]
    
    def clear(self) -> None:
        """Remove all items from the container."""
        self.items.clear()
    
    def __len__(self) -> int:
        """Return the number of items in the container."""
        return len(self.items)
    
    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        return self.items[index]
    
    def __contains__(self, item: Any) -> bool:
        """Check if item or ID is in the container."""
        if isinstance(item, (int, str)):
            return self.has_id(item)
        return item in self.items