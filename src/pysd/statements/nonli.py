from typing import Literal, Optional
from pydantic import Field
from .statement_base import StatementBase


class NONLI(StatementBase):
    """
    define data concerning the Consistent Stiffness Method (CSM) with linear elastic
    stiffness or updated non-linear stiffnesses in elements. Non-linear stiffness
    elements are defined by: SHSEC ET=VS (cracked concrete), all other elements will
    have constant elastic stiffnesses. Material parameters are defined with CMPNL,
    RMPNL and TMPNL. See Section 3.3 in user manual for detailed description of CSM!!
    The default input to the FE analysis must be kN, m and tonnes for CSM !!

    ### Examples:
    ```python
    # 1. Define NONLI statement with Sestra as FEA tool:
       NONLI(spa="C:/Path/To/Sestra/executable", fea='SES') -> 'NONLI SPA=C:/Path/To/Sestra/executable FEA=SES'

    ### Parameters:
    spa : Optional[str]
        Path to the Sestra executable when using FEA=SES. NB! Directory names with space must be enclosed by two ".
        Example: C:\”Program Files”\DNV\”Sestra VXX.XX-XX”\ bin\Sestra.exe
    fea : Optional[Literal['SES', 'OOS']]
        - 'SES': Use Sestra as the FEA tool.
        - 'OOS': Use OOsolver as the FEA tool.
    nsr: Optional[int]
        n=max number of FE analysis run per design case n=0 flags linear analysis and material properties from T-file wil be
        used. CMPNL data wil be ignored.
    ndt: Optional[int]
        Iteration stop condition, node Displacement difference threshold
    Other parameters are not implemented yet.
    """

    spa: Optional[str] = Field(
        ..., description="path to sestra executable when using FEA=SES"
    )

    fea: Optional[Literal["SES", "OOS"]] = Field(
        None, description="'SES' for Sestra, 'OOS' for OOsolver"
    )
    nsr: Optional[int] = Field(
        None,
        description="n=max number of FE analysis run per design case n=0 flags linear analysis and material properties from T-file wil be used. CMPNL data wil be ignored.",
    )
    ndt: Optional[float] = Field(
        None,
        description="iteration stop condition, node Displacement difference threshold",
    )

    @property
    def identifier(self) -> str:
        return self._build_identifier(field_order=["dm"], add_hash=True)

    def _build_input_string(self) -> None:
        """Build input string and run instance-level validation."""
        if self.dm:
            self.input = f"EXECD DM={self.dm}"
        else:
            self.input = "EXECD DM="
