from __future__ import annotations
from typing import Optional, Tuple, List, Union
from pydantic import  Field


from .statement_base import StatementBase

class XTFIL(StatementBase):
    """Define XTRACT plot files.
    
    Data is fetched from an OLC-file and optionally from a DEC-file.
    The XTFIL command defines what data should be included in plot files and how it should be presented.
    
    ### Parameters:
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
    ax: Optional[str] = Field(None, description="123-axes)")
    fh: Optional[str] = Field(None, description=" F- and H-section numbers")
    th: Optional[str] = Field(None, description="shell thickness")                           
    re: Optional[str] = Field(None, description="rebar layer cross section area")
    te: Optional[str] = Field(None, description="tendon layer cross section area")
    st: Optional[str] = Field(None, description="stirrup cross section area")
    nd: Optional[str] = Field(None, description="node displacements (only area plot)")
    df: Optional[str] = Field(None, description="design forces and moments")
    pf: Optional[str] = Field(None, description="principal membrane forces")
    pm: Optional[str] = Field(None, description="principal moments")
    ps: Optional[str] = Field(None, description="principal shear forces")
    pe: Optional[str] = Field(None, description="principal face strain")
    cs: Optional[str] = Field(None, description="utilization ratio concrete stresses")
    rs: Optional[str] = Field(None, description="utilization ratio rebar stresses")
    ts: Optional[str] = Field(None, description="utilization ratio tendon stresses")
    sc: Optional[str] = Field(None, description="utilization ratios shear capacity")
    cw: Optional[str] = Field(None, description="utilization ratio crack widths")
    tw: Optional[str] = Field(None, description="utilization ratio crack widths at tendons")
    cz: Optional[str] = Field(None, description="Results compression zone tightness")
    ct: Optional[str] = Field(None, description="Results crack width tightness")
    ms: Optional[str] = Field(None, description="Results maximum membrane stress tightness")
    lf: Optional[str] = Field(None, description="location dependent load factors")
    pv: Optional[str] = Field(None, description="only peak plots of all design cases are plotted if more than one case is stored")

   

    @property
    def identifier(self) -> str:
        """Get unique identifier for this XTFIL statement."""
        return self._build_identifier(field_order=['fn', 'pa'], add_hash=True)
    
    

    def _build_input_string(self) -> str:
        self.input = self._build_string_generic(
                field_order=['fn', 'pa', 'fs', 'hs', 'ax', 'fh', 'th', 're', 'te', 'st', 'nd', 'df', 'pf', 'pm', 'ps', 
                             'pe', 'cs', 'rs', 'ts', 'sc', 'cw', 'tw', 'cz', 'ct', 'ms', 'lf', 'pv'],
                float_precision=3  # Use 3 decimal places for better readability
            )
        
    
    