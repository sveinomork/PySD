# PySD Statement Migration Guide: Adding Validation System

## Overview

This guide provides step-by-step instructions for migrating PySD statements to use the new validation system. Based on analysis of the current codebase, statements fall into different migration categories requiring different approaches.

## Current Statement Status

### ✅ Fully Migrated (Validation System Integrated)

- **GRECO**: Complete with container, validation rules, and global severity control

### 🔄 Partially Migrated (Pydantic, Needs Validation Integration)

- **BASCO**: Pydantic model with basic validation, needs validation system integration
- **LOADC**: Pydantic model with basic validation, needs validation system integration

### 📝 Simple Migration (Dataclass to Pydantic)

- **HEADL**: Simple dataclass, easy conversion

### 🔧 Full Migration Required (Traditional Classes)

All other statements in `src/pysd/statements/` directory

## Migration Pathways

### Path A: Integrate Validation System (BASCO, LOADC)

For statements that are already Pydantic models but need validation system integration.

### Path B: Simple Conversion (HEADL)

For dataclass statements that need conversion to Pydantic with validation.

### Path C: Full Migration (All Others)

For traditional Python classes that need complete conversion.

---

## Path A: Integrate Validation System (For BASCO/LOADC)

### Step A1: Update Existing Pydantic Model

**Current State**: BASCO already has Pydantic fields and basic validators that raise errors directly.

**Goal**: Replace direct error raising with ValidationContext-based validation.

#### A1.1: Identify Current Validation

```python
# Current BASCO validation (PROBLEMATIC - raises directly)
@field_validator('id')
@classmethod
def validate_id_range(cls, v: int) -> int:
    if not 1 <= v <= 99999999:
        raise ValueError("ID must be between 1 and 99999999")  # ❌ Direct raise
    return v
```

#### A1.2: Convert to Validation System

```python
# Updated BASCO validation (CORRECT - uses ValidationContext)
@field_validator('id')
@classmethod
def validate_id_range(cls, v: int) -> int:
    # Don't raise here - let model_validator handle it with global config
    return v

@model_validator(mode='after')
def validate_with_global_system(self) -> 'BASCO':
    """Perform validation with global severity control."""
    context = ValidationContext(current_object=self)
    
    # ID range validation
    if not (1 <= self.id <= 99999999):
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code=ErrorCodes.BASCO_ID_INVALID,
            message=ErrorMessageBuilder.build_message(
                'INVALID_RANGE',
                field='ID',
                min_val=1,
                max_val=99999999
            ),
            location=f'BASCO.{self.id}',
            suggestion='Use an ID between 1 and 99999999'
        )
        context.add_issue(issue)  # Auto-raises if configured
    
    # Other validations...
    
    # Keep existing input string building
    self._build_existing_input_string()
    
    return self
```

### Step A2: Add Error Codes

Add BASCO-specific error codes to `src/pysd/validation/error_codes.py`:

```python
# BASCO validation errors
BASCO_ID_INVALID = "BASCO-ID-001"
BASCO_LOADCASES_INVALID = "BASCO-LOADCASES-001"
BASCO_TEXT_TOO_LONG = "BASCO-TEXT-001"
```

### Step A3: Test Integration

```python
# Test the integrated validation
from pysd.validation import set_validation_mode, ValidationMode

set_validation_mode(ValidationMode.NORMAL)
basco = BASCO(id=999999999)  # Should raise PySDValidationError

set_validation_mode(ValidationMode.DISABLED) 
basco = BASCO(id=999999999)  # Should allow invalid data
```

---

## Path B: Simple Conversion (HEADL Example)

### Step B1: Convert Dataclass to Pydantic

**Before** (dataclass):

```python
@dataclass
class HEADL:
    heading: str
    
    def __post_init__(self) -> None:
        if not self.heading:
            raise ValueError("Heading text cannot be empty")
        if len(self.heading) > 64:
            raise ValueError("Heading text must be maximum 64 characters")
    
    @property
    def input(self) -> str:
        return f"HEADL {self.heading}"
```

**After** (Pydantic with validation system):

```python
from pydantic import BaseModel, Field, model_validator
from ..validation.core import ValidationIssue, ValidationContext, ValidationSeverity
from ..validation.error_codes import ErrorCodes
from ..validation.messages import ErrorMessageBuilder

class HEADL(BaseModel):
    """HEADL statement for defining table headings."""
    
    heading: str = Field(..., description="Header text (max 64 characters)")
    input: str = Field(default="", init=False, description="Generated input string")
    
    @model_validator(mode='after')
    def validate_and_build_input(self) -> 'HEADL':
        """Validate with global system and build input string."""
        context = ValidationContext(current_object=self)
        
        # Empty heading validation
        if not self.heading:
            issue = ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code=ErrorCodes.HEADL_EMPTY,
                message="Heading text cannot be empty",
                location=f'HEADL.heading'
            )
            context.add_issue(issue)
        
        # Length validation
        if len(self.heading) > 64:
            issue = ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code=ErrorCodes.HEADL_TOO_LONG,
                message=ErrorMessageBuilder.build_message(
                    'TEXT_TOO_LONG',
                    field='heading',
                    max_length=64,
                    current_length=len(self.heading)
                ),
                location=f'HEADL.heading'
            )
            context.add_issue(issue)
        
        # Build input string
        self.input = f"HEADL {self.heading}"
        
        return self
```

### Step B2: Add Error Codes

```python
# In error_codes.py
HEADL_EMPTY = "HEADL-TEXT-001"
HEADL_TOO_LONG = "HEADL-TEXT-002"
```

---

## Path C: Full Migration (Traditional Classes)

For statements that are not yet Pydantic models.

### Step C1: Analyze Existing Structure

1. Examine the current implementation
2. Identify all fields and their types
3. Document validation requirements
4. Note any special business logic

### Step C2: Create Pydantic Model Structure

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from ..validation.core import ValidationIssue, ValidationContext, ValidationSeverity
from ..validation.error_codes import ErrorCodes

class STATEMENT_NAME(BaseModel):
    """Statement description."""
    
    # Define all fields with proper types
    field1: int = Field(..., description="Field description")
    field2: Optional[str] = Field(None, description="Optional field")
    
    # Auto-generated input string
    input: str = Field(default="", init=False, description="Generated input string")
    
    @field_validator('field1')
    @classmethod
    def validate_field1(cls, v: int) -> int:
        """Basic field validation - don't raise errors here."""
        # Perform any necessary data transformation
        return v
    
    @model_validator(mode='after')
    def validate_business_rules(self) -> 'STATEMENT_NAME':
        """Validate business rules with global severity control."""
        context = ValidationContext(current_object=self)
        
        # Add validation issues
        if self.field1 < 1:
            issue = ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code=ErrorCodes.STATEMENT_FIELD1_INVALID,
                message="Field1 must be positive",
                location=f'STATEMENT_NAME.field1'
            )
            context.add_issue(issue)
        
        # Build input string
        self._build_input_string()
        
        return self
    
    def _build_input_string(self) -> None:
        """Build the formatted input string."""
        self.input = f"STATEMENT_NAME FIELD1={self.field1}"
```

---

## Migration Priority & Strategy

### Recommended Migration Order

#### Phase 1: Quick Wins (Integrate Existing Pydantic)

1. **BASCO** - Already Pydantic, integrate validation system
2. **LOADC** - Already Pydantic, integrate validation system

#### Phase 2: Simple Conversions

3. **HEADL** - Simple dataclass conversion
4. **Other simple statements** (single file, minimal logic)

#### Phase 3: Complex Migrations

5. **Statements with cross-references** (need validation rules)
6. **Statements with complex business logic**
7. **Statements requiring containers**

### Quick Integration Script

Create a helper script to identify migration candidates:

```python
# migration_analyzer.py
import os
import re

def analyze_statement_files():
    """Analyze all statement files to categorize migration needs."""
    statements_dir = "src/pysd/statements"
    
    for file in os.listdir(statements_dir):
        if file.endswith('.py') and file != '__init__.py':
            filepath = os.path.join(statements_dir, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for Pydantic usage
            has_basemodel = 'BaseModel' in content
            has_dataclass = '@dataclass' in content
            has_field_validator = 'field_validator' in content
            has_validation_system = 'ValidationContext' in content
            
            print(f"\n{file}:")
            print(f"  - Pydantic BaseModel: {has_basemodel}")
            print(f"  - Dataclass: {has_dataclass}")
            print(f"  - Field Validators: {has_field_validator}")
            print(f"  - Validation System: {has_validation_system}")
            
            if has_validation_system:
                print("  ✅ FULLY MIGRATED")
            elif has_basemodel and has_field_validator:
                print("  🔄 NEEDS VALIDATION INTEGRATION")
            elif has_dataclass:
                print("  📝 SIMPLE CONVERSION NEEDED")
            else:
                print("  🔧 FULL MIGRATION REQUIRED")

if __name__ == "__main__":
    analyze_statement_files()
```

---

## Testing Strategy

### Test Templates

#### For Integrated Validation (Path A)

```python
def test_statement_validation_modes():
    """Test statement with different validation modes."""
    from pysd.validation import set_validation_mode, ValidationMode, PySDValidationError
    
    # Normal mode - should catch errors
    set_validation_mode(ValidationMode.NORMAL)
    with pytest.raises(PySDValidationError):
        STATEMENT(invalid_data=True)
    
    # Disabled mode - should allow invalid data
    set_validation_mode(ValidationMode.DISABLED)
    statement = STATEMENT(invalid_data=True)  # Should not raise
    assert statement.invalid_data is True
```

#### For New Conversions (Path B/C)

```python
def test_statement_conversion():
    """Test converted statement maintains functionality."""
    # Test valid creation
    statement = STATEMENT(valid_field=123)
    assert statement.valid_field == 123
    assert statement.input.startswith("STATEMENT")
    
    # Test validation
    with pytest.raises(PySDValidationError):
        STATEMENT(valid_field=-1)  # Invalid value
```

---

## Validation System Integration Checklist

For each statement migration, verify:

### ✅ Code Changes

- [ ] Replaced direct error raising with ValidationContext
- [ ] Added proper error codes to `error_codes.py`
- [ ] Updated field validators to not raise exceptions
- [ ] Added model validator with ValidationContext
- [ ] Maintained existing input string generation logic

### ✅ Integration

- [ ] Added to SD_BASE routing (if new)
- [ ] Updated container logic (if applicable)
- [ ] Added cross-reference validation rules (if needed)

### ✅ Testing

- [ ] Unit tests for validation modes
- [ ] Integration tests with SD_BASE
- [ ] Cross-reference validation tests
- [ ] Backward compatibility tests

### ✅ Documentation

- [ ] Updated docstring with validation information
- [ ] Added examples showing validation behavior
- [ ] Documented error codes and their meanings

---

## Common Pitfalls to Avoid

### ❌ DON'T: Raise Errors Directly in Validators

```python
@field_validator('id')
def validate_id(cls, v):
    if v < 1:
        raise ValueError("ID must be positive")  # ❌ WRONG
    return v
```

### ✅ DO: Use ValidationContext in Model Validator

```python
@model_validator(mode='after')
def validate_business_rules(self):
    context = ValidationContext(current_object=self)
    if self.id < 1:
        context.add_issue(ValidationIssue(...))  # ✅ CORRECT
    return self
```

### ❌ DON'T: Forget to Import Validation Components

```python
# Missing imports will cause runtime errors
from ..validation.core import ValidationContext  # ✅ Required
```

### ✅ DO: Follow Import Pattern

```python
from ..validation.core import ValidationIssue, ValidationContext, ValidationSeverity
from ..validation.error_codes import ErrorCodes
from ..validation.messages import ErrorMessageBuilder
```

---

## Next Steps

1. **Start with Path A**: Integrate validation system into BASCO and LOADC
2. **Quick wins with Path B**: Convert simple dataclasses like HEADL
3. **Plan Path C migrations**: Prioritize by usage frequency and complexity
4. **Test thoroughly**: Ensure backward compatibility throughout
5. **Document as you go**: Update this guide with lessons learned

This migration approach ensures gradual adoption of the validation system while maintaining stability and backward compatibility.