from __future__ import annotations
from typing import Optional, Tuple, Union, Literal
from pydantic import BaseModel, Field
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext


class RELOC(BaseModel):
    """
    Defines rebar locations and properties.
    
    ### Validation Rules
    
    1. **ID Length**: Must be max 4 characters
    2. **Angle Range**: AL (angle) must be between -90 and +90 degrees
    3. **Location Exclusivity**: Cannot use both LA and combination of PA/FS/HS
    4. **Positive Values**: COV, OS must be positive if specified
    5. **Reference Validation**: RT must reference existing RETYP statements
    
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
    """
    
    # Required fields
    id: str = Field(..., description="Location identity (max 4 characters)")
    rt: Union[int, Tuple[int, int]] = Field(..., description="Rebar type number or range (rt1, rt2), see RETYP")
    
    # Optional parameters
    cov: Optional[float] = Field(None, description="Rebar cover in mm. Overrides C2 from RETYP")
    fa: Literal[0, 1, 2] = Field(0, description="Shell face (0=center, 1=face1, 2=face2)")
    al: float = Field(0.0, description="Direction angle in degrees (-90 to +90)")
    os: Optional[float] = Field(None, description="Offset to layer center in meters. Overrides offset from RETYP")
    rp: Literal["12", "XY", "XZ", "YZ"] = Field("12", description="Reference plane for the direction angle AL")
    
    # Location area alternative 1
    pa: Optional[str] = Field(None, description="Part identity (name). Default applies to all parts")
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="F-section number or range (f1, f2)")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="H-section number or range (h1, h2)")
    
    # Location area alternative 2
    la: Optional[int] = Field(None, description="Section set number from LAREA statement. Mutually exclusive with pa, fs, hs")
    
    # Auto-generated fields
    input: str = Field(default="", init=False, description="Generated input string")
    
    def model_post_init(self, __context):
        """Generate input string after model creation."""
        self.build_input_string()
    
    def build_input_string(self) -> str:
        """Build the RELOC input string."""
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
        if self.cov is not None:
            parts.append(f"COV={self.cov}")
        if self.fa != 0:
            parts.append(f"FA={self.fa}")
        if self.al != 0.0:
            parts.append(f"AL={self.al}")
        if self.os is not None:
            parts.append(f"OS={self.os}")
        if self.rp != "12":
            parts.append(f"RP={self.rp}")
            
        # Location area parameters
        if self.la is not None:
            parts.append(f"LA={self.la}")
        else:
            if self.pa is not None:
                parts.append(f"PA={self.pa}")
            if self.fs is not None:
                if isinstance(self.fs, tuple):
                    parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
                else:
                    parts.append(f"FS={self.fs}")
            if self.hs is not None:
                if isinstance(self.hs, tuple):
                    parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
                else:
                    parts.append(f"HS={self.hs}")

        self.input = " ".join(parts)
        return self.input
    
    def validate_cross_references(self, context: ValidationContext) -> None:
        """Validate cross-references with other containers."""
        if context.full_model is None:
            return
        execute_validation_rules(self, context)
    
    def __str__(self) -> str:
        return self.input if self.input else self.build_input_string()