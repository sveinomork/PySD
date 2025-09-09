# Step-by-Step Guide: Implementing Validation System for Other Statements

## Overview

This guide provides a systematic approach to migrating existing PySD statements to use the new **Pydantic + Validation System** that was implemented for GRECO. You'll learn how to convert traditional Python classes to Pydantic models with custom validation, containers, and global severity control.

## 🎯 What You'll Accomplish

By following this guide, you'll be able to:

1. Convert any existing statement to a Pydantic model
2. Implement business rule validation with severity control
3. Create specialized containers for statement collections
4. Add cross-reference validation between statements
5. Integrate with the global validation system

## 📋 Prerequisites

Before starting, ensure you have:

- Understanding of the existing codebase structure
- Basic knowledge of Pydantic v2
- Familiarity with the GRECO implementation (reference example)
- Access to the validation framework components

## 🔄 Migration Process Overview

The migration follows this general pattern:

1. **Analyze** the existing statement structure
2. **Convert** to Pydantic model with validation
3. **Create** specialized container (if needed)
4. **Update** SD_BASE to use the new statement
5. **Add** cross-reference validation rules
6. **Test** the implementation

---

## Step 1: Analyze Current Statement Categories

Based on the current codebase, there are three main categories of statements:

### Category A: Already Migrated to Pydantic
- **GRECO** ✅ (fully migrated with validation system)
- **BASCO** ✅ (Pydantic model, but needs validation system integration)
- **LOADC** ✅ (Pydantic model, but needs validation system integration)

### Category B: Simple Data Classes (Easy Migration)
- **HEADL** (simple dataclass with basic validation)

### Category C: Traditional Classes (Requires Full Migration)
- All remaining statements in `src/pysd/statements/` directory

### Current Statement Inventory

Let me analyze what statements exist:
- [ ] Fields and their types
- [ ] Validation rules (if any)
- [ ] Input/output string formatting
- [ ] Business logic requirements
- [ ] Cross-references to other statements

Example for BASCO:
```python
# Current BASCO structure (example)
class BASCO:
    def __init__(self, id, cases=None, ...):
        self.id = id           # Integer ID
        self.cases = cases     # LoadCaseDefinition or similar
        # ... other fields
    
    def formatted(self):
        # String formatting logic
        pass
```

### 1.3 Identify Business Rules

Document the business rules for validation:
- **Field requirements**: Which fields are mandatory/optional
- **Format constraints**: ID ranges, string patterns, etc.
- **Count limitations**: Maximum/minimum items
- **Cross-references**: References to other statement types
- **Business logic**: Domain-specific validation rules

---

## Step 2: Convert to Pydantic Model

### 2.1 Create Basic Pydantic Structure

Create a new Pydantic model following the GRECO pattern:

```python
# src/pysd/statements/basco.py
from __future__ import annotations
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from .cases import Cases, normalize_cases
from ..validation.core import ValidationIssue, ValidationContext, ValidationSeverity
from ..validation.error_codes import ErrorCodes
from ..validation.messages import ErrorMessageBuilder

class BASCO(BaseModel):
    """
    BASCO statement for [describe purpose].
    
    [Add detailed docstring with examples, parameters, validation rules, etc.]
    """
    
    # Define fields with proper types and descriptions
    id: int = Field(..., description="BASCO ID (1-99999999)")
    cases: Optional[Cases] = Field(None, description="Load cases definition")
    # Add other fields as needed
    
    # Auto-generated field for compatibility
    input: str = Field(default="", init=False, description="Generated input string")
```

### 2.2 Add Field Validators

Implement field-level validation following the GRECO pattern:

```python
    @field_validator('id')
    @classmethod
    def validate_id_range(cls, v: int) -> int:
        """Validate ID is within acceptable range."""
        if not (1 <= v <= 99999999):
            # Don't raise directly - let model_validator handle it with global config
            pass
        return v
    
    @field_validator('cases', mode='before')
    @classmethod
    def normalize_cases_input(cls, v) -> Optional[Cases]:
        """Convert various input formats to Cases."""
        if v is None:
            return v
        return normalize_cases(v)
```

### 2.3 Add Model Validator with Global Validation System

This is the key part - implement the model validator that uses the global validation system:

```python
    @model_validator(mode='after')
    def build_input_string(self) -> 'BASCO':
        """Build input string and perform validation with severity-aware error handling."""
        
        # Create validation context
        context = ValidationContext(current_object=self)
        
        # Validate ID range with global validation control
        if not (1 <= self.id <= 99999999):
            issue = ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code=ErrorCodes.BASCO_ID_INVALID,  # Add to error_codes.py
                message=ErrorMessageBuilder.build_message(
                    'INVALID_RANGE',
                    field='ID',
                    min_val=1,
                    max_val=99999999
                ),
                location=f'BASCO.{self.id}',
                suggestion='Use an ID between 1 and 99999999'
            )
            context.add_issue(issue)  # This will auto-raise if configured to do so
        
        # Add other business rule validations here
        # Each validation should create a ValidationIssue and add to context
        
        # Build input string (existing logic)
        self._build_input_string()
        
        return self
    
    def _build_input_string(self) -> None:
        """Build the formatted input string."""
        parts = []
        if self.id or self.cases:
            normal = ["BASCO"]
            if self.id:
                normal.append(f"ID={self.id}")
            if self.cases:
                normal.append(f"CASES={self.cases.formatted()}")
            parts.append(" ".join(normal))
        
        self.input = "\n".join(parts)
```

---

## Step 3: Update Error Codes

### 3.1 Add Statement-Specific Error Codes

Add error codes for the new statement in `src/pysd/validation/error_codes.py`:

```python
class ErrorCodes:
    # ... existing codes ...
    
    # BASCO validation errors
    BASCO_ID_INVALID = "BASCO-ID-001"
    BASCO_CASES_INVALID = "BASCO-CASES-001"
    BASCO_DUPLICATE_ID = "BASCO-CONTAINER-001"
    
    @classmethod
    def get_description(cls, code: str) -> str:
        """Get human-readable description for error code."""
        descriptions = {
            # ... existing descriptions ...
            cls.BASCO_ID_INVALID: "BASCO ID must be between 1 and 99999999",
            cls.BASCO_CASES_INVALID: "BASCO cases format is invalid",
            cls.BASCO_DUPLICATE_ID: "BASCO ID already exists in container",
        }
        return descriptions.get(code, "Unknown error")
```

---

## Step 4: Create Specialized Container (Optional)

### 4.1 Assess if Container is Needed

Determine if the statement needs a specialized container:
- **Yes, if**: Multiple instances, unique ID requirements, special validation rules
- **No, if**: Single instance statements, simple collections

### 4.2 Create Container Class

If needed, create a specialized container following the `GrecoContainer` pattern:

```python
# src/pysd/containers/basco_container.py
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from .base_container import BaseContainer
from ..validation.core import ValidationIssue
from ..validation.error_codes import ErrorCodes
from ..validation.messages import ErrorMessageBuilder

if TYPE_CHECKING:
    from ..statements.basco import BASCO

class BascoContainer(BaseContainer):
    """
    Container for BASCO statements with specialized validation.
    
    BASCO-specific rules:
    - IDs must be unique integers 1-99999999
    - [Add other rules specific to BASCO]
    """
    
    def add(self, item: 'BASCO') -> None:
        """Add BASCO with specialized validation."""
        self._validate_basco_rules(item)
        super().add(item)
    
    def _validate_basco_rules(self, item: 'BASCO') -> None:
        """Validate BASCO-specific business rules."""
        issues = []
        
        # Check for duplicate ID
        if self.get_by_id(item.id) is not None:
            issues.append(ValidationIssue(
                severity='error',
                code=ErrorCodes.BASCO_DUPLICATE_ID,
                message=ErrorMessageBuilder.build_message(
                    'DUPLICATE_ID',
                    statement_type='BASCO',
                    id_value=str(item.id)
                ),
                location=f'BASCO.{item.id}'
            ))
        
        # Add other validation rules as needed
        
        # Raise errors if any critical issues found
        errors = [issue for issue in issues if issue.severity == 'error']
        if errors:
            error_messages = [issue.message for issue in errors]
            raise ValueError("BASCO validation failed:\n" + "\n".join(error_messages))
    
    def get_by_id(self, id_value: int) -> Optional['BASCO']:
        """Get BASCO by ID."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
```

### 4.3 Update Container __init__.py

Add the new container to the containers module:

```python
# src/pysd/containers/__init__.py
from .base_container import BaseContainer
from .greco_container import GrecoContainer
from .basco_container import BascoContainer  # Add this line

__all__ = ["BaseContainer", "GrecoContainer", "BascoContainer"]  # Add BascoContainer
```

---

## Step 5: Update SD_BASE Model

### 5.1 Add Container to SD_BASE

Update `src/pysd/sdmodel.py` to include the new container:

```python
class SD_BASE(BaseModel):
    """Enhanced SD_BASE with Pydantic validation and container management."""
    
    # ... existing containers ...
    greco_container: GrecoContainer = Field(default_factory=GrecoContainer)
    basco_container: BascoContainer = Field(default_factory=BascoContainer)  # Add this
    
    # ... rest of the class ...
```

### 5.2 Update Routing Logic

Add routing logic for the new statement type:

```python
    def _route_item(self, item: Any) -> None:
        """Route item to appropriate container or collection with validation."""
        from .statements.greco import GRECO
        from .statements.basco import BASCO  # Add this import
        
        if isinstance(item, GRECO):
            self.greco_container.add(item)
        elif isinstance(item, BASCO):  # Add this condition
            self.basco_container.add(item)
        else:
            # Handle other types or raise error
            raise ValueError(f"Unknown item type: {type(item)}")
```

### 5.3 Add Convenience Properties

Add convenience properties for accessing the container:

```python
    @property
    def basco(self) -> BascoContainer:
        """Access BASCO container."""
        return self.basco_container
    
    def get_basco_by_id(self, id_value: int) -> Optional['BASCO']:
        """Get BASCO by ID."""
        return self.basco_container.get_by_id(id_value)
```

---

## Step 6: Add Cross-Reference Validation

### 6.1 Create Cross-Reference Rules

Add cross-reference validation rules in `src/pysd/validation/cross_reference_rules.py`:

```python
class BascoLoadCaseCrossReferenceRule:
    """Validates that BASCO load cases reference existing definitions."""
    
    def validate(self, basco: 'BASCO', model: 'SD_BASE') -> List[ValidationIssue]:
        """Validate BASCO cross-references."""
        issues = []
        
        if not basco.cases:
            return issues
        
        # Example: Validate that load cases exist in other statements
        case_values = basco.cases.to_list() if hasattr(basco.cases, 'to_list') else []
        
        for case_value in case_values:
            if not self._is_case_defined_elsewhere(case_value, model):
                issues.append(ValidationIssue(
                    severity='error',
                    code=ErrorCodes.BASCO_CASES_INVALID,
                    message=ErrorMessageBuilder.build_message(
                        'CROSS_REFERENCE_MISSING',
                        statement_type='BASCO',
                        source_id=str(basco.id),
                        target_type='LoadCase',
                        target_id=str(case_value)
                    ),
                    location=f'BASCO.{basco.id}.cases',
                    suggestion=f'Define load case {case_value} or remove from BASCO {basco.id}'
                ))
        
        return issues
    
    def _is_case_defined_elsewhere(self, case_value: int, model: 'SD_BASE') -> bool:
        """Check if case is defined in other statements."""
        # TODO: Implement actual cross-reference checking
        # This depends on your specific business rules
        return True  # Placeholder to avoid false positives
```

### 6.2 Update Cross-Reference Validation in SD_BASE

Add the new cross-reference rule to the model validation:

```python
# In src/pysd/sdmodel.py
from .validation.cross_reference_rules import (
    GrecoELCCrossReferenceRule, 
    GrecoBasCountRule,
    BascoLoadCaseCrossReferenceRule  # Add this import
)

class SD_BASE(BaseModel):
    # ... existing code ...
    
    def _collect_validation_issues(self) -> List[ValidationIssue]:
        """Collect all validation issues from cross-object validation."""
        issues = []
        
        # GRECO cross-reference validation
        greco_elc_rule = GrecoELCCrossReferenceRule()
        greco_bas_rule = GrecoBasCountRule()
        
        for greco in self.greco_container.items:
            issues.extend(greco_elc_rule.validate(greco, self))
            issues.extend(greco_bas_rule.validate(greco, self))
        
        # BASCO cross-reference validation (Add this section)
        basco_rule = BascoLoadCaseCrossReferenceRule()
        
        for basco in self.basco_container.items:
            issues.extend(basco_rule.validate(basco, self))
        
        return issues
```

---

## Step 7: Create Tests

### 7.1 Create Unit Tests

Create comprehensive tests for the new statement:

```python
# tests/test_basco.py
import pytest
from pysd.statements.basco import BASCO
from pysd.statements.cases import Cases
from pysd.validation import set_validation_mode, ValidationMode, PySDValidationError

def test_basco_creation():
    """Test basic BASCO creation."""
    basco = BASCO(id=123, cases=Cases(ranges=[1, 2, 3]))
    assert basco.id == 123
    assert basco.input  # Should have generated input string

def test_basco_id_validation():
    """Test BASCO ID validation."""
    set_validation_mode(ValidationMode.NORMAL)
    
    # Valid ID
    basco = BASCO(id=12345)
    assert basco.id == 12345
    
    # Invalid ID (too large)
    with pytest.raises(PySDValidationError):
        BASCO(id=999999999)

def test_basco_validation_modes():
    """Test different validation modes."""
    # DISABLED mode should allow invalid data
    set_validation_mode(ValidationMode.DISABLED)
    basco = BASCO(id=999999999)  # Should not raise
    assert basco.id == 999999999
    
    # NORMAL mode should catch errors
    set_validation_mode(ValidationMode.NORMAL)
    with pytest.raises(PySDValidationError):
        BASCO(id=999999999)
```

### 7.2 Create Integration Tests

Test the statement within the SD_BASE model:

```python
# tests/test_basco_integration.py
import pytest
from pysd import SD_BASE
from pysd.statements.basco import BASCO
from pysd.statements.cases import Cases

def test_basco_in_sdbase():
    """Test BASCO integration with SD_BASE."""
    sd = SD_BASE()
    
    basco = BASCO(id=123, cases=Cases(ranges=[1, 2, 3]))
    sd.add(basco)
    
    assert len(sd.basco_container.items) == 1
    assert sd.get_basco_by_id(123) == basco

def test_basco_duplicate_ids():
    """Test duplicate ID handling."""
    sd = SD_BASE()
    
    basco1 = BASCO(id=123, cases=Cases(ranges=[1, 2, 3]))
    sd.add(basco1)
    
    basco2 = BASCO(id=123, cases=Cases(ranges=[4, 5, 6]))
    with pytest.raises(ValueError):  # Should fail due to duplicate ID
        sd.add(basco2)
```

### 7.3 Test Validation System Integration

```python
# tests/test_basco_validation_system.py
import pytest
from pysd.validation import (
    set_validation_mode, ValidationMode, no_validation,
    disable_validation_rule, enable_validation_rule
)
from pysd.statements.basco import BASCO

def test_basco_with_validation_modes():
    """Test BASCO with different validation modes."""
    
    # Test with context manager
    with no_validation():
        basco = BASCO(id=999999999)  # Invalid ID should be allowed
        assert basco.id == 999999999
    
    # Test rule disabling
    disable_validation_rule("BASCO-ID-001")
    basco = BASCO(id=999999999)  # Should be allowed
    
    enable_validation_rule("BASCO-ID-001")
    with pytest.raises(PySDValidationError):
        BASCO(id=999999999)  # Should fail again
```

---

## Step 8: Documentation and Migration

### 8.1 Update Documentation

Add documentation for the new statement:

```python
# Update the statement's docstring with comprehensive examples
class BASCO(BaseModel):
    """
    BASCO statement for [specific purpose].
    
    ### Usage
    
    Define as an object to generate BASCO input lines for ShellDesign.
    
    ### Examples
    
    ```python
    # Basic BASCO
    BASCO(id=123, cases=Cases(ranges=[1, 2, 3]))
    # -> 'BASCO ID=123 CASES=1,2,3'
    
    # BASCO with complex cases
    BASCO(
        id=456,
        cases=Cases(ranges=[(10, 20), 25, (30, 35)])
    )
    # -> 'BASCO ID=456 CASES=10-20,25,30-35'
    ```
    
    ### Parameters
    
    - **id**: int
        - Unique identifier (1-99999999). Required.
    - **cases**: Optional[Cases]
        - Load cases definition. Optional.
    
    ### Validation Rules
    
    1. **ID Range**: Must be between 1 and 99999999
    2. **ID Uniqueness**: Must be unique within the model
    3. **Cases Format**: Must follow Cases validation rules
    4. **Cross-References**: [Add specific cross-reference rules]
    """
```

### 8.2 Update Migration Checklist

Create a checklist for each statement migration:

```markdown
## BASCO Migration Checklist

- [x] Analyzed existing BASCO structure
- [x] Created Pydantic model with field validators
- [x] Added model validator with global validation system
- [x] Updated error codes for BASCO
- [x] Created BascoContainer (if needed)
- [x] Updated SD_BASE to include BASCO container
- [x] Added routing logic for BASCO
- [x] Created cross-reference validation rules
- [x] Added comprehensive unit tests
- [x] Added integration tests with SD_BASE
- [x] Tested validation system integration
- [x] Updated documentation
- [x] Verified backward compatibility
```

---

## Step 9: Testing and Validation

### 9.1 Run Comprehensive Tests

```bash
# Run all tests for the new statement
pytest tests/test_basco*.py -v

# Run integration tests
pytest tests/test_*_integration.py -v

# Run validation system tests
pytest tests/test_*_validation_system.py -v
```

### 9.2 Manual Testing

Create a manual test script:

```python
# manual_test_basco.py
from pysd import SD_BASE
from pysd.statements.basco import BASCO
from pysd.statements.cases import Cases
from pysd.validation import set_validation_mode, ValidationMode, no_validation

def test_basco_migration():
    """Manual test of BASCO migration."""
    print("Testing BASCO migration...")
    
    # Test 1: Basic creation
    basco = BASCO(id=123, cases=Cases(ranges=[1, 2, 3]))
    print(f"Created BASCO: {basco.input}")
    
    # Test 2: Integration with SD_BASE
    sd = SD_BASE()
    sd.add(basco)
    print(f"Added to SD_BASE, container size: {len(sd.basco_container.items)}")
    
    # Test 3: Validation modes
    set_validation_mode(ValidationMode.NORMAL)
    try:
        invalid_basco = BASCO(id=999999999)
        print("ERROR: Should have failed!")
    except Exception as e:
        print(f"Correctly caught validation error: {e}")
    
    # Test 4: Disabled validation
    with no_validation():
        invalid_basco = BASCO(id=999999999)
        print(f"No validation allowed invalid BASCO: {invalid_basco.id}")
    
    print("BASCO migration test completed successfully!")

if __name__ == "__main__":
    test_basco_migration()
```

---

## Step 10: Repeat for Other Statements

### 10.1 Prioritize Statements

Create a migration priority list based on:
1. **Frequency of use**: Most commonly used statements first
2. **Complexity**: Start with simpler statements
3. **Dependencies**: Statements with fewer cross-references first
4. **Business impact**: Critical statements for validation

Example priority order:
1. BASCO (example used in this guide)
2. CASES (if not already migrated)
3. LOADC (has cross-references with GRECO)
4. RELOC
5. RETYP
6. ... (continue with remaining statements)

### 10.2 Create Migration Templates

Create templates for quick migration:

```python
# Template: statement_template.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from ..validation.core import ValidationIssue, ValidationContext, ValidationSeverity
from ..validation.error_codes import ErrorCodes
from ..validation.messages import ErrorMessageBuilder

class STATEMENT_NAME(BaseModel):
    """
    STATEMENT_NAME statement for [purpose].
    
    [Add comprehensive docstring]
    """
    
    # Define fields
    id: int = Field(..., description="Statement ID")
    # Add other fields
    
    # Auto-generated field
    input: str = Field(default="", init=False, description="Generated input string")
    
    @field_validator('id')
    @classmethod
    def validate_id_range(cls, v: int) -> int:
        """Validate ID range."""
        # Add validation logic but don't raise here
        return v
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'STATEMENT_NAME':
        """Build input string and perform validation."""
        context = ValidationContext(current_object=self)
        
        # Add validation issues to context
        # Each issue will auto-raise if configured to do so
        
        # Build input string
        self._build_input_string()
        
        return self
    
    def _build_input_string(self) -> None:
        """Build the formatted input string."""
        # Implement string formatting logic
        self.input = f"STATEMENT_NAME ID={self.id}"
```

### 10.3 Automate Where Possible

Create scripts to automate parts of the migration:

```python
# migration_helper.py
def generate_error_codes(statement_name: str) -> str:
    """Generate error code definitions for a statement."""
    upper_name = statement_name.upper()
    return f"""
    # {upper_name} validation errors
    {upper_name}_ID_INVALID = "{upper_name}-ID-001"
    {upper_name}_FORMAT_INVALID = "{upper_name}-FORMAT-001"
    {upper_name}_DUPLICATE_ID = "{upper_name}-CONTAINER-001"
    """

def generate_container_template(statement_name: str) -> str:
    """Generate container class template."""
    # Implementation to generate container boilerplate
    pass

def generate_test_template(statement_name: str) -> str:
    """Generate test file template."""
    # Implementation to generate test boilerplate
    pass
```

---

## 🎯 Summary and Best Practices

### ✅ Key Success Factors

1. **Follow the Pattern**: Use GRECO as the reference implementation
2. **Test Thoroughly**: Unit tests, integration tests, validation system tests
3. **Document Everything**: Comprehensive docstrings and examples
4. **Validate Incrementally**: Test each step before moving to the next
5. **Use Global Validation**: Leverage the severity control system
6. **Maintain Backward Compatibility**: Ensure existing code still works

### 🚨 Common Pitfalls to Avoid

1. **Don't raise errors directly in field validators** - use the model validator with ValidationContext
2. **Don't forget to add error codes** for new validation rules
3. **Don't skip cross-reference validation** - it's crucial for data integrity
4. **Don't ignore the container layer** - it provides important business logic
5. **Don't forget to update SD_BASE routing** - statements won't work without it

### 🔄 Migration Checklist Template

For each statement, use this checklist:

```markdown
## [STATEMENT_NAME] Migration Checklist

### Analysis Phase
- [ ] Analyzed existing structure and requirements
- [ ] Documented business rules and validation needs
- [ ] Identified cross-references to other statements

### Implementation Phase
- [ ] Created Pydantic model with proper field types
- [ ] Added field validators (without raising errors)
- [ ] Implemented model validator with ValidationContext
- [ ] Added error codes to error_codes.py
- [ ] Created specialized container (if needed)
- [ ] Updated SD_BASE for routing and access
- [ ] Added cross-reference validation rules

### Testing Phase
- [ ] Created comprehensive unit tests
- [ ] Added integration tests with SD_BASE
- [ ] Tested validation system integration
- [ ] Verified different validation modes work
- [ ] Tested rule-specific controls
- [ ] Manual testing completed

### Documentation Phase
- [ ] Updated statement docstring with examples
- [ ] Added validation rules documentation
- [ ] Updated user guide if needed
- [ ] Verified backward compatibility

### Completion Phase
- [ ] All tests passing
- [ ] Code review completed
- [ ] Integration with main codebase
- [ ] Performance testing (if needed)
```

This step-by-step guide provides a systematic approach to migrating all PySD statements to the new validation system. Each statement you migrate will benefit from global validation control, standardized error handling, and robust business rule validation while maintaining backward compatibility with existing code.

Start with the simplest statements and work your way up to more complex ones. The pattern established with GRECO provides a solid foundation that can be adapted for any statement type in your codebase.