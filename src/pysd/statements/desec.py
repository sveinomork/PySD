from __future__ import annotations
from typing import Optional, Tuple, Union
from pydantic import Field
from .statement_base import StatementBase


class DESEC(StatementBase):
    """
    Define design sections and their geometry for structural analysis workflows.

    Supports multiple analysis cases: section geometry definition without OLC/FE files,
    section storage on DEC-file with OLC/FE results, and geometry redefinition for CSM analysis.

    ### Examples
    ```python
    # Basic design section with part name only
    DESEC(pa="WALL")
    # -> "DESEC PA=WALL"

    # Design section with thickness and coordinates
    DESEC(pa="PLATE", th=0.25, x=10.5, y=5.2, z=0.0)
    # -> "DESEC PA=PLATE TH=0.250000 X=10.500000 Y=5.200000 Z=0.000000"

    # Design section with section ranges and thickness gradients
    DESEC(pa="SHELL", fs=(1, 10), hs=(5, 15), th=0.3, t11=0.01, t22=-0.005)
    # -> "DESEC PA=SHELL FS=1-10 HS=5-15 TH=0.300000 T11=0.010000 T22=-0.005000"
    ```

    ### Parameters
    pa : str
        Structural part identity (max 8 characters). Must match existing part name.

    fs : Optional[Union[int, Tuple[int, int]]], default=None
        F-section range or single section. If None, applies to all F-sections.
        Examples: 5 (single section) or (1, 30) (range).

    hs : Optional[Union[int, Tuple[int, int]]], default=None
        H-section range or single section. If None, applies to all H-sections.
        Examples: 2 (single section) or (1, 5) (range).

    th : Optional[float], default=None
        Shell thickness in meters. Default value is 0 if not specified.

    t11 : Optional[float], default=None
        Shell thickness gradient ∂t1/∂x1. Default value is 0.

    t12 : Optional[float], default=None
        Shell thickness gradient ∂t1/∂x2. Default value is 0.

    t21 : Optional[float], default=None
        Shell thickness gradient ∂t2/∂x1. Default value is 0.

    t22 : Optional[float], default=None
        Shell thickness gradient ∂t2/∂x2. Default value is 0.

    x : Optional[float], default=None
        X-coordinate in global coordinate system. Default value is 0.

    y : Optional[float], default=None
        Y-coordinate in global coordinate system. Default value is 0.

    z : Optional[float], default=None
        Z-coordinate in global coordinate system. Default value is 0.

    ### Notes
    - Case 1: Without OLC/FE result file, DESEC defines section geometry
    - Case 2: With OLC/FE result file, DESEC stores sections on DEC-file
    - Case 3: In CSM analysis, DESEC may redefine existing geometry
    - PA parameter must reference existing structural part from other statements
    - All coordinate and thickness values use 6 decimal places for precision
    - Section ranges can be single values or tuples for range specification
    """

    pa: str = Field(..., description="Structural part identity (max 8 characters)")

    fs: Optional[Union[int, Tuple[int, int]]] = Field(
        None, description="F-section range or single section"
    )
    hs: Optional[Union[int, Tuple[int, int]]] = Field(
        None, description="H-section range or single section"
    )
    th: Optional[float] = Field(
        None, description="Shell thickness in meters, default=0"
    )
    t11: Optional[float] = Field(None, description="Shell thickness gradient ∂t1/∂x1")
    t12: Optional[float] = Field(None, description="Shell thickness gradient ∂t1/∂x2")
    t21: Optional[float] = Field(None, description="Shell thickness gradient ∂t2/∂x1")
    t22: Optional[float] = Field(None, description="Shell thickness gradient ∂t2/∂x2")
    x: Optional[float] = Field(None, description="X-coordinate")
    y: Optional[float] = Field(None, description="Y-coordinate")
    z: Optional[float] = Field(None, description="Z-coordinate")

    @property
    def identifier(self) -> str:
        """Generate unique ID and input string for this DESEC statement."""

        return self._build_identifier(field_order=["pa", "hs", "fs"], add_hash=True)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=[
                "pa",
                "hs",
                "fs",
                "th",
                "t11",
                "t12",
                "t21",
                "t22",
                "x",
                "y",
                "z",
            ],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
        )
