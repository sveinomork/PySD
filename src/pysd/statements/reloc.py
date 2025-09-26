from __future__ import annotations
from typing import Optional, Tuple, Union, Literal
from pydantic import Field
from .statement_base import StatementBase


class RELOC(StatementBase):
    """
    Define reinforcement bar placement and configuration within shell sections.

    Links to rebar types defined by RETYP statements and specifies placement through
    part names, section ranges, or location areas. Controls cover, face position,
    direction, and layer offsets.

    ### Examples

    ```python
    # Rebar in specific section range with face and direction
    RELOC(id='X11', rt=(16101, 20101), fa=1, fs=(5, 10), hs=3)
    # → "RELOC ID=X11 RT=16101-20101 FA=1 FS=5-10 HS=3"

    # Rebar with specific angle across entire model
    RELOC(id='Y21', rt=20101, fa=2, al=90)
    # → "RELOC ID=Y21 RT=20101 FA=2 AL=90"

    # Rebar defined by location area with custom cover
    RELOC(id='B1', rt=(101, 101), la=5, cov=50.0)
    # → "RELOC ID=B1 RT=101 COV=50.0 LA=5"

    # Center placement with part specification
    RELOC(id="Y02", pa="VEGG", rt=2, fa=0, al=90)
    # → "RELOC ID=Y02 PA=VEGG RT=2 FA=0 AL=90"
    ```

    ### Parameters

    id : str
        Location identity (max 4 characters). Must be unique within model.

    rt : int | Tuple[int, int]
        Rebar type number or range (rt1, rt2). References RETYP statement ID.
        Single value or tuple range, e.g., 101 or (101, 105).

    cov : Optional[float], default=None
        Rebar cover in millimeters. Overrides C2 value from RETYP statement.
        Must be positive value when specified.

    fa : Optional[Literal[0, 1, 2]], default=None
        Shell face placement:
        - 0: Center of shell thickness
        - 1: Face 1 (typically bottom/inner face)
        - 2: Face 2 (typically top/outer face)

    al : Optional[float], default=None
        Direction angle in degrees (-90 to +90).
        0° = local X-direction, 90° = local Y-direction.

    os : Optional[float], default=None
        Offset to layer center in meters. Overrides offset from RETYP statement.
        Positive values move toward face 2, negative toward face 1.

    rp : Optional[Literal["12", "XY", "XZ", "YZ"]], default=None
        Reference plane for direction angle AL:
        - "12": Local shell coordinate system
        - "XY", "XZ", "YZ": Global coordinate planes

    pa : Optional[str], default=None
        Structural part identity (name). If None, applies to all parts.
        Must match existing part name in model.

    fs : Optional[int | Tuple[int, int]], default=None
        F-section number or range (f1, f2). Mutually exclusive with la.

    hs : Optional[int | Tuple[int, int]], default=None
        H-section number or range (h1, h2). Mutually exclusive with la.

    la : Optional[int], default=None
        Section set number from LAREA statement.
        Mutually exclusive with pa, fs, hs parameters.

    ### Notes

    - Location can be specified by part/sections (pa/fs/hs) OR location area (la), not both
    - Cover and offset parameters override corresponding RETYP values when specified
    - Default face placement (fa=None) uses RETYP statement's face specification
    - Direction angle uses shell's local coordinate system unless rp specifies otherwise
    """

    # Required fields
    id: str = Field(..., description="Location identity (max 4 characters)")
    rt: Union[int, Tuple[int, int]] = Field(
        ..., description="Rebar type number or range (rt1, rt2), see RETYP"
    )

    # Optional parameters
    cov: Optional[float] = Field(
        None, description="Rebar cover in mm. Overrides C2 from RETYP"
    )
    fa: Optional[Literal[0, 1, 2]] = Field(
        None, description="Shell face (0=center, 1=face1, 2=face2)"
    )
    al: Optional[float] = Field(
        None, description="Direction angle in degrees (-90 to +90)"
    )
    os: Optional[float] = Field(
        None,
        description="Offset to layer center in meters. Overrides offset from RETYP",
    )
    rp: Optional[Literal["12", "XY", "XZ", "YZ"]] = Field(
        None, description="Reference plane for the direction angle AL"
    )

    # Location area alternative 1
    pa: Optional[str] = Field(
        None, description="Part identity (name). Default applies to all parts"
    )
    fs: Optional[Union[int, Tuple[int, int]]] = Field(
        None, description="F-section number or range (f1, f2)"
    )
    hs: Optional[Union[int, Tuple[int, int]]] = Field(
        None, description="H-section number or range (h1, h2)"
    )

    # Location area alternative 2
    la: Optional[int] = Field(
        None,
        description="Section set number from LAREA statement. Mutually exclusive with pa, fs, hs",
    )

    @property
    def identifier(self) -> str:
        """Get unique identifier for this RELOC statement."""
        return f"{self.id}_{self.pa}_{self.fs}_{self.hs}"

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=["id", "rt", "fa", "al", "os", "rp", "pa", "fs", "hs", "la"],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
        )
