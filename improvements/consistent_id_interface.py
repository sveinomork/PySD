from abc import ABC, abstractmethod
from typing import Protocol, Union, List, Optional, TypeVar, Generic

# Define consistent ID types
IdType = Union[int, str]
T = TypeVar('T')

class Identifiable(Protocol):
    """Protocol for objects with consistent ID access"""
    
    @property
    def identifier(self) -> IdType:
        """Get the unique identifier for this object"""
        ...

class BaseStatement(ABC):
    """Base class for all statements with consistent ID handling"""
    
    @property
    @abstractmethod
    def identifier(self) -> IdType:
        """Return the unique identifier for this statement"""
        pass
    
    def __hash__(self) -> int:
        return hash(self.identifier)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseStatement):
            return False
        return self.identifier == other.identifier

class StandardContainer(Generic[T]):
    """Standardized container interface for all statement types"""
    
    def __init__(self):
        self._items: dict[IdType, T] = {}
        self._insertion_order: list[IdType] = []
    
    def add(self, item: T) -> None:
        """Add item with consistent ID handling"""
        if not isinstance(item, Identifiable):
            raise TypeError(f"Item must implement Identifiable protocol")
        
        id_val = item.identifier
        if id_val in self._items:
            raise ValueError(f"Item with ID {id_val} already exists")
        
        self._items[id_val] = item
        self._insertion_order.append(id_val)
    
    def get_by_id(self, id_val: IdType) -> Optional[T]:
        """Get item by ID"""
        return self._items.get(id_val)
    
    def contains(self, id_val: IdType) -> bool:
        """Check if ID exists"""
        return id_val in self._items
    
    def get_all_ids(self) -> List[IdType]:
        """Get all IDs in insertion order"""
        return self._insertion_order.copy()
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __iter__(self):
        """Iterate in insertion order"""
        for id_val in self._insertion_order:
            yield self._items[id_val]

# Example usage
class BASCO_Improved(BaseStatement):
    def __init__(self, id: int, load_cases: list, **kwargs):
        self.id = id
        self.load_cases = load_cases
        # ... other fields
    
    @property
    def identifier(self) -> int:
        return self.id

class LOADC_Improved(BaseStatement):
    def __init__(self, key: str, **kwargs):
        self.key = key
        # ... other fields
    
    @property
    def identifier(self) -> str:
        return self.key

# Consistent container usage
basco_container = StandardContainer[BASCO_Improved]()
loadc_container = StandardContainer[LOADC_Improved]()

# All containers now have identical APIs:
# .add(item), .get_by_id(id), .contains(id), .get_all_ids()
