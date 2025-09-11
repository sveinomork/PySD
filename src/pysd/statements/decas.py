from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import Field, field_validator
from .cases import Cases, normalize_cases, CaseRange
from .statement_base import StatementBase
from .greco import GrecoID



class DECAS(StatementBase):
    """
### Usage
Defines design cases and their governing load combinations for structural verification.

### Examples
```python
# Single design case with load combinations
DECAS(ls="ULS", ilc=[101, 102, 103])
# -> 'DECAS LS=ULS ILC=101,102,103'

# Single design case with one load case
DECAS(ls="ULS", bas=101)
# -> 'DECAS LS=ULS BAS=101'

# Design case with phase angles using CaseBuilder
DECAS(ls="ULS", pha=CaseBuilder().add(0).add(45, 90))
# -> 'DECAS LS=ULS PHA=0,45-90'

# Design case with BAS and GRECO letter
DECAS(ls="FLS", bas="300-305", greco="A")
# -> 'DECAS LS=FLS BAS=300-305:A'

# Using tuple format with GRECO
DECAS(ls="ULS", bas=(101,102), greco="A")
# -> 'DECAS LS=ULS BAS=101-102:A'

# Using tuple format with step
DECAS(ls="ULS", bas=(101,110,2), greco="B")
# -> 'DECAS LS=ULS BAS=101-110-2:B'

# Using list format with GRECO  
DECAS(ls="ULS", bas=[(101,102)], greco="A")
# -> 'DECAS LS=ULS BAS=101-102:A'
```

### Parameters

- [Parameters documented in class definition]

### Notes

- Design cases group load combinations for different limit state verifications.
- Load case parameters support three input formats: CaseBuilder, string, or list.
- Phase angles (PHA) support stepped ranges for dynamic analysis.
- BAS can include GRECO letters for specific load combination versions.
"""
    ls: Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS'] = Field(..., description="Load scenario type: ULS=Ultimate Limit State, ALS=Accidental Limit State, SLS=Serviceability Limit State, CRW=Controlled Response Wave, FLS=Fatigue Limit State")

    # Optional IDs for various features
    stl: Optional[int] = Field(None, description="Steel ID reference")
    dwp: Optional[int] = Field(None, description="Deep water point ID reference")
    cw: Optional[int] = Field(None, description="Controlled wave ID (only for LS=CRW)")
    dcw: Optional[int] = Field(None, description="Design controlled wave ID (only for LS=CRW)")
    dtc: Optional[int] = Field(None, description="Design time constant ID (only for LS=CRW)")

    # Flags
    por: bool = Field(False, description="Enable pore pressure effects")
    emp_ok: bool = Field(False, description="Enable EMP=OK mode (not for LS=FLS)")

    # Phase angles for dynamic loads
    pha: Optional[Union[Literal['ALL'], str, list[CaseRange], Cases]] = Field(None, description="Phase angles for dynamic analysis. Use 'ALL' for all phases or specify ranges")

    # Load case definitions - now use unified formatting with cleaner types
    ilc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(None, description="Internal Load Cases")
    olc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(None, description="Output Load Cases")
    plc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(None, description="Primary Load Cases")
    elc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(None, description="Environmental Load Cases")
    bas: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(None, description="BAS load combinations (required for LS=FLS). Use with greco parameter to append GRECO reference.")

    # Optional text description
    txt: Optional[str] = Field(None, description="Optional text description (max 80 chars)")
    greco: Optional[GrecoID] = Field(None, description="Optional GRECO letter for BAS load combinations (appended as :A, :B, etc.)")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this DECAS statement."""
        return self.ls

    @field_validator('pha', 'ilc', 'olc', 'plc', 'elc', 'bas', mode='before')
    @classmethod
    def normalize_case_inputs(cls, v):
        """Convert any supported format to Cases."""
        if v is None or v == 'ALL':
            return v
        return normalize_cases(v)
    
    def model_post_init(self, __context):
        """Post-initialization to handle greco parameter integration."""
        # If we have both bas and greco, integrate greco into the Cases object
        if self.bas is not None and self.greco is not None and isinstance(self.bas, Cases):
            if not self.bas.greco:  # Only set if not already set
                self.bas.greco = self.greco
        
        # Build the input string after all initialization
        self._build_input_string()

    def _build_input_string(self) -> None:
        """Build the input string (pure formatting logic)."""
        parts = ["DECAS", f"LS={self.ls}"]

        if self.stl is not None:
            parts.append(f"STL={self.stl}")
        if self.dwp is not None:
            parts.append(f"DWP={self.dwp}")
        if self.cw is not None:
            parts.append(f"CW={self.cw}")
        if self.por:
            parts.append("POR=")
        if self.dcw is not None:
            parts.append(f"DCW={self.dcw}")
        if self.dtc is not None:
            parts.append(f"DTC={self.dtc}")

        if self.pha is not None:
            if self.pha == 'ALL':
                parts.append("PHA=ALL")
            else:
                parts.append(f"PHA={str(self.pha)}")

        if self.emp_ok:
            parts.append("EMP=OK")

        # Load cases - now use unified formatting
        if self.ilc is not None:
            parts.append(f"ILC={str(self.ilc)}")
        if self.olc is not None:
            parts.append(f"OLC={str(self.olc)}")
        if self.plc is not None:
            parts.append(f"PLC={str(self.plc)}")
        if self.elc is not None:
            parts.append(f"ELC={str(self.elc)}")
        if self.bas is not None:
            bas_str = str(self.bas)
            # Check if the Cases object already has greco, otherwise use the separate greco field
            if isinstance(self.bas, Cases) and self.bas.greco:
                # Greco is already included in the Cases object
                parts.append(f"BAS={bas_str}")
            elif self.greco is not None:
                # Use separate greco field if Cases doesn't have it
                bas_str += f":{self.greco}"
                parts.append(f"BAS={bas_str}")
            else:
                parts.append(f"BAS={bas_str}")

        if self.txt:
            txt_val = f'"{self.txt}"' if ' ' in self.txt else self.txt
            parts.append(f"TXT={txt_val}")

        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input