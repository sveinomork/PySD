from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext


class RETYP(BaseModel):
    """
    Defines rebar layer types to be referenced in the RELOC statement.
    
    ### Validation Rules
    
    1. **ID Range**: Must be between 1 and 99999999 (8 digits max)
    2. **Method Validation**: Must provide either AR (Method 1) or NR+DI (Method 2)
    3. **Label Length**: LB label must be ≤ 16 characters
    4. **Positive Values**: AR, NR, DI, CC, C2, TH, OS, BC must be positive if specified
    5. **Uniqueness**: ID must be unique within container
    
    ### Examples:
    ---------------
    ```python
    # Method 1 (direct area input):
    RETYP(id=20101, mp=1, ar=2094e-6, c2=0.060, th=0.025, di=0.020, nr=1, bc=0.75)
      → 'RETYP ID=20101 MP=1 AR=0.002094 NR=1 DI=0.02 C2=0.06 TH=0.025 BC=0.75'

    # Method 2 (calculated area from number & diameter):
    RETYP(id=20101, mp=1, nr=1, di=0.020, cc=0.200)                                 
    → 'RETYP ID=20101 MP=1 NR=1 DI=0.02 CC=0.2'

    # Method 3 (fixed offset mode):
    RETYP(id=20101, mp=1, ar=2094e-6, os=0.050)                                     
    → 'RETYP ID=20101 MP=1 AR=0.002094 OS=0.05'

    # Method 4 (crack width calculation mode):
    RETYP(id=20101, di=0.020, nr=1, bc=0.75)                                       
    → 'RETYP ID=20101 NR=1 DI=0.02 BC=0.75'
    ```
    """
    
    # Required for identification
    id: int = Field(..., description="Type number (max 8 digits)")
    
    # Optional parameters
    mp: Optional[int] = Field(None, description="Rebar material property set ID (MP=)")
    lb: Optional[str] = Field(None, description="Label for XTRACT plot file (max 16 chars)")
    ar: Optional[float] = Field(None, description="Cross-sectional area per unit length [m²/m] (Method 1)")
    nr: Optional[int] = Field(None, description="Number of rebars in bundle (default 1, Method 2)")
    di: Optional[float] = Field(None, description="Diameter of rebar [m or mm] (> 1.0 → mm, < 1.0 → m)")
    cc: Optional[float] = Field(None, description="Center distance between bars/bundles [mm]")
    c2: Optional[float] = Field(None, description="Nominal cover to first layer [m]")
    th: Optional[float] = Field(None, description="Thickness of rebar layer [m]")
    os: Optional[float] = Field(None, description="Offset to layer center [m]")
    bc: Optional[float] = Field(None, description="Bond coefficient (default 0.75)")
    comment: Optional[str] = Field(None, description="Comment to append at end of line")
    
    # Auto-generated fields
    input: str = Field(default="", init=False, description="Generated input string")
    
    @field_validator('id')
    @classmethod
    def validate_id_range(cls, v):
        """Validate ID is within acceptable range."""
        if not (1 <= v <= 99999999):
            raise ValueError("ID must be between 1 and 99999999")
        return v
    
    @field_validator('lb')
    @classmethod
    def validate_label_length(cls, v):
        """Validate label length."""
        if v is not None and len(v) > 16:
            raise ValueError("LB label must be ≤ 16 characters")
        return v
    
    @field_validator('ar', 'nr', 'di', 'cc', 'c2', 'th', 'bc')
    @classmethod
    def validate_positive_values(cls, v):
        """Validate that numeric values are positive when specified."""
        if v is not None and v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @field_validator('os')
    @classmethod
    def validate_offset_values(cls, v):
        """Validate offset values (can be zero or positive)."""
        if v is not None and v < 0:
            raise ValueError("Offset value cannot be negative")
        return v
    
    @model_validator(mode='after')
    def validate_method_requirements(self) -> 'RETYP':
        """Validate that required method combinations are provided."""
        if self.ar is None and (self.nr is None or self.di is None):
            raise ValueError("Must provide either AR (Method 1) or NR+DI (Method 2)")
        return self
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'RETYP':
        """Build the input string after validation."""
        parts = ["RETYP"]
        parts.append(f"ID={self.id}")

        if self.mp is not None:
            parts.append(f"MP={self.mp}")
        if self.lb:
            parts.append(f"LB={self.lb}")
        if self.ar is not None:
            parts.append(f"AR={self.ar:.6g}")
        if self.nr is not None:
            parts.append(f"NR={self.nr}")
        if self.di is not None:
            parts.append(f"DI={self.di:.6g}")
        if self.cc is not None:
            parts.append(f"CC={self.cc:.6g}")
        if self.c2 is not None:
            parts.append(f"C2={self.c2:.6g}")
        if self.th is not None:
            parts.append(f"TH={self.th:.6g}")
        if self.os is not None:
            parts.append(f"OS={self.os:.6g}")
        if self.bc is not None:
            parts.append(f"BC={self.bc:.6g}")

        if self.comment:
            parts.append(f"% {self.comment}")

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