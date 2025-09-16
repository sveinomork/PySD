from __future__ import annotations
from typing import Optional, Tuple, Union
from pydantic import Field, field_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext
from .statement_base import StatementBase

class DESEC(StatementBase):
    """
    Represents the DESEC statement used for defining design sections and their geometry.
    
    This is used in structural analysis workflows and supports several cases depending
    on the presence of OLC/FE result files or if it's a CSM analysis.
    
   ### Cases:
    -------
    Case 1: No OLC/FE result file -> DESEC defines section geometry.
    Case 2: OLC/FE result file -> DESEC stores sections on DEC-file.
    Case 3: CSM analysis -> DESEC may redefine geometry.

   ### Parameters:
    -----------
    pa : str
        Structural part identity (max 8 characters). Required.
    
    fs : Optional[Union[int, Tuple[int, int]]]
        F-section range or single section. Default is all.
        Examples: 5 (single section) or (1, 30) (range)

    hs : Optional[Union[int, Tuple[int, int]]]
        H-section range or single section. Default is all.
        Examples: 2 (single section) or (1, 5) (range)

    th : Optional[float]
        Shell thickness in meters. Default is 0.

    t11 : Optional[float]
        Shell thickness gradient ∂t1/∂x1. Default is 0.

    t12 : Optional[float]
        Shell thickness gradient ∂t1/∂x2. Default is 0.

    t21 : Optional[float]
        Shell thickness gradient ∂t2/∂x1. Default is 0.

    t22 : Optional[float]
        Shell thickness gradient ∂t2/∂x2. Default is 0.

    x : Optional[float]
        X-coordinate. Default is 0.

    y : Optional[float]
        Y-coordinate. Default is 0.

    z : Optional[float]
        Z-coordinate. Default is 0.
    """
    pa: str = Field(..., description="Structural part identity (max 8 characters)")
    
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="F-section range or single section")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="H-section range or single section")
    th: Optional[float] = Field(None, description="Shell thickness in meters, default=0")
    t11: Optional[float] = Field(None, description="Shell thickness gradient ∂t1/∂x1")
    t12: Optional[float] = Field(None, description="Shell thickness gradient ∂t1/∂x2")
    t21: Optional[float] = Field(None, description="Shell thickness gradient ∂t2/∂x1")
    t22: Optional[float] = Field(None, description="Shell thickness gradient ∂t2/∂x2")
    x: Optional[float] = Field(None, description="X-coordinate")
    y: Optional[float] = Field(None, description="Y-coordinate")
    z: Optional[float] = Field(None, description="Z-coordinate")



    @property
    def identifier(self) -> str:
        """Generate unique ID and input string for this DESEC statement."""

        return self._build_identifier(field_order=['pa', 'hs', 'fs'], add_hash=True)
    

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        self.input = self._build_string_generic(
            field_order=['pa', 'hs', 'fs', 'th', 't11', 't12', 't21', 't22', 'x', 'y', 'z'],
            exclude={'comment'},  # Exclude comment from regular field processing
            float_precision=6,
        )
     

    def _build_input_string1(self) -> str:
        """Build the DESEC input string."""
        parts = ["DESEC", f"PA={self.pa}"]
        
        # Handle fs parameter - can be int or tuple
        if self.fs is not None:
            if isinstance(self.fs, int):
                parts.append(f"FS={self.fs}")
            else:  # tuple
                parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
        
        # Handle hs parameter - can be int or tuple
        if self.hs is not None:
            if isinstance(self.hs, int):
                parts.append(f"HS={self.hs}")
            else:  # tuple
                parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
        
        if self.th != 0.0:
            parts.append(f"TH={self.th}")
        if self.t11 != 0.0:
            parts.append(f"T11={self.t11}")
        if self.t12 != 0.0:
            parts.append(f"T12={self.t12}")
        if self.t21 != 0.0:
            parts.append(f"T21={self.t21}")
        if self.t22 != 0.0:
            parts.append(f"T22={self.t22}")
        if self.x != 0.0:
            parts.append(f"X={self.x}")
        if self.y != 0.0:
            parts.append(f"Y={self.y}")
        if self.z != 0.0:
            parts.append(f"Z={self.z}")
            
        self.input = " ".join(parts)
        return self.input
    
    