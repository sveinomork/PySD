from __future__ import annotations
from typing import Optional
from pydantic import Field
from .statement_base import StatementBase


class RETYP(StatementBase):
    """
    Defines rebar layer types to be referenced in the RELOC statement.
    
    All validation rules are implemented in src/pysd/validation/rules/retyp_rules.py
    
    ### Examples:

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
    ar: Optional[float] = Field(None, description="Cross-sectional area per unit length [m²/m] (Method 1)")
    nr: Optional[int] = Field(None, description="Number of rebars in bundle (default 1, Method 2)")
    di: Optional[float] = Field(None, description="Diameter of rebar [m or mm] (> 1.0 → mm, < 1.0 → m)")
    cc: Optional[float] = Field(None, description="Center distance between bars/bundles [mm]")
    c2: Optional[float] = Field(None, description="Nominal cover to first layer [m]")
    th: Optional[float] = Field(None, description="Thickness of rebar layer [m]")
    os: Optional[float] = Field(None, description="Offset to layer center [m]")
    bc: Optional[float] = Field(None, description="Bond coefficient (default 0.75)")
    lb: Optional[str] = Field(None, description="Label for XTRACT plot file (max 16 chars)")
    comment: Optional[str] = Field(None, description="Comment to append at end of line")
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RETYP statement."""
        return str(self.id)
    
    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=['id', 'mp', 'ar', 'nr', 'di', 'cc', 'c2', 'th', 'os', 'bc', 'lb'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
            comment=self.comment
        )

