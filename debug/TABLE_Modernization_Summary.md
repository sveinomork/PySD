# TABLE Statement Modernization Summary

## Overview
Successfully modernized the PySD TABLE statement type to use:
- **Pydantic BaseModel** for type safety and validation
- **Specialized container** following the established pattern
- **Rule-based validation system** with instance, container, and model-level rules
- **SD_BASE integration** for orchestrated validation and batch processing

## Completed Changes

### 1. Statement Class (Pydantic BaseModel)
**File**: `src/pysd/statements/table.py`

#### Key Transformations:
- **Converted from dataclass to Pydantic BaseModel**
- **Added field validators** for parameter validation (nd, tv ranges)
- **Added model validator** for mode validation (exactly one of tab/ur)
- **Implemented input string generation** (`build_input_string()`)
- **Added unique ID generation** based on mode and parameters
- **Cross-container validation support**

#### Field Definitions:
```python
# Main mode: TAB or UR (mutually exclusive)
tab: Optional[TabType] = Field(None, description="The type of data table to print")
ur: Optional[UrType] = Field(None, description="The type of utilization ratio table to print")

# General filters
pa: Optional[str] = Field(None, description="Filter by structural part name")
fs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="Filter by F-section range")
hs: Optional[Union[int, Tuple[int, int]]] = Field(None, description="Filter by H-section range")
ls: Optional[Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']] = Field(None, description="Filter by limit state")
nd: Optional[int] = Field(None, description="Number of digits after decimal point")

# Load case filters
ilc: Optional[Union[Cases, str]] = Field(None, description="Filter by ILC load cases")
olc: Optional[Union[Cases, str]] = Field(None, description="Filter by OLC load cases")
elc: Optional[Union[Cases, str]] = Field(None, description="Filter by ELC load cases")
bas: Optional[Union[Cases, str]] = Field(None, description="Filter by BAS load cases")
pha: Optional[Union[Cases, str]] = Field(None, description="Filter by PHA load cases")

# TAB specific parameters
el: Optional[int] = Field(None, description="Element number filter")
x1: Optional[Tuple[float, float, float]] = Field(None, description="X1 coordinate filter")
enr: Optional[Tuple[int, int]] = Field(None, description="Element number range")

# UR specific parameters
tv: Optional[float] = Field(None, description="Threshold value for UR tables")
fm: bool = Field(False, description="For UR=MAX")
sk: Optional[Literal['E', 'F', 'H', 'A']] = Field(None, description="Peak value summary mode")
rl: Optional[Union[str, Literal['ALL']]] = Field(None, description="Filter by rebar location ID")

# File output
of: Optional[str] = Field(None, description="Redirect output to old file (append)")
nf: Optional[str] = Field(None, description="Redirect output to new file (overwrite)")
```

#### Validation Rules:
- **Mode validation**: Exactly one of `tab` or `ur` must be specified
- **Range validation**: `nd` must be between 0 and 10
- **Threshold validation**: `tv` must be non-negative
- **Tuple validation**: Coordinate tuples must have exactly 3 elements
- **Range validation**: Section ranges must have start ≤ end

### 2. Specialized Container
**File**: `src/pysd/containers/table_container.py`

#### Key Features:
- **Type-specific queries**: `get_by_tab_type()`, `get_by_ur_type()`
- **Filtering methods**: `get_by_part()`, `get_by_limit_state()`
- **Mode separation**: `get_tab_statements()`, `get_ur_statements()`
- **Threshold filtering**: `get_with_threshold(min_threshold)`
- **File output queries**: `get_with_file_output()`, `has_output_redirection()`
- **Analysis methods**: `get_unique_tab_types()`, `get_max_threshold()`
- **Batch processing**: Optimized `add_batch()` method

#### Specialized Methods:
```python
def get_by_tab_type(self, tab_type: 'TabType') -> List['TABLE']
def get_by_ur_type(self, ur_type: 'UrType') -> List['TABLE']
def get_by_part(self, pa: str) -> List['TABLE']
def get_tab_statements(self) -> List['TABLE']
def get_ur_statements(self) -> List['TABLE']
def get_by_limit_state(self, ls: Literal['ULS', 'ALS', 'SLS', 'CRW', 'FLS']) -> List['TABLE']
def get_with_file_output(self) -> List['TABLE']
def get_with_threshold(self, min_threshold: Optional[float] = None) -> List['TABLE']
def get_section_filtered(self) -> List['TABLE']
def get_load_case_filtered(self) -> List['TABLE']
def get_unique_tab_types(self) -> List['TabType']
def get_unique_ur_types(self) -> List['UrType']
def get_unique_parts(self) -> List[str]
def has_output_redirection(self) -> bool
def get_max_threshold(self) -> Optional[float]
```

### 3. Validation Rules
**File**: `src/pysd/validation/rules/table_rules.py`

#### Instance Rules:
- **TABLE_001-002**: Mode validation (exactly one of tab/ur)
- **TABLE_003-010**: Parameter validation (ranges, coordinates, tuples)
- **TABLE_011-012**: Mode-specific parameter usage warnings
- **TABLE_013**: File output conflict validation

#### Container Rules:
- **TABLE_014**: Duplicate configuration detection
- **TABLE_015**: File output mode conflicts

#### Model Rules:
- **TABLE_016**: Cross-reference validation with DESEC parts
- **TABLE_017**: Load case reference validation (placeholder)

### 4. SD_BASE Integration
**File**: `src/pysd/sdmodel.py`

#### Updates Made:
- **Added TABLE import** and StatementType inclusion
- **Added TableContainer field** with proper typing
- **Updated routing logic** in `_route_item()` method
- **Updated batch processing** in `_add_batch()` method
- **Updated validation summary** to include table count

#### Integration Points:
```python
# Field definition
table: TableContainer = Field(default_factory=TableContainer, description="TABLE statements with validation")

# Routing logic
elif isinstance(item, TABLE):
    self.table.add(item)

# Batch processing
elif item_type == TABLE:
    self.table.add_batch(type_items)

# Validation summary
'table': len(self.table),
```

### 5. Registration and Exports
- **Updated** `src/pysd/containers/__init__.py` to export `TableContainer`
- **Updated** `src/pysd/validation/rules/__init__.py` to import `table_rules`

## Key Features Implemented

### Pydantic Validation
- **Field-level validation** with custom validators for nd, tv, coordinate tuples
- **Model-level validation** for mutually exclusive modes (tab/ur)
- **Type safety** with proper type hints and Literal types
- **Automatic error reporting** with detailed validation messages

### Container Pattern
- **Specialized query methods** for TABLE-specific filtering
- **Mode-based organization** (TAB vs UR statements)
- **Performance optimization** with batch processing
- **Rich analysis capabilities** (unique types, thresholds, file outputs)

### Rule-based Validation
- **Layered validation**: Instance → Container → Model
- **Cross-container validation** with DESEC part references
- **File output conflict detection**
- **Duplicate configuration warnings**
- **Mode-specific parameter usage validation**

### SD_BASE Orchestration
- **Automatic routing** to TableContainer
- **Unified validation interface**
- **Batch processing** with type grouping
- **Comprehensive reporting** in validation summary

## Testing Results

All integration tests pass successfully:

```
=== Testing TABLE Integration ===
TABLE validation result: {'errors': [], 'warnings': [], 'info': []}
TABLE count in summary: 4

TABLE1 input string: TABLE TAB=DF PA=DECK1 FS=1-10 LS=ULS
TABLE2 input string: TABLE TAB=PF PA=WALL1 HS=5-15 ND=3
TABLE3 input string: TABLE UR=CS PA=SLAB1 TV=0.8 SK=F
TABLE4 input string: TABLE UR=MAX FM= NF=max_util.out

TAB statements: 2
UR statements: 2
Unique TAB types: ['DF', 'PF']
Unique UR types: ['CS', 'MAX']
Unique parts: ['DECK1', 'SLAB1', 'WALL1']

=== Testing TABLE Validation Errors ===
✅ Mode validation (both tab and ur specified) - PASS
✅ Mode validation (neither tab nor ur specified) - PASS
✅ Parameter validation (nd out of range) - PASS

=== Testing TABLE Batch Operations ===
TABLE count after batch: 4
Total items: 4
Tables with threshold >= 0.85: 2
Section filtered tables: 0

=== Testing Complex TABLE Scenarios ===
Complex TAB: TABLE TAB=EL PA=COMPLEX1 FS=1-50 HS=10-20 X1=0.0,0.0,0.0 X2=10.0,10.0,0.0 ENR=100-200 OF=element_data.out
Complex UR: TABLE UR=CC PA=SLAB_COMPLEX LS=SLS TV=0.3 RL=ALL AL=45.0 FA=ALL
Tables with file output: 1
Has output redirection: True
Max threshold: 0.3
```

## Usage Examples

### Basic TAB Mode
```python
from src.pysd.statements.table import TABLE

# Print design forces for a structural part
table_df = TABLE(
    tab="DF",      # Design forces
    pa="DECK1",    # Part name
    fs=(1, 10),    # F-section range
    ls="ULS",      # Ultimate limit state
    nd=3           # 3 decimal places
)
```

### Basic UR Mode
```python
# Print concrete stress utilization ratios above threshold
table_cs = TABLE(
    ur="CS",       # Concrete stress
    pa="WALL1",    # Part name
    tv=0.8,        # Show only values >= 0.8
    sk="F",        # Peak values by F-section
    nf="stress.out" # Output to new file
)
```

### Complex Filtering
```python
# Complex table with multiple filters
table_complex = TABLE(
    tab="PF",                    # Principal forces
    pa="BRIDGE_DECK",           # Part name
    fs=(10, 50),                # F-section range
    hs=(1, 20),                 # H-section range
    ls="SLS",                   # Serviceability limit state
    x1=(0.0, 0.0, 0.0),        # Start coordinate
    x2=(100.0, 20.0, 0.0),     # End coordinate
    enr=(1000, 2000),          # Element number range
    of="bridge_forces.out"      # Append to existing file
)
```

### Load Case Filtering
```python
# TABLE with load case filtering
table_lc = TABLE(
    ur="MAX",      # Maximum utilization
    ilc="1-5",     # ILC range
    bas="101,102", # BAS combinations
    fm=True,       # Force mode
    tv=0.9         # Threshold
)
```

### SD_BASE Integration
```python
from src.pysd.sdmodel import SD_BASE

# Create model and add TABLE statements
model = SD_BASE()
model.add([table_df, table_cs, table_complex])

# Validate and get summary
validation_result = model.validate_integrity()
summary = model.get_validation_summary()
print(f"TABLE count: {summary['containers']['table']}")

# Use container methods
tab_statements = model.table.get_tab_statements()
ur_statements = model.table.get_ur_statements()
parts_with_output = model.table.get_with_file_output()
max_threshold = model.table.get_max_threshold()
```

## Architecture Benefits

1. **Type Safety**: Pydantic ensures data integrity with comprehensive field validation
2. **Validation**: Multi-layered validation catches configuration errors early
3. **Flexibility**: Support for all TABLE modes (TAB/UR) with proper parameter validation
4. **Query Capabilities**: Rich container methods for filtering and analysis
5. **Performance**: Batch processing and optimized validation
6. **Maintainability**: Clear separation of concerns following established patterns
7. **Extensibility**: Easy to add new validation rules or container methods
8. **Developer Experience**: Rich error messages and auto-completion support

The TABLE modernization successfully follows the established GRECO/RETYP/RELOC/LORES/XTFIL/DESEC pattern, ensuring consistency across the codebase and making future maintenance straightforward. The comprehensive validation system prevents common configuration errors while the specialized container provides powerful query and analysis capabilities.