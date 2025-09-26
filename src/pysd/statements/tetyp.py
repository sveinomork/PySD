from __future__ import annotations
from typing import Optional
from pydantic import Field
from .statement_base import StatementBase


class TETYP(StatementBase):
    """
    define prestressing (tendon) layer types to be referenced in
    TELOC statement.



    ### Examples:

    ```python
    # Method 1 (direct area input):
    SRTYP(id=1, mp=1, ar=2094e-6)
      → 'SRTYP ID=1 MP=1 AR=0.002094'

    ```
    """

    # Required for identification
    id: int = Field(..., description="Type number (max 8 digits)")

    # optional parameters
    mp: Optional[int] = Field(
        None, description="material property set (see TEMAT statement)"
    )
    ar: Optional[float] = Field(
        None, description="Cross-sectional area per unit length [m²/m] (Method 1)"
    )
    eo: Optional[float] = Field(None, description="Initial strain [m]")
    os: Optional[float] = Field(
        None,
        description="face 1/2: distance concrete face-layer center face 0: x3-coordinate layer centre [mm]",
    )

    comment: Optional[str] = Field(None, description="Comment to append at end of line")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this RETYP statement."""
        return str(self.id)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=["id", "mp", "ar", "eo", "os"],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
            comment=self.comment,
        )
