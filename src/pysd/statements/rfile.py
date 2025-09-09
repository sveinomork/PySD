from __future__ import annotations
from typing import Optional, Literal, TypeAlias, Final
from pydantic import BaseModel, Field, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext

# Type aliases to make the types more meaningful and colorful in IDE
FilePath: TypeAlias = str
FileName: TypeAlias = str
ElementType: TypeAlias = Literal["SHE", "SOL"]

# Constants for default values
DEFAULT_UNIT_FACTOR: Final[int] = 1000  # Default for both length and force units

class RFILE(BaseModel):
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

    ### Validation Rules

    1. **FNM Format**: Filename (FNM) is required and cannot be empty
    2. **File Dependencies**: L-file (LFI) requires T-file (TFI) to be specified
    3. **Unit Factors**: Length (LUN) and force (FUN) unit factors must be positive
    4. **Uniqueness**: Typically only one RFILE per model (warning if multiple)

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
    fnm: FileName = Field("R1", description="Basename of the Sestra result file")
    pre: Optional[FilePath] = Field(None, description="Path to the folder containing the FE input/result files")
    tfi: Optional[FileName] = Field(None, description="T-file name")
    suf: Optional[str] = Field(None, description="Result file suffix")
    lfi: Optional[FileName] = Field(None, description="L-file name")
    
    # Unit conversion factors
    lun: int = Field(DEFAULT_UNIT_FACTOR, description="Length unit in mm")
    fun: int = Field(DEFAULT_UNIT_FACTOR, description="Force unit in N")
    
    # Element type selection
    typ: Optional[ElementType] = Field(None, description="Element type selection")
    
    # Auto-generated field
    input: str = Field(default="", init=False, description="Generated input string")

    @model_validator(mode='after')
    def build_input_string(self) -> 'RFILE':
        """Build input string and run instance-level validation."""
        
        # Execute instance-level validation rules
        context = ValidationContext(current_object=self)
        issues = execute_validation_rules(self, context, level='instance')
        
        # Handle issues according to global config
        for issue in issues:
            context.add_issue(issue)  # Auto-raises if configured
        
        # Build input string
        parts: list[str] = ["RFILE"]
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
        return self
    
    def execute_cross_container_validation(self, sd_model) -> list:
        """
        Execute cross-container validation rules for this RFILE instance.
        
        This method is called when the RFILE is added to the SD_BASE model.
        """
        context = ValidationContext(
            current_object=self,
            full_model=sd_model  # This enables access to all containers
        )
        
        # Execute model-level validation rules
        return execute_validation_rules(self, context, level='model')

    def __str__(self) -> str:
        return self.input
    
    def formatted(self) -> str:
        """Legacy method for backward compatibility."""
        return self.input