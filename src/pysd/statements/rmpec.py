
from __future__ import annotations
from typing import Optional, Literal
from pydantic import  Field

from .statement_base import StatementBase


class RMPEC(StatementBase):
    """
    Define rebar material property sets according to Eurocode 2.
    The ID is related to the MP statement in the RETYP statement.

    ### Validation Rules

    1. **ID Range**: Must be between 1 and 99999999
    2. **Density Range**: Must be positive value (typically around 7850 kg/m3 for steel)
    3. **Material Factors**: Must be positive values
    4. **Uniqueness**: ID must be unique within container
    """
    # Required for identification
    id: int = Field(..., description="Material property set ID (1-99999999)")
    
    # Material properties
    gr: Optional[float] = Field(None, description="Steel grade, eg. 500 [kPa]")
    esk: Optional[float] = Field(None, description="Modulus of elasticity [kPa] [default 200*1.0E6]")
    fyk: Optional[float] = Field(None, description="Yield strength [kPa]")
    fsk: Optional[float] = Field(None, description="Ultimate strength [kPa]")

    den: Optional[float] = Field(None, description="Steel density [kg/m3]")

    # Design properties - ULS
    mfu: Optional[float] = Field(None, description="Design material factor ULS [default 1.15]")
    epu: Optional[float] = Field(None, description="Ultimate tensile strain ULS [m/m] [default 0.010]")

    # Design properties - ALS
    mfa: Optional[float] = Field(None, description="Design material factor ALS [default 1.00]")
    epa: Optional[float] = Field(None, description="Ultimate tensile strains ALS [m/m] [default 0.010]")

    # Design properties - SLS
    mfs: Optional[float] = Field(None, description="Design material factor SLS [default 1.00]")
    eps: Optional[float] = Field(None, description="Ultimate tensile strain SLS [m/m] [default 0.010]")

    # Print option
    pri: Optional[Literal['']] = Field(None, description="Print option")
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RMPEC statement."""
        return str(self.id)

   

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri is not None:
            # Special case: print option only
            self.start_string()
            self.add_param("TAB","" )
            return

        self.input = self._build_string_generic(
            field_order=['id', 'gr', 'rh', 'esk', 'fyk', 'fsk', 'den', 'mfu', 'epu', 'mfa', 'epa', 'mfs', 'eps'],                
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
        )
    