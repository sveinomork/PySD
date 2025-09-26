from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import Field, field_validator
from .cases import Cases, normalize_cases, CaseRange
from .statement_base import StatementBase
from .greco import GrecoID
import hashlib


class DECAS(StatementBase):
    """

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
    - ls: Load scenario type (ULS, ALS, SLS, CRW, FLS)
    - stl: Steel ID reference
    - dwp: Deep water point ID reference
    - cw: Controlled wave ID (only for LS=CRW)
    - dcw: Design controlled wave ID (only for LS=CRW)
    - dtc: Design time constant ID (only for LS=CRW)
    - por: Enable pore pressure effects
    - emp_ok: Enable EMP=OK mode (not for LS=FLS)
    - pha: Phase angles for dynamic analysis. Use 'ALL' for all phases or specify ranges
    - ilc: Internal Load Cases
    - olc: Output Load Cases
    - plc: Primary Load Cases
    - elc: Environmental Load Cases
    - bas: BAS load combinations (required for LS=FLS). Use with greco
    - txt: Optional text description (max 80 chars)
    - greco: Optional GRECO letter for BAS load combinations (appended as :A, :B, etc.)






    ### Notes

    - Design cases group load combinations for different limit state verifications.
    - Load case parameters support three input formats: CaseBuilder, string, or list.
    - Phase angles (PHA) support stepped ranges for dynamic analysis.
    - BAS can include GRECO letters for specific load combination versions.
    """

    ls: Literal["ULS", "ALS", "SLS", "CRW", "FLS"] = Field(
        ...,
        description="Load scenario type: ULS=Ultimate Limit State, ALS=Accidental Limit State, SLS=Serviceability Limit State, CRW=Controlled Response Wave, FLS=Fatigue Limit State",
    )

    # Optional IDs for various features
    stl: Optional[int] = Field(None, description="Steel ID reference")
    dwp: Optional[int] = Field(None, description="Deep water point ID reference")
    cw: Optional[int] = Field(None, description="Controlled wave ID (only for LS=CRW)")
    dcw: Optional[int] = Field(
        None, description="Design controlled wave ID (only for LS=CRW)"
    )
    dtc: Optional[int] = Field(
        None, description="Design time constant ID (only for LS=CRW)"
    )

    # Flags
    por: bool = Field(False, description="Enable pore pressure effects")
    emp_ok: bool = Field(False, description="Enable EMP=OK mode (not for LS=FLS)")

    # Phase angles for dynamic loads
    pha: Optional[Union[Literal["ALL"], str, list[CaseRange], Cases]] = Field(
        None,
        description="Phase angles for dynamic analysis. Use 'ALL' for all phases or specify ranges",
    )

    # Load case definitions - now use unified formatting with cleaner types
    ilc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(
        None, description="Internal Load Cases"
    )
    olc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(
        None, description="Output Load Cases"
    )
    plc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(
        None, description="Primary Load Cases"
    )
    elc: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(
        None, description="Environmental Load Cases"
    )
    bas: Optional[Union[str, CaseRange, list[CaseRange], Cases]] = Field(
        None,
        description="BAS load combinations (required for LS=FLS). Use with greco parameter to append GRECO reference.",
    )

    # Optional text description
    txt: Optional[str] = Field(
        None, description="Optional text description (max 80 chars)"
    )
    greco: Optional[GrecoID] = Field(
        None,
        description="Optional GRECO letter for BAS load combinations (appended as :A, :B, etc.)",
    )

    @property
    def identifier(self) -> str:
        """Get unique identifier for this DECAS statement."""
        return self._build_identifier(field_order=["ls"], add_hash=True)

    @field_validator("pha", "ilc", "olc", "plc", "elc", "bas", mode="before")
    @classmethod
    def normalize_case_inputs(cls, v):
        """Convert any supported format to Cases."""
        if v is None or v == "ALL":
            return v
        return normalize_cases(v)

    def _build_input_string(self) -> None:
        """Build the input string using hybrid approach - builder for simple fields, custom for complex ones."""

        # If we have both bas and greco, integrate greco into the Cases object
        if (
            self.bas is not None
            and self.greco is not None
            and isinstance(self.bas, Cases)
        ):
            if not self.bas.greco:  # Only set if not already set
                self.bas.greco = self.greco

        # Start with enhanced generic builder for simple fields
        builder = self._get_string_builder()
        builder.input = (
            f"{self.statement_name} LS={self.ls}"  # Initialize with LS parameter
        )

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
            if self.pha == "ALL":
                builder.input += " PHA=ALL"
            else:
                builder.input += f" PHA={str(self.pha)}"

        # Load cases - use unified formatting
        for field_name, field_value in [
            ("ilc", self.ilc),
            ("olc", self.olc),
            ("plc", self.plc),
            ("elc", self.elc),
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
            txt_val = f'"{self.txt}"' if " " in self.txt else self.txt
            builder.input += f" TXT={txt_val}"

        self.input = builder.input
