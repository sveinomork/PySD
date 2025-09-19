"""
Input Statement: HEADL

Purpose: Give text for table headings.

This statement allows definition of up to 3 headlines for output tables.
Additional lines will replace the third line.
"""

from __future__ import annotations
from pydantic import field_validator
from .statement_base import StatementBase


class HEADL(StatementBase):
    """
### Usage
Defines header information for ShellDesign output files and reports.

### Examples
```python
# Simple header
HEADL(heading="VERIFICATION ANALYSIS")
# -> 'HEADL VERIFICATION ANALYSIS'

# Project identification header
HEADL(heading="Bridge Pier Analysis - Phase 1")
# -> 'HEADL Bridge Pier Analysis - Phase 1'
```

### Parameters

- [Parameters documented in class definition]

### Notes

- Header text is limited to 64 characters maximum.
- Headers appear in output files and reports for identification.
- Multiple HEADL statements can be used for multi-line headers.
"""
    
    heading: str
    
    @field_validator('heading')
    @classmethod
    def validate_heading(cls, v):
        """Validate heading text."""
        if not v:
            raise ValueError("Heading text cannot be empty")
        
        if len(v) > 64:
            raise ValueError("Heading text must be maximum 64 characters")
            
        return v
    
    @property
    def input(self) -> str:
        """Generate the HEADL input string."""
        return f"HEADL {self.heading}"
    
    def _build_input_string(self) -> str:
        """Build the input string for this HEADL statement."""
        return f"HEADL {self.heading}"
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this HEADL statement."""
        return self._build_identifier(field_order=['heading'], add_hash=True)