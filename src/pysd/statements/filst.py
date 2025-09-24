from __future__ import annotations
from typing import Optional
from pydantic import  Field

from .statement_base import StatementBase


class FILST(StatementBase):
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
    pri: Optional[bool] = Field(None, description="Print all current FILST lines")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this FILST statement."""
        return self._build_identifier(add_hash=True)
    

    
    def _build_input_string(self) -> None:
        """Build input string and run instance-level validation."""
        
        # Build input string
        if self.pri:
           self.start_string()  # Call the method, don't assign to it
           self.add_param("PRI", "")  # Empty value becomes "PRI="
        else:
           # For FILST, we need to include the 'name' field, but _build_string_generic
           # always excludes it. So we'll build it manually.
           from .statement_base import StringBuilderHelper
           
           helper = StringBuilderHelper(self.statement_name)
           
           # Add fields in the desired order
           for field_name in ['name', 'vers', 'date', 'resp']:
               value = getattr(self, field_name, None)
               if value is not None:
                   helper.add_param(field_name, value)
           
           self.input = helper.input
        
    
    