from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import warnings
from .cases import Cases, normalize_cases, CaseRange


class DECAS(BaseModel):
    """
### Usage
Defines design cases and their governing load combinations for structural verification.

### Examples
```python
# Single design case with load combinations
DECAS(ls="ULS", ilc=[101, 102, 103])
# -> 'DECAS LS=ULS ILC=101,102,103'

# Design case with phase angles using CaseBuilder
DECAS(ls="ULS", pha=CaseBuilder().add(0).add(45, 90))
# -> 'DECAS LS=ULS PHA=0,45-90'

# Design case with BAS and GRECO letter
DECAS(ls="FLS", bas=CaseBuilder().add(300, 305).add_greco("A"))
# -> 'DECAS LS=FLS BAS=300-305:A'
```

### Parameters

- [Parameters documented in class definition]

### Notes

- Design cases group load combinations for different limit state verifications.
- Load case parameters support three input formats: CaseBuilder, string, or list.
- Phase angles (PHA) support stepped ranges for dynamic analysis.
- BAS can include GRECO letters for specific load combination versions.
"""
    ls: Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']

    # Optional IDs for various features
    stl: Optional[int] = None
    dwp: Optional[int] = None
    cw: Optional[int] = None
    dcw: Optional[int] = None
    dtc: Optional[int] = None

    # Flags
    por: bool = False
    emp_ok: bool = False

    # Phase angles for dynamic loads
    pha: Optional[Union[Literal['ALL'], str, list[CaseRange], Cases]] = None

    # Load case definitions - now support Cases and strings too
    ilc: Optional[Union[str, list[CaseRange], Cases]] = None
    olc: Optional[Union[str, list[CaseRange], Cases]] = None
    plc: Optional[Union[str, list[CaseRange], Cases]] = None
    elc: Optional[Union[str, list[CaseRange], Cases]] = None
    bas: Optional[Union[str, list[CaseRange], Cases]] = None

    # Optional text description
    txt: Optional[str] = None

    input: str = Field(default="DECAS", init=False)

    @field_validator('pha', 'ilc', 'olc', 'plc', 'elc', 'bas', mode='before')
    @classmethod
    def normalize_case_inputs(cls, v):
        """Convert any supported format to Cases."""
        if v is None or v == 'ALL':
            return v
        return normalize_cases(v)

    @model_validator(mode='after')
    def validate_decas_requirements(self) -> 'DECAS':
        """Validate DECAS requirements and build input string."""
        # --- Validation ---
        if self.ls != 'CRW' and any([self.cw, self.dcw, self.dtc]):
            raise ValueError("CW, DCW, and DTC are only applicable for LS=CRW.")

        if self.ls == 'FLS' and self.emp_ok:
            raise ValueError("EMP=OK is not implemented for LS=FLS.")

        if self.ls == 'FLS':
            if not self.bas:
                raise ValueError("BAS must be provided for LS=FLS.")
            
            # Convert to string for validation
            if isinstance(self.bas, Cases):
                bas_str = str(self.bas)
            else:
                bas_str = str(self.bas)
            
            # Check if it's a single range format (e.g., "101-106" or "101-106:A")
            if ':' in bas_str:
                range_part = bas_str.split(':')[0]
            else:
                range_part = bas_str
            
            # Simple check: should contain exactly one dash and no commas
            if ',' in range_part or range_part.count('-') != 1:
                warnings.warn(
                    "For LS=FLS, BAS should be a single range (e.g., '101-106' or CaseBuilder().add(101, 106)) "
                    "for correct damage accumulation.", UserWarning
                )

        # --- String Building ---
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
            parts.append(f"BAS={str(self.bas)}")

        if self.txt:
            if len(self.txt) > 80:
                raise ValueError("TXT cannot exceed 80 characters.")
            txt_val = f'"{self.txt}"' if ' ' in self.txt else self.txt
            parts.append(f"TXT={txt_val}")

        self.input = " ".join(parts)
        return self

    def __str__(self) -> str:
        return self.input