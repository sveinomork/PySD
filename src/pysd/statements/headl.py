"""
Input Statement: HEADL

Purpose: Give text for table headings.

This statement allows definition of up to 3 headlines for output tables.
Additional lines will replace the third line.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class HEADL:
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
    
    def __post_init__(self) -> None:
        """Validate input parameters."""
        if not self.heading:
            raise ValueError("Heading text cannot be empty")
        
        if len(self.heading) > 64:
            raise ValueError("Heading text must be maximum 64 characters")
    
    @property
    def input(self) -> str:
        """Generate the HEADL input string."""
        return f"HEADL {self.heading}"