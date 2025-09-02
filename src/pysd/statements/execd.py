from dataclasses import dataclass, field
from typing import Literal, Optional

@dataclass
class EXECD:
    """
    Orders the execution of the data defined in the input file.

    This statement must always be included at the end of the top-level
    input file. It defines the design method to be used for the analysis.

    Usage Examples:
    ---------------
    1. No design calculations (e.g., for creating OLC-files):
       EXECD() -> "EXECD DM="

    2. Verification of user-defined reinforcement:
       EXECD(dm='V') -> "EXECD DM=V"

    3. Search for necessary section reinforcement:
       EXECD(dm='S') -> "EXECD DM=S"

    Parameters:
    -----------
    dm : Optional[Literal['V', 'S', 'A']]
        The design method to use.
        - None: No design calculations (DM=).
        - 'V': Verify user-defined reinforcement.
        - 'S': Search for necessary section reinforcement.
        - 'A': Search for necessary area reinforcement.
    """
    dm: Optional[Literal['V', 'S', 'A']] = None
    input: str = field(init=False)

    def __post_init__(self):
        if self.dm:
            self.input = f"EXECD DM={self.dm}"
        else:
            self.input = "EXECD DM="

    def __str__(self) -> str:
        return self.input