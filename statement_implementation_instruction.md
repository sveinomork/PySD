# Statement Implementation Instructions

This guide shows how to implement a new statement class following the established patterns in the PySD codebase.

## Basic Structure

```python
from __future__ import annotations
from typing import Optional, Union, Literal, Tuple
from pydantic import Field
from .statement_base import StatementBase

class MYSTATEMENT(StatementBase):
    """
    Brief description of what this statement does.

    ### Examples
    ```python
    # Basic usage
    MYSTATEMENT(id="TEST", param=123)
    # -> 'MYSTATEMENT ID=TEST PARAM=123'
    
    # With optional parameters
    MYSTATEMENT(id="TEST", param=123, flag=True)
    # -> 'MYSTATEMENT ID=TEST PARAM=123 FLAG='
    ```
    """
    
    # Required fields
    id: str = Field(..., description="Required identifier")
    param: int = Field(..., description="Required parameter")
    
    # Optional fields
    optional_param: Optional[float] = Field(None, description="Optional parameter")
    flag: bool = Field(False, description="Boolean flag")
    range_param: Optional[Union[int, Tuple[int, int]]] = Field(None, description="Single value or range")

    @property
    def identifier(self) -> str:
        """Get unique identifier for this statement."""
        return self.id

    def _build_input_string(self) -> None:
        """Build the input string (pure formatting logic)."""
        parts = ["MYSTATEMENT", f"ID={self.id}", f"PARAM={self.param}"]
        
        # Optional parameters (only add if not None/default)
        if self.optional_param is not None:
            parts.append(f"OPTIONAL={self.optional_param}")
        
        # Flags (only add if True)
        if self.flag:
            parts.append("FLAG=")
        
        # Handle ranges
        if self.range_param is not None:
            if isinstance(self.range_param, tuple):
                parts.append(f"RANGE={self.range_param[0]}-{self.range_param[1]}")
            else:
                parts.append(f"RANGE={self.range_param}")
        
        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input
```

## Key Implementation Points

### 1. Inheritance and Imports
- Always inherit from `StatementBase`


### 2. Field Types

- **Identifiers**: Use `str` for IDs and names
- **Numbers**: Use `int`, `float`, or `Optional[int]`, `Optional[float]`
- **Ranges**: Use `Union[int, Tuple[int, int]]` for single values or ranges
- **Flags**: Use `bool` with `Field(False, ...)` 
- **Load cases**: Use `Union[str, CaseRange, list[CaseRange], Cases]` (only when needed)

### 3. Required Methods
- **`identifier`**: Return unique identifier for the statement
- **`_build_input_string`**: Build the output string format
- **`__str__`**: Return `self.input`



### 5. String Building Patterns
- Start with statement name: `parts = ["MYSTATEMENT"]`
- Add required parameters unconditionally
- Add optional parameters only if not None/default
- Add flags only if True
- Use `str(self.field)` for Cases objects
- Join with spaces: `self.input = " ".join(parts)`

### 6. Documentation
- Include comprehensive docstring with examples
- Show input → output format mappings
- Document all parameters with Field descriptions
- Include validation rules and notes



### 8. Testing Pattern

Create `tests/test_mystatement.py` with basic tests (see Testing Requirements section below for complete example):

```python
def test_basic_creation():
    stmt = MYSTATEMENT(id="TEST", param=123)
    assert "MYSTATEMENT ID=TEST PARAM=123" in str(stmt)

def test_in_model_context():
    with SD_BASE.create_writer("test.inp") as model:
        model.add(MYSTATEMENT(id="TEST", param=123))
```

## Rule-Based Validation

**IMPORTANT**: All validation logic must be implemented in a separate rules file, NOT in the statement class itself. The statement class should only contain data modeling and formatting logic.

### Validation Rules File Structure

Create a single validation rules file: `src/pysd/validation/rules/mystatement_rules.py`

```python
"""
Validation rules for MYSTATEMENT statements.

Implements three levels of validation:
1. Instance-level: Individual MYSTATEMENT statement validation
2. Container-level: MYSTATEMENT container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (references, etc.)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.mystatement import MYSTATEMENT
    from ...containers.mystatement_container import MystatementContainer
    from ..core import ValidationContext


@instance_rule('MYSTATEMENT')
def validate_mystatement_instance(statement: 'MYSTATEMENT', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate individual MYSTATEMENT statement."""
    issues = []
    
    # Basic field validation
    if statement.param < 0:
        issues.append(ValidationIssue(
            severity="error",
            code="MYSTATEMENT_INVALID_PARAM",
            message=f"MYSTATEMENT {statement.id} parameter must be positive",
            location=f"MYSTATEMENT.{statement.id}",
            suggestion="Use a positive parameter value"
        ))
    
    return issues


@container_rule('MYSTATEMENT')
def validate_mystatement_container(container: 'MystatementContainer', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate MYSTATEMENT container for uniqueness."""
    issues = []
    
    # Check for duplicate IDs
    ids = [stmt.id for stmt in container.items]
    seen_ids = set()
    for stmt_id in ids:
        if stmt_id in seen_ids:
            issues.append(ValidationIssue(
                severity="error",
                code="MYSTATEMENT_DUPLICATE_ID",
                message=f"Duplicate MYSTATEMENT ID {stmt_id}",
                location=f"MYSTATEMENT.{stmt_id}",
                suggestion="Use unique IDs"
            ))
        seen_ids.add(stmt_id)
    
    return issues


@model_rule('MYSTATEMENT')
def validate_mystatement_model(statement: 'MYSTATEMENT', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate MYSTATEMENT statement against the complete model."""
    issues = []
    
    if context.full_model is None:
        return issues
    
    # Add model-level validation as needed
    # Example: Check references to other containers
    
    return issues
```

### Key Points for Validation Rules

1. **Separation of Concerns**: Statement classes handle data modeling, rules files handle validation
2. **Three Validation Levels**: Instance → Container → Model
3. **Use Decorators**: `@instance_rule`, `@container_rule`, `@model_rule`
4. **ValidationIssue Structure**: severity, code, message, location, suggestion

## Testing Requirements

Create a test file `tests/test_mystatement.py`:

```python
from src.pysd.statements.mystatement import MYSTATEMENT
from src.pysd.sdmodel import SD_BASE

def test_basic_creation():
    """Test basic statement creation."""
    stmt = MYSTATEMENT(id="TEST", param=123)
    assert stmt.id == "TEST"
    assert stmt.param == 123
    assert "MYSTATEMENT ID=TEST PARAM=123" in str(stmt)

def test_identifier():
    """Test identifier property."""
    stmt = MYSTATEMENT(id="UNIQUE", param=123)
    assert stmt.identifier == "UNIQUE"

def test_in_model_context():
    """Test statement in SD_BASE model context."""
    with SD_BASE.create_writer("test_output.inp") as model:
        stmt = MYSTATEMENT(id="MODEL_TEST", param=456)
        model.add(stmt)
        # Should not raise validation errors for basic case

# Run with: python -m pytest tests/test_mystatement.py -v
```

## Minimal Implementation Strategy

When starting a new statement, follow this implementation order:

### 1. Statement Class (Data Model Only)

- Create the statement class inheriting from `StatementBase`
- Define fields with Pydantic Field descriptions
- Implement `identifier` property and `_build_input_string` method
- **NO validation logic in the statement class**

### 2. Validation Rules File

- Create `src/pysd/validation/rules/mystatement_rules.py`
- Start with minimal validation:
  - **Instance Rules**: Basic field validation (required fields, ranges)
  - **Container Rules**: Only essential uniqueness checks
  - **Model Rules**: Only critical cross-references (if any)

### 3. Basic Tests

- Create `tests/test_mystatement.py` for statement functionality
- Create `tests/test_mystatement_validation.py` for validation rules
- Focus on:
  - Basic creation and string output
  - Identifier property
  - Model integration
  - Validation rule coverage

### 4. Iterative Enhancement

- Add more sophisticated validation rules as requirements become clearer
- Expand test coverage based on real usage patterns
- **Keep statement class focused on data modeling only**

### Key Principle: Separation of Concerns

- **Statement Class**: Pure data modeling and string formatting
- **Validation Rules**: All business logic and validation
- **Tests**: Separate coverage for data modeling vs validation
