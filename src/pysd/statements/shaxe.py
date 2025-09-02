from dataclasses import dataclass, field
from typing import Optional, Tuple, Literal


@dataclass
class SHAXE:
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
        >>> print(SHAXE.input)
        'SHAXE PA=A1 X1=1,0,0 X2=0,1,0 X3=0,0,-1 FS=1-10'

    Cylinder walls:
        >>> shaxe2 = SHAXE(pa="A2", xp=(0, 0, 0), xa=(0, 0, 1), al=-90, fs=(1, 10), hs=(1, 5))
        >>> print(SHAXE.input)  
        'SHAXE PA=A2 XP=0,0,0 XA=0,0,1 AL=-90 FS=1-10 HS=1-5'

    Circlar plate /dome with radial arrangement:
        >>> shaxe3 = SHAXE(pa="A3", xc=(0, 0, 0), xa=(0, 0, 1), fs=(1, 10), hs=(15, 50))
        >>> print(SHAXE.input)  
        'SHAXE PA=A3 XC=0,0,0 XA=0,0,1 FS=1-10 HS=15-50'


    
    """

    # ─── Common Parameters ──────────────────────────────────────────────

    pa: str 
    """PA: Structural part name to which the axes apply."""

    fs: Optional[Tuple[int, int]] = None
    """FS: F-section index range (i1, i2). If omitted, applies to all F-sections."""

    hs: Optional[Tuple[int, int]] = None
    """HS: H-section index range (j1, j2). If omitted, applies to all H-sections."""

    # ─── Mode 1: Explicit Axes ──────────────────────────────────────────

    x1: Optional[Tuple[float, float, float]] = None
    """X1: XYZ components of the local 1-axis."""

    x2: Optional[Tuple[float, float, float]] = None
    """X2: XYZ components of the local 2-axis."""

    x3: Optional[Tuple[float, float, float]] = None
    """X3: XYZ components of the local 3-axis."""

    # ─── Mode 2: Point-Axis Definition ─────────────────────────────────

    xp: Optional[Tuple[float, float, float]] = None
    """XP: Coordinates of point P (target for 3-axis direction)."""

    xa: Optional[Tuple[float, float, float]] = None
    """XA: Components of direction vector A (approximate direction for 1-axis in Mode 2; shell normal in Mode 3)."""

    # ─── Mode 3: Center-Axis (Polar Coordinate System) ─────────────────

    xc: Optional[Tuple[float, float, float]] = None
    """XC: Coordinates of center point C for radial/polar systems (used in Mode 3)."""

    # ─── Optional Axes Modifiers ───────────────────────────────────────

    sy: Optional[Literal["R", "L"]] = "R"
    """SY: Handedness of the axis system. 'R' = right-hand (default), 'L' = left-hand."""

    al: Optional[float] = 0.0
    """AL: Rotation angle (degrees) for adjusting the 1-axis direction toward the 2-axis."""

    # Key for dictionary storage - computed during initialization
    key: str = field(init=False)
    
    # ─── Validation ────────────────────────────────────────────────────
    
    input: str = field(init=False, default="SHAXE")

    def __post_init__(self):
        # Generate the key
        if not self.pa:
            raise ValueError("PA (structural part name) is required")
            
        key_parts = [f"{self.pa}"]
        if self.fs is not None:
            key_parts.append(f"{self.fs[0]}-{self.fs[1]}")
        if self.hs is not None:
            key_parts.append(f"{self.hs[0]}-{self.hs[1]}")
        self.key = "_".join(key_parts)
            
        # Establish method of defining axes
        mode1 = all([self.x1, self.x2, self.x3])
        mode2 = all([self.xp,self.xa])
        mode3 = all([self.xc,self.xa])

        mode_count = sum([mode1, mode2, mode3])
        if mode_count == 0:
            raise ValueError("SHAXE must be initialized using one of the 3 alternatives: "
                            "(x1/x2/x3), (xp/xa), or (xc/xa).")
        if mode_count > 1:
            raise ValueError("Only one SHAXE mode may be used at a time (fields are mutually exclusive).")

        if mode1:
            if not all([self.x1, self.x2, self.x3]):
                raise ValueError("Mode 1 requires all of x1, x2, and x3 to be defined.")
        elif mode2:
            if not self.xp or not self.xa:
                raise ValueError("Mode 2 requires xp and xa to be defined.")
        elif mode3:
            if not self.xc or not self.xa:
                raise ValueError("Mode 3 requires xc and xa to be defined.")

        # Then build the input string
        parts = ["SHAXE"]

       
        
        parts.append(f"PA={self.pa}")
        
        if self.fs is not None:
            parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
            
        if self.hs is not None:
            parts.append(f"HS={self.hs[0]}-{self.hs[1]}")

        # Add mode-specific parameters
        if mode1:
            assert self.x1 is not None and self.x2 is not None and self.x3 is not None
            parts.append(f"X1={self.x1[0]:.4g},{self.x1[1]:.4g},{self.x1[2]:.4g}")
            parts.append(f"X2={self.x2[0]:.4g},{self.x2[1]:.4g},{self.x2[2]:.4g}")
            parts.append(f"X3={self.x3[0]:.4g},{self.x3[1]:.4g},{self.x3[2]:.4g}")
        elif mode2:
            assert self.xp is not None and self.xa is not None
            parts.append(f"XP={self.xp[0]:.4g},{self.xp[1]:.4g},{self.xp[2]:.4g}")
            parts.append(f"XA={self.xa[0]:.4g},{self.xa[1]:.4g},{self.xa[2]:.4g}")
        elif mode3:
            assert self.xc is not None and self.xa is not None
            parts.append(f"XC={self.xc[0]:.4g},{self.xc[1]:.4g},{self.xc[2]:.4g}")
            parts.append(f"XA={self.xa[0]:.4g},{self.xa[1]:.4g},{self.xa[2]:.4g}")

        # Add optional modifiers if they differ from defaults
        if self.sy != "R":
            parts.append(f"SY={self.sy}")
            
        if self.al != 0.0:
            parts.append(f"AL={self.al}")

        # Join all parts with spaces
        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input
