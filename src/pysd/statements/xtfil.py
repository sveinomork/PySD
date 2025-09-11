from __future__ import annotations
from typing import Optional, Tuple, List, Union
from pydantic import  Field


from .statement_base import StatementBase

class XTFIL(StatementBase):
    """Define XTRACT plot files.
    
    Data is fetched from an OLC-file and optionally from a DEC-file.
    The XTFIL command defines what data should be included in plot files and how it should be presented.
    
    Parameters:
        fn: str
            Name of plot file (max 32 characters)
        pa: str
            Structural part name - must be defined to create a plot (max 8 characters)
        fs: Tuple[int, int], optional
            F-section range [default: all]
        hs: Tuple[int, int], optional
            H-section range [default: all]
        plot_items: List[str], optional
            List of plot items to include. Valid values:
            From OLC-file:
                - AX: 123-axes
                - FH: F- and H-section numbers
                - TH: shell thickness
            From DEC-file:
                - RE: rebar layer cross section area
                - RC: rebar configuration layer cross section areas
                - TE: tendon layer cross section area
                - ST: stirrup cross section area
            Design cases:
                - ND: node displacements (only area plot)
                - DF: design forces and moments
                - PF: principal membrane forces
                - PM: principal moments
                - PS: principal shear forces
            Design calculations:
                - PE: principal face strain
                - CS: utilization ratio concrete stresses
                - RS: utilization ratio rebar stresses
                - TS: utilization ratio tendon stresses
                - SC: utilization ratios shear capacity
                - CW: utilization ratio crack widths
                - TW: utilization ratio crack widths at tendons
                - CZ: Results compression zone tightness
                - CT: Results crack width tightness
                - MS: Results maximum membrane stress tightness
                - LF: location dependent load factors
        peak_value_only: bool = False
            Only peak plots of all design cases are plotted if more than one case is stored
        reb_tol: float = 10.0
            Rebar tolerance in mm² (>0) for legend level
        ten_tol: float = 100.0
            Tendon tolerance in mm² (>0) for legend level
        thi_tol: float = 10.0
            Thickness tolerance in mm (>0) for legend level
        num_levels: int = 64
            Number of levels on legend for rebar area and thickness
        reb_labels: bool = True
            Whether to plot rebar labels
        thi_labels: bool = True
            Whether to plot thickness labels
        time_it: bool = False
            Whether to show time used for plotting
    """
    # Required parameters
    fn: str = Field(..., description="Name of plot file (max 32 characters)")
    pa: str = Field(..., description="Structural part name (max 8 characters)")

    # Optional section ranges
    fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="F-section range")
    hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="H-section range")

    # Plot items
    plot_items: List[str] = Field(default_factory=list, description="List of plot items to include")

    # Plot options
    peak_value_only: bool = Field(False, description="Only plot peak values")
    reb_tol: float = Field(10.0, description="Rebar tolerance (mm²)")
    ten_tol: float = Field(100.0, description="Tendon tolerance (mm²)")
    thi_tol: float = Field(10.0, description="Thickness tolerance (mm)")
    num_levels: int = Field(64, description="Number of legend levels")
    reb_labels: bool = Field(True, description="Show rebar labels")
    thi_labels: bool = Field(True, description="Show thickness labels")
    time_it: bool = Field(False, description="Show plotting time")
    
    # Auto-generated fields
    key: str = Field(default="", init=False, description="Key for dictionary storage")
 
    @property
    def identifier(self) -> str:
        """Get unique identifier for this XTFIL statement."""
        return self.key
    
    

    def _build_input_string(self) -> str:
        """Build the XTFIL input string."""
        # Generate the key
        key_parts = [f"FN={self.fn}"]
        key_parts.append(f"{self.pa}")
        if self.fs is not None:
            if isinstance(self.fs, tuple):
                key_parts.append(f"FS{self.fs[0]}-{self.fs[1]}")
            else:
                key_parts.append(f"FS{self.fs}")
        if self.hs is not None:
            if isinstance(self.hs, tuple):
                key_parts.append(f"HS{self.hs[0]}-{self.hs[1]}")
            else:
                key_parts.append(f"HS{self.hs}")
        self.key = "_".join(key_parts)
            
        # Build the XTFIL input string
        parts = ["XTFIL"]
        
        # Add required parameters
        parts.append(f"FN={self.fn}")
        parts.append(f"PA={self.pa}")
        
        # Add section ranges if specified
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
            
        # Add plot items if specified
        for item in self.plot_items:
            parts.append(f"PI={item}")
            
        # Add peak value flag if True
        if self.peak_value_only:
            parts.append("PV")
            
        # Add tolerance values if non-default
        if self.reb_tol != 10.0:
            parts.append(f"REBTOL={self.reb_tol}")
        if self.ten_tol != 100.0:
            parts.append(f"TENTOL={self.ten_tol}")
        if self.thi_tol != 10.0:
            parts.append(f"THITOL={self.thi_tol}")
            
        # Add legend levels if non-default
        if self.num_levels != 64:
            parts.append(f"NUMLEV={self.num_levels}")
            
        # Add label settings if not default
        if not self.reb_labels:
            parts.append("REBLAB=OFF")
        if not self.thi_labels:
            parts.append("THILAB=OFF")
            
        # Add timing flag if True
        if self.time_it:
            parts.append("TIMEIT")
            
        # Join all parts with spaces
        self.input = " ".join(parts)
        return self.input
    
    