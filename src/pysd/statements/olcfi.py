
from typing import Optional, Literal, TypeAlias, Final
from pydantic import Field

from .statement_base import StatementBase

# Type aliases to make the types more meaningful and colorful in IDE
FilePath: TypeAlias = str
FileName: TypeAlias = str
ElementType: TypeAlias = Literal["SHE", "SOL"]

# Constants for default values
DEFAULT_UNIT_FACTOR: Final[int] = 1000  # Default for both length and force units


class OLCFI(StatementBase):
    """define OLC-file data when OLC files are created, merged or read. See 
    Section 5.8.1 in Shell Design manual. An OLC-file is a database generated with ShellDesign 
    containing results from a FE analysis file, such as geometry and stress resultants 
    (section forces) for each load case (OLC) and node displacements.

    ### Examples:
    ```python
       # Example 1: a new file shall be created
       OLCFI(nf="DOMEA.OLC", name="Lower_dome_A", vers="1.0", date="8jan-94", resp="kf")
       # -> OLCFI NF=DOMEA.OLC NAME=Lower_dome_A VERS=1.0 DATE=8jan-94 RESP=kf

       # Example 2: two old files shall be read
       OLCFI(of="DOMEA.OLC")
       OLCFI(of="DOMEB.OLC")
       # -> OLCFI OF=DOMEA.OLC
       # -> OLCFI OF=DOMEB.OLC

       # Example 3: two old files shall be merged
       OLCFI(of="DOMEA.OLC", of="DOMEB.OLC", mf="DOMEAB.OLC", name="Lower_dome_AB", vers="1.1", date="8jan-94", resp="BESNY")
         # -> OLCFI OF=DOMEA.OLC OF=DOMEB.OLC MF=DOMEAB.OLC NAME=Lower_dome_AB VERS=1.1 DATE=8jan-94 RESP=BESNY
         
    ```     

    ### Args:
        of  OLC-file path (old)

        nf (str): Basename of the new OLC file (e.g., "DOMEA.OLC").
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

    ### Note:
        - The T-file (tfi) is required when an L-file (lfi) is specified
        - Unit conversion factors (lun, fun) only apply to CDM analyses
        - Paths with spaces are automatically quoted in the output
    """

    # File identifiers
    of: Optional[FilePath] = Field(None, description="OLC-file path (old)")
    nf: Optional[FilePath] = Field(
        None, description="Path to new OLC-file"
    )
    name: Optional[str] = Field(None,description="name max 48 char")
    vers: Optional[str] = Field(None,description="version max 8 char")
    date: Optional[str] = Field(None,description="date max 12 char")
    resp: Optional[str] = Field(None,description="responsible max 8 char")
    mf: Optional[FilePath] = Field(None,description="Merge file name")
    pre: Optional[FilePath] = Field(
        None, description="Path to the folder containing OLC file(s)") 
    
    
    @property
    def identifier(self) -> str:
        """Get unique identifier for this RFILE statement."""
        return self._build_identifier(field_order=["fnm"], add_hash=True)

    def _build_input_string(self) -> None:
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
        return self.input
