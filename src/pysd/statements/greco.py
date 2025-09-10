from __future__ import annotations
from typing import Optional, Any
from pydantic import  Field, field_validator
from .cases import Cases, normalize_cases


from .statement_base import StatementBase

# Define the type for valid GRECO IDs (single uppercase letters A-Z)
# Note: Using str instead of Literal to allow custom validation control
# GrecoID = Literal['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

class GRECO(StatementBase):
    """
    Active loads (ELC) are balanced by GRECO boundary reactions containing 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz). 
    ShellDesign calculates scale factors ensuring equilibrium between ELC and scaled GRECO reactions.

    ### Usage

    Define as a object to generate GRECO input lines for ShellDesign to ensure proper load balancing and reaction scaling.

    ### Examples

    ```python
    # Basic GRECO with BAS range
    GRECO(
        id='A',
        bas=LoadCaseDefinition(cases=[(11, 16)])
    )
    # -> 'GRECO ID=A BAS=11-16'

    # GRECO with multiple BAS values and ranges
    GRECO(
        id='B',
        bas=LoadCaseDefinition(cases=[21, 22, (31, 34)]),
        elc=LoadCaseDefinition(cases=[(1, 34)])
    )
    # -> 'GRECO ID=B BAS=21,22,31-34 ELC=1-34'

    ```

    ### Parameters

    - **id**: str
        - Version identified by a single uppercase letter (A-Z). Required.
    - **bas**: Optional[Cases]
        - BAS combinations to include. Can be single values or ranges.
        - Examples: [(11, 16)] -> "BAS=11-16", [21, 22, (31,34)] -> "BAS=21,22,31-34"
        - Must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)
    - **elc**: Optional[Cases]
        - Range of equilibrium load cases to include.
        - Example: [(1, 34)] -> "ELC=1-34"
        - ELC must be defined as OLC in LOADC statements

    ### Validation Rules

    1. **ID Format**: Must be a single uppercase letter A-Z
    2. **BAS Count**: Must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)
    3. **ELC Reference**: All ELC values must be defined as OLC in LOADC statements
    4. **Uniqueness**: GRECO ID must be unique within the model

    ### Notes

    - GRECO only allows simple ranges and individual values (no step sizes).
    - No versions are allowed in the LoadCaseDefinition parameter.
    - When using LoadCaseDefinition, the version parameter must be empty.
    """
    # Required fields - using str instead of Literal for flexible validation
    id: str = Field(..., description="GRECO version ID (single uppercase letter A-Z)")
    bas: Optional[Cases] = Field(None, description="BAS load cases (must be exactly 6)")
    elc: Optional[Cases] = Field(None, description="ELC load cases (must reference OLC in LOADC)")
    
    

    @property
    def identifier(self) -> str:
        """Get unique identifier for this GRECO statement."""
        return self.id

    @field_validator('bas', 'elc', mode='before')
    @classmethod
    def normalize_cases_input(cls, v: Any) -> Optional[Cases]:
        """Convert various input formats to Cases."""
        if v is None:
            return v
        return normalize_cases(v)
    
  
    def _build_input_string(self) -> None:
        """Build the input string (pure formatting logic)."""
        parts = []
        if self.id or self.bas or self.elc:
            normal = ["GRECO"]
            if self.id:
                normal.append(f"ID={self.id}")
            if self.bas:
                normal.append(f"BAS={self.bas.formatted()}")
            if self.elc:
                normal.append(f"ELC={self.elc.formatted()}")
            parts.append(" ".join(normal))
        
        self.input = "\n".join(parts)
    

    def __iter__(self):
        """Make the object iterable so list(obj) works"""
        if self.bas:
            return iter(self.bas)
        else:
            return iter([])
    
    def to_list(self) -> list[int]:
        """
        Get a list of all BAS case numbers.
        
        Returns:
            List[int]: All BAS case numbers expanded from ranges
            
        Examples:
            greco.to_list() -> [211, 212, 213, 214, 215, 218]
        """
        if self.bas:
            return self.bas.to_list()
        else:
            return []

   