
from dataclasses import dataclass, field
from typing import Optional, Literal

@dataclass
class RMPEC:
    """
    Define rebar material property sets according to Eurocode 2.
    The ID is related to the MP statement in the RETYP statement.
    """
    # Required for identification
    id: Optional[int] = 1
    
    # Material properties
    gr: Optional[str] = None  # steel grade
    esk: float = 200.0E6     # modulus of elasticity [kPa]
    fyk: Optional[float] = None  # yield strength [kPa]
    fsk: Optional[float] = None  # ultimate strength (design) [kPa]
    den: float = 7850.0      # steel density [kg/m3]
    
    # Design properties - ULS
    mfu: float = 1.15    # design material factor ULS
    epu: float = 0.010   # ultimate tensile strain ULS [m/m]
    
    # Design properties - ALS
    mfa: float = 1.00    # design material factor ALS
    epa: float = 0.010   # ultimate tensile strains ALS [m/m]
    
    # Design properties - SLS
    mfs: float = 1.00    # design material factor SLS, CRW
    eps: Optional[float] = None  # ultimate tensile strain SLS [m/m]
    
    # Print option
    pri: Optional[Literal['']] = None
    
    # Output string
    input: str = field(init=False, default="RMPEC")
    
    def __post_init__(self):
        # Validation
        if self.id is not None and not (1 <= self.id <= 99999999):
            raise ValueError("ID must be between 1 and 99999999")
        
        def format_float(value: float) -> str:
            """Format float value according to the requirements"""
            if value.is_integer():
                return f"{int(value)}"
            elif abs(value) < 0.01:
                return f"{value:.4f}"
            elif abs(value) > 1000:
                return f"{value:.0f}"
            elif abs(value) < 10:
                return f"{value:.2f}"
            else:
                return f"{value:.0f}"

        # Build the RMPEC input string
        if self.pri is not None:
            self.input = "RMPEC PRI="
            return
            
        parts = ["RMPEC"]
        
        # Add identification
        if self.id is not None:
            parts.append(f"ID={self.id}")
        
        # Add material properties
        if self.gr is not None:
            parts.append(f"GR={self.gr}")
            
        if self.esk != 200.0E6:
            parts.append(f"ESK={format_float(self.esk)}")
            
        if self.fyk is not None:
            parts.append(f"FYK={format_float(self.fyk)}")
            
        if self.fsk is not None:
            parts.append(f"FSK={format_float(self.fsk)}")
            
        if self.den != 7850.0:
            parts.append(f"DEN={format_float(self.den)}")
        
        # Add design properties if they differ from defaults
        # Add design properties
        if self.mfu != 1.15:
            parts.append(f"MFU={format_float(self.mfu)}")
            parts.append(f"EPU={format_float(self.epu)}")
        
        if self.mfa != 1.00:
            parts.append(f"MFA={format_float(self.mfa)}")
            
        if self.epa != 0.010:
            parts.append(f"EPA={format_float(self.epa)}")
            
        # Only include MFS if it differs from default or if EPS is specified
        if self.mfs != 1.00 or self.eps is not None:
            parts.append(f"MFS={format_float(self.mfs)}")
            
        if self.eps is not None:
            parts.append(f"EPS={format_float(self.eps)}")
            
        # Join all parts with spaces
        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input