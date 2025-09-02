from dataclasses import dataclass, field
from typing import Optional, Tuple, Literal

@dataclass
class CMPEC:
    """
    Define concrete material property sets according to EuroCode 2.
    Most parameters are optional. Values belonging to the chosen concrete quality will be used if not specified.
    """
    # Required for identification
    id: Optional[int] = None
    
    # Concrete grade definition
    gr: Optional[str] = None  # concrete grade, legal range 12-90 (integer) [MPa]
    rh: Optional[float] = None  # density for lightweight concrete (1150-2150 kg/m3)
    
    # Single data parameters (when no concrete grade is defined)
    fck: Optional[float] = None  # cylinder compression strength after 28 days [Pa]
    ecm: Optional[float] = None  # secant modulus of elasticity [kPa]
    fcn: Optional[float] = None  # in situ compression strength [kPa]
    ftm: Optional[float] = None  # in situ tensile strength [kPa]
    acc: float = 0.85  # coefficient for longterm effects
    
    # Figure 3.3 related parameters
    exp: Optional[float] = None  # exponent n in equation 3.17
    ec2: Optional[float] = None  # strain at start stress plateau
    ecu: Optional[float] = None  # ultimate strain
    
    # Design properties with defaults
    mfu: float = 1.5   # design material factor (ULS)
    mfa: float = 1.2   # design material factor (ALS)
    mfs: float = 1.0   # design material factor (SLS/CRW)
    k1c: float = 0.15  # Shear parameter k1 for compression
    k1t: float = 0.30  # Shear parameter k1 for tension
    k2: float = 0.15   # Shear parameter k2
    cot: float = 2.5   # Shear cot(theta)
    
    # Reduced compression strength parameters
    tsp: float = 100.0  # design fc2d = fcd/(0.8+tsp*ept)
    tsd: float = 1.0    # design min(fc2d) = fac*fcd
    
    # Location parameters
    la: Optional[int] = None  # LAREA id-number
    pa: Optional[str] = None  # structural part (max 8 chars)
    fs: Optional[Tuple[int, int]] = None  # F-section range
    hs: Optional[Tuple[int, int]] = None  # H-section range
    
    # Print options
    pri: Optional[Literal['', 'TAB']] = None
    
    # Output string
    input: str = field(init=False, default="CMPEC")
    
    def __post_init__(self):
        # Validation
        if self.id is not None and not (1 <= self.id <= 99999999):
            raise ValueError("ID must be between 1 and 99999999")
            
        if self.gr and not self.gr.startswith('B'):
            raise ValueError("Concrete grade (GR) must start with 'B'")
            
        if self.gr:
            grade = int(self.gr[1:])
            if not (12 <= grade <= 90):
                raise ValueError("Concrete grade must be between B12 and B90")
                
        if self.rh is not None and not (1150 <= self.rh <= 2150):
            raise ValueError("Density (RH) must be between 1150 and 2150 kg/m3")
            
        if self.pa and len(self.pa) > 8:
            raise ValueError("Structural part (PA) cannot exceed 8 characters")

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

    def __str__(self) -> str:
        return self.input
