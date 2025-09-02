from dataclasses import dataclass, field
from typing import Optional, List, Literal

@dataclass
class LORES:
    """
    Represents the LORES statement for defining load resultants.

    Purpose:
    --------
    Defines load resultants of the OLCs (Output Load Cases) where the response
    is to be re-calculated for a new support system defined with GRECO.

    This class supports three mutually exclusive modes of operation:
    1.  **Manual Definition**: Specify an OLC number, its part (REAL or IMAG),
        and the load resultant values directly.
    2.  **Automatic Generation**: Generate LORES data from a SIN file.
    3.  **Print/List**: List reaction forces for OLCs or ALCs.

    Usage Examples:
    ---------------
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

    Parameters:
    -----------
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
    lc: Optional[int] = None
    part: Optional[Literal['REAL', 'IMAG']] = None
    resultants: List[float] = field(default_factory=lambda: [])

    # Mode 2: Automatic generation from SIN file
    sin: bool = False

    # Mode 3: Print options
    pri_olc: bool = False
    pri_alc: bool = False

    input: str = field(init=False, default="LORES")

    def __post_init__(self):
        # Validation for mutually exclusive modes
        manual_mode = self.lc is not None and self.part is not None
        sin_mode = self.sin
        pri_olc_mode = self.pri_olc
        pri_alc_mode = self.pri_alc

        modes = [manual_mode, sin_mode, pri_olc_mode, pri_alc_mode]
        if sum(modes) != 1:
            raise ValueError("Exactly one mode must be used: (lc, part), sin, pri_olc, or pri_alc.")

        parts:list[str] = ["LORES"]
        if manual_mode:
            if not 1 <= len(self.resultants) <= 6:
                raise ValueError("Number of load resultants must be between 1 and 6.")
            parts.append(str(self.lc))
            if self.part is not None:  # Type check to ensure part is not None
                parts.append(self.part)
            parts.extend(f"{r:.4E}" for r in self.resultants)
        elif sin_mode:
            parts.append("SIN=")
        elif pri_olc_mode:
            parts.append("PRI=OLC")
        elif pri_alc_mode:
            parts.append("PRI=ALC")

        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input