"""All validation rules for CMPEC statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.cmpec import CMPEC

# Instance-level validation rules (run during object creation)
@instance_rule('CMPEC')
def validate_cmpec_id_range(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CMPEC ID is within valid range."""
    if obj.id is not None and not (1 <= obj.id <= 99999999):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CMPEC-ID-001",
            message=f"CMPEC ID {obj.id} must be between 1 and 99999999",
            location=f'CMPEC.{obj.id}',
            suggestion='Use an ID between 1 and 99999999'
        )]
    return []

@instance_rule('CMPEC')
def validate_cmpec_concrete_grade(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate concrete grade format and range."""
    issues = []
    if obj.gr is not None:
        if not obj.gr.startswith('B'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="CMPEC-GR-001",
                message=f"CMPEC concrete grade '{obj.gr}' must start with 'B'",
                location=f'CMPEC.{obj.id}.gr',
                suggestion="Use format like 'B25', 'B35', etc."
            ))
        else:
            try:
                grade = int(obj.gr[1:])
                if not (12 <= grade <= 90):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR.value,
                        code="CMPEC-GR-002",
                        message=f"CMPEC concrete grade {grade} must be between 12 and 90",
                        location=f'CMPEC.{obj.id}.gr',
                        suggestion='Use a grade between B12 and B90'
                    ))
            except ValueError:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="CMPEC-GR-003",
                    message=f"CMPEC concrete grade '{obj.gr}' has invalid format",
                    location=f'CMPEC.{obj.id}.gr',
                    suggestion="Use format like 'B25', 'B35', etc."
                ))
    return issues

@instance_rule('CMPEC')
def validate_cmpec_density_range(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate density range for lightweight concrete."""
    if obj.rh is not None and not (1150 <= obj.rh <= 2150):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CMPEC-RH-001",
            message=f"CMPEC density {obj.rh} kg/m3 must be between 1150 and 2150 for lightweight concrete",
            location=f'CMPEC.{obj.id}.rh',
            suggestion='Use density between 1150 and 2150 kg/m3'
        )]
    return []

@instance_rule('CMPEC')
def validate_cmpec_part_name(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate structural part name length."""
    if obj.pa is not None and len(obj.pa) > 8:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CMPEC-PA-001",
            message=f"CMPEC part name '{obj.pa}' exceeds 8 character limit (has {len(obj.pa)})",
            location=f'CMPEC.{obj.id}.pa',
            suggestion='Use a part name with 8 characters or fewer'
        )]
    return []

# Container-level validation rules (run when adding to container)
@container_rule('CMPEC')
def validate_cmpec_uniqueness(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CMPEC ID uniqueness in container."""
    if obj.id is not None and context.parent_container and context.parent_container.contains(obj.id):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CMPEC-DUP-001",
            message=f"Duplicate CMPEC ID {obj.id} found",
            location=f'CMPEC.{obj.id}',
            suggestion='Use a unique CMPEC ID'
        )]
    return []

# Model-level validation rules (run when adding to SD_BASE - cross-container)
@model_rule('CMPEC')
def validate_cmpec_part_references(obj: 'CMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that PA references exist in SHSEC statements."""
    issues = []
    
    if not context.full_model or not obj.pa:
        return issues
    
    shsec_container = getattr(context.full_model, 'shsec', None)
    if not shsec_container:
        if obj.pa:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="CMPEC-PA-NO-CONTAINER",
                message=f"CMPEC {obj.id} references PA '{obj.pa}' but no SHSEC container exists",
                location=f"CMPEC.{obj.id}.pa",
                suggestion="Add SHSEC statements before adding CMPEC with PA references"
            ))
        return issues
    
    # Check if PA exists in any SHSEC statement
    pa_exists = any(shsec.pa == obj.pa for shsec in shsec_container)
    
    if not pa_exists:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING.value,
            code="CMPEC-PA-REF-001",
            message=f"CMPEC {obj.id} references non-existent part '{obj.pa}' in SHSEC",
            location=f"CMPEC.{obj.id}.pa",
            suggestion=f"Add SHSEC with PA '{obj.pa}' before referencing it in CMPEC"
        ))
    
    return issues
