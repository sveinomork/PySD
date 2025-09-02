from __future__ import annotations
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re
from .cases import Cases, normalize_cases

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

    # Verification mode
    GRECO(verification=True)
    # -> 'GRECO VER='
    ```

    ### Parameters

    - **id**: Optional[GrecoID]
        - Version identified by a single uppercase letter (A-Z). Required unless verification=True.
    - **bas**: Optional[LoadCaseDefinition]
        - BAS combinations to include. Can be single values or ranges.
        - Examples: [(11, 16)] -> "BAS=11-16", [21, 22, (31,34)] -> "BAS=21,22,31-34"
    - **elc**: Optional[LoadCaseDefinition]
        - Range of equilibrium load cases to include.
        - Example: [(1, 34)] -> "ELC=1-34"
    - **verification**: bool
        - If True, prints ELC verification tables. Default is False.
    - **allow_verification_and_normal**: bool
        - Internal flag for special verification modes. Default is False.

    ### Notes

    - Either verification must be True, or id must be provided with bas/elc definitions.
    - Maximum 6 BAS combinations allowed.
    - GRECO only allows simple ranges and individual values (no step sizes).
    - No versions are allowed in the LoadCaseDefinition parameter.
    - When using LoadCaseDefinition, the version parameter must be empty.
    """

    id: Optional[GrecoID] = None
    bas: Optional[Cases] = None
    elc: Optional[Cases] = None
    verification: bool = False
    allow_verification_and_normal: bool = False

    @property
    def input(self) -> str:
        """Backward compatibility property that returns formatted output."""
        return self.formatted()

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate ID format if provided."""
        if v is not None and not re.match(r'^[A-Z]$', v):
            raise ValueError("GRECO ID must be a single uppercase letter A-Z")
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
            raise ValueError("Maximum 6 BAS combinations allowed")
        return v

    @model_validator(mode='after')
    def validate_model(self) -> 'GRECO':
        """Validate the complete model."""
        # Validation
        if not self.verification and not self.id:
            raise ValueError("Either verification must be True or id must be provided")
        
        # Check if verification is True with other parameters (unless explicitly allowed)
        if self.verification and not self.allow_verification_and_normal:
            if self.id or self.bas or self.elc:
                raise ValueError("When verification is True, no other parameters should be set")
        
        if not self.verification and not self.bas:
            raise ValueError("BAS must be provided when not in verification mode")

        return self

    def formatted(self) -> str:
        """Generate the formatted output string."""
        parts: list[str] = []
        
        # Normal GRECO statement if id/bas/elc are set
        if self.id or self.bas or self.elc:
            normal = ["GRECO"]
            if self.id:
                normal.append(f"ID={self.id}")
            if self.bas:
                normal.append(f"BAS={self.bas.formatted()}")
            if self.elc:
                normal.append(f"ELC={self.elc.formatted()}")
            parts.append(" ".join(normal))
        
        # Always add GRECO VER= if verification is True
        if self.verification:
            parts.append("GRECO VER=")
        
        return "\n".join(parts)
    

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
        return self.formatted()