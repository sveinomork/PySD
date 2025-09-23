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
            self.add_param("TAB","" )
            return

        self.input = self._build_string_generic(
            field_order=['id', 'gr', 'rh', 'fck', 'ecm', 'fcn', 'ftm', 'acc', 'exp', 'ec2', 'ecu', 'mfu',
                          'mfa', 'mfs', 'k1c', 'k1t', 'k2', 'cot', 'tsp', 'tsd', 'la', 'pa', 'fs', 'hs'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
        )

    def _build_input_string1(self) -> None:
        """Build input string and run instance-level validation."""
        

        # Build the CMPEC input string
        parts = ["CMPEC"]
        
        # Add identification if provided
        if self.id is not None:
            parts.append(f"ID={self.id}")
        
        # Add concrete grade parameters
        if self.gr:
            parts.append(f"GR={self.gr}")
        if self.rh:
            parts.append(f"RH={self.rh}")
            
        # Add location parameters
        if self.la:
            parts.append(f"LA={self.la}")
        if self.pa:
            parts.append(f"PA={self.pa}")
        if self.fs:
            parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
        if self.hs:
            parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
            
        # Add material properties if provided
        for param, name in [
            (self.fck, 'FCK'), (self.ecm, 'ECM'), (self.fcn, 'FCN'),
            (self.ftm, 'FTM'), (self.exp, 'EXP'), (self.ec2, 'EC2'),
            (self.ecu, 'ECU')
        ]:
            if param is not None:
                parts.append(f"{name}={param}")
                
        # Add design properties if they differ from defaults
        if self.mfu != 1.5:
            parts.append(f"MFU={self.mfu}")
        if self.mfa != 1.2:
            parts.append(f"MFA={self.mfa}")
        if self.mfs != 1.0:
            parts.append(f"MFS={self.mfs}")
        if self.k1c != 0.15:
            parts.append(f"K1C={self.k1c}")
        if self.k1t != 0.30:
            parts.append(f"K1T={self.k1t}")
        if self.k2 != 0.15:
            parts.append(f"K2={self.k2}")
        if self.cot != 2.5:
            parts.append(f"COT={self.cot}")
            
        # Add compression strength parameters if they differ from defaults
        if self.tsp != 100.0:
            parts.append(f"TSP={self.tsp}")
        if self.tsd != 1.0:
            parts.append(f"TSD={self.tsd}")
        if self.acc != 0.85:
            parts.append(f"ACC={self.acc}")
            
        # Handle print options
        if self.pri is not None:
            parts = ["CMPEC", "PRI=" + ("TAB" if self.pri == "TAB" else "")]
            
        # Join all parts with spaces
        self.input = " ".join(parts)
        
        return self
    
    