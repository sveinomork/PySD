
from typing import Literal, Optional
from pydantic import  Field
from .statement_base import StatementBase

class EXECD(StatementBase):
    """
    Orders the execution of the data defined in the input file.

    This statement must always be included at the end of the top-level
    input file. It defines the design method to be used for the analysis.

    ### Examples:
    ```python
    # 1. No design calculations (e.g., for creating OLC-files):
       EXECD() -> "EXECD DM="

    # 2. Verification of user-defined reinforcement:
       EXECD(dm='V') -> "EXECD DM=V"

    # 3. Search for necessary section reinforcement:
       EXECD(dm='S') -> "EXECD DM=S"

    ### Parameters:
   
    dm : Optional[Literal['V', 'S', 'A']]
        The design method to use.
        - None: No design calculations (DM=).
        - 'V': Verify user-defined reinforcement.
        - 'S': Search for necessary section reinforcement.
        - 'A': Search for necessary area reinforcement.
    """
    dm: Optional[Literal['V', 'S', 'A']] = Field(None, description="Design method: None (no design), 'V' (verify), 'S' (search), 'A' (area search)")

    @property
    def identifier(self) -> str:
        return self._build_identifier(field_order=['dm'], add_hash=True)
    
    def _build_input_string(self) -> None:
        """Build input string and run instance-level validation."""
        if self.dm:
            self.input = f"EXECD DM={self.dm}"
        else:
            self.input = "EXECD DM="