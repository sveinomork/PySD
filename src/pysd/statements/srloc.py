from __future__ import annotations
from typing import Optional, Tuple, Union
from pydantic import Field
from .statement_base import StatementBase


class SRLOC(StatementBase):
    """
    Define shear reinforcement bar placement and configuration within shell sections.

    Links to stirrup types defined by SRTYP statements and specifies placement through
    part names, section ranges, or location areas.

    ### Examples
 
    ```python
    # Stirrup in specific section range with face and direction
    SRLOC(id='stiA1', st=5, pa="VEGG", fs=(5, 10), hs=3)
    # → "SRLOC ID=stiA1 ST=5 PA=VEGG FS=5-10 HS=3"

    ```

    ### Parameters
  
    id : str
        Location identity (max 4 characters). Must be unique within model.

    st : int | Tuple[int, int]
        Stirrup type number or range (st1, st2). References SRTYP statement ID.
        Single value or tuple range, e.g., 101 or (101, 105).

    pa : Optional[str], default=None
        Structural part identity (name). If None, applies to all parts.
        Must match existing part name in model.

    fs : Optional[int | Tuple[int, int]], default=None
        F-section number or range (f1, f2). Mutually exclusive with la.

    hs : Optional[int | Tuple[int, int]], default=None  
        H-section number or range (h1, h2). Mutually exclusive with la.

    la : Optional[int], default=None
        Section set number from LAREA statement. 
        Mutually exclusive with pa, fs, hs parameters.

    ### Notes
   

    """
    
    # Required fields
    id: str = Field(..., description="Location identity (max 4 characters)")
    st: Union[int, Tuple[int, int]] = Field(..., description="Rebar type number or range (rt1, rt2), see RETYP")
    
   
    # Location area alternative 1
    pa: Optional[str] = Field(None, description="Part identity (name). Default applies to all parts")
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="F-section number or range (f1, f2)")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="H-section number or range (h1, h2)")
    
    # Location area alternative 2
    la: Optional[int] = Field(None, description="Section set number from LAREA statement. Mutually exclusive with pa, fs, hs")
    
  
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RELOC statement."""
        return f'{self.id}_{self.pa}_{self.fs}_{self.hs}'

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=['id', 'st', 'pa', 'fs', 'hs', 'la'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6
        )

