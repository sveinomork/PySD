from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import Field

from .statement_base import StatementBase


class SHAXE(StatementBase):
    """
    Define local 1-2-3 axes for finite element sections using three mutually exclusive modes.

    Mode 1 provides explicit X1, X2, X3 vectors. Mode 2 uses point-axis definition where
    3-axis points toward P and 1-axis approximates A-vector. Mode 3 creates polar coordinate
    system with radial 1-axis, tangential 2-axis, and normal 3-axis.

    ### Examples
    ```python
    # Mode 1: Explicit axes definition
    SHAXE(pa="PLATE", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, 1))
    # -> "SHAXE PA=PLATE X1=1.000,0.000,0.000 X2=0.000,1.000,0.000 X3=0.000,0.000,1.000"

    # Mode 2: Point-axis definition for cylinder walls
    SHAXE(pa="WALL", xp=(0, 0, 0), xa=(0, 0, 1), al=-90, fs=(1, 10))
    # -> "SHAXE PA=WALL XP=0.000,0.000,0.000 XA=0.000,0.000,1.000 AL=-90.000 FS=1-10"

    # Mode 3: Center-axis definition for radial arrangement
    SHAXE(pa="DOME", xc=(0, 0, 0), xa=(0, 0, 1), fs=(1, 10), hs=(15, 50))
    # -> "SHAXE PA=DOME XC=0.000,0.000,0.000 XA=0.000,0.000,1.000 FS=1-10 HS=15-50"
    ```

    ### Parameters
    pa : str
        Structural part name to which the axes apply. Must match existing part name.

    x1 : Optional[Tuple[float, float, float]], default=None
        XYZ components of the local 1-axis (Mode 1 only).

    x2 : Optional[Tuple[float, float, float]], default=None
        XYZ components of the local 2-axis (Mode 1 only).

    x3 : Optional[Tuple[float, float, float]], default=None
        XYZ components of the local 3-axis (Mode 1 only).

    xp : Optional[Tuple[float, float, float]], default=None
        Coordinates of point P - target for 3-axis direction (Mode 2 only).

    xa : Optional[Tuple[float, float, float]], default=None
        Direction vector A components. Approximate 1-axis direction in Mode 2,
        shell normal direction in Mode 3.

    xc : Optional[Tuple[float, float, float]], default=None
        Center point C coordinates for radial/polar systems (Mode 3 only).

    fs : Optional[Tuple[int, int]], default=None
        F-section index range (i1, i2). If None, applies to all F-sections.

    hs : Optional[Tuple[int, int]], default=None
        H-section index range (j1, j2). If None, applies to all H-sections.

    sy : Optional[Literal["R", "L"]], default=None
        Handedness of axis system. "R" = right-hand (default), "L" = left-hand.

    al : Optional[float], default=None
        Rotation angle in degrees for adjusting 1-axis direction toward 2-axis.

    ### Notes
    - Exactly one mode must be active: either (x1,x2,x3) OR (xp,xa) OR (xc,xa)
    - Mode 1 requires all three vectors x1, x2, x3 to be specified
    - Mode 2 requires both xp and xa parameters
    - Mode 3 requires both xc and xa parameters
    - PA parameter must reference existing part name from SHSEC statements
    - Vector components use 3 decimal places for precision
    """

    # ─── Common Parameters ──────────────────────────────────────────────

    pa: str = Field(..., description="PA: Structural part name to which the axes apply")

    fs: Optional[Tuple[int, int]] = Field(
        None,
        description="FS: F-section index range (i1, i2). If omitted, applies to all F-sections",
    )

    hs: Optional[Tuple[int, int]] = Field(
        None,
        description="HS: H-section index range (j1, j2). If omitted, applies to all H-sections",
    )

    # ─── Mode 1: Explicit Axes ──────────────────────────────────────────

    x1: Optional[Tuple[float, float, float]] = Field(
        None, description="X1: XYZ components of the local 1-axis"
    )

    x2: Optional[Tuple[float, float, float]] = Field(
        None, description="X2: XYZ components of the local 2-axis"
    )

    x3: Optional[Tuple[float, float, float]] = Field(
        None, description="X3: XYZ components of the local 3-axis"
    )

    # ─── Mode 2: Point-Axis Definition ─────────────────────────────────

    xp: Optional[Tuple[float, float, float]] = Field(
        None, description="XP: Coordinates of point P (target for 3-axis direction)"
    )

    xa: Optional[Tuple[float, float, float]] = Field(
        None,
        description="XA: Components of direction vector A (approximate direction for 1-axis in Mode 2; shell normal in Mode 3)",
    )

    # ─── Mode 3: Center-Axis (Polar Coordinate System) ─────────────────

    xc: Optional[Tuple[float, float, float]] = Field(
        None,
        description="XC: Coordinates of center point C for radial/polar systems (used in Mode 3)",
    )

    # ─── Optional Axes Modifiers ───────────────────────────────────────

    sy: Literal["R", "L"] = Field(
        None,
        description="SY: Handedness of the axis system. 'R' = right-hand (default), 'L' = left-hand",
    )

    al: float = Field(
        None,
        description="AL: Rotation angle (degrees) for adjusting the 1-axis direction toward the 2-axis",
    )

    @property
    def identifier(self) -> str:
        """Get unique identifier for this SHAXE statement."""
        return self._build_identifier(field_order=["pa", "hs", "fs"], add_hash=True)

    def _build_input_string(self) -> None:
        self.input = self._build_string_generic(
            field_order=[
                "pa",
                "fs",
                "hs",
                "x1",
                "x2",
                "x3",
                "xp",
                "xa",
                "xc",
                "sy",
                "al",
            ],
            float_precision=3,  # Use 3 decimal places for better readability
        )
