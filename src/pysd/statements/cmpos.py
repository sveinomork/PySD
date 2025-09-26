from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import Field

from .statement_base import StatementBase


class CMPOS(StatementBase):
    """
    define concrete material property sets according to DNV-ST-C502 [2].
    DEPAR D_COD=OS statement must also be included in input file. Most of the
    parameters are optional. Values related to the chosen concrete quality according
    to DNV-ST-C502 will then be used.


    """

    # Required for identification
    id: Optional[int] = Field(None, description="Material property set ID (1-99999999)")

    # Concrete grade definition
    gr: Optional[str] = Field(
        None, description="GR=Cxx Concrete grade, legal range C-grade 25-90, LC-grade 25-35 (integer) [MPa]"
    )
    rh: Optional[float] = Field(
        None, description="RH=rho Density for lightweight concrete (1150-2150 kg/m3)"
    )
    fig: Optional[Tuple[int, int]] = Field(
        None, description="Define non-linear or linear material curve."
    )
    fcn: Optional[float] = Field(None, description="In situ compression strength [kPa]")
    ecn: Optional[float] = Field(None, description="Secant modulus of elasticity [kPa]")
    
    epu: Optional[float] = Field(
        None, description="Ultimate compression strain ULS/ALS [m/m]"
    )

    csd: Optional[float] = Field(
        None, description="Design compression strengtherning factor"
    )
    tsp: Optional[float] = Field(None, description="Design fc2d = fcd/(0.8+tsp*ept)")
    tsd: Optional[float] = Field(None, description="Design min(fc2d) = fac*fcd")

    ftk: Optional[float] = Field(
        None, description="characteristic tensile strength (CRW)"
    )
    ftn: Optional[float] = Field(
        None, description="In situ tensile strength (ULS/ALS/SLS/CRW)"
    )

    ac1: Optional[float] = Field(
        None,
        description="Reduced compression strength for ULS, ALS and SLS limit states",
    )
    ac2: Optional[float] = Field(
        None, description="Reduced compression strength for FLS"
    )

    # Design properties with defaults
    mfu: Optional[float] = Field(None, description="Design material factor (ULS)")
    mfa: Optional[float] = Field(None, description="Design material factor (ALS)")
    mff: Optional[float] = Field(None, description="Design material factor (FLS)")
    mfs: Optional[float] = Field(None, description="Design material factor (SLS/CRW)")

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
                "rh",
                "fig",
                "fcn",
                "ecn",
                "epu",
                "csd",
                "tsp",
                "tsd",
                "ftk",
                "ftn",
                "ac1",
                "ac2",
                "mfu",
                "mfa",
                "mff",
                "mfs",
                "la",
                "pa",
                "fs",
                "hs",
            ],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
        )
