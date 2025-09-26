from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import  Field

from .statement_base import StatementBase


class SHSEC(StatementBase):
    """
    ### Purpose
    Create extrapolated section.
    
    ### Example
     ```python
     SHSEC(pa="plate1", se=1001, el=113,xf=(1,0,0),xh=(0,-1,0),fs=(1,7),hs=(2,5))
     → 'SHSEC PA=plate1 SE=1001 EL=113 XF=1,0,0 XH=0,-1,0 FS=1-7 HS=2-5'
     ```

    ### Parameters:
        pa: structural part name (max 8 characters)
        se: start super element number
            - 1000*type+index for SESAM
            - type for .aba-file in ABAFIL
        
        Element Specification (one of these must be provided):
        el: start element number to be given
        xp: start element coordinates (x,y,z)
        elset: element group number (ABAQUS)
        elsetname: element group name (Sesam), FS=1-nel, HS=1-4
        te: triangular elements range (stored as separate part)
        
        Optional Parameters:
        et: stiffness calculation type
            - LI = linear stiffness elements
            - VS = variable stiffness elements [default]
        ne: wanted number of elements over thickness (max=10)
        td: thickness direction vector
        xf: F-direction start vector
        xh: H-direction start vector
        fs: F-section range
        hs: H-section range
        ns: number of sections per element [default=4]
        tab: element table wanted or not [default=OFF]
        ver: OLC number to be verified (integration verification)
 
    """
    # Required parameters
    pa: str = Field(..., description="Structural part name (max 8 chars)")
    se: Optional[int] = Field(None, description="Start super element number")
    
    # Element specification (one of these must be provided)
    el: Optional[int] = Field(None, description="Start element number (external)")
    xp: Optional[Tuple[float, float, float]] = Field(None, description="Start element coordinates")
    elset: Optional[int] = Field(None, description="Element group number")
    elsetname: Optional[str] = Field(None, description="Element group name (Sesam)")
    te: Optional[Tuple[int, int]] = Field(None, description="Triangular elements range")
    
    # Optional parameters
   
    
    td: Optional[Tuple[float, float, float]] = Field(None, description="Thickness direction vector")
    xf: Optional[Tuple[float, float, float]] = Field(None, description="F-direction start vector")
    xh: Optional[Tuple[float, float, float]] = Field(None, description="H-direction start vector")
    fs: Optional[Tuple[int, int]] = Field(None, description="F-section range")
    hs: Optional[Tuple[int, int]] = Field(None, description="H-section range")
    ne: Optional[int] = Field(None, description="Number of elements over thickness (max 10)")
    et: Literal['LI', 'VS'] = Field(None, description="Stiffness calculation type")
    ns: int = Field(None, description="Number of sections per element")
    tab: bool = Field(False, description="Element table wanted or not")
    ver: Optional[int] = Field(None, description="OLC number to be verified")
    
   

    @property
    def identifier(self) -> str:    
        """Get unique identifier for this SHSEC statement."""
        return self._build_identifier(field_order=['pa', 'hs', 'fs'], add_hash=True)
    
    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.tab or self.ver is not None:
            # Special case: table or verification mode
            self.start_string() 
            if self.tab:
                self.add_param("TAB", "")  # Empty value becomes "TAB="
            if self.ver is not None:
                self.add_param("VER","")
        else:
            # Normal mode: use generic builder with proper exclusions and defaults
            self.input = self._build_string_generic(
                field_order=['pa', 'se', 'el', 'xp', 'elset', 'elsetname', 'te', 'td', 'xf', 'xh', 'fs', 'hs', 'ne', 'et', 'ns'],
                # Exclude boolean fields and auto-generated fields
                exclude={'tab', 'ver'},
                
                float_precision=1  # Match expected output format
            )

        

