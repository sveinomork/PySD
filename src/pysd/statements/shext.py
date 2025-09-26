from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import  Field

from .statement_base import StatementBase


class SHEXT(StatementBase):
    """
    ### Purpose
    Creation of shell sections/design sections.
    
    ### Example
     ```python
     SHEXT(pa="WY2",efs=(1,4,3,2),hs=1,xp=(-31.6,0,0),xa=(-1,0,0))
     → 'SHEXT PA=WY2 EF=1,4,3,2 HS=1 XP=-31.6,0,0 XA=-1,0,0'
     ```
    ### Parameters
  
    pa : str
        Structural part name

    efs : Tuple[int,int, int,int]
        i new F-section number
        i,i1,i2,i3: F-section to be extrapolated from
        hs: (j1,j2) H-section range

    ehs : Tuple[int,int, int,int]
        i new H-section number
        j,j1,j2,j3: H-section to be extrapolated from
        fs: (f1,f2) F-section range

    fact : Tuple[float, float, float]
        factors f1,f2,f3 given in input
        

    dist : Optional[float]
        distance from last section

    face: Optional[Literal[0, 1, 2]], 
        0 :Section located on a shell element edge
        1,2 Section loated on sold element surface

    xp : Optional[Tuple[int,int, int]]
        Section located on a plane surface.
        Defined by XP=plane point, xA=plane normal
    
    xc : Optional[Tuple[int,int, int]]
        Section located on a cylindrical surface.
        Defined by XC=center XA=axis direction
    
    xa : Optional[Tuple[int,int, int]]
       Plane normal (face=0) or axis direction (face=1,2)
    
    ra : Optional[float]
        radius for cylindrical surface

    xs : Optional[Tuple[float, float, float]]
        Section located on a spherical surface.Defined by XS=center and RA=radius
    
    """
    # Required parameters
    pa: str = Field(..., description="Structural part name (max 8 chars)")
 
    
    # Element specification (one of these must be provided)
    efs: Optional[Tuple[int, int, int, int]] = Field(None, description="i,i1,i2,i3: F-section to be extrapolated from")
    ehs: Optional[Tuple[int, int, int, int]] = Field(None, description="i,i1,i2,i3: H-section to be extrapolated from")

    hs: Optional[int | Tuple[int, int]] = Field(None, description="H-section range (j1, j2)")
    fs: Optional[int | Tuple[int, int]] = Field(None, description="F-section range (f1, f2)")

    fact: Optional[Tuple[float, float, float]] = Field(None, description="f1,f2,f3: factors given in input")   
    dist: Optional[float] = Field(None, description="distance from last section")
    face: Optional[Literal[0, 1, 2]] = Field(None, description="0: Section on shell edge, 1/2: Section on solid surface") 
    xp: Optional[Tuple[float, float, float]] = Field(None, description="Section located on a plane surface. Defined by XP=plane point, xA=plane normal")
    xc: Optional[Tuple[float, float, float]] = Field(None, description="Section located on a cylindrical surface. Defined by XC=center XA=axis direction")
    xa: Optional[Tuple[float, float, float]] = Field(None, description="Plane normal (face=0) or axis direction (face=1,2)")
    ra: Optional[float] = Field(None, description="radius for cylindrical surface")  
    
    

    @property
    def identifier(self) -> str:    
        """Get unique identifier for this SHSEC statement."""
        return self._build_identifier(add_hash=True)
    
    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
     
        # Normal mode: use generic builder with proper exclusions and defaults
        self.input = self._build_string_generic(
                field_order=['pa', 'efs', 'ehs', 'hs', 'fact', 'dist', 'face', 'xp', 'xc', 'xa', 'ra', 'xs'],
                # Exclude boolean fields and auto-generated fields
                exclude={},
                # Use special formatting to print EF instead of EFS
                special_formatting={
                    'efs': lambda v: f"EF={','.join(str(x) for x in v)}"
                },
                # Use sufficient precision to avoid scientific notation for typical coordinates
                float_precision=4
            )

        

