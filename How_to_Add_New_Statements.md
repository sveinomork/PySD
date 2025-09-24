# How to Add New Statements to PySD

This guide provides step-by-step instructions for implementing new statement types in the PySD system. The architecture has been designed to minimize boilerplate and make adding new statements require changes in only a few places.

## Overview

The PySD system uses a **container-based architecture** where:
- **Statements** define the data structure and input string generation
- **Containers** provide storage, validation, and management
- **ContainerFactory** dynamically creates and registers containers
- **StatementRouter** automatically routes statements to their containers

## Prerequisites

Before implementing a new statement, ensure you have:
1. The statement specification (field definitions, validation rules, input format)
2. Understanding of the expected input string format
3. Any validation rules or cross-references with other statements

## Step-by-Step Implementation

### Step 1: Create the Statement Class

Create a new file in `src/pysd/statements/` (e.g., `mynewstatement.py`):

```python
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field, field_validator
from .statement_base import StatementBase, StringBuilderHelper

# Define any nested models first (if needed)
class MyNestedModel(BaseModel):
    \"\"\"Optional nested model for complex fields.\"\"\"
    field1: str
    field2: int = 1
    
    def __str__(self) -> str:
        return f"{self.field1}={self.field2}"

class MYNEWSTATEMENT(StatementBase):
    \"\"\"
    ### Usage
    Brief description of what this statement does.
    
    ### Examples
    ```python
    # Basic usage example
    MYNEWSTATEMENT(
        id=1,
        required_field="value",
        optional_field=42
    )
    # -> 'MYNEWSTATEMENT ID=1 REQ=value OPT=42'
    
    # Advanced usage with nested models
    MYNEWSTATEMENT(
        id=2,
        nested_data=MyNestedModel(field1="test", field2=5)
    )
    # -> 'MYNEWSTATEMENT ID=2 NESTED=test=5'
    ```
    
    ### Parameters
    
    - **id**: int
        - Unique identifier for the statement (required)
    - **required_field**: str
        - Description of required field
    - **optional_field**: Optional[int]
        - Description of optional field (default: None)
    - **nested_data**: Optional[MyNestedModel]
        - Complex nested data structure
    \"\"\"
    
    # Define fields using Pydantic
    id: int = Field(..., description="Unique identifier")
    required_field: str = Field(..., description="Required string field")
    optional_field: Optional[int] = Field(None, description="Optional integer field")
    nested_data: Optional[MyNestedModel] = Field(None, description="Nested model data")
    
    # Add field validators if needed
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        if v <= 0:
            raise ValueError("ID must be positive")
        return v
    
    @field_validator('required_field')
    @classmethod
    def validate_required_field(cls, v):
        if not v.strip():
            raise ValueError("Required field cannot be empty")
        return v.strip().upper()
    
    @property
    def identifier(self) -> str:
        \"\"\"Return unique identifier for this statement.\"\"\"
        return str(self.id)
    
    def _build_identifier(self, add_hash: bool = False) -> str:
        \"\"\"Build the identifier string for input generation.\"\"\"
        # Use the parent implementation that handles the add_hash logic
        return super()._build_identifier(add_hash)
    
    def _build_input_string(self) -> str:
        \"\"\"Build the complete input string for this statement.\"\"\"
        helper = StringBuilderHelper(self.statement_name)
        
        # Add ID (usually required for most statements)
        helper.add_param("ID", self.id)
        
        # Add required field
        helper.add_param("REQ", self.required_field)
        
        # Add optional fields (skip if None/default values)
        helper.add_param("OPT", self.optional_field, skip_if=None)
        
        # Handle nested models
        if self.nested_data:
            helper.add_param("NESTED", str(self.nested_data))
        
        return helper.input
```

### Step 2: Add Statement to __init__.py

Update `src/pysd/statements/__init__.py` to export your new statement:

```python
from .mynewstatement import MYNEWSTATEMENT

# Add to __all__ list
__all__ = [
    # ... existing statements ...
    'MYNEWSTATEMENT',
]
```

### Step 3: Register in ContainerFactory

Update `src/pysd/model/container_factory.py`:

1. **Add the import** (around line 32):
```python
from ..statements.mynewstatement import MYNEWSTATEMENT
```

2. **Add to the registry** (in the `_statement_registry` dict around line 60):
```python
'mynewstatement': {
    'type': MYNEWSTATEMENT,
    'description': 'MYNEWSTATEMENT statements for [purpose description]'
},
```

3. **Add to the container registry** (in the `_container_registry` dict around line 130):
```python
'mynewstatement': {
    'container_class': BaseContainer[MYNEWSTATEMENT],
    'field_name': 'mynewstatement',  # This will be the attribute name on SD_BASE
    'description': 'Container for MYNEWSTATEMENT statements'
},
```

### Step 4: Add Validation Rules (Optional)

If your statement needs validation rules, create `src/pysd/validation/rules/mynewstatement_rules.py`:

```python
from typing import List, TYPE_CHECKING
from ..core import ValidationRule, ValidationContext, ValidationResult

if TYPE_CHECKING:
    from ...statements.mynewstatement import MYNEWSTATEMENT

class MynewstatementBasicValidation(ValidationRule):
    \"\"\"Basic validation for MYNEWSTATEMENT statements.\"\"\"
    
    def applies_to(self, context: ValidationContext) -> bool:
        return hasattr(context.model, 'mynewstatement') and len(context.model.mynewstatement.items) > 0
    
    def validate(self, context: ValidationContext) -> List[ValidationResult]:
        results = []
        statements: List['MYNEWSTATEMENT'] = context.model.mynewstatement.items
        
        for stmt in statements:
            # Example validation: check some business rule
            if stmt.optional_field and stmt.optional_field < 0:
                results.append(ValidationResult(
                    is_valid=False,
                    error_code="MYNEWSTATEMENT-001",
                    message=f"MYNEWSTATEMENT {stmt.id} has negative optional_field: {stmt.optional_field}",
                    statement_type="MYNEWSTATEMENT",
                    statement_id=stmt.identifier
                ))
        
        return results

# Register the rule
MYNEWSTATEMENT_RULES = [
    MynewstatementBasicValidation(),
]
```

### Step 5: Register Validation Rules

Update `src/pysd/validation/rule_system.py` to include your rules:

```python
# Add import
from .rules.mynewstatement_rules import MYNEWSTATEMENT_RULES

# Add to VALIDATION_RULES list
VALIDATION_RULES = [
    # ... existing rules ...
    *MYNEWSTATEMENT_RULES,
]
```

### Step 6: Add Tests

Create `tests/test_mynewstatement.py`:

```python
import pytest
from src.pysd.statements import MYNEWSTATEMENT
from src.pysd import SD_BASE

def test_mynewstatement_creation():
    \"\"\"Test basic MYNEWSTATEMENT creation.\"\"\"
    stmt = MYNEWSTATEMENT(
        id=1,
        required_field="TEST"
    )
    
    assert stmt.id == 1
    assert stmt.required_field == "TEST"
    assert stmt.optional_field is None
    assert stmt.identifier == "1"

def test_mynewstatement_input_string():
    \"\"\"Test input string generation.\"\"\"
    stmt = MYNEWSTATEMENT(
        id=1,
        required_field="TEST",
        optional_field=42
    )
    
    expected = "MYNEWSTATEMENT ID=1 REQ=TEST OPT=42"
    assert stmt.input == expected

def test_mynewstatement_in_model():
    \"\"\"Test adding MYNEWSTATEMENT to model.\"\"\"
    model = SD_BASE()
    model.validator.disable_validation()  # For testing
    
    stmt = MYNEWSTATEMENT(id=1, required_field="TEST")
    model.add(stmt)
    
    assert len(model.mynewstatement.items) == 1
    assert model.mynewstatement.items[0] == stmt
    
def test_mynewstatement_validation():
    \"\"\"Test validation rules.\"\"\"
    stmt = MYNEWSTATEMENT(
        id=1,
        required_field="TEST",
        optional_field=-5  # Should trigger validation error
    )
    
    model = SD_BASE()
    model.add(stmt)
    
    # This should raise validation errors
    with pytest.raises(ValueError, match="MYNEWSTATEMENT-001"):
        model.validator.validate_cross_references()
```

## Complete Example: NEWLOAD Statement

Here's a complete example implementing a fictional `NEWLOAD` statement:

**File: `src/pysd/statements/newload.py`**

```python
from typing import Optional, Literal
from pydantic import Field, field_validator
from .statement_base import StatementBase, StringBuilderHelper

class NEWLOAD(StatementBase):
    \"\"\"
    ### Usage
    Defines new load conditions with direction and magnitude.
    
    ### Examples
    ```python
    # Basic load
    NEWLOAD(id=1, direction='X', magnitude=100.0)
    # -> 'NEWLOAD ID=1 DIR=X MAG=100.0'
    
    # Load with factor
    NEWLOAD(id=2, direction='Y', magnitude=50.0, factor=1.5)
    # -> 'NEWLOAD ID=2 DIR=Y MAG=50.0 FAC=1.5'
    ```
    \"\"\"
    
    id: int = Field(..., description="Load ID")
    direction: Literal['X', 'Y', 'Z'] = Field(..., description="Load direction")
    magnitude: float = Field(..., description="Load magnitude")
    factor: Optional[float] = Field(None, description="Load factor")
    
    @field_validator('magnitude')
    @classmethod
    def validate_magnitude(cls, v):
        if v <= 0:
            raise ValueError("Magnitude must be positive")
        return v
    
    @property
    def identifier(self) -> str:
        return str(self.id)
    
    def _build_input_string(self) -> str:
        helper = StringBuilderHelper(self.statement_name)
        helper.add_param("ID", self.id)
        helper.add_param("DIR", self.direction)
        helper.add_param("MAG", self.magnitude)
        helper.add_param("FAC", self.factor, skip_if=None)
        return helper.input
```

## Usage After Implementation

Once implemented, your new statement can be used like this:

```python
from src.pysd import SD_BASE
from src.pysd.statements import MYNEWSTATEMENT

# Create model
model = SD_BASE()

# Create statement
stmt = MYNEWSTATEMENT(
    id=1,
    required_field="VALUE",
    optional_field=42
)

# Add to model (automatically routed to correct container)
model.add(stmt)

# Access via container (both naming schemes work)
print(f"Statements: {len(model.mynewstatement.items)}")
print(f"Statements: {len(model.mynewstatement_container.items)}")

# Write model
model.write("output.inp")
```

## Key Points

1. **Single Point of Change**: Only need to update ContainerFactory registry
2. **Automatic Routing**: StatementRouter automatically routes to correct container
3. **Dynamic Containers**: Containers are created on-demand via `__getattr__`
4. **Validation Integration**: Optional validation rules integrate seamlessly
5. **Backward Compatibility**: Both `statement` and `statement_container` naming work
6. **Type Safety**: Full Pydantic validation and type hints

## Common Patterns

### For Simple Statements
- Inherit from `StatementBase`
- Define fields with Pydantic `Field()`
- Implement `identifier` property
- Implement `_build_input_string()` method

### For Complex Statements
- Create nested `BaseModel` classes for complex structures
- Use field validators for business logic validation
- Override `_build_identifier()` if needed for special ID handling

### For Statements with Cross-References
- Create validation rules in `validation/rules/`
- Register rules in `rule_system.py`
- Use `ValidationContext` to access other statements

This architecture ensures that adding new statements is straightforward and follows consistent patterns throughout the codebase.