"""
Input Statement: DEPAR

Purpose: Define global structural analysis parameters and parameters.

This statement allows definition of various parameters for structural analysis,
including design iterations, stress tolerances, code selection, and other
analysis-specific settings.
"""

from __future__ import annotations
from pydantic import Field
from typing import Optional, Tuple, Literal, Union
from .statement_base import StatementBase


class DEPAR(StatementBase):
    """
    Design Parameters statement for global structural analysis settings.

    Defines various parameters for structural analysis including design iterations,
    stress tolerances, thickness tolerances, code selection, and other settings.
    None of the parameters are required - default values will be used if not specified.

    ### Parameters:
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
    ```python

    # DEPAR with specific number of layers and iterations
    DEPAR(n_lay=15, n_ite=500)
    # -> "DEPAR N_LAY=15 N_ITE=500"
    # DEPAR with stress deviation and thickness tolerance
    DEPAR(d_sig=(5.0, 0.005), t_tol=0.01)
    """

    n_lay: Optional[int] = Field(
        None, description="Number of integration layers through shell thickness"
    )
    n_ite: Optional[int] = Field(
        None, description="Maximum number of design iterations"
    )
    d_sig: Optional[Union[float, Tuple[float, float]]] = Field(
        None, description="Maximum stress deviation before iteration stops"
    )
    t_tol: Optional[float] = Field(
        None, description="Shell thickness tolerance in meters"
    )
    p_tol: Optional[float] = Field(None, description="Shell thickness tolerance in %")
    z_tol: Optional[float] = Field(
        None, description="Rebar layer z-coordinate tolerance in meters"
    )
    z_che: Optional[bool] = Field(
        None,
        description="If True, rebar layer x3-coordinate check will not be carried out",
    )
    w_che: Optional[bool] = Field(
        None,
        description="If True, crack check will not be carried out for CRW limit state",
    )
    u_fai: Optional[int] = Field(
        None, description="UR to report when design iteration failure occurs"
    )
    u_she: Optional[int] = Field(
        None, description="UR to report when no shear tensile capacity in concrete"
    )
    u_fat: Optional[int] = Field(
        None, description="UR to report when rebar yields for fatigue"
    )
    e_mod: Optional[float] = Field(
        None,
        description="Linear analysis modulus of elasticity in kPa (for BASCO TYP=F)",
    )
    p_rat: Optional[float] = Field(
        None,
        description="Linear analysis Poisson's ratio (for BASCO TYP=F, default: 0)",
    )
    i_wav: Optional[Literal[1, -1]] = Field(
        None, description="Imaginary wave sign (+1 or -1, required if waves present)"
    )
    d_cod: Optional[Literal["NS", "EC", "OS", "GM"]] = Field(
        None, description="Design code ('NS', 'EC', 'OS', 'GM', default: 'NS')"
    )
    pri: Optional[bool] = Field(
        None, description="If True, DEPAR data will be printed in output file"
    )

    @property
    def identifier(self) -> str:
        return self._build_identifier(add_hash=True)

    def _build_input_string(self) -> None:
        """Build the input string using enhanced generic builder."""
        if self.pri:
            # Special case: print option only
            self.start_string()
            self.add_param("PRI", "")
            return

        self.input = self._build_string_generic(
            field_order=[
                "n_lay",
                "n_ite",
                "d_sig",
                "t_tol",
                "p_tol",
                "z_tol",
                "z_che",
                "w_che",
                "u_fai",
                "u_she",
                "u_fat",
                "e_mod",
                "p_rat",
                "i_wav",
                "d_cod",
            ],
            exclude={"comment"},  # Exclude comment from regular field processing
            float_precision=6,
        )
