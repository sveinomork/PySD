from dataclasses import dataclass, field
from typing import Optional, Literal, TypeAlias, Final

# Type aliases to make the types more meaningful and colorful in IDE
FilePath: TypeAlias = str
FileName: TypeAlias = str
ElementType: TypeAlias = Literal["SHE", "SOL"]

# Constants for default values
DEFAULT_UNIT_FACTOR: Final[int] = 1000  # Default for both length and force units

@dataclass
class RFILE:
    """Defines input and result file references for a Sestra finite element (FE) analysis.
    
    The RFILE statement specifies the location and properties of input/result files for analysis.
    Usage depends on the type of analysis (CDM vs. CSM), unit consistency, and file structure.

    Examples:
        Basic file reference:
            >>> from statements.rfile import RFILE
            >>> rfile = RFILE(fnm="R1", suf="SIN")
            >>> print(rfile.input)
            'RFILE FNM=R1 SUF=SIN'

        File reference with a path containing spaces:
            >>> rfile = RFILE(
            ...     pre=r"C:\\My Models\\Project A",
            ...     fnm="R1",
            ...     suf="SIN",
            ...     typ="SHE"
            ... )
            >>> print(rfile.input)
            'RFILE PRE="C:\\My Models\\Project A" FNM=R1 SUF=SIN TYP=SHE'

        Full configuration with unit conversion:
            >>> rfile = RFILE(
            ...     pre="path/to/files",
            ...     fnm="R1",
            ...     tfi="model.T1",
            ...     suf="SIN",
            ...     lfi="loads.L1",
            ...     lun=1000,  # mm
            ...     fun=1000,  # N
            ...     typ="SHE"
            ... )

    Args:
        pre (Optional[str]): Path to the folder containing the FE input/result files.
            - Relative or full path accepted
            - If path contains spaces, it will be automatically quoted
            - Defaults to same directory as input file
        
        fnm (str): Basename of the Sestra result file (e.g., "R1").
            This is typically a short identifier for the analysis.
        
        tfi (Optional[str]): Sestra input file (T-file).
            Required only for CSM analysis.
        
        suf (Optional[str]): Suffix of the Sestra result file (e.g., "SIN").
            Identifies the type or version of results.
        
        lfi (Optional[str]): Sestra load input file (L-file).
            Required only if dynamic loads are used in CSM.
            Must be provided together with tfi.
        
        lun (Optional[int]): Length unit conversion factor.
            Number of millimeters per length unit.
            Not used in CSM analyses.
            Defaults to 1000 (i.e., mm).
        
        fun (Optional[int]): Force unit conversion factor.
            Number of Newtons per force unit.
            Not used in CSM analyses.
            Defaults to 1000 (i.e., N).
        
        typ (Optional[Literal["SHE", "SOL"]]): Element type selection.
            Specifies which elements to use when both types exist:
            - "SHE" for shell elements
            - "SOL" for solid elements
            Only needed if both element types exist in the FEM model.

    Note:
        - The T-file (tfi) is required when an L-file (lfi) is specified
        - Unit conversion factors (lun, fun) only apply to CDM analyses
        - Paths with spaces are automatically quoted in the output
    """
    # File identifiers
    fnm: FileName = "R1"
    pre: Optional[FilePath] = None  # Path to the folder containing the FE input/result files
    tfi: Optional[FileName] = None  # T-file name
    suf: Optional[str] = None  # Result file suffix
    lfi: Optional[FileName] = None  # L-file name
    
    # Unit conversion factors
    lun: int = DEFAULT_UNIT_FACTOR  # Length unit in mm
    fun: int = DEFAULT_UNIT_FACTOR  # Force unit in N
    
    # Element type selection
    typ: Optional[ElementType] = None
    
    # Generated SESAM input string
    input: str = field(init=False, default="RFILE")
    
    def __post_init__(self):
        if self.tfi is None and self.lfi is not None:
            raise ValueError("T-file (tfi) is required when L-file (lfi) is provided.")
        if self.lfi is not None and self.tfi is None:
            raise ValueError("L-file (lfi) requires a T-file (tfi).")

        parts:list[str] = ["RFILE"]
        if self.pre is not None:
            # Add quotes if path contains spaces, as per docstring.
            pre_val = f'"{self.pre}"' if " " in self.pre else self.pre
            parts.append(f"PRE={pre_val}")
        
        parts.append(f"FNM={self.fnm}")

        if self.suf is not None:
            parts.append(f"SUF={self.suf}")

        if self.tfi is not None:
            parts.append(f"TFI={self.tfi}")
        if self.lfi is not None:
            parts.append(f"LFI={self.lfi}")
        if self.lun != 1000:
            parts.append(f"LUN={self.lun}")
        if self.fun != 1000:
            parts.append(f"FUN={self.fun}")
        if self.typ is not None:
            parts.append(f"TYP={self.typ}")
        
        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input