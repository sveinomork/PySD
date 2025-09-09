# Pydantic Migration and Container-Based Validation Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Phase 1: Pydantic Statement Migration](#phase-1-pydantic-statement-migration)
3. [Phase 2: Object Instance Validation](#phase-2-object-instance-validation)
4. [Phase 3: Generalized Validation Framework](#phase-3-generalized-validation-framework)
5. [Phase 4: Standardized Error Messages](#phase-4-standardized-error-messages)
6. [Phase 5: Container-Based Implementation](#phase-5-container-based-implementation)
7. [Phase 6: SD_BASE Pydantic Transformation](#phase-6-sd_base-pydantic-transformation)
8. [Testing Strategy](#testing-strategy)
9. [Migration Checklist](#migration-checklist)

## Overview

This document outlines the comprehensive migration of the sdpython codebase to use Pydantic v2 for validation, containers for collection management, and standardized error handling. The implementation follows a layered validation approach:

- **Level 1**: Individual object validation (Pydantic)
- **Level 2**: Container validation (unique IDs, cross-instance rules)
- **Level 3**: Model validation (cross-object references, business rules)

## Phase 1: Pydantic Statement Migration

### 1.1 Base Statement Pattern

All statement classes should follow this standardized pattern:

```python
from __future__ import annotations
from typing import Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class ExampleStatement(BaseModel):
    """
    Example statement with standardized Pydantic structure.
    
    Args:
        id: Unique identifier (1-99999999)
        required_param: Required parameter with validation
        optional_param: Optional parameter with default
    """
    
    # Required fields
    id: int = Field(..., description="Unique statement ID")
    required_param: str = Field(..., description="Required parameter")
    
    # Optional fields with defaults
    optional_param: Optional[float] = Field(None, description="Optional parameter")
    
    # Auto-generated fields
    input: str = Field(default="", init=False, description="Generated input string")
    
    # Validation methods
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: int) -> int:
        """Validate ID range and format."""
        if not isinstance(v, int):
            raise ValueError("ID must be an integer")
        if not 1 <= v <= 99999999:
            raise ValueError("ID must be between 1 and 99999999")
        return v
    
    @field_validator('required_param')
    @classmethod
    def validate_required_param(cls, v: str) -> str:
        """Validate required parameter."""
        if not v or not v.strip():
            raise ValueError("Required parameter cannot be empty")
        if len(v) > 16:
            raise ValueError("Parameter must be ≤ 16 characters")
        return v.strip().upper()
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'ExampleStatement':
        """Build the statement input string and perform cross-field validation."""
        # Cross-field validation
        if self.optional_param is not None and self.optional_param < 0:
            raise ValueError("Optional parameter must be non-negative when provided")
        
        # Build input string
        parts = [f"EXAMPLE ID={self.id} PARAM={self.required_param}"]
        
        if self.optional_param is not None:
            parts.append(f"OPT={self.optional_param}")
        
        self.input = " ".join(parts)
        return self
    
    def __str__(self) -> str:
        return self.input
```

### 1.2 Migration Priority List

Migrate statements in this order (dependencies first):

1. **Base types**: `Cases`, utility classes
2. **Simple statements**: `RFILE`, `HEADL`, `FILST`
3. **Core statements**: `RETYP`, `DESEC`, `SHAXE`, `SHSEC`
4. **Complex statements**: `BASCO`, `GRECO`, `LOADC`, `DECAS`
5. **Cross-referencing**: `RELOC`, `CMPEC`, `RMPEC`

### 1.3 Dataclass to Pydantic Conversion Template

For existing dataclass statements like `SHEXT`:

```python
# Before (dataclass)
@dataclass
class SHEXT:
    pa: str
    sections: List[str]
    
# After (Pydantic)
class SHEXT(BaseModel):
    """Shell extension definition."""
    
    pa: str = Field(..., description="Part name (max 8 characters)")
    sections: List[str] = Field(..., min_length=1, description="Section definitions")
    input: str = Field(default="", init=False)
    
    @field_validator('pa')
    @classmethod
    def validate_part_name(cls, v: str) -> str:
        if len(v) > 8:
            raise ValueError("Part name (PA) must be max 8 characters")
        return v.upper()
    
    @field_validator('sections')
    @classmethod
    def validate_sections(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one section must be provided")
        return [s.upper() for s in v]
    
    @model_validator(mode='after')
    def build_input_string(self) -> 'SHEXT':
        sections_str = " ".join(self.sections)
        self.input = f"SHEXT PA={self.pa} {sections_str}"
        return self
```

## Phase 2: Object Instance Validation

### 2.1 Field Validation Standards

Implement consistent field validation patterns:

```python
class ValidationMixin:
    """Common validation methods for reuse across statements."""
    
    @classmethod
    def validate_id_range(cls, v: int, min_val: int = 1, max_val: int = 99999999) -> int:
        """Standard ID validation."""
        if not isinstance(v, int):
            raise ValueError("ID must be an integer")
        if not min_val <= v <= max_val:
            raise ValueError(f"ID must be between {min_val} and {max_val}")
        return v
    
    @classmethod
    def validate_part_name(cls, v: Optional[str], max_length: int = 8) -> Optional[str]:
        """Standard part name validation."""
        if v is None:
            return v
        if len(v) > max_length:
            raise ValueError(f"Part name must be max {max_length} characters")
        return v.upper()
    
    @classmethod
    def validate_positive_number(cls, v: Optional[float], field_name: str) -> Optional[float]:
        """Standard positive number validation."""
        if v is not None and v <= 0:
            raise ValueError(f"{field_name} must be positive")
        return v
```

### 2.2 Complex Validation Examples

```python
class RETYP(BaseModel):
    """Rebar type definition with method-based validation."""
    
    id: int = Field(..., description="Rebar type ID")
    mp: Optional[int] = Field(None, description="Material property reference")
    
    # Method 1: Area directly
    ar: Optional[float] = Field(None, description="Rebar area (mm²)")
    
    # Method 2: Number + diameter
    nr: Optional[int] = Field(None, description="Number of rebars")
    di: Optional[float] = Field(None, description="Diameter (mm or m)")
    
    # Optional parameters
    lb: Optional[str] = Field(None, description="Label (max 16 chars)")
    
    input: str = Field(default="", init=False)
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: int) -> int:
        if not 1 <= v <= 99999999:
            raise ValueError("ID must be a positive integer with max 8 digits")
        return v
    
    @field_validator('lb')
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 16:
            raise ValueError("LB label must be ≤ 16 characters")
        return v
    
    @model_validator(mode='after')
    def validate_methods(self) -> 'RETYP':
        """Validate that exactly one definition method is used."""
        method1 = self.ar is not None
        method2 = self.nr is not None and self.di is not None
        
        if not method1 and not method2:
            raise ValueError("Must provide either AR (Method 1) or NR+DI (Method 2)")
        
        if method1 and method2:
            raise ValueError("Cannot specify both AR and NR+DI methods")
        
        if self.nr is not None and self.di is None:
            raise ValueError("Must provide either AR (Method 1) or NR+DI (Method 2)")
        
        # Build input string
        parts = [f"RETYP ID={self.id}"]
        
        if self.mp:
            parts.append(f"MP={self.mp}")
        
        if self.ar:
            parts.append(f"AR={self.ar}")
        elif self.nr and self.di:
            parts.append(f"NR={self.nr}")
            # Format diameter appropriately
            if self.di >= 1.0:
                parts.append(f"DI={int(self.di)}")  # mm
            else:
                parts.append(f"DI={self.di}")  # m
        
        if self.lb:
            parts.append(f"LB={self.lb}")
        
        self.input = " ".join(parts)
        return self
```

## Phase 3: Generalized Validation Framework

### 3.1 Validation Registry Pattern

Create a flexible validation system:

```python
# validation/core.py
from typing import Protocol, TypeVar, Callable, Dict, List
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class ValidationRule(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, obj: T, context: 'ValidationContext') -> List['ValidationIssue']:
        """Validate an object and return issues."""
        ...

class ValidationIssue(BaseModel):
    """Represents a validation issue."""
    
    severity: Literal['error', 'warning', 'info']
    code: str
    message: str
    location: str
    suggestion: Optional[str] = None

class ValidationContext(BaseModel):
    """Context for validation operations."""
    
    current_object: Optional[BaseModel] = None
    parent_container: Optional['BaseContainer'] = None
    full_model: Optional['SD_BASE'] = None
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        if not hasattr(self, '_issues'):
            self._issues = []
        self._issues.append(issue)
    
    def get_issues(self) -> List[ValidationIssue]:
        """Get all validation issues."""
        return getattr(self, '_issues', [])

# validation/rules.py
class IDRangeRule:
    """Validates ID ranges for different statement types."""
    
    RANGES = {
        'BASCO': (1, 99999999),
        'RETYP': (1, 99999999),
        'RELOC': (1, 9999),  # String IDs with different limits
    }
    
    def validate(self, obj: BaseModel, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        statement_type = obj.__class__.__name__
        
        if hasattr(obj, 'id') and statement_type in self.RANGES:
            min_val, max_val = self.RANGES[statement_type]
            if not min_val <= obj.id <= max_val:
                issues.append(ValidationIssue(
                    severity='error',
                    code=f'{statement_type}-ID-001',
                    message=f'ID must be between {min_val} and {max_val}',
                    location=f'{statement_type}.id',
                    suggestion=f'Use an ID between {min_val} and {max_val}'
                ))
        
        return issues

# Register validation rules
VALIDATION_RULES: List[ValidationRule] = [
    IDRangeRule(),
    # Add more rules...
]
```

### 3.2 Cross-Reference Validation

```python
# validation/cross_reference.py
class CrossReferenceRule:
    """Validates cross-references between statements."""
    
    def validate(self, obj: BaseModel, context: ValidationContext) -> List[ValidationIssue]:
        issues = []
        
        if context.full_model is None:
            return issues
        
        # RELOC must reference existing RETYP
        if isinstance(obj, RELOC) and hasattr(obj, 'rt'):
            if obj.rt not in context.full_model.retyp:
                issues.append(ValidationIssue(
                    severity='error',
                    code='RELOC-REF-001',
                    message=f'RELOC {obj.id} references non-existent RETYP ID {obj.rt}',
                    location=f'RELOC.{obj.id}.rt',
                    suggestion=f'Create RETYP with ID {obj.rt} or use existing RETYP ID'
                ))
        
        return issues
```

## Phase 4: Standardized Error Messages

### 4.1 Error Message Standards

Implement consistent, actionable error messages:

```python
# validation/messages.py
from typing import Dict, Callable

class ErrorMessageBuilder:
    """Builds standardized error messages."""
    
    TEMPLATES = {
        'REQUIRED_FIELD': "{field} is required for {statement_type}",
        'INVALID_RANGE': "{field} must be between {min_val} and {max_val}",
        'INVALID_LENGTH': "{field} must be max {max_length} characters",
        'INVALID_FORMAT': "{field} must match format: {format_desc}",
        'MUTUAL_EXCLUSION': "Cannot specify both {field1} and {field2}",
        'MISSING_DEPENDENCY': "{field} requires {dependency_field} to be specified",
        'INVALID_REFERENCE': "{field} references non-existent {ref_type} {ref_value}",
    }
    
    @classmethod
    def build_message(cls, template_key: str, **kwargs) -> str:
        """Build a standardized error message."""
        template = cls.TEMPLATES.get(template_key, "Validation error: {error}")
        return template.format(**kwargs)

# Example usage in validators
@field_validator('id')
@classmethod
def validate_id(cls, v: int) -> int:
    if not 1 <= v <= 99999999:
        raise ValueError(
            ErrorMessageBuilder.build_message(
                'INVALID_RANGE',
                field='ID',
                min_val=1,
                max_val=99999999
            )
        )
    return v
```

### 4.2 Error Code System

```python
# validation/error_codes.py
class ErrorCodes:
    """Standardized error codes for different validation types."""
    
    # Format: {STATEMENT}-{CATEGORY}-{NUMBER}
    
    # ID validation errors
    BASCO_ID_RANGE = "BASCO-ID-001"
    RETYP_ID_RANGE = "RETYP-ID-001"
    
    # Field validation errors
    BASCO_LOAD_CASES_EMPTY = "BASCO-FIELD-001"
    BASCO_LOAD_CASES_TOO_MANY = "BASCO-FIELD-002"
    
    # Cross-reference errors
    RELOC_RETYP_MISSING = "RELOC-REF-001"
    
    # Business logic errors
    DECAS_FLS_BAS_REQUIRED = "DECAS-LOGIC-001"
    
    @classmethod
    def get_description(cls, code: str) -> str:
        """Get human-readable description for error code."""
        descriptions = {
            cls.BASCO_ID_RANGE: "BASCO ID must be within valid range",
            cls.RELOC_RETYP_MISSING: "RELOC references non-existent RETYP",
            # Add more descriptions...
        }
        return descriptions.get(code, "Unknown error")
```

## Phase 5: Container-Based Implementation

### 5.1 Enhanced BaseContainer

Extend the existing BaseContainer with validation integration:

```python
# containers/validated_container.py
from typing import TypeVar, Generic, List, Optional, Type
from pydantic import BaseModel, Field, model_validator
from .base_container import BaseContainer, HasID
from validation.core import ValidationContext, ValidationIssue, VALIDATION_RULES

T = TypeVar('T', bound=HasID)

class ValidatedContainer(BaseContainer[T], Generic[T]):
    """Container with integrated validation."""
    
    validation_enabled: bool = Field(default=True, description="Enable validation")
    
    def add(self, item: T) -> None:
        """Add item with validation."""
        if self.validation_enabled:
            self._validate_item(item)
        super().add(item)
    
    def add_batch(self, items: List[T]) -> None:
        """Add multiple items with batch validation."""
        if self.validation_enabled:
            self._validate_batch(items)
        
        for item in items:
            super().add(item)  # Skip individual validation since batch validation passed
    
    def _validate_item(self, item: T) -> None:
        """Validate a single item."""
        context = ValidationContext(
            current_object=item,
            parent_container=self
        )
        
        issues = []
        for rule in VALIDATION_RULES:
            issues.extend(rule.validate(item, context))
        
        # Check for duplicate IDs
        if hasattr(item, 'id') and self.get_by_id(item.id) is not None:
            issues.append(ValidationIssue(
                severity='error',
                code='CONTAINER-DUPLICATE-001',
                message=f'Duplicate ID {item.id} in container',
                location=f'{item.__class__.__name__}.{item.id}'
            ))
        
        if any(issue.severity == 'error' for issue in issues):
            error_messages = [issue.message for issue in issues if issue.severity == 'error']
            raise ValueError(f"Validation failed:\n" + "\n".join(error_messages))
    
    def _validate_batch(self, items: List[T]) -> None:
        """Validate a batch of items."""
        # Check for duplicate IDs within the batch
        seen_ids = set()
        for item in items:
            if hasattr(item, 'id'):
                if item.id in seen_ids:
                    raise ValueError(f"Duplicate ID {item.id} in batch")
                if self.get_by_id(item.id) is not None:
                    raise ValueError(f"ID {item.id} already exists in container")
                seen_ids.add(item.id)
        
        # Validate each item
        for item in items:
            self._validate_item(item)
```

### 5.2 Specialized Statement Containers

Create type-specific containers with specialized validation:

```python
# containers/basco_container.py
from statements.basco import BASCO
from .validated_container import ValidatedContainer

class BascoContainer(ValidatedContainer[BASCO]):
    """Container for BASCO statements with specialized validation."""
    
    def validate_load_case_references(self) -> List[ValidationIssue]:
        """Validate that all referenced load cases exist."""
        issues = []
        
        for basco in self.items:
            for load_case in basco.load_cases:
                # Check if load case number exists in model
                # This would require access to full model context
                pass
        
        return issues
    
    def get_by_load_case(self, load_case_number: int) -> List[BASCO]:
        """Get all BASCO statements containing a specific load case."""
        return [
            basco for basco in self.items
            if any(lc.lc_numb == load_case_number for lc in basco.load_cases)
        ]

# containers/loadc_container.py
from statements.loadc import LOADC
from .validated_container import ValidatedContainer

class LoadcContainer(ValidatedContainer[LOADC]):
    """Container for LOADC statements with OLC uniqueness validation."""
    
    @model_validator(mode='after')
    def validate_olc_uniqueness(self) -> 'LoadcContainer':
        """Ensure no overlapping OLC values."""
        all_olcs = set()
        
        for loadc in self.items:
            if loadc.olc:
                loadc_olcs = loadc.get_olc_list()  # Assuming this method exists
                for olc in loadc_olcs:
                    if olc in all_olcs:
                        raise ValueError(f"Duplicate OLC value found: {olc}")
                    all_olcs.add(olc)
        
        return self
```

## Phase 6: SD_BASE Pydantic Transformation

### 6.1 Enhanced SD_BASE with Containers

Transform SD_BASE to use Pydantic and container-based validation:

```python
# sd_base.py
from __future__ import annotations
from typing import List, Union, Optional, Type, TypeVar
from pydantic import BaseModel, Field, model_validator
from contextlib import contextmanager

# Import containers
from containers import (
    ValidatedContainer, BascoContainer, LoadcContainer,
    create_statement_container
)

# Import validation
from validation.core import ValidationContext, VALIDATION_RULES
from validation.cross_reference import CrossReferenceRule

# Import statements (all Pydantic now)
from statements import *

T = TypeVar('T', bound=BaseModel)

class SD_BASE(BaseModel):
    """
    Main ShellDesign model with container-based validation.
    
    Features:
    - Automatic container creation and validation
    - Cross-object reference validation
    - Layered validation (object -> container -> model)
    - Backward compatible API
    """
    
    # Container-based collections for ID objects
    basco: BascoContainer = Field(default_factory=BascoContainer)
    retyp: ValidatedContainer[RETYP] = Field(default_factory=lambda: ValidatedContainer[RETYP]())
    greco: ValidatedContainer[GRECO] = Field(default_factory=lambda: ValidatedContainer[GRECO]())
    reloc: ValidatedContainer[RELOC] = Field(default_factory=lambda: ValidatedContainer[RELOC]())
    cmpec: ValidatedContainer[CMPEC] = Field(default_factory=lambda: ValidatedContainer[CMPEC]())
    rmpec: ValidatedContainer[RMPEC] = Field(default_factory=lambda: ValidatedContainer[RMPEC]())
    cmpns: ValidatedContainer[CMPNS] = Field(default_factory=lambda: ValidatedContainer[CMPNS]())
    rmpns: ValidatedContainer[RMPNS] = Field(default_factory=lambda: ValidatedContainer[RMPNS]())
    inplc: ValidatedContainer[INPLC] = Field(default_factory=lambda: ValidatedContainer[INPLC]())
    cmpnl: ValidatedContainer[CMPNL] = Field(default_factory=lambda: ValidatedContainer[CMPNL]())
    rmpnl: ValidatedContainer[RMPNL] = Field(default_factory=lambda: ValidatedContainer[RMPNL]())
    
    # Specialized containers
    loadc: LoadcContainer = Field(default_factory=LoadcContainer)
    
    # Key-based collections
    shaxe: Dict[str, SHAXE] = Field(default_factory=dict)
    shsec: Dict[str, SHSEC] = Field(default_factory=dict)
    xtfil: Dict[str, XTFIL] = Field(default_factory=dict)
    desec: Dict[str, DESEC] = Field(default_factory=dict)
    
    # List-based collections
    rfile: List[RFILE] = Field(default_factory=list)
    incdf: List[INCDF] = Field(default_factory=list)
    headl: List[HEADL] = Field(default_factory=list)
    filst: List[FILST] = Field(default_factory=list)
    lores: List[LORES] = Field(default_factory=list)
    table: List[TABLE] = Field(default_factory=list)
    execd: List[EXECD] = Field(default_factory=list)
    decas: List[DECAS] = Field(default_factory=list)
    
    # Singleton objects
    depar: Optional[DEPAR] = None
    nonli: Optional[NONLI] = None
    
    # Maintain order
    _all_items: List[StatementType] = Field(default_factory=list, exclude=True)
    
    # Validation settings
    validation_enabled: bool = Field(default=True, exclude=True)
    
    def add(self, item: Union[StatementType, List[StatementType]]) -> None:
        """
        Enhanced add method with automatic container routing and validation.
        
        Features:
        - Automatic container selection based on type
        - Batch processing for lists
        - Layered validation (object -> container -> model)
        - Maintains backward compatibility
        """
        if isinstance(item, list):
            self._add_batch(item)
            return
        
        # Route to appropriate container/collection
        self._route_item(item)
        
        # Add to master list (maintain order)
        if isinstance(item, EXECD):
            # Remove existing EXECD items and add at end
            self._all_items = [x for x in self._all_items if not isinstance(x, EXECD)]
        
        self._all_items.append(item)
        
        # Perform model-level validation
        if self.validation_enabled:
            self._validate_model()
    
    def _route_item(self, item: StatementType) -> None:
        """Route item to appropriate container or collection."""
        
        # Container-based routing (with validation)
        if isinstance(item, BASCO):
            self.basco.add(item)
        elif isinstance(item, RETYP):
            self.retyp.add(item)
        elif isinstance(item, GRECO):
            if item.id is not None:
                self.greco.add(item)
            else:
                raise ValueError("GRECO item must have a non-None id to be stored")
        elif isinstance(item, RELOC):
            self.reloc.add(item)
        elif isinstance(item, LOADC):
            self.loadc.add(item)
        elif isinstance(item, CMPEC):
            if item.id is not None:
                self.cmpec.add(item)
            else:
                raise ValueError("CMPEC item must have a non-None id to be stored")
        # ... add other container types
        
        # Key-based routing
        elif isinstance(item, SHAXE):
            if item.key in self.shaxe:
                raise ValueError(f"Duplicate SHAXE key: {item.key}")
            self.shaxe[item.key] = item
        elif isinstance(item, DESEC):
            if item.pa in self.desec:
                raise ValueError(f"Duplicate DESEC part: {item.pa}")
            self.desec[item.pa] = item
        # ... add other key-based types
        
        # List-based routing
        elif isinstance(item, RFILE):
            self.rfile.append(item)
        elif isinstance(item, HEADL):
            self.headl.append(item)
        # ... add other list-based types
        
        # Singleton routing
        elif isinstance(item, DEPAR):
            if self.depar is not None:
                raise ValueError("Only one DEPAR statement allowed")
            self.depar = item
        elif isinstance(item, NONLI):
            if self.nonli is not None:
                raise ValueError("Only one NONLI statement allowed")
            self.nonli = item
        
        else:
            raise TypeError(f"Unsupported type for add(): {type(item).__name__}")
    
    def _add_batch(self, items: List[StatementType]) -> None:
        """Add multiple items with optimized batch validation."""
        
        # Group items by type for batch processing
        grouped_items = {}
        for item in items:
            item_type = type(item)
            if item_type not in grouped_items:
                grouped_items[item_type] = []
            grouped_items[item_type].append(item)
        
        # Process each group
        for item_type, type_items in grouped_items.items():
            if item_type == BASCO:
                self.basco.add_batch(type_items)
            elif item_type == RETYP:
                self.retyp.add_batch(type_items)
            # ... handle other container types
            else:
                # Fall back to individual processing for non-container types
                for item in type_items:
                    self._route_item(item)
        
        # Add all to master list
        self._all_items.extend(items)
        
        # Model-level validation
        if self.validation_enabled:
            self._validate_model()
    
    def _validate_model(self) -> None:
        """Perform model-level cross-object validation."""
        context = ValidationContext(full_model=self)
        issues = []
        
        # Run cross-reference validation
        cross_ref_rule = CrossReferenceRule()
        
        for item in self._all_items:
            context.current_object = item
            issues.extend(cross_ref_rule.validate(item, context))
        
        # Check for critical errors
        errors = [issue for issue in issues if issue.severity == 'error']
        if errors:
            error_messages = [f"[{error.code}] {error.message}" for error in errors]
            raise ValueError(f"Model validation failed:\n" + "\n".join(error_messages))
    
    def get_all_ids(self, statement_type: Type[T]) -> List[int]:
        """Get all IDs for a specific statement type."""
        container = self._get_container_for_type(statement_type)
        if container:
            return container.get_ids()
        return []
    
    def get_cross_references(self) -> Dict[str, List[str]]:
        """Get all cross-references in the model."""
        references = {}
        
        # RELOC -> RETYP references
        for reloc in self.reloc.items:
            if hasattr(reloc, 'rt'):
                key = f"RELOC.{reloc.id}"
                references[key] = [f"RETYP.{reloc.rt}"]
        
        # Add other cross-references...
        
        return references
    
    def validate_integrity(self) -> Dict[str, List[str]]:
        """Comprehensive integrity validation."""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Run all validation rules
        context = ValidationContext(full_model=self)
        
        for item in self._all_items:
            context.current_object = item
            for rule in VALIDATION_RULES:
                rule_issues = rule.validate(item, context)
                for issue in rule_issues:
                    issues[issue.severity + 's'].append(f"[{issue.code}] {issue.message}")
        
        return issues
    
    @model_validator(mode='after')
    def validate_complete_model(self) -> 'SD_BASE':
        """Final model validation after all fields are set."""
        if self.validation_enabled:
            self._validate_model()
        return self
    
    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str, validation_enabled: bool = True):
        """
        Enhanced context manager with validation control.
        
        Args:
            output_file: Output file path
            validation_enabled: Enable/disable validation during construction
        """
        sd_model = cls(validation_enabled=validation_enabled)
        try:
            yield sd_model
        finally:
            # Re-enable validation for final check if it was disabled
            if not validation_enabled:
                sd_model.validation_enabled = True
                sd_model._validate_model()
            
            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                for item in sd_model._all_items:
                    f.write(str(item) + "\n")
    
    def to_dict(self) -> Dict:
        """Export model to dictionary for serialization."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SD_BASE':
        """Import model from dictionary."""
        return cls.model_validate(data)
```

### 6.2 Migration Helper Functions

```python
# migration/helpers.py
def migrate_existing_sd_base(old_sd: 'OldSD_BASE') -> SD_BASE:
    """Migrate existing SD_BASE instance to new Pydantic version."""
    
    new_sd = SD_BASE(validation_enabled=False)  # Disable during migration
    
    # Migrate container-based collections
    if hasattr(old_sd, 'basco'):
        for basco in old_sd.basco.values():
            new_sd.add(basco)
    
    # Migrate other collections...
    
    # Re-enable validation and validate
    new_sd.validation_enabled = True
    new_sd._validate_model()
    
    return new_sd
```

## Phase 7: Testing Strategy

### 7.1 Validation Testing

```python
# tests/test_validation_framework.py
import pytest
from pydantic import ValidationError
from statements.basco import BASCO
from containers import BascoContainer
from sd_base import SD_BASE

class TestValidationFramework:
    
    def test_field_validation(self):
        """Test individual field validation."""
        # Valid case
        basco = BASCO(id=1, load_cases=[...])
        assert basco.id == 1
        
        # Invalid ID range
        with pytest.raises(ValidationError, match="ID must be between"):
            BASCO(id=0, load_cases=[...])
    
    def test_container_validation(self):
        """Test container-level validation."""
        container = BascoContainer()
        
        basco1 = BASCO(id=1, load_cases=[...])
        basco2 = BASCO(id=2, load_cases=[...])
        
        container.add(basco1)
        container.add(basco2)
        
        # Duplicate ID should fail
        basco3 = BASCO(id=1, load_cases=[...])
        with pytest.raises(ValueError, match="Duplicate ID"):
            container.add(basco3)
    
    def test_model_validation(self):
        """Test model-level cross-object validation."""
        sd = SD_BASE()
        
        # Add RELOC that references non-existent RETYP
        reloc = RELOC(id="REL1", rt=999)
        
        with pytest.raises(ValueError, match="references non-existent RETYP"):
            sd.add(reloc)
    
    def test_batch_validation(self):
        """Test batch processing with validation."""
        sd = SD_BASE()
        
        bascos = [
            BASCO(id=1, load_cases=[...]),
            BASCO(id=2, load_cases=[...])
        ]
        
        sd.add(bascos)  # Should work
        
        # Batch with duplicate IDs should fail
        duplicate_batch = [
            BASCO(id=3, load_cases=[...]),
            BASCO(id=3, load_cases=[...])  # Duplicate
        ]
        
        with pytest.raises(ValueError, match="Duplicate ID.*in batch"):
            sd.add(duplicate_batch)
```

### 7.2 Migration Testing

```python
# tests/test_migration.py
def test_backward_compatibility():
    """Test that existing code still works."""
    
    # Old style usage should still work
    sd = SD_BASE()
    basco = BASCO(id=1, load_cases=[...])
    sd.add(basco)
    
    # Access patterns should be preserved
    assert sd.basco.get_by_id(1) == basco
    assert len(sd.basco) == 1
    
def test_pydantic_features():
    """Test new Pydantic features work."""
    
    # Serialization
    sd = SD_BASE()
    sd.add(BASCO(id=1, load_cases=[...]))
    
    data = sd.to_dict()
    sd2 = SD_BASE.from_dict(data)
    
    assert len(sd2.basco) == 1
    assert sd2.basco.get_by_id(1).id == 1
```

## Migration Checklist

### Phase 1: Preparation
- [ ] Create validation framework structure
- [ ] Set up error message standards
- [ ] Create migration helper utilities
- [ ] Set up comprehensive test suite

### Phase 2: Statement Migration
- [ ] Migrate base types (Cases, etc.)
- [ ] Migrate simple statements (RFILE, HEADL, FILST)
- [ ] Migrate core statements (RETYP, DESEC, SHAXE)
- [ ] Migrate complex statements (BASCO, GRECO, LOADC)
- [ ] Migrate cross-referencing statements (RELOC, CMPEC)

### Phase 3: Container Implementation
- [ ] Enhance BaseContainer with validation
- [ ] Create specialized containers (BascoContainer, LoadcContainer)
- [ ] Implement container factory pattern
- [ ] Add batch processing capabilities

### Phase 4: SD_BASE Transformation
- [ ] Convert SD_BASE to Pydantic
- [ ] Implement container-based routing
- [ ] Add model-level validation
- [ ] Preserve backward compatibility

### Phase 5: Testing & Validation
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Performance benchmarking
- [ ] Migration validation

### Phase 6: Documentation
- [ ] Update API documentation
- [ ] Create migration guide
- [ ] Update examples and tutorials
- [ ] Performance and best practices guide

## Conclusion

This implementation guide provides a comprehensive roadmap for migrating the sdpython codebase to a modern, validated, container-based architecture. The phased approach ensures:

1. **Reliability**: Layered validation catches errors early
2. **Maintainability**: Standardized patterns and error messages
3. **Performance**: Batch processing and optimized validation
4. **Backward Compatibility**: Existing code continues to work
5. **Extensibility**: Easy to add new statement types and validation rules

The result will be a robust, type-safe, and user-friendly API that maintains the simplicity of the current interface while providing enterprise-grade validation and error handling.