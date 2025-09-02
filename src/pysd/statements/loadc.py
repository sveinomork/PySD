from typing import Optional, Union, Any, Tuple
from typing_extensions import Annotated, Doc
from pydantic import BaseModel, Field, field_validator, model_validator
from .cases import Cases, normalize_cases

class LOADC(BaseModel):
    """
### Usage
Controls load case processing, output formatting, and analysis execution parameters.

### Examples
```python
# Simplified syntax - automatically sets RN from ALC
LOADC(alc=1, olc=101)
# -> 'LOADC RN=1 LC=1,101'

LOADC(alc=2, olc=102)
# -> 'LOADC RN=2 LC=2,102'

# Tuple syntax for ranges - automatically sets RN from first ALC value
LOADC(alc=(1,6), olc=(101,106))
# -> 'LOADC RN=1 LC=1-6 OLC=101-106'

LOADC(alc=(5,10), olc=(201,206))
# -> 'LOADC RN=5 LC=5-10 OLC=201-206'

# Traditional syntax using Cases
LOADC(run_number=1, alc=Cases(ranges=[1, (2, 6)]), olc=Cases(ranges=[(101, 106)]))
# -> 'LOADC RN=1 LC=1,2-6 OLC=101-106'

# Using string format
LOADC(run_number=1, alc="1,2-6", olc="101-106")
# -> 'LOADC RN=1 LC=1,2-6 OLC=101-106'

# Using list format  
LOADC(run_number=1, alc=[1, (2, 6)], olc=[(101, 106)])
# -> 'LOADC RN=1 LC=1,2-6 OLC=101-106'

# Enable table output for load results
LOADC(table=True)
# -> 'LOADC TAB='

# Enable print output for debugging
LOADC(pri=True)
# -> 'LOADC PRI='
```

### Parameters

- **run_number**: Optional[int]
    - Result file run number to reference (RN=n). If not provided and alc is a single integer or tuple, alc value will be used.
- **alc**: Optional[Union[str, int, tuple, list, Cases]]
    - Analysis Load Cases. Supports multiple formats including tuples for ranges. Must be used with olc. If single integer or tuple and run_number not set, will auto-set run_number.
- **olc**: Optional[Union[str, int, tuple, list, Cases]]
    - Output Load Cases. Supports multiple formats including tuples for ranges. Must be used with alc.
- **table**: bool
    - If True, indicates table-based input mode. Default is False.
- **pri**: bool
    - If True, indicates priority-based mode. Default is False.
- **comment**: Optional[str]
    - Optional comment to add at end of line (for RN and LC modes).

### Notes

- LOADC statements control which load cases are processed and how results are output.
- RUN parameter specifies the analysis run number for organization.
- ALC (Analysis Load Cases) defines the range of input load cases to process.
- OLC (Output Load Cases) defines the range for result output numbering.
- TABLE enables tabular output of load case results.
- PRI enables detailed print output for debugging and verification.
- Multiple LOADC statements can be used to control different aspects.
- Load case ranges are inclusive (e.g., ALC=1,6 processes cases 1 through 6).
- Simplified syntax: LOADC(alc=1, olc=101) automatically generates LOADC RN=1 LC=1,101
- Tuple syntax: LOADC(alc=(1,6), olc=(101,106)) automatically generates LOADC RN=1 LC=1-6 OLC=101-106
"""

    run_number: Annotated[
        Optional[int],
        Doc("Result file run number to reference (RN=n). Required when using alc or olc.")
    ] = None
    alc: Annotated[
        Optional[Union[str, int, tuple[int, int], list[int], Cases]],
        Doc("Analysis Load Cases. Supports multiple formats including tuples for ranges. Must be used with olc.")
    ] = None
    olc: Annotated[
        Optional[Union[str, int, tuple[int, int], list[int], Cases]],
        Doc("Output Load Cases. Supports multiple formats including tuples for ranges. Must be used with alc.")
    ] = None
    table: Annotated[
        bool,
        Doc("If True, indicates table-based input mode. Default is False.")
    ] = False
    pri: Annotated[
        bool,
        Doc("If True, indicates priority-based mode. Default is False.")
    ] = False
    comment: Annotated[
        Optional[str],
        Doc("Optional comment to add at end of line (for RN and LC modes).")
    ] = None
    input: str = Field(default="LOADC", init=False)
    key: str = Field(default="", init=False)

    @field_validator('alc', 'olc', mode='before')
    @classmethod
    def normalize_case_inputs(cls, v: Any) -> Any:
        """Convert any supported format to Cases."""
        if v is None:
            return v
        
        # Handle tuple input like (1,6) -> convert to range (1,6)
        if isinstance(v, tuple) and len(v) == 2:
            start, end = v
            if isinstance(start, int) and isinstance(end, int):
                # Convert to range tuple for Cases - end should be inclusive in the tuple format
                return normalize_cases([(start, end)])
        
        # Only pass non-tuple values to normalize_cases
        if not isinstance(v, tuple):
            return normalize_cases(v)
        
        # If we get here, it's an unsupported tuple format
        raise ValueError(f"Unsupported tuple format: {v}. Expected (start, end) with integers.")

    @field_validator('alc', 'olc')
    @classmethod
    def validate_simple_ranges_only(cls, v: Optional[Cases]) -> Optional[Cases]:
        """LOADC only supports simple ranges, no steps or GRECO letters."""
        if v is None:
            return v
            
        for range_item in v.ranges:
            if isinstance(range_item, tuple) and len(range_item) > 2:
                raise ValueError("LOADC does not support stepped ranges")
                
        if v.greco:
            raise ValueError("LOADC does not support GRECO letters")
            
        return v

    @model_validator(mode='after')
    def validate_loadc_requirements(self) -> 'LOADC':
        """Validate LOADC requirements and build input string."""
        
        # Auto-set run_number from alc if not provided and alc is a single integer or range
        if self.run_number is None and self.alc is not None:
            # Check if alc is a single integer or can be converted to one
            if isinstance(self.alc, Cases) and len(self.alc.ranges) == 1:
                first_range = self.alc.ranges[0]
                if isinstance(first_range, int):
                    self.run_number = first_range
                elif isinstance(first_range, tuple) and len(first_range) == 2:
                    # Use the start of the range as run_number
                    self.run_number = first_range[0]
                    
        # Generate the key
        key_parts: list[str] = []
        if self.run_number is not None:
            key_parts.append(f"RN{self.run_number}")
            if self.alc is not None and isinstance(self.alc, Cases):
                # Get first and last values for key
                first_range = self.alc.ranges[0]
                last_range = self.alc.ranges[-1]
                
                if isinstance(first_range, int):
                    start = first_range
                else:
                    start = first_range[0]
                    
                if isinstance(last_range, int):
                    end = last_range
                else:
                    end = last_range[1]
                    
                key_parts.append(f"ALC{start}-{end}")
                
        self.key = "_".join(key_parts) if key_parts else str(id(self))

        # Validation
        mode_count = sum([
            bool(self.alc),
            bool(self.olc),
            self.table,
            self.pri
        ])

        if mode_count == 0:
            raise ValueError("LOADC must have one mode active: alc/olc, table, or pri")
        
        if (self.alc and not self.olc) or (self.olc and not self.alc):
            raise ValueError("Both alc and olc must be provided together")
            
        if (self.alc or self.olc) and self.run_number is None:
            raise ValueError("run_number is required when using alc or olc")

        # Build input string
        parts: list[str] = ["LOADC"]

        # Handle load cases with run number
        if self.alc and self.olc:
            # Add run number
            parts.append(f"RN={self.run_number}")
            
            # Check if both are single ranges (from tuples)
            alc_is_single_range = (isinstance(self.alc, Cases) and len(self.alc.ranges) == 1 
                                 and isinstance(self.alc.ranges[0], tuple))
            olc_is_single_range = (isinstance(self.olc, Cases) and len(self.olc.ranges) == 1 
                                 and isinstance(self.olc.ranges[0], tuple))
            
            if alc_is_single_range and olc_is_single_range:
                # Use LC=alc OLC=olc format for tuple inputs
                lc_part = f"LC={str(self.alc)} OLC={str(self.olc)}"
            else:
                # Use traditional LC=alc,olc format
                lc_part = f"LC={str(self.alc)},{str(self.olc)}"
                
            if self.comment:
                lc_part += f" % {self.comment}"
            parts.append(lc_part)
            
        # Handle table mode
        elif self.table:
            parts.append("TAB=")
            
        # Handle priority mode
        elif self.pri:
            parts.append("PRI=")

        # Join all parts with spaces
        self.input = " ".join(parts)
        return self

    def __str__(self) -> str:
        return self.input
    
    def is_olc(self, olc: int) -> bool:
        """
        Check if the given OLC number is contained in this LOADC's OLC ranges.
        
        Examples:
            LOADC(alc=1, olc=(1,6)).is_olc(2) -> True (2 is in range 1-6)
            LOADC(alc=1, olc=(1,6)).is_olc(7) -> False (7 is not in range 1-6)
            LOADC(alc=1, olc=5).is_olc(5) -> True (exact match)
            LOADC(alc=1, olc=[1,3,5]).is_olc(3) -> True (3 is in list)
        """
        if self.olc is None:
            return False
        
        # After field validation, self.olc should be a Cases object
        if isinstance(self.olc, Cases):
            return olc in list(self.olc)
        
        return False

    def is_alc(self, alc: int) -> bool:
        """
        Check if the given ALC number is contained in this LOADC's ALC ranges.
        
        Examples:
            LOADC(alc=(1,6), olc=101).is_alc(3) -> True (3 is in range 1-6)
            LOADC(alc=(1,6), olc=101).is_alc(8) -> False (8 is not in range 1-6)
            LOADC(alc=5, olc=101).is_alc(5) -> True (exact match)
        """
        if self.alc is None:
            return False
        
        # After field validation, self.alc should be a Cases object
        if isinstance(self.alc, Cases):
            return alc in list(self.alc)
        
        return False
    
    def get_olc_list(self) -> list[int]:
        """
        Get all OLC numbers as a list.
        
        Returns:
            List of all individual OLC numbers from ranges
            
        Examples:
            LOADC(alc=1, olc=(101,106)).get_olc_list() -> [101, 102, 103, 104, 105, 106]
            LOADC(alc=1, olc=101).get_olc_list() -> [101]
        """
        if self.olc is None:
            return []
        
        # After field validation, self.olc should be a Cases object
        if isinstance(self.olc, Cases):
            return list(self.olc)
        
        return []

    def get_alc_list(self) -> list[int]:
        """
        Get all ALC numbers as a list.
        
        Returns:
            List of all individual ALC numbers from ranges
            
        Examples:
            LOADC(alc=(1,6), olc=101).get_alc_list() -> [1, 2, 3, 4, 5, 6]
            LOADC(alc=5, olc=101).get_alc_list() -> [5]
        """
        if self.alc is None:
            return []
        
        # After field validation, self.alc should be a Cases object
        if isinstance(self.alc, Cases):
            return list(self.alc)
        
        return []

    def get_corresponding_alc(self, olc: int) -> int | None:
        """
        Get the corresponding ALC number for a given OLC number based on their index positions.
        
        The ALC and OLC lists are paired by index - the first ALC corresponds to the first OLC, etc.
        
        Args:
            olc: The OLC number to find the corresponding ALC for
            
        Returns:
            The corresponding ALC number, or None if OLC not found or no correspondence
            
        Examples:
            LOADC(alc=(1,6), olc=(101,106)).get_corresponding_alc(103) -> 3
            LOADC(alc=5, olc=105).get_corresponding_alc(105) -> 5
            LOADC(alc=(1,3), olc=(101,103)).get_corresponding_alc(999) -> None
        """
        if self.olc is None or self.alc is None:
            return None
            
        olc_list = self.get_olc_list()
        alc_list = self.get_alc_list()
        
        # Check if the lists have the same length
        if len(olc_list) != len(alc_list):
            return None
            
        try:
            # Find the index of the OLC
            index = olc_list.index(olc)
            # Return the corresponding ALC at the same index
            return alc_list[index]
        except ValueError:
            # OLC not found in the list
            return None

    def get_corresponding_olc(self, alc: int) -> int | None:
        """
        Get the corresponding OLC number for a given ALC number based on their index positions.
        
        The ALC and OLC lists are paired by index - the first ALC corresponds to the first OLC, etc.
        
        Args:
            alc: The ALC number to find the corresponding OLC for
            
        Returns:
            The corresponding OLC number, or None if ALC not found or no correspondence
            
        Examples:
            LOADC(alc=(1,6), olc=(101,106)).get_corresponding_olc(3) -> 103
            LOADC(alc=5, olc=105).get_corresponding_olc(5) -> 105
            LOADC(alc=(1,3), olc=(101,103)).get_corresponding_olc(999) -> None
        """
        if self.alc is None or self.olc is None:
            return None
            
        alc_list = self.get_alc_list()
        olc_list = self.get_olc_list()
        
        # Check if the lists have the same length
        if len(alc_list) != len(olc_list):
            return None
            
        try:
            # Find the index of the ALC
            index = alc_list.index(alc)
            # Return the corresponding OLC at the same index
            return olc_list[index]
        except ValueError:
            # ALC not found in the list
            return None

    def get_alc_olc_pairs(self) -> list[tuple[int, int]]:
        """
        Get all ALC-OLC pairs as a list of tuples.
        
        Returns:
            List of (alc, olc) tuples showing the correspondence
            
        Examples:
            LOADC(alc=(1,3), olc=(101,103)).get_alc_olc_pairs() -> [(1,101), (2,102), (3,103)]
            LOADC(alc=5, olc=105).get_alc_olc_pairs() -> [(5,105)]
        """
        alc_list = self.get_alc_list()
        olc_list = self.get_olc_list()
        
        # Only return pairs if both lists have the same length
        if len(alc_list) == len(olc_list):
            return list(zip(alc_list, olc_list))
        else:
            return []
        
    
class LoadcList(BaseModel):
    """
    Container for multiple LOADC statements.
    """
    loadc: list[LOADC] = Field(default_factory=list)

    @staticmethod
    def _validate_olc_uniqueness(loadc_list: list[LOADC]):
        """Checks for OLC uniqueness within a given list of LOADC items."""
        all_olcs:set[int] = set()
        for loadc_item in loadc_list:
            for olc in loadc_item.get_olc_list():
                if olc in all_olcs:
                    raise ValueError(f"Duplicate OLC value found: {olc}")
                all_olcs.add(olc)

    @model_validator(mode='after')
    def validate_unique_olc(self) -> 'LoadcList':
        """Ensures that no two LOADC items have overlapping OLC values."""
        self._validate_olc_uniqueness(self.loadc)
        return self

    def add_loadc(self, loadc: LOADC) -> None:
        """Add a LOADC statement to the list."""
        self._validate_olc_uniqueness(self.loadc + [loadc])
        self.loadc.append(loadc)

    def __iter__(self):
        """Make the object iterable so list(obj) works"""
        return iter(self.loadc)
    
    def to_list(self) -> list[LOADC]:
        """Get the list of LOADC statements."""
        return self.loadc
    
  

    def get_corresponding_alc(self, olc: int) -> int | None:
        for lc in self:
            if lc.is_olc(olc):
                return lc.get_corresponding_alc(olc)
        return None
    
    