from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import Field


from .statement_base import StatementBase


class LORES(StatementBase):
    """
    Represents the LORES statement for defining load resultants.

    Defines load resultants of the OLCs (Output Load Cases) where the response
    is to be re-calculated for a new support system defined with GRECO.

    This class supports three mutually exclusive modes of operation:
    1.  **Manual Definition**: Specify an OLC number, its part (REAL or IMAG),
        and the load resultant values directly.
    2.  **Automatic Generation**: Generate LORES data from a SIN file.
    3.  **Print/List**: List reaction forces for OLCs or ALCs.

    ### Examples:
    1. Manual definition of real part for OLC 1:
       LORES(lc=1, part='REAL', resultants=[-9.7283E+02, 4.1105E-09])
       -> "LORES 1 REAL -9.7283E+02 4.1105E-09"

    2. Manual definition of imaginary part for OLC 2:
       LORES(lc=2, part='IMAG', resultants=[-2.0579E+03, -2.9789E+00])
       -> "LORES 2 IMAG -2.0579E+03 -2.9789E+00"

    3. Automatic generation from SIN file:
       LORES(sin=True) -> "LORES SIN="

    4. Print OLC reaction forces:
       LORES(pri_olc=True) -> "LORES PRI=OLC"

    5. Print ALC reaction forces:
       LORES(pri_alc=True) -> "LORES PRI=ALC"

    ### Parameters:

    lc : Optional[int]
        OLC-number for manual definition.

    part : Optional[Literal['REAL', 'IMAG']]
        The part of the load resultant (real or imaginary).

    resultants : List[float]
        A list of 1 to 6 load resultant values.

    sin : bool
        If True, generate LORES data automatically from a SIN file.

    pri_olc : bool
        If True, list OLC reaction forces.

    pri_alc : bool
        If True, list ALL reaction forces on SIN file.
    """

    # Mode 1: Manual definition
    lc: Optional[int] = Field(None, description="OLC-number for manual definition")
    part: Optional[Literal["REAL", "IMAG"]] = Field(
        None, description="The part of the load resultant (real or imaginary)"
    )
    resultants: List[float] = Field(
        default_factory=list, description="A list of 1 to 6 load resultant values"
    )

    # Mode 2: Automatic generation from SIN file
    sin: bool = Field(
        False, description="If True, generate LORES data automatically from a SIN file"
    )

    # Mode 3: Print options
    pri_olc: bool = Field(False, description="If True, list OLC reaction forces")
    pri_alc: bool = Field(
        False, description="If True, list ALL reaction forces on SIN file"
    )

    @property
    def identifier(self) -> str:
        return self._build_identifier(add_hash=True)

    def _build_input_string(self) -> str:
        """Build the LORES input string."""
        manual_mode = self.lc is not None and self.part is not None

        parts: List[str] = ["LORES"]
        if manual_mode:
            parts.append(str(self.lc))
            if self.part is not None:
                parts.append(self.part)
            parts.extend(f"{r:.4E}" for r in self.resultants)
        elif self.sin:
            parts.append("SIN=")
        elif self.pri_olc:
            parts.append("PRI=OLC")
        elif self.pri_alc:
            parts.append("PRI=ALC")

        self.input = " ".join(parts)
        return self.input
