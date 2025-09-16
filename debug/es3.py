from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import  Field




class SHSEC(StatementBase):
    """
    
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
    et: Literal['LI', 'VS'] = Field('VS', description="Stiffness calculation type")
    ns: int = Field(4, description="Number of sections per element")
    tab: bool = Field(False, description="Element table wanted or not")
    ver: Optional[int] = Field(None, description="OLC number to be verified")


    def __str__(self) -> str:
        """Return the SHSEC input string."""
        built_str=f"SHSEC PA={self.pa}"
        if self.se is not None:
            built_str += f" SE={self.se}"
        if self.el is not None:      #if None
            built_str += f" EL={self.el}"
        if self.xp is not None:
            built_str += f" XP={self.xp[0]},{self.xp[1]},{self.xp[2]}" # if it is a tuple with three elements
        if self.elset is not None:
            built_str += f" ELSET={self.elset}"
        if self.elsetname is not None:
            built_str += f" ELSETNAME={self.elsetname}"
        if self.te is not None:
            built_str += f" TE={self.te[0]}-{self.te[1]}" # if it is a tuple with two elements
        if self.td is not None:
            built_str += f" TD={self.td[0]},{self.td[1]},{self.td[2]}" # if it is a tuple with three elements
        if self.xf is not None:
            built_str += f" XF={self.xf[0]},{self.xf[1]},{self.xf[2]}" # if it is a tuple with three elements
        if self.xh is not None:
            built_str += f" XH={self.xh[0]},{self.xh[1]},{self.xh[2]}" # if it is a tuple with three elements
        if self.fs is not None:
            built_str += f" FS={self.fs[0]}-{self.fs[1]}" # if it is a tuple with two elements
        if self.hs is not None:
            built_str += f" HS={self.hs[0]}-{self.hs[1]}" # if it is a tuple with two elements
        if self.ne is not None:
            built_str += f" NE={self.ne}" # if it is int or string
        if self.ns != 4:
            built_str += f" NS={self.ns}"
        if self.et != 'VS':
            built_str += " ET=LI"
        
        return built_str
