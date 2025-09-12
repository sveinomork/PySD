"""
Input Statement: DEPAR

Purpose: Define global structural analysis parameters and parameters.

This statement allows definition of various parameters for structural analysis,
including design iterations, stress tolerances, code selection, and other
analysis-specific settings.
"""

from __future__ import annotations
from pydantic import  Field 
from typing import Optional, Tuple, Literal, Union
from .statement_base import StatementBase


class DEPAR(StatementBase):
    """
    Design Parameters statement for global structural analysis settings.
    
    Defines various parameters for structural analysis including design iterations,
    stress tolerances, thickness tolerances, code selection, and other settings.
    None of the parameters are required - default values will be used if not specified.
    
    Parameters:
        n_lay: Number of integration layers through shell thickness (default: 10)
        n_ite: Maximum number of design iterations (default: 1000)
        d_sig: Maximum stress deviation before iteration stops (default: 10.0, 0.001)
        t_tol: Shell thickness tolerance in meters (default: 0.0)
        p_tol: Shell thickness tolerance in % (replaces T_TOL if defined, default: 0.0)
        z_tol: Rebar layer z-coordinate tolerance in meters (default: 0.0)
        z_che: If True, rebar layer x3-coordinate check will not be carried out
        w_che: If True, crack check will not be carried out for CRW limit state
        u_fai: UR to report when design iteration failure occurs (default: 10)
        u_she: UR to report when no shear tensile capacity in concrete (default: 20)
        u_fat: UR to report when rebar yields for fatigue (default: 30)
        e_mod: Linear analysis modulus of elasticity in kPa (for BASCO TYP=F)
        p_rat: Linear analysis Poisson's ratio (for BASCO TYP=F, default: 0)
        i_wav: Imaginary wave sign (+1 or -1, required if waves present)
        d_cod: Design code ('NS', 'EC', 'OS', 'GM', default: 'NS')
        pri: If True, DEPAR data will be printed in output file
    
    Examples:
        >>> # Basic parameters
        >>> depar1 = DEPAR(n_lay=20, d_sig=100, d_cod="NS")
        >>> print(depar1.input)
        DEPAR N_LAY=20 D_SIG=100 D_COD=NS
        
        >>> # With stress deviation tuple
        >>> depar2 = DEPAR(d_sig=(20, 0.002), t_tol=0.02, z_tol=0.02, d_cod="EC")
        >>> print(depar2.input)
        DEPAR D_SIG=20,0.002 T_TOL=0.02 Z_TOL=0.02 D_COD=EC
        
        >>> # Print statement only
        >>> depar3 = DEPAR(pri=True)
        >>> print(depar3.input)
        DEPAR PRI=
    """

    n_lay: Optional[int] = Field(None,description="Number of integration layers through shell thickness")
    n_ite: Optional[int] = Field(None,description="Maximum number of design iterations")
    d_sig: Optional[Union[float, Tuple[float, float]]] = Field(None,description="Maximum stress deviation before iteration stops")
    t_tol: Optional[float] = Field(None,description="Shell thickness tolerance in meters")
    p_tol: Optional[float] = Field(None,description="Shell thickness tolerance in %")
    z_tol: Optional[float] = Field(None,description="Rebar layer z-coordinate tolerance in meters")
    z_che: Optional[bool] = Field(None,description="If True, rebar layer x3-coordinate check will not be carried out")
    w_che: Optional[bool] = Field(None,description="If True, crack check will not be carried out for CRW limit state")
    u_fai: Optional[int] = Field(None,description="UR to report when design iteration failure occurs")
    u_she: Optional[int] = Field(None,description="UR to report when no shear tensile capacity in concrete")
    u_fat: Optional[int] = Field(None,description="UR to report when rebar yields for fatigue")
    e_mod: Optional[float] = Field(None,description="Linear analysis modulus of elasticity in kPa (for BASCO TYP=F)")
    p_rat: Optional[float] = Field(None,description="Linear analysis Poisson's ratio (for BASCO TYP=F, default: 0)")
    i_wav: Optional[Literal[1, -1]] = Field(None,description="Imaginary wave sign (+1 or -1, required if waves present)")
    d_cod: Optional[Literal["NS", "EC", "OS", "GM"]] = Field(None,description="Design code ('NS', 'EC', 'OS', 'GM', default: 'NS')")
    pri: Optional[bool] = Field(None,description="If True, DEPAR data will be printed in output file")
    
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this DEPAR statement."""
        import hashlib
        
        # Use the complete input string for uniqueness, but hash it for brevity
        input_str = self.input if hasattr(self, 'input') else str(self)
        hash_obj = hashlib.sha256(input_str.encode())
        short_hash = hash_obj.hexdigest()[:10]  # 10 chars for good uniqueness
        
        return f"DEPAR_{short_hash}"
  
    def _build_input_string(self) -> str:

        def _format_number(value: float) -> str:
            """Format a number for output, handling integers and floats appropriately."""
            if value == int(value):
                return str(int(value))
            else:
                return str(value)

        """Generate the DEPAR input string."""
        parts = ["DEPAR"]
        
        # Add parameters in the order they appear in the manual
        if self.n_lay is not None:
            parts.append(f"N_LAY={self.n_lay}")
        
        if self.n_ite is not None:
            parts.append(f"N_ITE={self.n_ite}")
        
        if self.d_sig is not None:
            if isinstance(self.d_sig, tuple):
                parts.append(f"D_SIG={_format_number(self.d_sig[0])},{_format_number(self.d_sig[1])}")
            else:
                parts.append(f"D_SIG={_format_number(self.d_sig)}")
        
        if self.t_tol is not None:
            parts.append(f"T_TOL={_format_number(self.t_tol)}")
        
        if self.p_tol is not None:
            parts.append(f"P_TOL={_format_number(self.p_tol)}")
        
        if self.z_tol is not None:
            parts.append(f"Z_TOL={_format_number(self.z_tol)}")
        
        if self.z_che is not None:
            parts.append("Z_CHE=")
        
        if self.w_che is not None:
            parts.append("W_CHE=")
        
        if self.u_fai is not None:
            parts.append(f"U_FAI={self.u_fai}")
        
        if self.u_she is not None:
            parts.append(f"U_SHE={self.u_she}")
        
        if self.u_fat is not None:
            parts.append(f"U_FAT={self.u_fat}")
        
        if self.e_mod is not None:
            parts.append(f"E_MOD={_format_number(self.e_mod)}")
        
        if self.p_rat is not None:
            parts.append(f"P_RAT={_format_number(self.p_rat)}")
        
        if self.i_wav is not None:
            parts.append(f"I_WAV={self.i_wav}")
        
        if self.d_cod is not None:
            parts.append(f"D_COD={self.d_cod}")
        
        if self.pri is not None:
            parts.append("PRI=")
        
        return " ".join(parts)
    
    
