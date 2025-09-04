from typing import List
from statements import basco
from .base_container import BaseContainer

class BascoContainer(BaseContainer[basco.BASCO]):
    """
    Container for multiple BASCO statements that ensure no duplicate IDs.
    Inherits from BaseContainer with BASCO-specific typing.
    """
    
    @property
    def bascos(self) -> List[basco.BASCO]:
        """Alias for items to maintain backward compatibility."""
        return self.items  # type: ignore
    
    @bascos.setter
    def bascos(self, value: List[basco.BASCO]) -> None:
        """Setter for bascos property."""
        self.items = value