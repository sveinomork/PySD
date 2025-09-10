from abc import ABC, abstractmethod
from typing import Protocol, Union,  TypeVar

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
