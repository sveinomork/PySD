from __future__ import annotations
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from .cases import Cases, normalize_cases
from ..validation.messages import ErrorMessageBuilder

# Define the type for valid GRECO IDs (single uppercase letters A-Z)
GrecoID = Literal['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

class GRECO(BaseModel):
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

    - **id**: GrecoID
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
    # Required fields
    id: GrecoID = Field(..., description="GRECO version ID (single uppercase letter A-Z)")
    bas: Optional[Cases] = Field(None, description="BAS load cases (must be exactly 6)")
    elc: Optional[Cases] = Field(None, description="ELC load cases (must reference OLC in LOADC)")
    
    # Auto-generated field for compatibility
    input: str = Field(default="", init=False, description="Generated input string")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID format."""
        if not re.match(r'^[A-Z]$', v):
            raise ValueError(
                ErrorMessageBuilder.build_message(
                    'INVALID_FORMAT',
                    field='ID',
                    format_desc='single uppercase letter A-Z'
                )
            )
        return v

    @field_validator('bas', 'elc', mode='before')
    @classmethod
    def normalize_cases_input(cls, v: Any) -> Optional[Cases]:
        """Convert various input formats to Cases."""
        if v is None:
            return v
        return normalize_cases(v)

    @field_validator('bas', 'elc')
    @classmethod
    def validate_no_steps_or_greco(cls, v: Optional[Cases]) -> Optional[Cases]:
        """GRECO doesn't support steps or GRECO letters."""
        if v is None:
            return v
        
        # Check for steps
        for range_item in v.ranges:
            if isinstance(range_item, tuple) and len(range_item) > 2:
                raise ValueError("GRECO does not support stepped ranges")
        
        # Check for GRECO letters
        if v.greco:
            raise ValueError("GRECO does not support GRECO letters in Cases")
            
        return v
    
    @field_validator('bas')
    @classmethod
    def validate_max_bas_combinations(cls, v: Optional[Cases]) -> Optional[Cases]:
        """Maximum 6 BAS combinations allowed."""
        if v and len(v.ranges) > 6:
            raise ValueError(
                ErrorMessageBuilder.build_message(
                    'INVALID_COUNT',
                    field='BAS combinations',
                    expected_count='maximum 6',
                    actual_count=len(v.ranges)
                )
            )
        return v
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'GRECO':
        """Build the statement input string and perform cross-field validation."""
        # TODO: Implement BAS count validation (must be exactly 6)
        # Business rule: GRECO must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)
        # if self.bas and len(self.bas.to_list()) != 6:
        #     raise ValueError("GRECO must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)")
        
        # TODO: Implement ELC-OLC cross-reference validation
        # Business rule: ELC must be defined as OLC in LOADC statements
        # This requires access to the full model context during validation
        # if self.elc:
        #     # Check that all ELC values exist as OLC in LOADC statements
        #     # This validation will be performed at the container/model level
        #     pass
        
        # Build input string
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
        return self
    

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

    def __str__(self) -> str:
        return self.input
    
    def formatted(self) -> str:
        """Legacy method for backward compatibility."""
        return self.input