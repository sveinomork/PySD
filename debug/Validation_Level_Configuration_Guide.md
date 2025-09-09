# Validation Level Configuration Guide for PySD

## Overview
The PySD validation system provides multiple levels of validation control that you can configure in your `main.py` file. The system supports global validation modes, rule-specific controls, and temporary validation contexts.

## Available Validation Modes

### 1. **STRICT Mode** (Default for Model Validation)
- Raises exceptions for all validation issues (errors, warnings, info)
- Strictest validation level
- Recommended for development and testing

### 2. **NORMAL Mode** (Default Global Mode)
- Raises exceptions only for ERROR severity issues
- Warnings and info messages are logged but don't stop execution
- Good balance for production use

### 3. **PERMISSIVE Mode**
- Only raises exceptions for critical system errors
- Most validation issues are logged but don't stop execution
- Useful for importing legacy data with known issues

### 4. **DISABLED Mode**
- No validation errors raise exceptions
- All validation is performed but only logged
- Useful for batch operations or debugging

## How to Configure Validation in main.py

### Method 1: Import and Set Global Validation Mode

```python
from src.pysd.validation import set_validation_mode, ValidationMode
from src.pysd.sdmodel import SD_BASE

# Set global validation mode at the start of your script
set_validation_mode(ValidationMode.PERMISSIVE)  # or "permissive"

def main(output_file: str = r"tutorial.inp") -> None:
    with SD_BASE.create_writer(output_file) as sd_model:
        # Your model creation code here
        create_basic_model_components(sd_model)
        # ... rest of your code
```

### Method 2: Use Context Managers for Temporary Validation Changes

```python
from src.pysd.validation import strict_validation, permissive_validation, no_validation
from src.pysd.sdmodel import SD_BASE

def main(output_file: str = r"tutorial.inp") -> None:
    with SD_BASE.create_writer(output_file) as sd_model:
        
        # Use strict validation for critical components
        with strict_validation():
            create_basic_model_components(sd_model)
        
        # Use permissive validation for experimental features
        with permissive_validation():
            create_design_sections(sd_model)
        
        # Disable validation for bulk operations
        with no_validation():
            create_load_components(sd_model)
```

### Method 3: Disable Validation in SD_BASE

```python
from src.pysd.sdmodel import SD_BASE

def main(output_file: str = r"tutorial.inp") -> None:
    # Create writer with validation disabled
    with SD_BASE.create_writer(output_file, validation_enabled=False) as sd_model:
        # Your model creation code here
        create_basic_model_components(sd_model)
        # ... rest of your code
    
    # OR use the validation context manager
    with SD_BASE.create_writer(output_file) as sd_model:
        with sd_model.validation_disabled():
            # Bulk operations without validation
            create_load_components(sd_model)
```

### Method 4: Fine-Grained Rule Control

```python
from src.pysd.validation import disable_validation_rule, set_rule_severity_threshold, ValidationSeverity
from src.pysd.sdmodel import SD_BASE

def main(output_file: str = r"tutorial.inp") -> None:
    # Disable specific validation rules
    disable_validation_rule("RFILE_DUPLICATE_WARNING")
    disable_validation_rule("FILST_DUPLICATE_NAME_WARNING")
    
    # Set custom severity thresholds for specific rules
    set_rule_severity_threshold("LOADC_MISSING_TABLE", ValidationSeverity.WARNING)
    
    with SD_BASE.create_writer(output_file) as sd_model:
        # Your model creation code here
        create_basic_model_components(sd_model)
```

## Complete Example for Your main.py

Here's how to modify your current `main.py` to include validation level configuration:

```python
from src.pysd.statements import (
    DESEC, RFILE, SHAXE, LOADC, GRECO, FILST, BASCO, LoadCase,
    RETYP, DECAS, RELOC, EXECD, LORES, CMPEC, SHSEC, XTFIL,
    TABLE, RMPEC, CaseBuilder, Cases
)
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode, permissive_validation, no_validation
from pysd.helpers import create_axes_based_on_3_points_in_plane
from shapely.geometry import Point

# Set global validation mode for the entire script
set_validation_mode(ValidationMode.NORMAL)  # Options: STRICT, NORMAL, PERMISSIVE, DISABLED

def create_basic_model_components(sd_model: SD_BASE) -> None:
    """Create and add basic model components like FILST and RFILE."""
    # Add FILST entry
    filst_entry = FILST(
        name="aquapod",
        vers="1.0", 
        date="14.aug-2025",
        resp="som"
    )
    sd_model.add(filst_entry)

    # Add RFILE entry
    rfile_definition = RFILE(
        pre=r"C:\Users\nx74\Work\ShellDesign1\AquaPod_09\Analyse_file",
        fnm="R1",
        suf="SIN",
        typ="SHE",
    )
    sd_model.add(rfile_definition)

# ... (your other functions remain the same)

def main(output_file: str = r"tutorial.inp") -> None:
    """Main function to create and write the model."""
    print(f"Building model to be written to {output_file}...")
    
    with SD_BASE.create_writer(output_file) as sd_model:
        # Use different validation levels for different parts
        
        # Strict validation for basic components
        create_basic_model_components(sd_model)
        
        # Permissive validation for experimental design sections
        with permissive_validation():
            # create_design_sections(sd_model)  # Uncommented when ready
            pass
        
        # Normal validation for load components
        create_load_components(sd_model)
        
        # No validation for bulk operations that might have known issues
        with no_validation():
            # create_material_components(sd_model)
            # create_reinforment_components(sd_model) 
            # create_analysis_components(sd_model)
            pass
             
    print(f"Model successfully written to {output_file}")

if __name__ == "__main__":
    main()
```

## Validation Level Recommendations

### For Development/Testing:
- Use `ValidationMode.STRICT` to catch all issues early
- Enable all validation rules for comprehensive checking

### For Production:
- Use `ValidationMode.NORMAL` for balanced validation
- Disable warning-only rules that are not critical

### For Legacy Data Import:
- Use `ValidationMode.PERMISSIVE` or `DISABLED`
- Selectively enable only critical error rules

### For Batch Operations:
- Use `no_validation()` context manager temporarily
- Re-enable validation after bulk operations complete

## Checking Validation Status

You can also check the current validation status and get summaries:

```python
from src.pysd.validation import get_validation_mode

def main(output_file: str = r"tutorial.inp") -> None:
    print(f"Current validation mode: {get_validation_mode()}")
    
    with SD_BASE.create_writer(output_file) as sd_model:
        create_basic_model_components(sd_model)
        
        # Get validation summary
        summary = sd_model.get_validation_summary()
        print(f"Validation summary: {summary}")
        
        # Check for validation issues
        integrity = sd_model.validate_integrity()
        if integrity['errors']:
            print(f"Found {len(integrity['errors'])} validation errors")
        if integrity['warnings']:
            print(f"Found {len(integrity['warnings'])} validation warnings")
```

This gives you complete control over validation behavior in your PySD models while maintaining the benefits of the validation system when you need it.