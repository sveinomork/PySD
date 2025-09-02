from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RETYP:
    """

   ### Purpose:
    --------
    Defines rebar layer types to be referenced in the RELOC statement.

   ### Examples:
    ---------------
    ```python
    # Method 1 (direct area input):
    RETYP(id=20101, mp=1, ar=2094e-6, c2=0.060, th=0.025, di=0.020, nr=1, bc=0.75)
      → 'RETYP ID=20101 MP=1 AR=0.002094 NR=1 DI=0.02 C2=0.06 TH=0.025 BC=0.75'

    # Method 2 (calculated area from number & diameter):
    RETYP(id=20101, mp=1, nr=1, di=0.020, cc=0.200)                                 
    → 'RETYP ID=20101 MP=1 NR=1 DI=0.02 CC=0.2'

    # Method 3 (fixed offset mode):
    RETYP(id=20101, mp=1, ar=2094e-6, os=0.050)                                     
    → 'RETYP ID=20101 MP=1 AR=0.002094 OS=0.05'

    # Method 4 (crack width calculation mode):
    RETYP(id=20101, di=0.020, nr=1, bc=0.75)                                       
    → 'RETYP ID=20101 NR=1 DI=0.02 BC=0.75'
    ```

    ### Parameters:
    -----------
    id : int
        Type number (max 8 digits)

    mp : Optional[int]
        Rebar material property set ID (MP=)
        Required for most geometric definitions.

    lb : Optional[str]
        Label for XTRACT plot file (max 16 chars)

    ar : Optional[float]
        Cross-sectional area per unit length [m²/m] (Method 1)

    nr : Optional[int]
        Number of rebars in bundle (default 1, Method 2)

    di : Optional[float]
        Diameter of rebar [m or mm]
        > 1.0 → mm, < 1.0 → m

    cc : Optional[float]
        Center distance between bars/bundles [mm]

    c2 : Optional[float]
        Nominal cover to first layer [m]

    th : Optional[float]
        Thickness of rebar layer [m]

    os : Optional[float]
        Offset to layer center [m]

    bc : Optional[float]
        Bond coefficient (default 0.75)

    comment : Optional[str]
        Comment to append at end of line.
    """

    id: int
    mp: Optional[int] = None
    lb: Optional[str] = None
    ar: Optional[float] = None
    nr: Optional[int] = None
    di: Optional[float] = None
    cc: Optional[float] = None
    c2: Optional[float] = None
    th: Optional[float] = None
    os: Optional[float] = None
    bc: Optional[float] = None
    comment: Optional[str] = None

    input: str = field(init=False, default="RETYP")

    def __post_init__(self):
        # Basic validation
        if self.ar is None and (self.nr is None or self.di is None):
            raise ValueError("Must provide either AR (Method 1) or NR+DI (Method 2).")

        if self.lb and len(self.lb) > 16:
            raise ValueError("LB label must be ≤ 16 characters.")

        if not (0 < self.id < 10**8):
            raise ValueError("ID must be a positive integer with max 8 digits.")

        # Build input string
        parts = ["RETYP"]
        parts.append(f"ID={self.id}")

        if self.mp is not None:
            parts.append(f"MP={self.mp}")
        if self.lb:
            parts.append(f"LB={self.lb}")
        if self.ar is not None:
            parts.append(f"AR={self.ar:.6g}")
        if self.nr is not None:
            parts.append(f"NR={self.nr}")
        if self.di is not None:
            parts.append(f"DI={self.di:.6g}")
        if self.cc is not None:
            parts.append(f"CC={self.cc:.6g}")
        if self.c2 is not None:
            parts.append(f"C2={self.c2:.6g}")
        if self.th is not None:
            parts.append(f"TH={self.th:.6g}")
        if self.os is not None:
            parts.append(f"OS={self.os:.6g}")
        if self.bc is not None:
            parts.append(f"BC={self.bc:.6g}")

        if self.comment:
            parts.append(f"% {self.comment}")

        self.input = " ".join(parts)


    def __str__(self) -> str:
        return self.input