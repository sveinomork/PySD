from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

@dataclass
class INCDF:
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
    input: str = field(init=False)

    def __post_init__(self):
        self.input = f"INCDF {self.path}"

    def __str__(self) -> str:
        return self.input
