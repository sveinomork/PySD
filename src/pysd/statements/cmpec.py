from __future__ import annotations
from typing import Optional, Tuple, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext


class CMPEC(BaseModel):
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
    acc: float = Field(0.85, description="Coefficient for longterm effects")
    
    # Figure 3.3 related parameters
    exp: Optional[float] = Field(None, description="Exponent n in equation 3.17")
    ec2: Optional[float] = Field(None, description="Strain at start stress plateau")
    ecu: Optional[float] = Field(None, description="Ultimate strain")
    
    # Design properties with defaults
    mfu: float = Field(1.5, description="Design material factor (ULS)")
    mfa: float = Field(1.2, description="Design material factor (ALS)")
    mfs: float = Field(1.0, description="Design material factor (SLS/CRW)")
    k1c: float = Field(0.15, description="Shear parameter k1 for compression")
    k1t: float = Field(0.30, description="Shear parameter k1 for tension")
    k2: float = Field(0.15, description="Shear parameter k2")
    cot: float = Field(2.5, description="Shear cot(theta)")
    
    # Reduced compression strength parameters
    tsp: float = Field(100.0, description="Design fc2d = fcd/(0.8+tsp*ept)")
    tsd: float = Field(1.0, description="Design min(fc2d) = fac*fcd")
    
    # Location parameters
    la: Optional[int] = Field(None, description="LAREA id-number")
    pa: Optional[str] = Field(None, description="Structural part (max 8 chars)")
    fs: Optional[Tuple[int, int]] = Field(None, description="F-section range")
    hs: Optional[Tuple[int, int]] = Field(None, description="H-section range")
    
    # Print options
    pri: Optional[Literal['', 'TAB']] = Field(None, description="Print options")
    
    # Auto-generated fields
    input: str = Field(default="", init=False, description="Generated input string")

    @field_validator('id')
    @classmethod
    def validate_id_range(cls, v):
        """Validate ID is within acceptable range."""
        if v is not None and not (1 <= v <= 99999999):
            raise ValueError("ID must be between 1 and 99999999")
        return v

    @field_validator('gr')
    @classmethod
    def validate_concrete_grade(cls, v):
        """Validate concrete grade format and range."""
        if v is not None:
            if not v.startswith('B'):
                raise ValueError("Concrete grade (GR) must start with 'B'")
            try:
                grade = int(v[1:])
                if not (12 <= grade <= 90):
                    raise ValueError("Concrete grade must be between B12 and B90")
            except ValueError:
                raise ValueError("Invalid concrete grade format")
        return v

    @field_validator('rh')
    @classmethod
    def validate_density(cls, v):
        """Validate density range for lightweight concrete."""
        if v is not None and not (1150 <= v <= 2150):
            raise ValueError("Density (RH) must be between 1150 and 2150 kg/m3")
        return v

    @field_validator('pa')
    @classmethod
    def validate_part_name(cls, v):
        """Validate structural part name length."""
        if v is not None and len(v) > 8:
            raise ValueError("Structural part (PA) cannot exceed 8 characters")
        return v

    @model_validator(mode='after')
    def build_input_string(self) -> 'CMPEC':
        """Build input string and run instance-level validation."""
        
        # Execute instance-level validation rules
        context = ValidationContext(current_object=self)
        issues = execute_validation_rules(self, context, level='instance')
        
        # Handle issues according to global config
        for issue in issues:
            context.add_issue(issue)  # Auto-raises if configured

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
    
    def execute_cross_container_validation(self, sd_model) -> list:
        """
        Execute cross-container validation rules for this CMPEC instance.
        
        This method is called when the CMPEC is added to the SD_BASE model,
        allowing validation against other containers.
        """
        context = ValidationContext(
            current_object=self,
            full_model=sd_model  # This enables access to all containers
        )
        
        # Execute model-level (cross-container) validation rules
        return execute_validation_rules(self, context, level='model')

    def __str__(self) -> str:
        return self.input
    
    def formatted(self) -> str:
        """Legacy method for backward compatibility."""
        return self.input
