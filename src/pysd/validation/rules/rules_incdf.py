"""All validation rules for FILST statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, model_rule

if TYPE_CHECKING:
    from ...statements.filst import FILST

# Instance-level validation rules (run during object creation)
@instance_rule('FILST')
def validate_filst_parameter_exclusivity(obj: 'FILST', context: ValidationContext) -> List[ValidationIssue]:
    """Validate FILST parameter exclusivity (PRI vs other parameters)."""
    issues = []
    
    # When pri=True, no other parameters should be set
    if obj.pri:
        other_params = [obj.name, obj.vers, obj.date, obj.resp]
        if any(param is not None for param in other_params):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="FILST-PRI-001",
                message="FILST with PRI=True cannot have other parameters (NAME, VERS, DATE, RESP)",
                location='FILST.pri',
                suggestion='Remove other parameters when using PRI=True'
            ))
    
    # When pri=False, name is required (will use default "sd" if None)
    elif not obj.pri and obj.name is None:
        # This is actually OK since we'll use default "sd" - no error needed
        pass
    
    return issues

@instance_rule('FILST')
def validate_filst_field_lengths(obj: 'FILST', context: ValidationContext) -> List[ValidationIssue]:
    """Validate FILST field length constraints."""
    issues = []
    
    # NAME max 48 characters
    if obj.name is not None and len(obj.name) > 48:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="FILST-NAME-002",
            message=f"FILST NAME '{obj.name}' exceeds 48 character limit (has {len(obj.name)})",
            location='FILST.name',
            suggestion='Use a shorter name (max 48 characters)'
        ))
    
    # VERS max 8 characters
    if obj.vers is not None and len(obj.vers) > 8:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="FILST-VERS-001",
            message=f"FILST VERS '{obj.vers}' exceeds 8 character limit (has {len(obj.vers)})",
            location='FILST.vers',
            suggestion='Use a shorter version string (max 8 characters)'
        ))
    
    # DATE max 12 characters
    if obj.date is not None and len(obj.date) > 12:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="FILST-DATE-001",
            message=f"FILST DATE '{obj.date}' exceeds 12 character limit (has {len(obj.date)})",
            location='FILST.date',
            suggestion='Use a shorter date string (max 12 characters)'
        ))
    
    # RESP max 4 characters
    if obj.resp is not None and len(obj.resp) > 4:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="FILST-RESP-001",
            message=f"FILST RESP '{obj.resp}' exceeds 4 character limit (has {len(obj.resp)})",
            location='FILST.resp',
            suggestion='Use a shorter responsible person code (max 4 characters)'
        ))
    
    return issues

@instance_rule('FILST')
def validate_filst_field_content(obj: 'FILST', context: ValidationContext) -> List[ValidationIssue]:
    """Validate FILST field content and format."""
    issues = []
    
    # NAME should not be empty if provided
    if obj.name is not None and len(obj.name.strip()) == 0:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="FILST-NAME-003",
            message="FILST NAME cannot be empty",
            location='FILST.name',
            suggestion='Provide a non-empty name or set PRI=True'
        ))
    
    # VERS format validation (optional)
    if obj.vers is not None and len(obj.vers.strip()) == 0:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING.value,
            code="FILST-VERS-002",
            message="FILST VERS is empty",
            location='FILST.vers',
            suggestion='Provide a version string or remove VERS parameter'
        ))
    
    return issues

# Model-level validation rules (run when adding to SD_BASE)
@model_rule('FILST')
def validate_filst_model_consistency(obj: 'FILST', context: ValidationContext) -> List[ValidationIssue]:
    """Validate FILST consistency within the model."""
    issues = []
    
    if not context.full_model:
        return issues
    
    # Check for multiple PRI=True statements
    existing_filsts = getattr(context.full_model, 'filst', [])
    if obj.pri:
        pri_count = sum(1 for f in existing_filsts if getattr(f, 'pri', False))
        if pri_count > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="FILST-PRI-002",
                message=f"Model already has {pri_count} FILST statement(s) with PRI=True",
                location='FILST.pri',
                suggestion='Consider if multiple PRI statements are necessary'
            ))
    
    # Check for duplicate names
    if obj.name is not None:
        existing_names = [getattr(f, 'name', None) for f in existing_filsts if not getattr(f, 'pri', False)]
        if obj.name in existing_names:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="FILST-NAME-004",
                message=f"FILST NAME '{obj.name}' already exists in model",
                location='FILST.name',
                suggestion='Use a unique name for each FILST entry'
            ))
    
    return issues