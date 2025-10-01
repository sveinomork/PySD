from __future__ import annotations
from typing import Optional
from pydantic import Field



from .statement_base import StatementBase

class INPLC(StatementBase):
    """
    Define load cases with input shell section forrces/moments
    ### Examples

    ```python
    # Basic IMPLC with forces and moments
    IMPLC(id=1, N1=1000.0, M2=500.0, M12=200.0, V1=300.0)
    # -> 'IMPLC ID=1 N1=1000.0 M2=500.0 M12=200.0 V1=300.0'
    ```

    ### Parameters

    
    """

    # Required fields - using str instead of Literal for flexible validation
    id: str|int = Field(..., description="IMPLC version ID (single uppercase letter A-Z)")
    n1: Optional[float|int] = Field(None, description="N1 force")
    n2: Optional[float|int] = Field(None, description="N2 force")
    n12: Optional[float|int] = Field(None, description="N12 membrane shear force")
    m1: Optional[float|int] = Field(None, description="M1 moment")
    m2: Optional[float|int] = Field(None, description="M2 moment")
    m12: Optional[float|int] = Field(None, description="M12 moment")
    v1: Optional[float|int] = Field(None, description="V1 shear")
    v2: Optional[float|int] = Field(None, description="V2 shear")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this IMPLC statement."""
        return self.id

    

    def _build_input_string(self) -> None:
        """Build the input string (pure formatting logic)."""
        self.input = self._build_string_generic(
            field_order=[
                "id",
                "n1",
                "n2",
                "n12",
                "m1",
                "m2",
                "m12",
                "v1",
                "v2",
            ],
            float_precision=3,
        )