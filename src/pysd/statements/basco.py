from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from .statement_base import StatementBase

class LoadCase(BaseModel):
    """
    Represents a load case in BASCO statement load type, load number and load factor
    ### Examples
    ```python
    # Basic combination of two load cases
    LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.11)
    # -> 'LF=1.11 ELC=1'
    ```

    ### Parameters
    - **lc_type**: Literal['ILC', 'OLC', 'ELC', 'BAS', 'PLC', 'BLC']
        - Type of load case:
            - ILC: Input Load Case
            - OLC: Original Load Case
            - ELC: Equilibrium Load Case
            - BAS: Basic Load Combination
            - PLC: Prestressing Tendon Load Case
    - **lc_numb**: int
        - Load case number (1-99999999).
    - **lc_fact**: float 
        - Load factor (default is 1.0).

    """
    lc_type: Literal['ILC', 'OLC', 'ELC', 'BAS', 'PLC', 'BLC']
    lc_numb: int
    lc_fact: float = 1.0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoadCase):
            return NotImplemented
        return (self.lc_type, self.lc_numb) == (other.lc_type, other.lc_numb)
    
    def __str__(self) -> str:
        return f"LF={self.lc_fact} {self.lc_type}={self.lc_numb}"

    def is_in_loadcase(self, id: int,type:str) -> bool:
        return self.lc_type == type and self.lc_numb == id
    


    


class BASCO( StatementBase):
    """
    
    Defines load combinations from existing load cases (ILC, OLC, ELC, BAS, PLC, BLC) with specified factors for the ShellDesign system.
    
    ### Examples
    ```python
    # Basic combination of two load cases
    BASCO(
        id=101,
        load_cases=[
            LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.11),
            LoadCase(lc_type='OLC', lc_numb=2, lc_fact=1.5)
        ]
    )
    # -> 'BASCO ID=101 LF=1.11 ELC=1 LF=1.5 OLC=2'

    # With type and location dependent factor
    BASCO(
        id=102,
        load_cases=[LoadCase(lc_type='BAS', lc_numb=200, lc_fact=1.35)],
        typ='R',
        ldf=5
    )
    # -> 'BASCO ID=102 LDF=5 TYP=R LF=1.35 BAS=200'

    # With identification text
    BASCO(
        id=103,
        load_cases=[LoadCase(lc_type='ILC', lc_numb=10, lc_fact=0.5)],
        txt="ULS Combination"
    )
    # -> 'BASCO ID=103 LF=0.5 ILC=10 TXT=ULS Combination'
    ```

    ### Parameters
    - **id**: int
        - Identification number (1-99999999).
    - **load_cases**: List[LoadCase]
        - List of load cases with their source types and factors. Each load case can be ILC, OLC, ELC, BAS, PLC, or BLC with an optional factor.
    - **typ**: Optional[Literal['R', 'I', 'F']]
        - Load type marker:
            - None: Ordinary load (default)
            - 'R': Real part of complex wave
            - 'I': Imaginary part of complex wave
            - 'F': Use factors from FSFAC statement
    - **ldf**: Optional[int]
        - Reference to Location Dependent Factor defined with LDFAC statement.
    - **txt**: Optional[str]
        - Identification text (max 80 chars).

    ### Notes
    - At least one load case must be provided (max 30).
    - The input string is automatically split into multiple lines if it exceeds 100 characters.
    - Each load case is always paired with its factor (LF=...).
    - The `txt` field is appended to the last line if it fits, otherwise placed on a new line.
    - The `typ` and `ldf` fields are optional modifiers.
    """
    id: int = Field(..., description="Identification number (1-99999999)")
    load_cases: List[LoadCase] = Field(..., description="List of load cases with their source types and factors. Each load case can be ILC, OLC, ELC, BAS, PLC, or BLC with an optional factor")
    typ: Optional[Literal['R', 'I', 'F']] = Field(None, description="Load type marker: None=Ordinary load, 'R'=Real part of complex wave, 'I'=Imaginary part of complex wave, 'F'=Use factors from FSFAC statement")
    ldf: Optional[int] = Field(None, description="Reference to Location Dependent Factor defined with LDFAC statement")
    txt: Optional[str] = Field(None, description="Identification text (max 80 chars)")
   
    @property
    def identifier(self) -> str:
        return str(self.id)


    def _build_input_string(self) -> 'BASCO':
        """Build BASCO input string and run instance-level validation."""
        
        
        # Build the BASCO input string
        final_lines: list[str] = []
        
        # Base line with ID and optional parameters
        base_line: str = f"BASCO ID={self.id}"
        if self.ldf is not None:
            base_line += f" LDF={self.ldf}"
        if self.typ:
            base_line += f" TYP={self.typ}"

        # Process load cases
        current_line = base_line
        line_cases: list[str] = []
        line_case_count = 0
        line_lf_count = 0

        for lc in self.load_cases:
            # Always include LF=... for each load case
            case_text = f"LF={lc.lc_fact} {lc.lc_type}={lc.lc_numb}"
            new_lf_count = line_lf_count + 1

            # Test if adding this case would make line too long or break LF/case pairing
            test_line = current_line
            if line_cases:
                test_line += " " + " ".join(line_cases)
            test_line += " " + case_text

            if (len(test_line) > 100 and line_cases) or \
               (new_lf_count != line_case_count + 1 and new_lf_count != 0):
                # Start a new line
                final_lines.append(current_line + " " + " ".join(line_cases))
                current_line = base_line
                line_cases = [case_text]
                line_case_count = 1
                line_lf_count = 1 if lc.lc_fact != 1.0 else 0
            else:
                line_cases.append(case_text)
                line_case_count += 1
                line_lf_count = new_lf_count

        # Add the final line, including text if present
        if line_cases:
            line = current_line + " " + " ".join(line_cases)
            if self.txt:
                if len(line + f" TXT={self.txt}") <= 100:
                    line += f" TXT={self.txt}"
                else:
                    final_lines.append(line)
                    line = f"{base_line} TXT={self.txt}"
            final_lines.append(line)

        self.input = "\n".join(final_lines)
        return self

    def contains(self, bas_number: int,type:str) -> bool:
        """Check if the load case is in the specified BAS number."""
        return any(lc.is_in_loadcase(bas_number,type=type) for lc in self.load_cases)

    def __str__(self) -> str:
        return self.input
    
   