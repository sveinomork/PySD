from typing import Optional, List, Literal, Self
from pydantic import BaseModel, Field, model_validator
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext

# Forward declarations for extended ELC functionality
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .loadc import LoadcList
    from .greco import GRECO

class LoadCase(BaseModel):
    """
    Represents a load case in BASCO statement load type, load number and load factor
    """
    lc_type: Literal['ILC', 'OLC', 'ELC', 'BAS', 'PLC', 'BLC']
    lc_numb: int
    lc_fact: float = 1.0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoadCase):
            return NotImplemented
        return (self.lc_type, self.lc_numb) == (other.lc_type, other.lc_numb)
    
    def is_in_loadcase(self, id: int,type:str) -> bool:
        return self.lc_type == type and self.lc_numb == id
    
class LoadCaseList(BaseModel):
    """
    Container for multiple LOADC statements.
    # TODO: Implement if lc_type is 'ELC' or 'OLC' that it is in loadc_container Loadc.olc. 
    # TODO: Implement if lc_type is 'ELC' greco_container must have at least one GRECO with bas containing lc_numb
    # TODO: Implement if lc_type is 'BAS' basco_container must contain the bas with lc_numb
    """
    loadcases: list[LoadCase] = Field(default_factory=list)

    def add_loadc(self, loadcase: LoadCase) -> None:
        """Add a LOADC statement to the list."""
        self.loadcases.append(loadcase)

    def __iter__(self):
        """Make the object iterable so list(obj) works"""
        return iter(self.loadcases)

    def to_list(self) -> list[LoadCase]:
        """Get the list of LOADC statements."""
        return self.loadcases


    


class BASCO(BaseModel):    
    """
    ### Usage
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
    id: int
    load_cases: List[LoadCase]
    typ: Optional[Literal['R', 'I', 'F']] = None
    ldf: Optional[int] = None
    txt: Optional[str] = None
    input: str = Field(default="BASCO", init=False)
    
    @property
    def identifier(self) -> int:
        """Get the unique identifier for this BASCO statement."""
        return self.id

    @model_validator(mode='after')
    def build_input_string(self) -> 'BASCO':
        """Build BASCO input string and run instance-level validation."""
        
        # Execute instance-level validation rules
        context = ValidationContext(current_object=self)
        issues = execute_validation_rules(self, context, level='instance')
        
        # Handle issues according to global config
        for issue in issues:
            context.add_issue(issue)  # Auto-raises if configured
        
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
    
    def execute_cross_container_validation(self, sd_model) -> list:
        """
        Execute cross-container validation rules for this BASCO instance.
        
        This method is called when the BASCO is added to the SD_BASE model,
        allowing validation against other containers.
        """
        context = ValidationContext(
            current_object=self,
            full_model=sd_model  # This enables access to all containers
        )
        
        # Execute model-level (cross-container) validation rules
        return execute_validation_rules(self, context, level='model')
    

    



def convert_to_only_olcs(basco_input: list[BASCO], target_id: int,
                        alc_olc_mapping: Optional['LoadcList'] = None,
                        grecos: Optional[list['GRECO']] = None,
                        load_resultant_str: Optional[str] = None) -> BASCO:
    """
    Convert a BASCO that contains BAS and ELC references to one that only contains OLCs.
    
    Args:
        basco_input: List of all BASCO statements to search through
        target_id: ID of the BASCO to convert
        alc_olc_mapping: LoadcList for ELC to OLC mapping (required for ELC conversion)
        grecos: List of GRECO statements (required for ELC conversion)
        load_resultant_str: Load resultant data string (required for ELC conversion)
    
    Returns:
        New BASCO with only OLC load cases, with factors calculated by:
        - Direct OLC cases: keep as-is
        - BAS references: expand and multiply factors
        - ELC references: calculate equilibrium factors and expand to OLCs
    
    Logic:
        For each BAS reference with factor F:
        1. Find the referenced BASCO by ID
        2. For each OLC in that BASCO with factor G:
           - Add/combine to result with factor F * G
        
        For each ELC reference with factor F:
        1. Calculate equilibrium factors for balancing OLCs 
        2. Add OLC cases with factors = F * equilibrium_factor
        
    Example:
        BASCO 201: ELC=201 LF=10, ELC=202 LF=10
        Result: OLC cases with calculated equilibrium factors
    """
    # Create lookup dictionary for quick BASCO access
    basco_lookup = {basco.id: basco for basco in basco_input}
    
    # Find the target BASCO
    if target_id not in basco_lookup:
        raise ValueError(f"BASCO with ID {target_id} not found")
    
    target_basco = basco_lookup[target_id]
    
    # Dictionary to accumulate OLC factors {olc_number: total_factor}
    olc_factors: dict[int, float] = {}
    
    # Process each load case in the target BASCO
    for load_case in target_basco.load_cases:
        if load_case.lc_type == 'OLC':
            # Direct OLC case - add to result
            olc_num = load_case.lc_numb
            olc_factors[olc_num] = olc_factors.get(olc_num, 0) + load_case.lc_fact
            
        elif load_case.lc_type == 'BAS':
            # BAS reference - expand to OLCs
            bas_id = load_case.lc_numb
            bas_factor = load_case.lc_fact
            
            if bas_id not in basco_lookup:
                raise ValueError(f"Referenced BAS {bas_id} not found")
            
            # Recursively expand if the referenced BASCO also has BAS references
            expanded_basco = convert_to_only_olcs(basco_input, bas_id, alc_olc_mapping, grecos, load_resultant_str)
            
            # Add each OLC from the expanded BASCO with multiplied factor
            for olc_case in expanded_basco.load_cases:
                if olc_case.lc_type == 'OLC':
                    olc_num = olc_case.lc_numb
                    combined_factor = bas_factor * olc_case.lc_fact
                    olc_factors[olc_num] = olc_factors.get(olc_num, 0) + combined_factor
                    
        elif load_case.lc_type == 'ELC':
            # ELC reference - calculate equilibrium factors and expand to OLCs
            elc_id = load_case.lc_numb
            elc_factor = load_case.lc_fact
            
            # Check if required parameters are provided for ELC conversion
            if not all([alc_olc_mapping, grecos, load_resultant_str]):
                raise ValueError("ELC conversion requires alc_olc_mapping, grecos, and load_resultant_str parameters")
            
            # Import here to avoid circular imports
            from equlibrium.load_factor_calculator import get_elc_factors
            
            # Get balancing OLCs from GRECO statements (assuming first GRECO contains the balancing OLCs)
            if not grecos:
                raise ValueError("No GRECO statements provided for ELC conversion")
            
            # Get the balancing OLC numbers from the first GRECO statement
            balancing_olcs = list(grecos[0].bas) if grecos[0].bas else []
            
            if not balancing_olcs:
                raise ValueError("No balancing OLCs found in GRECO statements")
            
            # Calculate equilibrium factors for this ELC
            # Type guard to ensure non-None values
            assert load_resultant_str is not None, "load_resultant_str cannot be None for ELC conversion"
            assert alc_olc_mapping is not None, "alc_olc_mapping cannot be None for ELC conversion"
            elc_factors = get_elc_factors(load_resultant_str, balancing_olcs, elc_id, alc_olc_mapping)
            
            # Add OLC cases with calculated factors (negative for equilibrium)
            for i, balancing_olc in enumerate(balancing_olcs):
                if i < len(elc_factors):  # Safety check
                    combined_factor = elc_factor * (-elc_factors[i])  # Negative for equilibrium
                    olc_factors[balancing_olc] = olc_factors.get(balancing_olc, 0) + combined_factor
            
            # Also add the original ELC as OLC (direct mapping)
            olc_factors[elc_id] = olc_factors.get(elc_id, 0) + elc_factor
    
    # Create new load cases from accumulated factors
    new_load_cases = [
        LoadCase(lc_type='OLC', lc_numb=olc_num, lc_fact=factor)
        for olc_num, factor in sorted(olc_factors.items())
    ]
    
    # Create new BASCO with only OLC cases
    return BASCO(
        id=target_id,
        load_cases=new_load_cases,
        typ=target_basco.typ,
        ldf=target_basco.ldf,
        txt=target_basco.txt
    )
    

if __name__ == "__main__":
    # Test data from the example
    basco1 = BASCO(
        id=101,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=1, lc_fact=1),
            LoadCase(lc_type='OLC', lc_numb=2, lc_fact=2),
        ]
    )
    basco2 = BASCO(
        id=102,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=1, lc_fact=2),
            LoadCase(lc_type='OLC', lc_numb=2, lc_fact=3),
            LoadCase(lc_type='OLC', lc_numb=3, lc_fact=4),
        ]
    )
    basco3 = BASCO(
        id=103,
        load_cases=[
            LoadCase(lc_type='BAS', lc_numb=101, lc_fact=1),
            LoadCase(lc_type='BAS', lc_numb=102, lc_fact=2),
            LoadCase(lc_type='OLC', lc_numb=3, lc_fact=1),
        ]
    )
    basco_input: list[BASCO] = [basco1, basco2, basco3]

    # Convert BASCO 103 to only OLCs
    result = convert_to_only_olcs(basco_input, 103)
    
    print("Original BASCO 103:")
    print(basco3)
    print("\nConverted to OLCs only:")
    print(result)
    
    print("\nLoad cases breakdown:")
    for lc in result.load_cases:
        print(f"  {lc.lc_type}={lc.lc_numb} LF={lc.lc_fact}")
    
    # Verify the calculation manually
    print("\nManual verification:")
    print("OLC 1: 1*1 (from BAS 101) + 2*2 (from BAS 102) = 1 + 4 = 5")
    print("OLC 2: 1*2 (from BAS 101) + 2*3 (from BAS 102) = 2 + 6 = 8") 
    print("OLC 3: 2*4 (from BAS 102) + 1*1 (direct) = 8 + 1 = 9")
    
    # Expected result (manually calculated)
    expected_basco = BASCO(
        id=104,
        load_cases=[
            # 1*1+2*2=5 (corrected from original comment)
            LoadCase(lc_type='OLC', lc_numb=1, lc_fact=5),
            # 1*2+2*3=8 (corrected from original comment)
            LoadCase(lc_type='OLC', lc_numb=2, lc_fact=8),
            # 2*4+1*1=9
            LoadCase(lc_type='OLC', lc_numb=3, lc_fact=9),
        ]
    )
    
    print("\nExpected result (corrected calculation):")
    print(expected_basco)
  