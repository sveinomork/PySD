from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, Literal



@dataclass
class SHSEC:
    """
    ### Purpose
    Creation of shell sections/design sections.
    
    ### Example
     ```python
     SHSEC(pa="plate1", se=1001, el=113,xf=(1,0,0),xh=(0,-1,0),fs=(1,7),hs=(2,5))
     → 'SHSEC PA=plate1 SE=1001 EL=113 XF=1,0,0 XH=0,-1,0 FS=1-7 HS=2-5'


     ```
   

    Parameters:
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
        
    Examples:
       
        
    Note: For alternative 3 and 4, local shell axis system from the analysis is used as
          123-axes if no SHAXE-statement is given.
    """
    # Required parameters
    pa: str  # structural part name (max 8 chars)
    se: Optional[int] = None    # start super element number
    
    # Element specification (one of these must be provided)
    el: Optional[int] = None         # start element number (external)
    xp: Optional[Tuple[float, float, float]] = None    # start element coordinates
    elset: Optional[int] = None      # element group number
    elsetname: Optional[str] = None  # element group name (Sesam)
    te: Optional[Tuple[int, int]] = None  # triangular elements range
    
    # Optional parameters
    et: Literal['LI', 'VS'] = 'VS'   # stiffness calculation type
    ne: Optional[int] = None         # number of elements over thickness (max 10)
    td: Optional[Tuple[float, float, float]] = None    # thickness direction vector
    xf: Optional[Tuple[float, float, float]] = None    # F-direction start vector
    xh: Optional[Tuple[float,float,float]] = None    # H-direction start vector
    fs: Optional[Tuple[int, int]] = None  # F-section range
    hs: Optional[Tuple[int, int]] = None  # H-section range
    ns: int = 4  # number of sections per element
    tab: bool = False  # element table wanted or not
    ver: Optional[int] = None  # OLC number to be verified
    
    # Output string
    input: str = field(init=False, default="SHSEC")

    def __post_init__(self):
        # Validation
        if len(self.pa) > 8:
            raise ValueError("Structural part name (PA) cannot exceed 8 characters")
            
        # At least one element specification must be provided
        specs: list[Any] = [self.el, self.xp, self.elset, self.elsetname, self.te]
        if not any(spec is not None for spec in specs):
            raise ValueError("One element specification (EL, XP, ELSET, ELSETNAME, or TE) must be provided")
            
        if sum(spec is not None for spec in specs) > 1:
            raise ValueError("Only one element specification can be provided")
            
        if self.ne is not None and (self.ne < 1 or self.ne > 10):
            raise ValueError("Number of elements over thickness (NE) must be between 1 and 10")
        
        # Build the SHSEC input string
        parts = ["SHSEC"]
        
        # Add required parameters
        parts.append(f"PA={self.pa}")
        if self.se is not None:
            parts.append(f"SE={self.se}")
        
        # Add element specification
        if self.el is not None:
            parts.append(f"EL={self.el}")
        elif self.xp is not None:
            parts.append(f"XP={self.xp[0]},{self.xp[1]},{self.xp[2]}")
        elif self.elset is not None:
            parts.append(f"ELSET={self.elset}")
        elif self.elsetname is not None:
            parts.append(f"ELSETNAME={self.elsetname}")
        elif self.te is not None:
            parts.append(f"TE={self.te[0]}-{self.te[1]}")
            
        # Add optional parameters
        if self.et != 'VS':
            parts.append(f"ET={self.et}")
            
        if self.ne is not None:
            parts.append(f"NE={self.ne}")
            
        if self.td is not None:
            parts.append(f"TD={self.td}")
            
        if self.xf is not None:
            parts.append(f"XF={self.xf[0]},{self.xf[1]},{self.xf[2]}")

        if self.xh is not None:
            parts.append(f"XH={self.xh[0]},{self.xh[1]},{self.xh[2]}")
            
        if self.fs is not None:
            parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
            
        if self.hs is not None:
            parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
            
        if self.ns != 4:
            parts.append(f"NS={self.ns}")
            
        if self.tab:
            parts.append("TAB=ON")
            
        if self.ver is not None:
            parts.append(f"VER={self.ver}")
            
        # Join all parts with spaces
        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input