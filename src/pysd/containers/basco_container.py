from typing import List
from ..statements import greco
from .base_container import BaseContainer

class BascoContainer(BaseContainer[greco.GRECO]):
    """
    Container for multiple BASCO statements that ensure no duplicate IDs.
    Inherits from BaseContainer with BASCO-specific typing.
    """
    
    @property
    def bascos(self) -> List[greco.GRECO]:
        """Alias for items to maintain backward compatibility."""
        return self.items  # type: ignore
    
    @bascos.setter
    def bascos(self, value: List[greco.GRECO]) -> None:
        """Setter for bascos property."""
        self.items = value