from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import Field, field_validator
from .cases import Cases, normalize_cases, CaseRange
from .statement_base import StatementBase
from .greco import GrecoID
import hashlib



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
     
        
        # Start with load scenario
        parts = [self.ls]
        
        # Add key distinguishing parameters
        if self.stl is not None:
            parts.append(f"STL{self.stl}")
        if self.dwp is not None:
            parts.append(f"DWP{self.dwp}")
        if self.cw is not None:
            parts.append(f"CW{self.cw}")
        if self.por:
            parts.append("POR")
        if self.emp_ok:
            parts.append("EMP")
        
        # Add load case information - this is the key extension you requested
        if self.bas and isinstance(self.bas, Cases) and self.bas.ranges:
            first_range = self.bas.ranges[0]
            if isinstance(first_range, int):
                parts.append(f"BAS{first_range}")
            elif isinstance(first_range, tuple):
                parts.append(f"BAS{first_range[0]}-{first_range[1]}")
        elif self.bas:
            # Handle string or other formats
            bas_str = str(self.bas).replace(',', '').replace('-', '_')[:10]  # Truncate for readability
            parts.append(f"BAS{bas_str}")
        
        if self.olc and isinstance(self.olc, Cases) and self.olc.ranges:
            first_range = self.olc.ranges[0]
            if isinstance(first_range, int):
                parts.append(f"OLC{first_range}")
            elif isinstance(first_range, tuple):
                parts.append(f"OLC{first_range[0]}-{first_range[1]}")
        elif self.olc:
            olc_str = str(self.olc).replace(',', '').replace('-', '_')[:10]
            parts.append(f"OLC{olc_str}")
        
        if self.elc and isinstance(self.elc, Cases) and self.elc.ranges:
            first_range = self.elc.ranges[0]
            if isinstance(first_range, int):
                parts.append(f"ELC{first_range}")
            elif isinstance(first_range, tuple):
                parts.append(f"ELC{first_range[0]}-{first_range[1]}")
        elif self.elc:
            elc_str = str(self.elc).replace(',', '').replace('-', '_')[:10]
            parts.append(f"ELC{elc_str}")
        
        # Add GRECO if present
        if self.greco:
            parts.append(f"G{self.greco}")
        
        # Build human-readable identifier
        identifier = "_".join(parts)
        
        # If identifier gets too long or complex, use hash fallback
        if len(identifier) > 60:
            # Use the complete input string for uniqueness, but hash it for brevity
            input_str = self.input if hasattr(self, 'input') else str(self)
            hash_obj = hashlib.sha256(input_str.encode())
            short_hash = hash_obj.hexdigest()[:10]  # 10 chars for better uniqueness
            return f"{self.ls}_{short_hash}"
        
        return identifier

    @field_validator('pha', 'ilc', 'olc', 'plc', 'elc', 'bas', mode='before')
    @classmethod
    def normalize_case_inputs(cls, v):
        """Convert any supported format to Cases."""
        if v is None or v == 'ALL':
            return v
        return normalize_cases(v)
    


    def _build_input_string(self) -> None:
        """Build the input string using hybrid approach - builder for simple fields, custom for complex ones."""
        
        # If we have both bas and greco, integrate greco into the Cases object
        if self.bas is not None and self.greco is not None and isinstance(self.bas, Cases):
            if not self.bas.greco:  # Only set if not already set
                self.bas.greco = self.greco

        # Start with enhanced generic builder for simple fields
        builder = self._get_string_builder()
        builder.input = f"{self.statement_name} LS={self.ls}"  # Initialize with LS parameter
        
        # Add simple fields using the builder
        builder.add_param("stl", self.stl)
        builder.add_param("dwp", self.dwp)  
        builder.add_param("cw", self.cw)
        builder.add_param("dcw", self.dcw)
        builder.add_param("dtc", self.dtc)
        
        # Handle boolean flags
        if self.por:
            builder.input += " POR="
        if self.emp_ok:
            builder.input += " EMP=OK"
        
        # Handle complex fields manually for better control
        if self.pha is not None:
            if self.pha == 'ALL':
                builder.input += " PHA=ALL"
            else:
                builder.input += f" PHA={str(self.pha)}"

        # Load cases - use unified formatting
        for field_name, field_value in [
            ("ilc", self.ilc), ("olc", self.olc), ("plc", self.plc), 
            ("elc", self.elc)
        ]:
            if field_value is not None:
                builder.input += f" {field_name.upper()}={str(field_value)}"

        # Handle BAS with special GRECO logic
        if self.bas is not None:
            bas_str = str(self.bas)
            # Check if the Cases object already has greco, otherwise use the separate greco field
            if isinstance(self.bas, Cases) and self.bas.greco:
                # Greco is already included in the Cases object
                builder.input += f" BAS={bas_str}"
            elif self.greco is not None:
                # Use separate greco field if Cases doesn't have it
                bas_str += f":{self.greco}"
                builder.input += f" BAS={bas_str}"
            else:
                builder.input += f" BAS={bas_str}"

        # Handle text with potential quoting
        if self.txt:
            txt_val = f'"{self.txt}"' if ' ' in self.txt else self.txt
            builder.input += f" TXT={txt_val}"

        self.input = builder.input

    def __str__(self) -> str:
        return self.input