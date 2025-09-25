
from __future__ import annotations
from typing import Optional, Literal
from pydantic import  Field

from .statement_base import StatementBase


class TEMAT(StatementBase):
    """
    Define tendon (prestressing) material property sets according to DNV-ST-C502, NS 3473 and EC2 curve.
    The ID is related to the TT statement in the TETYP statement.

    ### Examples
    ```python
    # Define a tendon material property set
    TEMAT(id=1, fsy=1670.E3, esk=196.E6, fam=0.8,  mfu=1.15, mff=1.15)
    # → "TEMAT ID=1 FSY=1670000 ESK=196000000 FAM=0.8 MFU=1.15 MFF=1.15"


    ### Parameters
    id : int
        Material property set ID (1-99999999)   
    fsy : float
        Yield stress [kPa]
    esk : float
        Modulus of elasticity [kPa]
    fam : Optional[float]
        Factor for calculating modeified curve from eps=FAM*eps to epm. Default is no modified curve.
        See Section 4.1.1.3  for DNV curve, section 4.2.1.3 for NS curve and 4.3.1.3 for EC2 curve.
        (default:1.0) 
    epm : Optional[float]
        modified strain  (default:0.010)
    epu : Optional[float]
        Ultimate tensile strain [m/m] (default:0.020)
    mfu : Optional[float]
        Design material factor ULS 
    mfa : Optional[float]
        Design material factor ALS 
    mfs : Optional[float]
        Design material factor SLS 
    mff : Optional[float]
        Design material factor FLS 
    pri : Optional[Literal['','TAB']]
        PRI= Print out all stored TEMAT sets  PRI=TAB prints material curve
    
    """
    # Required for identification
    id: int = Field(..., description="Material property set ID (1-99999999)")
    
    # Material properties
    # Required fields
    fsy: float = Field(None, description="Yield stress [kPa]")
    esk: float = Field(None, description="Modulus of elasticity [kPa]")
    # optional fields
    fam: Optional[float] = Field(None, description="Factor for calculating modeified curve from eps.")
    epm: Optional[float] = Field(None, description="Modified strain  (default:0.010)")
    epu: Optional[float] = Field(None, description="Ultimate strength [kPa]")

    # Design properties - ULS
    mfu: Optional[float] = Field(None, description="Design material factor ULS ")
  
    # Design properties - ALS
    mfa: Optional[float] = Field(None, description="Design material factor ALS ")
   
    # Design properties - SLS
    mfs: Optional[float] = Field(None, description="Design material factor SLS ")
   
    # Design properties - FLS
    mff: Optional[float] = Field(None, description="Design material factor FLS ")

    # Print option
    pri: Optional[Literal['', 'TAB']] = Field(None, description="Print option")
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RMPEC statement."""
        return str(self.id)

   

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri is not None:
            # Special case: print option only
            self.start_string()
            self.add_param("PRI","" )
            return
        if self.pri == 'TAB':
            self.start_string()
            self.add_param("PRI","TAB" )
            return

        self.input = self._build_string_generic(
            field_order=['id', 'fsy', 'esk', 'fam', 'epm', 'epu', 'mfu', 'mfa', 'mfs', 'mff'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
        )
    