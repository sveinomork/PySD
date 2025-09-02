from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Union, Literal

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

@dataclass
class TABLE:
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
    tab: Optional[TabType] = None
    ur: Optional[UrType] = None

    # General filters
    pa: Optional[str] = None
    fs: Optional[Union[int, Tuple[int, int]]] = None
    hs: Optional[Union[int, Tuple[int, int]]] = None
    ls: Optional[Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']] = None
    nd: Optional[int] = None
    of: Optional[str] = None
    nf: Optional[str] = None

    # Load case filters
    ilc: Optional[Cases|str] = None
    olc: Optional[Cases|str] = None
    elc: Optional[Cases|str] = None
    bas: Optional[Cases|str] = None
    pha: Optional[Cases|str] = None

    # TAB specific parameters
    el: Optional[int] = None
    se: Optional[int] = None
    rn: Optional[int] = None
    x1: Optional[Tuple[float, float, float]] = None
    x2: Optional[Tuple[float, float, float]] = None
    x3: Optional[Tuple[float, float, float]] = None
    enr: Optional[Tuple[int, int]] = None
    cc: Optional[Tuple[float, float]] = None

    # UR specific parameters
    tv: Optional[float] = None
    fm: bool = False  # For UR=MAX
    sk: Optional[Literal['E', 'F', 'H', 'A']] = None
    rl: Optional[Union[str, Literal['ALL']]] = None
    al: Optional[float] = None
    fa: Optional[Union[int, Literal['ALL']]] = None
    tl: Optional[Union[str, Literal['ALL']]] = None

    input: str = field(init=False, default="TABLE")

    def __post_init__(self):
        # --- Validation ---
        if (self.tab is None and self.ur is None) or \
           (self.tab is not None and self.ur is not None):
            raise ValueError("Exactly one of 'tab' or 'ur' must be specified for a TABLE statement.")

        # --- String Building ---
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

        # Add ELC and BAS load case filters (as objects, not dicts)
        if self.elc:
            parts.append(f"ELC={str(self.elc)}")
        if self.bas:
            parts.append(f"BAS={str(self.bas)}")                                                                                                                                                                                                                                                                                               

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

    def __str__(self) -> str:
        return self.input