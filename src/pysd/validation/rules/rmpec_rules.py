
"""All validation rules for RMPEC statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.rmpec import RMPEC

# Instance-level validation rules (run during object creation)
@instance_rule('RMPEC')
def validate_rmpec_id_range(obj: 'RMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate RMPEC ID is within valid range."""
    if not (1 <= obj.id <= 99999999):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="RMPEC-ID-001",
            message=f"RMPEC ID {obj.id} must be between 1 and 99999999",
            location=f'RMPEC.{obj.id}',
            suggestion='Use an ID between 1 and 99999999'
        )]
    return []

@instance_rule('RMPEC')
def validate_rmpec_positive_values(obj: 'RMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that material properties are positive."""
    issues = []
    
    # Check density
    if obj.den <= 0:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="RMPEC-DEN-001",
            message=f"RMPEC density {obj.den} must be positive",
            location=f'RMPEC.{obj.id}.den',
            suggestion='Use a positive density value (typically around 7850 kg/m3 for steel)'
        ))
    
    # Check material factors
    for factor, name in [(obj.mfu, 'MFU'), (obj.mfa, 'MFA'), (obj.mfs, 'MFS')]:
        if factor <= 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code=f"RMPEC-{name}-001",
                message=f"RMPEC {name} {factor} must be positive",
                location=f'RMPEC.{obj.id}.{name.lower()}',
                suggestion=f'Use a positive value for {name} (typically around 1.0-1.2)'
            ))
    
    # Check optional strength values if provided
    if obj.fyk is not None and obj.fyk <= 0:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="RMPEC-FYK-001",
            message=f"RMPEC yield strength {obj.fyk} must be positive",
            location=f'RMPEC.{obj.id}.fyk',
            suggestion='Use a positive yield strength value'
        ))
    
    if obj.fsk is not None and obj.fsk <= 0:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="RMPEC-FSK-001",
            message=f"RMPEC ultimate strength {obj.fsk} must be positive",
            location=f'RMPEC.{obj.id}.fsk',
            suggestion='Use a positive ultimate strength value'
        ))
    
    return issues

@instance_rule('RMPEC')
def validate_rmpec_strength_relationship(obj: 'RMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that ultimate strength >= yield strength."""
    if obj.fyk is not None and obj.fsk is not None and obj.fsk < obj.fyk:
        return [ValidationIssue(
            severity=ValidationSeverity.WARNING.value,
            code="RMPEC-STR-001",
            message=f"RMPEC ultimate strength ({obj.fsk}) should be >= yield strength ({obj.fyk})",
            location=f'RMPEC.{obj.id}',
            suggestion='Ensure FSK >= FYK for realistic material properties'
        )]
    return []

# Container-level validation rules (run when adding to container)
@container_rule('RMPEC')
def validate_rmpec_uniqueness(obj: 'RMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate RMPEC ID uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.id):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="RMPEC-DUP-001",
            message=f"Duplicate RMPEC ID {obj.id} found",
            location=f'RMPEC.{obj.id}',
            suggestion='Use a unique RMPEC ID'
        )]
    return []

# Model-level validation rules (run when adding to SD_BASE - cross-container)
@model_rule('RMPEC')
def validate_rmpec_usage_in_retyp(obj: 'RMPEC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that RMPEC is referenced by RETYP statements."""
    issues = []
    
    if not context.full_model:
        return issues
    
    # Check if this RMPEC is referenced by any RETYP
    retyp_container = getattr(context.full_model, 'retyp', None)
    if retyp_container:
        # RETYP references RMPEC through the 'mp' field
        rmpec_used = any(retyp.mp == obj.id for retyp in retyp_container.items if hasattr(retyp, 'mp'))
        
        if not rmpec_used:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO.value,
                code="RMPEC-USAGE-001",
                message=f"RMPEC {obj.id} is not referenced by any RETYP statement",
                location=f"RMPEC.{obj.id}",
                suggestion=f"Consider adding RETYP with MP={obj.id} to use this material property"
            ))
    
    return issues

