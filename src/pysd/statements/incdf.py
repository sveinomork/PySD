from pathlib import Path
from typing import Union
from .statement_base import StatementBase

class INCDF(StatementBase):
    """
    Opens an additional input file.

    This allows for including other input files into the main file,
    making it possible to structure large models.

    Parameters:
    -----------
    path : Union[str, Path]
        The file name or path to the input file to be included.
    """
    path: Union[str, Path]
     
    @property
    def identifier(self) -> str:
        """Get unique identifier for this INCDF statement."""
        return self._build_identifier(field_order=['path'], add_hash=True)

    def _build_input_string(self) -> str:
        """Build the input string for this INCDF statement."""
        return f"INCDF {self.path}"
   
