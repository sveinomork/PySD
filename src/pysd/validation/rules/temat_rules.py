"""All validation rules for RMPEC statements."""

from typing import List, TYPE_CHECKING


from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule

if TYPE_CHECKING:
    from ...statements.temat import TEMAT


# Instance-level validation rules (run during object creation)
@instance_rule("TEMAT")
def validate_temat_id_range(
    obj: "TEMAT", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate TEMAT ID is within valid range."""
    if not (1 <= obj.id <= 99999999):
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="TEMAT-ID-001",
                message=f"TEMAT ID {obj.id} must be between 1 and 99999999",
                location=f"TEMAT.{obj.id}",
                suggestion="Use an ID between 1 and 99999999",
            )
        ]
    return []


@instance_rule("TEMAT")
def validate_temat_positive_values(
    obj: "TEMAT", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that material properties are positive."""
    issues = []

    if obj.fsy is None:
        return []

    if obj.fsy <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="TEMAT-DEN-001",
                message=f"TEMAT density {obj.fsy} must be positive",
                location=f"TEMAT.{obj.id}.fsy",
                suggestion="Use a positive density value (typically around 7850 kg/m3 for steel)",
            )
        )

    # Check material factors
    for factor, name in [(obj.mfu, "MFU"), (obj.mfa, "MFA"), (obj.mfs, "MFS")]:
        if factor is not None and factor <= 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code=f"TEMAT-{name}-001",
                    message=f"TEMAT {name} {factor} must be positive",
                    location=f"TEMAT.{obj.id}.{name.lower()}",
                    suggestion=f"Use a positive value for {name} (typically around 1.0-1.2)",
                )
            )

    # Check optional strength values if provided
    if obj.esk is not None and obj.esk <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="TEMAT-ESK-001",
                message=f"TEMAT equivalent stress {obj.esk} must be positive",
                location=f"TEMAT.{obj.id}.esk",
                suggestion="Use a positive modules of elasticity value",
            )
        )

    return issues


# Container-level validation rules (run when adding to container)
@container_rule("TEMAT")
def validate_temat_uniqueness(
    obj: "TEMAT", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate TEMAT ID uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.id):
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="TEMAT-DUP-001",
                message=f"Duplicate TEMAT ID {obj.id} found",
                location=f"TEMAT.{obj.id}",
                suggestion="Use a unique TEMAT ID",
            )
        ]
    return []
