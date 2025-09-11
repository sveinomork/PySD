
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
    esk: float = Field(default=200.0E6, description="Modulus of elasticity [kPa] [default 200*1.0E6]")
    fyk: Optional[float] = Field(None, description="Yield strength [kPa]")
    fsk: Optional[float] = Field(None, description="Ultimate strength [kPa]")
   
    den: float = Field(7850.0, description="Steel density [kg/m3]")
    
    # Design properties - ULS
    mfu: float = Field(default=1.15, description="Design material factor ULS [default 1.15]")
    epu: float = Field(default=0.010, description="Ultimate tensile strain ULS [m/m] [default 0.010]")

    # Design properties - ALS
    mfa: float = Field(default=1.00, description="Design material factor ALS [default 1.00]")
    epa: float = Field(default=0.010, description="Ultimate tensile strains ALS [m/m] [default 0.010]")

    # Design properties - SLS
    mfs: float = Field(default=1.00, description="Design material factor SLS [default 1.00]")
    eps: Optional[float] = Field(default=None, description="Ultimate tensile strain SLS [m/m]")
    
    # Print option
    pri: Optional[Literal['']] = Field(None, description="Print option")
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RMPEC statement."""
        return str(self.id)

   

 
    def _build_input_string(self) -> 'RMPEC':


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
            return self
            
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
        if self.mfu != 1.15:
            parts.append(f"MFU={format_float(self.mfu)}")
            
        if self.epu != 0.010:
            parts.append(f"EPU={format_float(self.epu)}")
        
        if self.mfa != 1.00:
            parts.append(f"MFA={format_float(self.mfa)}")
            
        if self.epa != 0.010:
            parts.append(f"EPA={format_float(self.epa)}")
            
        # Only include MFS if it differs from default or if EPS is specified
        if self.mfs != 1.00:
            parts.append(f"MFS={format_float(self.mfs)}")
            
        if self.eps is not None:
            parts.append(f"EPS={format_float(self.eps)}")
            
        # Join all parts with spaces
        self.input = " ".join(parts)
        
        return self.input
    
    