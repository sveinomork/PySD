from dataclasses import dataclass, field
from typing import Optional, Tuple, Union, Literal

@dataclass
class RELOC:
    """

   ### Purpose:
    --------
    Defines rebar locations and properties.

    This statement is used to specify where and how reinforcement bars (rebars)
    are placed within shell sections. It links to a rebar type defined by a
    RETYP statement and can specify the location through part names, section
    ranges, or location areas.

   ### Examples:
    ---------------
    ```python
    # Rebar in a specific section range:
    RELOC(id='X11', rt=(16101, 20101), fa=1, fs=(5, 10), hs=3)
    → "RELOC ID=X11 RT=16101-20101 FA=1 FS=5-10 HS=3"

    # Rebar with a specific angle across the entire model:
    RELOC(id='Y21', rt=20101, fa=2, al=90)
    → "RELOC ID=Y21 RT=20101 FA=2 AL=90"

    # Rebar defined by a location area with a specific cover:
    RELOC(id='B1', rt=(101, 101), la=5, cov=50.0)
    → "RELOC ID=B1 RT=101 COV=50.0 LA=5"

    # Example of rebar in the centre of the cross section
    RELOC(id="Y02", pa="VEGG", rt=2, fa=0, al=90)
    → "RELOC ID=Y02 PA=VEGG RT=2 FA=0 AL=90"
    ```

    ### Parameters:
    -----------
    id : str
        Location identity (max 4 characters).
    
    rt : Union[int, Tuple[int, int]]
        Rebar type number or range (rt1, rt2), see RETYP.
    
    cov : Optional[float]
        Rebar cover in mm. Overrides C2 from RETYP.
    
    fa : Literal[0, 1, 2]
        Shell face (0=center, 1=face1, 2=face2). Default is 0.
    
    al : float
        Direction angle in degrees (-90 to +90). Default is 0.0.
    
    os : Optional[float]
        Offset to layer center in meters. Overrides offset from RETYP.
    
    rp : Literal["12", "XY", "XZ", "YZ"]
        Reference plane for the direction angle AL. Default is "12".
    
    pa : Optional[str]
        Part identity (name). Default applies to all parts.
    
    fs : Optional[Union[int, Tuple[int, int]]]
        F-section number or range (f1, f2). Default applies to all F-sections.
    
    hs : Optional[Union[int, Tuple[int, int]]]
        H-section number or range (h1, h2). Default applies to all H-sections.
    
    la : Optional[int]
        Section set number from LAREA statement. Mutually exclusive with pa, fs, hs.
    """
    id: str
    rt: Union[int, Tuple[int, int]]
    cov: Optional[float] = None
    fa: Literal[0, 1, 2] = 0
    al: float = 0.0
    os: Optional[float] = None
    rp: Literal["12", "XY", "XZ", "YZ"] = "12"
    
    # Location area alternative 1
    pa: Optional[str] = None
    fs: Optional[Union[int, Tuple[int, int]]] = None
    hs: Optional[Union[int, Tuple[int, int]]] = None
    
    # Location area alternative 2
    la: Optional[int] = None
    
    input: str = field(init=False, default="RELOC")

    def __post_init__(self):
        # --- Validation ---
        if len(self.id) > 4:
            raise ValueError("ID must be max 4 characters.")
        
        if not -90 <= self.al <= 90:
            raise ValueError("AL (angle) must be between -90 and +90 degrees.")

        location_alt1 = any([self.pa, self.fs, self.hs])
        location_alt2 = self.la is not None
        
        if location_alt1 and location_alt2:
            raise ValueError("Location area alternatives are mutually exclusive. Use either 'la' or a combination of 'pa', 'fs', 'hs'.")

        # --- String Building ---
        parts = ["RELOC", f"ID={self.id}"]
        
        # RT (Rebar Type)
        if isinstance(self.rt, tuple):
            if self.rt[0] == self.rt[1]:
                parts.append(f"RT={self.rt[0]}")
            else:
                parts.append(f"RT={self.rt[0]}-{self.rt[1]}")
        else:
            parts.append(f"RT={self.rt}")
            
        # Optional parameters
        if self.cov is not None: parts.append(f"COV={self.cov}")
        if self.fa != 0: parts.append(f"FA={self.fa}")
        if self.al != 0.0: parts.append(f"AL={self.al}")
        if self.os is not None: parts.append(f"OS={self.os}")
        if self.rp != "12": parts.append(f"RP={self.rp}")
            
        # Location area parameters
        if self.la is not None:
            parts.append(f"LA={self.la}")
        else:
            if self.pa is not None: parts.append(f"PA={self.pa}")
            if self.fs is not None:
                if isinstance(self.fs, tuple): parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
                else: parts.append(f"FS={self.fs}")
            if self.hs is not None:
                if isinstance(self.hs, tuple): parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
                else: parts.append(f"HS={self.hs}")

        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input