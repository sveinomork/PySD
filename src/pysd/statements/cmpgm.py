from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import Field

from .statement_base import StatementBase


class CMPGM(StatementBase):
    """
    define concrete material property sets according to NS 3473.
    Most of the parameters are optional. Values related to the chosen concrete quality according
    to NS 3473 will then be used.

    """

    # Required for identification
    id: Optional[int] = Field(None, description="Material property set ID (1-99999999)")

    # Concrete grade definition
    gr: Optional[str] = Field(
        None, description="GR=Bxx Concrete grade, legal range C-grade 10-95, LC-grade 12-75 (integer) [MPa]"
    )
    epu: Optional[float] = Field(
        None, description="Ultimate compression strain ULS/ALS [m/m]"
    )
    ftc: Optional[float] = Field(
        None, description="Tensile strength cracing of concrete [kPa].ftc=0-> no crack check, ftc>0-> crack check"
    )

    rh: Optional[float] = Field(
        None, description="RH=rho Density for lightweight concrete (1150-2150 kg/m3)"
    )
    ags: Optional[float] = Field(
        None, description="Maximum aggregate particle. Used in shear stress calculations in cracks [m]"
    )

     # Design properties with defaults
    mfu: Optional[float] = Field(None, description="Design material factor (ULS)")
    mfa: Optional[float] = Field(None, description="Design material factor (ALS)")
    mfs: Optional[float] = Field(None, description="Design material factor (SLS/CRW)")

    sp: Optional[float] = Field(
        default=None, description="reference to fixed crack spacing data CRASP stmts.")


    # Location parameters
    la: Optional[int] = Field(None, description="LAREA id-number")
    pa: Optional[str] = Field(None, description="Structural part (max 8 chars)")
    fs: Optional[Tuple[int, int]] = Field(None, description="F-section range")
    hs: Optional[Tuple[int, int]] = Field(None, description="H-section range")

    # Print options
    pri: Optional[Literal["", "TAB"]] = Field(None, description="Print options")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this GRECO statement."""
        return self.id

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri is not None:
            # Special case: print option only
            self.start_string()
            self.add_param("PRI", "TAB")
            return

        self.input = self._build_string_generic(
            field_order=[
                "id",
                "gr",
                "epu",
                "ftc",
                "ags",
                "mfu",
                "mfa",
                "mfs",
                "sp",
                "la",
                "pa",
                "fs",
                "hs",
            ],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
        )
