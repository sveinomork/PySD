from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import Field

from .statement_base import StatementBase

class SHAXE(StatementBase):
    """
    Define local 1-2-3 axes for FE sections based on one of three mutually exclusive modes:

    **Mode 1 (Explicit Axes):**
        Provide X1, X2, X3 vectors directly as xyz-components.

    **Mode 2 (Point-Axis Definition):**
        Define axis system based on a point P and a direction vector A.
        3-axis points toward P, 1-axis approximates A-vector.

    **Mode 3 (Center-Axis Definition - Polar):**
        Define local axes for radial geometry using center point C and direction vector A.
        1-axis is radial, 2-axis tangential, 3-axis normal to shell plane.
    
    Only one mode may be active per instance.

    Examples:
    Independent of section location:
        >>> shaxe1 = SHAXE(pa="A1", x1=(1, 0, 0), x2=(0, 1, 0), x3=(0, 0, -1), fs=(1, 10))
        >>> print(shaxe1.input)
        'SHAXE PA=A1 X1=1,0,0 X2=0,1,0 X3=0,0,-1 FS=1-10'

    Cylinder walls:
        >>> shaxe2 = SHAXE(pa="A2", xp=(0, 0, 0), xa=(0, 0, 1), al=-90, fs=(1, 10), hs=(1, 5))
        >>> print(shaxe2.input)  
        'SHAXE PA=A2 XP=0,0,0 XA=0,0,1 AL=-90 FS=1-10 HS=1-5'

    Circlar plate /dome with radial arrangement:
        >>> shaxe3 = SHAXE(pa="A3", xc=(0, 0, 0), xa=(0, 0, 1), fs=(1, 10), hs=(15, 50))
        >>> print(shaxe3.input)  
        'SHAXE PA=A3 XC=0,0,0 XA=0,0,1 FS=1-10 HS=15-50'

    ### Validation Rules

    1. **PA Format**: Must be provided and non-empty
    2. **Mode Validation**: Exactly one of the three modes must be active
    3. **Vector Components**: All vector components must be valid floats
    4. **Cross-Reference**: PA must exist as a part name in SHSEC statements
    """

    # ─── Common Parameters ──────────────────────────────────────────────

    pa: str = Field(..., description="PA: Structural part name to which the axes apply")

    fs: Optional[Tuple[int, int]] = Field(None, description="FS: F-section index range (i1, i2). If omitted, applies to all F-sections")

    hs: Optional[Tuple[int, int]] = Field(None, description="HS: H-section index range (j1, j2). If omitted, applies to all H-sections")

    # ─── Mode 1: Explicit Axes ──────────────────────────────────────────

    x1: Optional[Tuple[float, float, float]] = Field(None, description="X1: XYZ components of the local 1-axis")

    x2: Optional[Tuple[float, float, float]] = Field(None, description="X2: XYZ components of the local 2-axis")

    x3: Optional[Tuple[float, float, float]] = Field(None, description="X3: XYZ components of the local 3-axis")

    # ─── Mode 2: Point-Axis Definition ─────────────────────────────────

    xp: Optional[Tuple[float, float, float]] = Field(None, description="XP: Coordinates of point P (target for 3-axis direction)")

    xa: Optional[Tuple[float, float, float]] = Field(None, description="XA: Components of direction vector A (approximate direction for 1-axis in Mode 2; shell normal in Mode 3)")

    # ─── Mode 3: Center-Axis (Polar Coordinate System) ─────────────────

    xc: Optional[Tuple[float, float, float]] = Field(None, description="XC: Coordinates of center point C for radial/polar systems (used in Mode 3)")

    # ─── Optional Axes Modifiers ───────────────────────────────────────

    sy: Literal["R", "L"] = Field(None, description="SY: Handedness of the axis system. 'R' = right-hand (default), 'L' = left-hand")

    al: float = Field(None, description="AL: Rotation angle (degrees) for adjusting the 1-axis direction toward the 2-axis")

 
   

    @property
    def identifier(self) -> str:
        """Get unique identifier for this SHAXE statement."""
        return self._build_identifier(field_order=['pa', 'hs', 'fs'], add_hash=True)
        


   
    def _build_input_string(self) -> None:
         self.input = self._build_string_generic(
                field_order=['pa', 'fs', 'hs', 'x1', 'x2', 'x3', 'xp', 'xa', 'xc', 'sy', 'al'],               
                float_precision=3  # Use 3 decimal places for better readability
            )
       
    
    
