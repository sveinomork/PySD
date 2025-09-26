"""
Input Statement: HEADL

Purpose: Give text for table headings.

This statement allows definition of up to 3 headlines for output tables.
Additional lines will replace the third line.
"""

from __future__ import annotations

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

    @property
    def identifier(self) -> str:
        """Get unique identifier for this HEADL statement."""
        return self._build_identifier(field_order=["heading"], add_hash=True)

    def _build_input_string(self) -> str:
        """Build the input string for this HEADL statement."""
        return f"HEADL {self.heading}"
