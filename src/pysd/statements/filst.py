from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext


class FILST(BaseModel):
    """
    Represents the FILST statement for providing file status information.

    This can be used to define a new file status entry or to print all
    existing FILST entries.

    Purpose:
    --------
    Give file status for input files. The status will be printed at the end
    of the ShellDesign output file.

    Modes:
    ------
    1. Define a new entry by providing 'name'. Other parameters are optional.
       Example: FILST(name="RETYP_Lower_domes", vers="1.0", date="8jan-94", resp="kf")

    2. Print all entries by setting 'pri' to True.
       Example: FILST(pri=True)

    ### Validation Rules

    1. **Parameter Exclusivity**: When PRI=True, no other parameters should be set
    2. **NAME Required**: NAME is required unless PRI=True
    3. **Field Lengths**: NAME≤48, VERS≤8, DATE≤12, RESP≤4 characters
    4. **Content Validation**: Fields should not be empty if provided
    5. **Model Consistency**: Warnings for duplicate names or multiple PRI statements

    Parameters:
    -----------
    name : Optional[str]
        File identity (max 48 characters). Required for new entries.

    vers : Optional[str]
        File version (max 8 characters).

    date : Optional[str]
        Date of last revision (max 12 characters).

    resp : Optional[str]
        Responsible person/group (max 4 characters).

    pri : bool
        If True, prints all current FILST lines. Mutually exclusive with
        other parameters. Default is False.
    """
    name: Optional[str] = Field(None, description="File identity (max 48 characters)")
    vers: Optional[str] = Field(None, description="File version (max 8 characters)")
    date: Optional[str] = Field(None, description="Date of last revision (max 12 characters)")
    resp: Optional[str] = Field(None, description="Responsible person/group (max 4 characters)")
    pri: bool = Field(False, description="Print all current FILST lines")
    
    # Auto-generated field
    input: str = Field(default="", init=False, description="Generated input string")

    @model_validator(mode='after')
    def build_input_string(self) -> 'FILST':
        """Build input string and run instance-level validation."""
        
        # Execute instance-level validation rules
        context = ValidationContext(current_object=self)
        issues = execute_validation_rules(self, context, level='instance')
        
        # Handle issues according to global config
        for issue in issues:
            context.add_issue(issue)  # Auto-raises if configured
        
        # Build input string
        parts = ["FILST"]
        if self.pri:
            parts.append("PRI=")
        else:
            # The 'name' is mandatory in this case, use default if None
            name_value = self.name if self.name is not None else "sd"
            parts.append(f"NAME={name_value}")
            if self.vers is not None:
                parts.append(f"VERS={self.vers}")
            if self.date is not None:
                parts.append(f"DATE={self.date}")
            if self.resp is not None:
                parts.append(f"RESP={self.resp}")

        self.input = " ".join(parts)
        return self
    
    def execute_cross_container_validation(self, sd_model) -> list:
        """
        Execute cross-container validation rules for this FILST instance.
        
        This method is called when the FILST is added to the SD_BASE model.
        """
        context = ValidationContext(
            current_object=self,
            full_model=sd_model  # This enables access to all containers
        )
        
        # Execute model-level validation rules
        return execute_validation_rules(self, context, level='model')

    def __str__(self) -> str:
        return self.input
    
    def formatted(self) -> str:
        """Legacy method for backward compatibility."""
        return self.input