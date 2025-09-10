from __future__ import annotations
from typing import Optional, Tuple, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext
from .cases import Cases

# Define Literals for the TAB and UR types to ensure valid options
TabType = Literal[
    'ES', 'NC', 'ND', 'EL', 'IN', 'EX', 'AX', 'GE', 'OL', 'FM', 'ST',
    'OC', 'EC', 'BC', 'LR', 'CMP', 'DF', 'WF', 'PF', 'DP', 'PP', 'DR',
    'DRV', 'SR', 'RS', 'RQ'
]

UrType = Literal[
    'MAX', 'CS', 'RS', 'RC', 'RR', 'TS', 'VC', 'CC', 'ST', 'CW', 'TW',
    'CZ', 'CT', 'MS', 'NS'
]

class TABLE(BaseModel):
    """
    Represents the TABLE statement to order print of tables.

    This class supports two primary modes:
    1. TAB mode: For printing specific data tables (e.g., geometry, forces).
    2. UR mode: For printing utilization ratios (e.g., stress, capacity).

    Numerous filters can be applied to narrow down the output.

    Usage Examples:
    ---------------
    1. Print max utilization ratios for all checks:
       TABLE(ur='MAX')
       -> "TABLE UR=MAX"

    2. Print design forces for specific sections and a single BAS combination:
       TABLE(tab='DF', fs=(1, 10), bas={'': [101]})
       -> "TABLE TAB=DF FS=1-10 BAS=101"

    3. Print concrete stress utilization, skipping values below 0.8:
       TABLE(ur='CS', tv=0.8, fa='ALL')
       -> "TABLE UR=CS TV=0.8 FA=ALL"

    Parameters:
    -----------
    tab : Optional[TabType]
        The type of data table to print. Mutually exclusive with 'ur'.
    ur : Optional[UrType]
        The type of utilization ratio table to print. Mutually exclusive with 'tab'.
    pa : Optional[str]
        Filter by structural part name.
    fs : Optional[Tuple[int, int]]
        Filter by F-section range.
    hs : Optional[Tuple[int, int]]
        Filter by H-section range.
    ls : Optional[Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']]
        Filter by limit state.
    nd : Optional[int]
        Number of digits after the decimal point.
    of : Optional[str]
        Redirect output to an old file (append).
    nf : Optional[str]
        Redirect output to a new file (overwrite).
    ilc, olc, pha : Optional[LoadCaseDef]
        Filter by ILC, OLC, or PHA load cases.
    elc, bas : Optional[LoadCaseVersionDef]
        Filter by ELC or BAS load cases, with optional versioning.
    tv : Optional[float]
        Threshold value for UR tables.
    sk : Optional[Literal['E', 'F', 'H', 'A']]
        Peak value summary mode for UR tables.
    rl, tl : Optional[Union[str, Literal['ALL']]]
        Filter by rebar or tendon location ID.
    ... and other specific parameters.
    """
    # Main mode: TAB or UR
    tab: Optional[TabType] = Field(None, description="The type of data table to print")
    ur: Optional[UrType] = Field(None, description="The type of utilization ratio table to print")

    # General filters
    pa: Optional[str] = Field(None, description="Filter by structural part name")
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="Filter by F-section range")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="Filter by H-section range")
    ls: Optional[Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']] = Field(None, description="Filter by limit state")
    nd: Optional[int] = Field(None, description="Number of digits after decimal point")
    of: Optional[str] = Field(None, description="Redirect output to old file (append)")
    nf: Optional[str] = Field(None, description="Redirect output to new file (overwrite)")

    # Load case filters
    ilc: Optional[Union[Cases, str]] = Field(None, description="Filter by ILC load cases")
    olc: Optional[Union[Cases, str]] = Field(None, description="Filter by OLC load cases")
    elc: Optional[Union[Cases, str]] = Field(None, description="Filter by ELC load cases")
    bas: Optional[Union[Cases, str]] = Field(None, description="Filter by BAS load cases")
    pha: Optional[Union[Cases, str]] = Field(None, description="Filter by PHA load cases")

    # TAB specific parameters
    el: Optional[int] = Field(None, description="Element number filter")
    se: Optional[int] = Field(None, description="Section number filter")
    rn: Optional[int] = Field(None, description="Result number filter")
    x1: Optional[Tuple[float, float, float]] = Field(None, description="X1 coordinate filter")
    x2: Optional[Tuple[float, float, float]] = Field(None, description="X2 coordinate filter")
    x3: Optional[Tuple[float, float, float]] = Field(None, description="X3 coordinate filter")
    enr: Optional[Tuple[int, int]] = Field(None, description="Element number range")
    cc: Optional[Tuple[float, float]] = Field(None, description="Coordinate center")

    # UR specific parameters
    tv: Optional[float] = Field(None, description="Threshold value for UR tables")
    fm: bool = Field(False, description="For UR=MAX")
    sk: Optional[Literal['E', 'F', 'H', 'A']] = Field(None, description="Peak value summary mode")
    rl: Optional[Union[str, Literal['ALL']]] = Field(None, description="Filter by rebar location ID")
    al: Optional[float] = Field(None, description="Angle limit")
    fa: Optional[Union[int, Literal['ALL']]] = Field(None, description="Face filter")
    tl: Optional[Union[str, Literal['ALL']]] = Field(None, description="Filter by tendon location ID")

    # Auto-generated fields
    id: str = Field(default="", init=False, description="Unique identifier")
    input: str = Field(default="", init=False, description="Generated input string")

    def model_post_init(self, __context):
        """Generate unique ID and input string for this TABLE statement."""
        if self.tab:
            self.id = f"TABLE_TAB_{self.tab}"
        elif self.ur:
            self.id = f"TABLE_UR_{self.ur}"
        else:
            self.id = "TABLE_UNKNOWN"
            
        # Add filters to make ID more specific if needed
        if self.pa:
            self.id += f"_{self.pa}"
        
        # Generate the input string
        self.build_input_string()

    @model_validator(mode='after')
    def validate_modes(self) -> 'TABLE':
        """Validate that exactly one of tab or ur is specified."""
        if (self.tab is None and self.ur is None) or \
           (self.tab is not None and self.ur is not None):
            raise ValueError("Exactly one of 'tab' or 'ur' must be specified for a TABLE statement.")
        return self

    @field_validator('nd')
    @classmethod
    def validate_nd(cls, v):
        """Validate number of digits is reasonable."""
        if v is not None and (v < 0 or v > 10):
            raise ValueError("Number of digits (nd) must be between 0 and 10")
        return v

    @field_validator('tv')
    @classmethod
    def validate_tv(cls, v):
        """Validate threshold value is positive."""
        if v is not None and v < 0:
            raise ValueError("Threshold value (tv) must be non-negative")
        return v

    def build_input_string(self) -> str:
        """Build the TABLE input string."""
        parts = ["TABLE"]

        if self.tab:
            parts.append(f"TAB={self.tab}")
        elif self.ur:
            parts.append(f"UR={self.ur}")

        # Add general filters
        if self.pa is not None:
            parts.append(f"PA={self.pa}")
        if self.fs is not None:
            if isinstance(self.fs, tuple):
                parts.append(f"FS={self.fs[0]}-{self.fs[1]}")
            else:
                parts.append(f"FS={self.fs}")
        if self.hs is not None:
            if isinstance(self.hs, tuple):
                parts.append(f"HS={self.hs[0]}-{self.hs[1]}")
            else:
                parts.append(f"HS={self.hs}")
        if self.ls:
            parts.append(f"LS={self.ls}")
        if self.nd is not None:
            parts.append(f"ND={self.nd}")

        # Add load case filters
        if self.ilc:
            parts.append(f"ILC={str(self.ilc)}")
        if self.olc:
            parts.append(f"OLC={str(self.olc)}")
        if self.pha:
            parts.append(f"PHA={str(self.pha)}")
        if self.elc:
            parts.append(f"ELC={str(self.elc)}")
        if self.bas:
            parts.append(f"BAS={str(self.bas)}")

        # Add TAB specific parameters
        if self.tab is not None:
            if self.el is not None:
                parts.append(f"EL={self.el}")
            if self.se is not None:
                parts.append(f"SE={self.se}")
            if self.rn is not None:
                parts.append(f"RN={self.rn}")
            if self.x1 is not None:
                parts.append(f"X1={self.x1[0]},{self.x1[1]},{self.x1[2]}")
            if self.x2 is not None:
                parts.append(f"X2={self.x2[0]},{self.x2[1]},{self.x2[2]}")
            if self.x3 is not None:
                parts.append(f"X3={self.x3[0]},{self.x3[1]},{self.x3[2]}")
            if self.enr is not None:
                parts.append(f"ENR={self.enr[0]}-{self.enr[1]}")
            if self.cc is not None:
                parts.append(f"CC={self.cc[0]},{self.cc[1]}")

        # Add UR specific parameters
        if self.ur is not None:
            if self.tv is not None:
                parts.append(f"TV={self.tv}")
            if self.fm:
                parts.append("FM=")
            if self.sk:
                parts.append(f"SK={self.sk}")
            if self.rl is not None:
                parts.append(f"RL={self.rl}")
            if self.al is not None:
                parts.append(f"AL={self.al}")
            if self.fa is not None:
                parts.append(f"FA={self.fa}")
            if self.tl is not None:
                parts.append(f"TL={self.tl}")

        # Add file redirection last
        if self.of is not None:
            parts.append(f"OF={self.of}")
        if self.nf is not None:
            parts.append(f"NF={self.nf}")

        self.input = " ".join(parts)
        return self.input

    def validate_cross_references(self, context: ValidationContext) -> None:
        """Validate cross-references with other containers."""
        if context.full_model is None:
            return
        execute_validation_rules(self, context)

    def __str__(self) -> str:
        return self.build_input_string() if not self.input else self.input