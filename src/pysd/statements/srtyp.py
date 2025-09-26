from __future__ import annotations
from typing import Optional
from pydantic import Field
from .statement_base import StatementBase


class SRTYP(StatementBase):
    """
    Defines shear reinforcement types to be used in SRLOC statement



    ### Examples:

    ```python
    # Method 1 (direct area input):
    SRTYP(id=1, mp=1, ar=2094e-6)
      → 'SRTYP ID=1 MP=1 AR=0.002094'

    ```
    """

    # Required for identification
    id: int = Field(..., description="Type number (max 8 digits)")

    # Optional parameters
    lb: Optional[str] = Field(
        None, description="Label for XTRACT plot file (max 16 chars)"
    )
    mp: Optional[float] = Field(
        None, description="material property set (see RMPNS statement)"
    )
    # Method 1 (direct area input):
    ar: Optional[float] = Field(
        None, description="Cross-sectional area per unit length [m²/m] (Method 1)"
    )
    # Method 2 (calculated area based on diameter and spacing):
    nr: Optional[int] = Field(
        None, description="Number of rebars in bundle (default 1, Method 2)"
    )
    di: Optional[float] = Field(
        None,
        description="shear reinforcement diameter (also input if MCFT is used as design code [mm}])",
    )
    c1: Optional[float] = Field(
        None, description="bar distance direction 1 [mm] (Method 2)"
    )
    c2: Optional[float] = Field(
        None, description="bar distance direction 2 [mm] (Method 2)"
    )

    comment: Optional[str] = Field(None, description="Comment to append at end of line")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this RETYP statement."""
        return str(self.id)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=["id", "mp", "ar", "di", "nr", "c1", "c2", "lb"],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
            comment=self.comment,
        )
