from __future__ import annotations
from typing import Optional, Tuple, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
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
    
    @field_validator('id')
    @classmethod
    def validate_id_length(cls, v):
        """Validate ID length."""
        if len(v) > 4:
            raise ValueError("ID must be max 4 characters")
        return v
    
    @field_validator('al')
    @classmethod
    def validate_angle_range(cls, v):
        """Validate angle is within acceptable range."""
        if not -90 <= v <= 90:
            raise ValueError("AL (angle) must be between -90 and +90 degrees")
        return v
    
    @field_validator('cov', 'os')
    @classmethod
    def validate_positive_values(cls, v):
        """Validate that numeric values are positive when specified."""
        if v is not None and v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @model_validator(mode='after')
    def validate_location_exclusivity(self) -> 'RELOC':
        """Validate that location area alternatives are mutually exclusive."""
        location_alt1 = any([self.pa, self.fs, self.hs])
        location_alt2 = self.la is not None
        
        if location_alt1 and location_alt2:
            raise ValueError("Location area alternatives are mutually exclusive. Use either 'la' or a combination of 'pa', 'fs', 'hs'")
        return self
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'RELOC':
        """Build the input string after validation."""
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
        return self
    
    def validate_cross_container_references(self, context: ValidationContext) -> None:
        """Validate cross-container references."""
        issues = execute_validation_rules(self, context, level='model')
        if any(issue.severity == 'error' for issue in issues):
            error_messages = [issue.message for issue in issues if issue.severity == 'error']
            raise ValueError(f"Cross-container validation failed: {'; '.join(error_messages)}")
    
    def __str__(self) -> str:
        return self.input