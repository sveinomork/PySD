from __future__ import annotations
from typing import List, Union, Tuple, overload, Iterator, Optional, Any
from pydantic import BaseModel, Field, field_validator

# Type aliases
CaseRange = Union[int, Tuple[int, int], Tuple[int, int, int]]


class Cases(BaseModel):
    """
    Universal case sequence handler for DECAS statements.
    Supports single values, ranges, stepped ranges, and optional GRECO letters.

    ### Examples:
        Cases(ranges=[1, (2, 5)]) -> "1,2-5"
        Cases(ranges=[1, (2, 5, 2)], greco="A") -> "1,2-5-2:A"
        Cases(value=(1, 5)) -> "1-5"  # Direct tuple input
        Cases(value="1,3-5") -> "1,3-5"  # Direct string input
        Cases(value=101) -> "101"  # Direct int input
    """

    ranges: List[CaseRange] = Field(..., min_length=1)
    greco: str = Field(default="", description="Optional GRECO letter identifier")

    def __init__(
        self,
        value: int | float = None,
        ranges: List[CaseRange] = None,
        greco: str = "",
        **kwargs,
    ):
        if value is not None and ranges is None:
            # Convert value to ranges using normalize_cases logic
            normalized = normalize_cases(value)
            ranges = normalized.ranges
            if not greco and normalized.greco:
                greco = normalized.greco

        super().__init__(ranges=ranges, greco=greco, **kwargs)

    @field_validator("ranges", mode="before")
    @classmethod
    def normalize_ranges_input(cls, v: Any) -> List[CaseRange]:
        """Handle various input formats and normalize to ranges list."""
        if isinstance(v, list):
            return v  # Already a list of ranges
        else:
            # Use normalize_cases to handle other formats
            normalized = normalize_cases(v)
            return normalized.ranges

    @field_validator("ranges")
    @classmethod
    def validate_range_format(cls, v: List[CaseRange]) -> List[CaseRange]:
        """Validate individual range formats."""
        for item in v:
            if isinstance(item, int):
                if item < 0:
                    raise ValueError("Case numbers must be non-negative")
            else:  # item is a tuple
                if len(item) not in [2, 3]:
                    raise ValueError("Range tuples must have 2 or 3 elements")
                if len(item) >= 2 and item[1] <= item[0]:
                    raise ValueError("End value must be greater than start value")
                if len(item) == 3 and (item[2] <= 0 or item[2] > (item[1] - item[0])):
                    raise ValueError("Step must be positive and <= range size")
        return v

    @field_validator("greco")
    @classmethod
    def validate_greco(cls, v: str) -> str:
        """Validate GRECO format."""
        if v and (not v.isupper() or not v.isalpha()):
            raise ValueError("GRECO must be uppercase letters only")
        return v

    @staticmethod
    def _expand_range(range_item: CaseRange) -> Iterator[int]:
        """Expand a single range item into individual numbers.
        
        Extracted to eliminate duplication between __iter__ and to_list.
        
        Args:
            range_item: Single value, 2-tuple (start, end), or 3-tuple (start, end, step)
            
        Yields:
            Individual case numbers from the range
        """
        if isinstance(range_item, int):
            yield range_item
        elif len(range_item) == 2:
            start, end = range_item
            yield from range(start, end + 1)
        elif len(range_item) == 3:
            start, end, step = range_item
            yield from range(start, end + 1, step)

    def formatted(self) -> str:
        """Get formatted string representation."""
        parts: list[str] = []
        for range_item in self.ranges:
            if isinstance(range_item, int):
                parts.append(str(range_item))
            elif len(range_item) == 2:
                parts.append(f"{range_item[0]}-{range_item[1]}")
            elif len(range_item) == 3:
                parts.append(f"{range_item[0]}-{range_item[1]}-{range_item[2]}")

        result = ",".join(parts)
        return f"{result}:{self.greco}" if self.greco else result

    def __str__(self) -> str:
        return self.formatted()

    def __iter__(self) -> Iterator[int]:
        """
        Iterate over all individual case numbers in the ranges.

        Examples:
            Cases(ranges=[1, (3, 6)]) -> yields 1, 3, 4, 5, 6
            Cases(ranges=[(10, 20, 2)]) -> yields 10, 12, 14, 16, 18, 20
        """
        for range_item in self.ranges:
            yield from self._expand_range(range_item)

    def to_list(self) -> List[int]:
        """
        Convert all ranges to a list of individual case numbers.

        Returns:
            List[int]: All case numbers expanded from ranges

        Examples:
            Cases(ranges=[1, (3, 6)]).to_list() -> [1, 3, 4, 5, 6]
            Cases(ranges=[(10, 15, 2)]).to_list() -> [10, 12, 14]
        """
        return list(self)

    @classmethod
    def parse(cls, text: str) -> Cases:
        """
        Parse a case definition string.

        Examples:
            Cases.parse("1,2-5,10-20-2") -> Cases with ranges and steps
            Cases.parse("1-5:A") -> Cases with GRECO letter
        """
        greco = ""
        if ":" in text:
            text, greco = text.split(":", 1)

        ranges: List[CaseRange] = []
        for part in text.split(","):
            if "-" in part:
                nums = [int(x) for x in part.split("-")]
                if len(nums) == 2:
                    ranges.append((nums[0], nums[1]))
                elif len(nums) == 3:
                    ranges.append((nums[0], nums[1], nums[2]))
                else:
                    raise ValueError(f"Invalid range format: {part}")
            else:
                ranges.append(int(part))

        return cls(ranges=ranges, greco=greco)


class CaseBuilder:
    """Fluent builder for Cases with automatic building and caching."""

    def __init__(self):
        self._ranges: List[CaseRange] = []
        self._greco: str = ""
        self._cached_cases: Optional[Cases] = None

    @classmethod
    def create(cls) -> "CaseBuilder":
        """Factory method to create a new CaseBuilder instance."""
        return cls()

    @overload
    def add(self, value: int) -> "CaseBuilder":
        """Add single case number."""
        ...

    @overload
    def add(self, start: int, end: int) -> "CaseBuilder":
        """Add range of cases."""
        ...

    @overload
    def add(self, start: int, end: int, step: int) -> "CaseBuilder":
        """Add range with step."""
        ...

    def add(
        self, value: int, end: Optional[int] = None, step: Optional[int] = None
    ) -> "CaseBuilder":
        """
        Add a case number or range.

        Args:
            value: Case number, or start of range if end is provided
            end: End of range (inclusive) - optional
            step: Step value for range - optional

        Examples:
            builder.add(101) -> single case 101
            builder.add(101, 105) -> range 101-105
            builder.add(101, 110, 2) -> stepped range 101-110-2
        """
        self._cached_cases = None  # Invalidate cache
        if end is None:
            # Single value
            self._ranges.append(value)
        elif step is None:
            # Simple range
            self._ranges.append((value, end))
        else:
            # Stepped range
            self._ranges.append((value, end, step))
        return self

    def add_greco(self, greco: str) -> "CaseBuilder":
        """Add GRECO letter identifier."""
        self._cached_cases = None  # Invalidate cache
        self._greco = greco
        return self

    # Backward compatibility methods
    def add_single(self, value: int) -> "CaseBuilder":
        """Backward compatibility: Add single case number."""
        return self.add(value)

    def add_range(self, start: int, end: int) -> "CaseBuilder":
        """Backward compatibility: Add range of cases."""
        return self.add(start, end)

    def add_stepped_range(self, start: int, end: int, step: int) -> "CaseBuilder":
        """Backward compatibility: Add range with step."""
        return self.add(start, end, step)

    def with_greco(self, greco: str) -> "CaseBuilder":
        """Backward compatibility: Add GRECO suffix."""
        return self.add_greco(greco)

    def build(self) -> Cases:
        """Build the Cases object (cached)."""
        if self._cached_cases is None:
            self._cached_cases = Cases(ranges=self._ranges, greco=self._greco)
        return self._cached_cases

    def _build(self) -> Cases:
        """Backward compatibility: Alias for build()."""
        return self.build()

    def __str__(self) -> str:
        """Auto-build when converted to string."""
        return str(self.build())

    def formatted(self) -> str:
        """Get formatted string (auto-builds)."""
        return self.build().formatted()

    # Support for Cases interface
    @property
    def ranges(self) -> List[CaseRange]:
        """Get ranges (auto-builds)."""
        return self.build().ranges

    @property
    def greco(self) -> str:
        """Get GRECO letter (auto-builds)."""
        return self.build().greco

    def __iter__(self) -> Iterator[int]:
        """Iterate over all individual case numbers (auto-builds)."""
        return iter(self.build())

    def to_list(self) -> List[int]:
        """Convert to list of individual case numbers (auto-builds)."""
        return self.build().to_list()


# Helper function to normalize inputs
def normalize_cases(
    value: Union[str, List[CaseRange], CaseBuilder, Cases, int, tuple],
) -> Cases:
    """
    Convert various input formats to Cases object.

    Supports:
    - String: "0,45-90" or "300-305:A"
    - List: [0, (45, 90)] or [0, (45, 90, 5)]
    - Tuple: (101, 102) - single range tuple
    - Int: 101 - single case number
    - CaseBuilder: CaseBuilder().add(0).add(45, 90)
    - Cases: Already a Cases object
    """
    if isinstance(value, str):
        return Cases.parse(value)
    elif isinstance(value, list):
        return Cases(ranges=value)
    elif isinstance(value, tuple):
        # Handle single tuple as a range: (101, 102) -> [(101, 102)]
        return Cases(ranges=[value])
    elif isinstance(value, int):
        # Handle single integer as a single case: 101 -> [101]
        return Cases(ranges=[value])
    elif isinstance(value, CaseBuilder):
        # Use the build method to get cached Cases object
        return value.build()
    elif isinstance(value, Cases):
        return value
    else:
        # Handle legacy formats for backward compatibility
        if hasattr(value, "cases") and hasattr(value, "version"):
            # Old LoadCaseDefinition format
            greco = getattr(value, "version", "")
            return Cases(ranges=value.cases, greco=greco)
        elif hasattr(value, "_ranges") and hasattr(value, "_suffix"):
            # Old CaseBuilder format - try to convert
            greco = getattr(value, "_suffix", "") or getattr(value, "_greco", "")
            ranges = getattr(value, "_ranges", [])
            return Cases(ranges=ranges, greco=greco)
        else:
            raise ValueError(f"Cannot convert {type(value)} to Cases")
