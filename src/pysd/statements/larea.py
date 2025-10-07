from __future__ import annotations
from typing import Optional, Tuple
from pydantic import Field

from .statement_base import StatementBase


class LAREA(StatementBase):
    """
    Define location areas with PA= FS= and HS= or with global coordinates. 
    The location areas can be referenced in CMPNS, CMPOS, CMPEC to define 
    different areas with different concrete properties, in RELOC, SRLOC to 
    define areas with reinforcement or in SHAXE.

    ### Example
     ```python
     LAREA(id=1, pa="BASE", fs=(1,24), hs=(5,15))
     → 'LAREA ID=1 PA=BASE FS=1-24 HS=5-15'
    LAREA(id=2, pa="BASE", xr=(2,30), yr=(7,8), al=30)
    → 'LAREA ID=2 PA=BASE XR=2.,30. YR=7.,8. AL=30.'
     ```

    ### Parameters:
        id: LAREA id-number
        pa: structural part name (max 8 characters)
        fs: F-section range
        hs: H-section range
        xr: X-range (min, max) area defined by box,rectangle
        yr: Y-range (min, max) area defined by box,rectangle
        zr: Z-range (min, max) area defined by box,rectangle
        al: rotation angle in degrees (-90 to +90) of the area deined, pos. dir. couterclockwise
        pri: print data for all stored LAREA sets
    """

    # Required parameters
    id: int = Field(..., description="LAREA id-number")
    pa: str = Field(..., description="Structural part name (max 8 chars)")
    
    fs: Optional[Tuple[int, int]] = Field(None, description="F-section range")
    hs: Optional[Tuple[int, int]] = Field(None, description="H-section range")

    xr: Optional[Tuple[float, float]] = Field(  
        None, description="X-range (min, max) area defined by box,rectangle"
    )
    yr: Optional[Tuple[float, float]] = Field(
        None, description="Y-range (min, max) area defined by box,rectangle"
    )
    zr: Optional[Tuple[float, float]] = Field(
        None, description="Z-range (min, max) area defined by box,rectangle"
    )
    al: Optional[float] = Field(
        None, description="rotation angle in degrees (-90 to +90) of the area deined, pos. dir. couterclockwise"
    )

    pri: bool = Field(False, description="print data for all stored LAREA sets")
    

    @property
    def identifier(self) -> str:
        """Get unique identifier for this SHSEC statement."""
        return self._build_identifier(field_order=["id", "pa"], add_hash=False)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri:
            # Special case: print mode
            self.start_string()
            if self.pri:
                self.add_param("PRI", "")  # Empty value becomes "PRI="
        else:
            # Normal mode: FS/HS keep default (2 -> '-') while XR/YR/ZR use ',' for pairs
            self.input = self._build_string_generic(
                field_order=[
                    "pa",
                    "fs",
                    "hs",
                    "xr",
                    "yr",
                    "zr",
                    "al",
                ],
                exclude={"tab", "ver"},
                float_precision=1,
                field_tuple_separators={
                    "xr": {2: ","},
                    "yr": {2: ","},
                    "zr": {2: ","},
                },
            )
