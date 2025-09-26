from __future__ import annotations
from typing import Optional, Literal
from pydantic import Field

from .statement_base import StatementBase


class RMPNS(StatementBase):
    """
    Define rebar material property sets according to NS 3473. 
    The ID is related to the MP statement in the RETYP statement. 
    The other parameters are optionally. Values belonging to the chosen steel quality 
    according to NS 3473 will then be used.


    """

    # Required for identification
    id: int = Field(..., description="Material property set ID (1-99999999)")

    # Material properties
    gr: Optional[float] = Field(None, description="Steel grade, eg. 500 [kPa]")
    esk: Optional[float] = Field(
        None, description="Modulus of elasticity [kPa] [default 200*1.0E6]"
    )
    fyk: Optional[float] = Field(None, description="Yield strength [kPa]")
    fsk: Optional[float] = Field(None, description="Ultimate strength [kPa]")

    den: Optional[float] = Field(None, description="Steel density [kg/m3]")

    # Design properties - ULS
    mfu: Optional[float] = Field(
        None, description="Design material factor ULS [default 1.15]"
    )
    epu: Optional[float] = Field(
        None, description="Ultimate tensile strain ULS [m/m] [default 0.010]"
    )

    # Design properties - ALS
    mfa: Optional[float] = Field(
        None, description="Design material factor ALS [default 1.00]"
    )
    epa: Optional[float] = Field(
        None, description="Ultimate tensile strains ALS [m/m] [default 0.010]"
    )

    # Design properties - SLS
    mfs: Optional[float] = Field(
        None, description="Design material factor SLS [default 1.00]"
    )
    eps: Optional[float] = Field(
        None, description="Ultimate tensile strain SLS [m/m] [default 0.010]"
    )
    mff: Optional[float] = Field(
        None, description="Design material factor FLS [default 1.10]"
    )
    ccf: Optional[float] = Field(
        None, description="compression capacity factor ULS,ALS [default 1.0]" 
    )
    # Print option
    pri: Optional[Literal[""]] = Field(None, description="Print option")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this RMPEC statement."""
        return str(self.id)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri is not None:
            # Special case: print option only
            self.start_string()
            self.add_param("TAB", "")
            return

        self.input = self._build_string_generic(
            field_order=[
                "id",
                "gr",
                "esk",
                "fyk",
                "fsk",
                "den",
                "mfu",
                "epu",
                "mfa",
                "epa",
                "mfs",
                "eps",
                "mff",
                "ccf"
            ],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=12,
        )
