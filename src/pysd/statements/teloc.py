from __future__ import annotations
from typing import Optional, Tuple, Union
from pydantic import Field
from .statement_base import StatementBase


class TELOC(StatementBase):
    """
    Define tendon (prestressing) layer data.

    Links to tendon types defined by TETYP statements and specifies placement through

    ### Examples
 
    ```python
    # Tendon in specific section range with face and direction
    TELOC(id='tenA1', tt=5, pa="VEGG", fs=(5, 10), hs=3)
    # → "TELOC ID=tenA1 TT=5 PA=VEGG FS=5-10 HS=3"

    ```

    ### Parameters
  
    id : str
        Location identity (max 4 characters). Must be unique within model.

    tt : int 
        Tendon type number . References TETYP statement ID.
    
    fa : int
        Offset from shell section face =0/1/2, see TETYP.

    tb : Optional[str], default=None
        tang(beta) = dx3/dl

    al : Optional[float], default=None
        direction angle in 1-2 plane [deg]
    
    pa: Optional[str], default=None
        Structural part identity (name). If None, applies to all parts.
    
    fs : Optional[int | Tuple[int, int]], default=None
        F-section number or range (f1, f2). Mutually exclusive with la.

    hs : Optional[int | Tuple[int, int]], default=None  
        H-section number or range (h1, h2). Mutually exclusive with la.

    ### Notes
   

    """
    
    # Required fields
    id: str = Field(None, description="Location identity (max 4 characters)")
    tt: int = Field(None, description="Tendon type number, see TETYP")
    fa: Optional[float] = Field(None, description="Offset from shell section face =0/1/2, see TETYP"   )
    al: Optional[float] = Field(None, description="direction angle in 1-2 plane [deg]")
  
    pa: Optional[str] = Field(None, description="Part identity (name). Default applies to all parts")
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="F-section number or range (f1, f2)")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="H-section number or range (h1, h2)")
    
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RELOC statement."""
        return f'{self.id}_{self.pa}_{self.fs}_{self.hs}'

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=['id', 'tt', 'fa', 'tb', 'al', 'pa', 'fs', 'hs'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6
        )

