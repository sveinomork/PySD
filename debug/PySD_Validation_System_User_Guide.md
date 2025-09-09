# PySD Validation System User Guide

## Overview

The PySD validation system provides **global severity control** for validation errors with support for different validation modes, rule-specific controls, and custom validation behaviors. This allows you to control when validation errors are raised based on your development context (development, testing, production, data migration, etc.).

## 🎯 Key Features

### 1. **Global Validation Modes**
- **STRICT**: All validation issues raise exceptions (errors, warnings, info)
- **NORMAL**: Only ERROR severity raises exceptions (default behavior)
- **PERMISSIVE**: Only critical errors raise exceptions
- **DISABLED**: No validation errors raise exceptions

### 2. **Custom Exception Type**
- **`PySDValidationError`**: Custom exception that extends `ValueError`
- Contains severity, error code, location, suggestion, and validation issues
- Only raised based on global validation configuration

### 3. **Rule-Specific Control**
- Disable/enable specific validation rules by error code
- Set custom severity thresholds per rule
- Thread-safe global configuration

### 4. **Context Managers**
- Temporarily change validation mode for specific operations
- Automatically restore previous mode when exiting context

## 🚀 Quick Start

### Basic Usage

```python
from pysd.validation import set_validation_mode, ValidationMode
from pysd.statements.greco import GRECO
from pysd.statements.cases import Cases

# Set global validation mode
set_validation_mode(ValidationMode.STRICT)    # Raise for everything
set_validation_mode(ValidationMode.NORMAL)   # Raise for errors only (default)
set_validation_mode(ValidationMode.PERMISSIVE)  # Raise for critical only
set_validation_mode(ValidationMode.DISABLED) # Never raise

# Create GRECO with validation
try:
    greco = GRECO(id="A", bas=Cases(ranges=[1, 2, 3, 4, 5, 6]))
    print("Valid GRECO created")
except PySDValidationError as e:
    print(f"Validation error: {e}")
```

### Context Managers

```python
from pysd.validation import strict_validation, permissive_validation, no_validation

# Temporary strict validation
with strict_validation():
    greco = GRECO(...)  # All validation issues will raise errors

# Temporary permissive validation  
with permissive_validation():
    greco = GRECO(...)  # Only critical issues will raise errors

# Disable validation temporarily
with no_validation():
    greco = GRECO(id="INVALID", ...)  # No validation errors will raise
```

## 📋 Detailed API Reference

### Validation Modes

#### `ValidationMode.STRICT`
- **Behavior**: All validation issues raise exceptions
- **Use Case**: Development mode, unit testing
- **Example**:
```python
set_validation_mode(ValidationMode.STRICT)
greco = GRECO(id="ABC", ...)  # Raises PySDValidationError for invalid ID
```

#### `ValidationMode.NORMAL` (Default)
- **Behavior**: Only ERROR severity raises exceptions
- **Use Case**: Production mode, normal operations
- **Example**:
```python
set_validation_mode(ValidationMode.NORMAL)
greco = GRECO(id="ABC", ...)  # Raises PySDValidationError for invalid ID
# Hypothetical warning would not raise but would be logged
```

#### `ValidationMode.PERMISSIVE`
- **Behavior**: Only critical errors raise exceptions
- **Use Case**: Data migration, legacy data processing
- **Example**:
```python
set_validation_mode(ValidationMode.PERMISSIVE)
greco = GRECO(id="ABC", ...)  # May or may not raise depending on criticality
```

#### `ValidationMode.DISABLED`
- **Behavior**: No validation errors raise exceptions
- **Use Case**: Bulk data imports, debugging, emergency operations
- **Example**:
```python
set_validation_mode(ValidationMode.DISABLED)
greco = GRECO(id="INVALID", ...)  # No errors raised, but validation info still collected
```

### Global Configuration Functions

#### `set_validation_mode(mode)`
Set the global validation mode.

```python
from pysd.validation import set_validation_mode, ValidationMode

set_validation_mode(ValidationMode.STRICT)
set_validation_mode("strict")  # String version also supported
```

#### `get_validation_mode()`
Get the current validation mode.

```python
from pysd.validation import get_validation_mode

current_mode = get_validation_mode()
print(f"Current mode: {current_mode}")
```

#### `disable_validation_rule(rule_code)`
Disable a specific validation rule globally.

```python
from pysd.validation import disable_validation_rule

disable_validation_rule("GRECO-ID-001")  # Disable GRECO ID validation
greco = GRECO(id="ABC", ...)  # Invalid ID allowed
```

#### `enable_validation_rule(rule_code)`
Re-enable a previously disabled validation rule.

```python
from pysd.validation import enable_validation_rule

enable_validation_rule("GRECO-ID-001")  # Re-enable GRECO ID validation
```

#### `set_rule_severity_threshold(rule_code, min_severity)`
Set minimum severity for a rule to raise errors.

```python
from pysd.validation import set_rule_severity_threshold, ValidationSeverity

# Only raise for WARNING or ERROR severity for this rule
set_rule_severity_threshold("GRECO-BAS-001", ValidationSeverity.WARNING)
set_rule_severity_threshold("GRECO-BAS-001", "warning")  # String version
```

### Context Managers

#### `strict_validation()`
Temporarily enable strict validation mode.

```python
from pysd.validation import strict_validation

with strict_validation():
    # All validation issues will raise exceptions in this block
    greco = GRECO(...)
# Returns to previous validation mode
```

#### `permissive_validation()`
Temporarily enable permissive validation mode.

```python
from pysd.validation import permissive_validation

with permissive_validation():
    # Only critical issues will raise exceptions
    greco = GRECO(...)
```

#### `no_validation()`
Temporarily disable all validation.

```python
from pysd.validation import no_validation

with no_validation():
    # No validation errors will raise exceptions
    greco = GRECO(id="COMPLETELY_INVALID", ...)
```

#### `validation_mode_context(mode)`
Generic context manager for any validation mode.

```python
from pysd.validation import validation_mode_context, ValidationMode

with validation_mode_context(ValidationMode.DISABLED):
    # Specific mode for this block
    greco = GRECO(...)
```

### Exception Handling

#### `PySDValidationError`
Custom validation exception with additional information.

```python
from pysd.validation import PySDValidationError

try:
    greco = GRECO(id="ABC", ...)
except PySDValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Error code: {e.code}")
    print(f"Location: {e.location}")
    print(f"Suggestion: {e.suggestion}")
    print(f"Severity: {e.severity}")
    
    # Access all validation issues
    for issue in e.validation_issues:
        print(f"Issue: {issue.message}")
```

## 🛠️ Real-World Usage Scenarios

### Development Mode
Use strict validation to catch all issues early:

```python
from pysd.validation import strict_validation

def test_greco_creation():
    with strict_validation():
        # All validation issues will raise errors
        greco = GRECO(id="A", bas=Cases(ranges=[1, 2, 3, 4, 5, 6]))
        assert greco.id == "A"
```

### Production Mode
Use normal validation for robust error handling:

```python
from pysd.validation import set_validation_mode, ValidationMode

# Set normal mode for production
set_validation_mode(ValidationMode.NORMAL)

def create_greco_safely(id_val, bas_data):
    try:
        return GRECO(id=id_val, bas=bas_data)
    except PySDValidationError as e:
        # Log error and return None or default
        logger.error(f"Invalid GRECO data: {e}")
        return None
```

### Data Migration
Disable validation for bulk imports:

```python
from pysd.validation import no_validation

def migrate_legacy_data(legacy_grecos):
    with no_validation():
        migrated = []
        for legacy_greco in legacy_grecos:
            # Even invalid data will be processed
            greco = GRECO(
                id=legacy_greco.get('id', 'X'),  # May be invalid
                bas=legacy_greco.get('bas', [])
            )
            migrated.append(greco)
        return migrated
```

### Rule-Specific Control
Disable specific problematic rules:

```python
from pysd.validation import disable_validation_rule, enable_validation_rule

# Temporarily disable strict ID validation for legacy data
disable_validation_rule("GRECO-ID-001")

try:
    # Process data with relaxed ID validation
    for data in legacy_data:
        greco = GRECO(id=data['id'], bas=data['bas'])
        process_greco(greco)
finally:
    # Always re-enable the rule
    enable_validation_rule("GRECO-ID-001")
```

### Testing Different Severity Levels
Set custom thresholds for testing:

```python
from pysd.validation import set_rule_severity_threshold, ValidationSeverity

# Make BAS count issues only raise on WARNING or higher
set_rule_severity_threshold("GRECO-BAS-001", ValidationSeverity.WARNING)

# Test with relaxed BAS count validation
greco = GRECO(id="A", bas=Cases(ranges=[1, 2, 3, 4, 5, 6, 7]))  # May not raise
```

## 🔧 Available Error Codes

### GRECO Validation Codes
- **GRECO-ID-001**: Invalid GRECO ID format
- **GRECO-BAS-001**: Invalid BAS count or format  
- **GRECO-ELC-001**: Invalid ELC cross-reference
- **GRECO-CONTAINER-001**: Duplicate GRECO ID in container

### Using Error Codes
```python
from pysd.validation import disable_validation_rule
from pysd.validation.error_codes import ErrorCodes

# Disable using class constant
disable_validation_rule(ErrorCodes.GRECO_ID_INVALID)

# Or using string directly
disable_validation_rule("GRECO-ID-001")
```

## 🎯 Best Practices

### 1. **Choose the Right Mode for Your Context**
- **Development**: Use `STRICT` to catch all issues early
- **Production**: Use `NORMAL` for balanced error handling
- **Data Migration**: Use `DISABLED` or `PERMISSIVE` for flexibility
- **Testing**: Use context managers for isolated test scenarios

### 2. **Use Context Managers for Temporary Changes**
```python
# Good: Temporary change with automatic restoration
with no_validation():
    process_legacy_data()

# Avoid: Manual mode changes that might not be restored
set_validation_mode(ValidationMode.DISABLED)
process_legacy_data()
# Easy to forget to restore mode!
```

### 3. **Handle PySDValidationError Appropriately**
```python
# Good: Specific error handling
try:
    greco = GRECO(...)
except PySDValidationError as e:
    # Handle validation errors specifically
    log_validation_error(e)
    return default_greco()
except Exception as e:
    # Handle other errors
    log_system_error(e)
    raise
```

### 4. **Use Rule-Specific Controls Sparingly**
```python
# Good: Temporary rule disabling with restoration
disable_validation_rule("GRECO-ID-001")
try:
    process_special_case()
finally:
    enable_validation_rule("GRECO-ID-001")

# Avoid: Permanently disabling rules without good reason
disable_validation_rule("GRECO-ID-001")  # Never re-enabled
```

### 5. **Log Validation Issues Even When Not Raising**
The validation system still collects validation information even when not raising errors. Consider implementing logging to capture these issues:

```python
from pysd.validation import ValidationContext, no_validation

with no_validation():
    context = ValidationContext()
    greco = GRECO(...)
    
    # Even with validation disabled, you can still check for issues
    issues = context.get_issues()
    for issue in issues:
        logger.warning(f"Validation issue (not raised): {issue.message}")
```

## 🚨 Thread Safety

The validation configuration is **thread-safe** and uses a singleton pattern with proper locking. You can safely use the validation system in multi-threaded applications:

```python
import threading
from pysd.validation import set_validation_mode, ValidationMode

def worker_thread():
    # Safe to call from multiple threads
    set_validation_mode(ValidationMode.STRICT)
    # Process data...

# Start multiple threads
threads = [threading.Thread(target=worker_thread) for _ in range(10)]
for t in threads:
    t.start()
```

## 📚 Migration Guide

### From Previous Validation System
If you were using direct `ValueError` catching:

```python
# Old way
try:
    greco = GRECO(id="ABC", ...)
except ValueError as e:
    handle_error(e)

# New way
try:
    greco = GRECO(id="ABC", ...)
except PySDValidationError as e:
    handle_validation_error(e)  # More specific handling
except ValueError as e:
    handle_other_error(e)       # Other value errors
```

### Adding Validation Control to Existing Code
```python
# Before: Fixed validation behavior
def create_greco(data):
    return GRECO(**data)  # Always raises on invalid data

# After: Configurable validation behavior
def create_greco(data, strict=True):
    if strict:
        with strict_validation():
            return GRECO(**data)
    else:
        with permissive_validation():
            return GRECO(**data)
```

## 🔍 Debugging and Troubleshooting

### Check Current Configuration
```python
from pysd.validation import get_validation_mode, validation_config

print(f"Current mode: {get_validation_mode()}")
print(f"Disabled rules: {validation_config._disabled_rules}")
print(f"Custom thresholds: {validation_config._custom_thresholds}")
```

### Test Validation Behavior
```python
from pysd.validation import set_validation_mode, ValidationMode, PySDValidationError

# Test if validation is working
set_validation_mode(ValidationMode.NORMAL)
try:
    greco = GRECO(id="INVALID", ...)
    print("ERROR: Validation not working!")
except PySDValidationError:
    print("SUCCESS: Validation working correctly")
```

### Reset to Default State
```python
from pysd.validation import set_validation_mode, ValidationMode, validation_config

# Reset to default configuration
set_validation_mode(ValidationMode.NORMAL)
validation_config._disabled_rules.clear()
validation_config._custom_thresholds.clear()
```

## 🎉 Summary

The PySD validation system provides powerful, flexible control over when and how validation errors are raised. By choosing the appropriate validation mode and using context managers, you can adapt the validation behavior to match your specific use case - from strict development testing to flexible data migration scenarios.

Key takeaways:
- Use **global modes** to set overall validation behavior
- Use **context managers** for temporary validation changes  
- Use **rule-specific controls** for fine-tuned validation behavior
- Handle **PySDValidationError** specifically for better error management
- Choose the **right mode** for your development context

This system ensures that PySD can be both robust in production and flexible during development and data migration tasks.