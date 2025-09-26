from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import  Field

from .statement_base import StatementBase


class CMPEC(StatementBase):
    """
    Define concrete material property sets according to EuroCode 2.
    Most parameters are optional. Values belonging to the chosen concrete quality will be used if not specified.

    ### Validation Rules

    1. **ID Range**: Must be between 1 and 99999999
    2. **GR Format**: Must start with 'B' and be between B12-B90
    3. **RH Range**: Density must be between 1150-2150 kg/m3 for lightweight concrete
    4. **PA Length**: Structural part cannot exceed 8 characters
    5. **Uniqueness**: ID must be unique within container
    """
    # Required for identification
    id: Optional[int] = Field(None, description="Material property set ID (1-99999999)")
    
    # Concrete grade definition
    gr: Optional[str] = Field(None, description="Concrete grade, legal range 12-90 (integer) [MPa]")
    rh: Optional[float] = Field(None, description="Density for lightweight concrete (1150-2150 kg/m3)")
    
    # Single data parameters (when no concrete grade is defined)
    fck: Optional[float] = Field(None, description="Cylinder compression strength after 28 days [Pa]")
    ecm: Optional[float] = Field(None, description="Secant modulus of elasticity [kPa]")
    fcn: Optional[float] = Field(None, description="In situ compression strength [kPa]")
    ftm: Optional[float] = Field(None, description="In situ tensile strength [kPa]")
    acc: Optional[float] = Field(None, description="Coefficient for longterm effects")
    
    # Figure 3.3 related parameters
    exp: Optional[float] = Field(None, description="Exponent n in equation 3.17")
    ec2: Optional[float] = Field(None, description="Strain at start stress plateau")
    ecu: Optional[float] = Field(None, description="Ultimate strain")
    
    # Design properties with defaults
    mfu: Optional[float] = Field(None, description="Design material factor (ULS)")
    mfa: Optional[float] = Field(None, description="Design material factor (ALS)")
    mfs: Optional[float] = Field(None, description="Design material factor (SLS/CRW)")
    k1c: Optional[float] = Field(None, description="Shear parameter k1 for compression")
    k1t: Optional[float] = Field(None, description="Shear parameter k1 for tension")
    k2: Optional[float] = Field(None, description="Shear parameter k2")
    cot: Optional[float] = Field(None, description="Shear cot(theta)")
    
    # Reduced compression strength parameters
    tsp: Optional[float] = Field(None, description="Design fc2d = fcd/(0.8+tsp*ept)")
    tsd: Optional[float] = Field(None, description="Design min(fc2d) = fac*fcd")
    
    # Location parameters
    la: Optional[int] = Field(None, description="LAREA id-number")
    pa: Optional[str] = Field(None, description="Structural part (max 8 chars)")
    fs: Optional[Tuple[int, int]] = Field(None, description="F-section range")
    hs: Optional[Tuple[int, int]] = Field(None, description="H-section range")
    
    # Print options
    pri: Optional[Literal['', 'TAB']] = Field(None, description="Print options")
    

    @property
    def identifier(self) -> str:
        """Get unique identifier for this GRECO statement."""
        return self.id
    
    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri is not None:
            # Special case: print option only
            self.start_string()
            self.add_param("PRI","TAB" )
            return

        self.input = self._build_string_generic(
            field_order=['id', 'gr', 'rh', 'fck', 'ecm', 'fcn', 'ftm', 'acc', 'exp', 'ec2', 'ecu', 'mfu',
                          'mfa', 'mfs', 'k1c', 'k1t', 'k2', 'cot', 'tsp', 'tsd', 'la', 'pa', 'fs', 'hs'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
        )

   