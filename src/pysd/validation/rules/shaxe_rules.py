"""All validation rules for SHAXE statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.shaxe import SHAXE


# Instance-level validation rules (run during object creation)
@instance_rule("SHAXE")
def validate_shaxe_pa_required(
    obj: "SHAXE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate PA (part name) is provided and non-empty."""
    if not obj.pa or not obj.pa.strip():
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-PA-001",
                message="SHAXE PA (part name) is required and cannot be empty",
                location=f"SHAXE.{getattr(obj, 'key', 'unknown')}.pa",
                suggestion="Provide a valid part name for the PA parameter",
            )
        ]
    return []


@instance_rule("SHAXE")
def validate_shaxe_mode_exclusive(
    obj: "SHAXE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that exactly one of the three modes is active."""
    mode1 = all([obj.x1, obj.x2, obj.x3])
    mode2 = all([obj.xp, obj.xa])
    mode3 = all([obj.xc, obj.xa])

    mode_count = sum([mode1, mode2, mode3])

    if mode_count == 0:
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-MODE-001",
                message="SHAXE must use one of three modes: (X1/X2/X3), (XP/XA), or (XC/XA)",
                location=f"SHAXE.{getattr(obj, 'key', 'unknown')}",
                suggestion="Define one complete set: X1+X2+X3, or XP+XA, or XC+XA",
            )
        ]

    if mode_count > 1:
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-MODE-002",
                message="SHAXE modes are mutually exclusive - only one mode may be used",
                location=f"SHAXE.{getattr(obj, 'key', 'unknown')}",
                suggestion="Use only one mode: either X1+X2+X3, or XP+XA, or XC+XA",
            )
        ]

    return []


@instance_rule("SHAXE")
def validate_shaxe_section_ranges(
    obj: "SHAXE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate FS and HS section ranges."""
    issues = []

    if obj.fs and obj.fs[0] > obj.fs[1]:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-FS-001",
                message=f"SHAXE FS range invalid: start {obj.fs[0]} > end {obj.fs[1]}",
                location=f"SHAXE.{getattr(obj, 'key', 'unknown')}.fs",
                suggestion="Ensure FS start index ≤ end index",
            )
        )

    if obj.hs and obj.hs[0] > obj.hs[1]:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-HS-001",
                message=f"SHAXE HS range invalid: start {obj.hs[0]} > end {obj.hs[1]}",
                location=f"SHAXE.{getattr(obj, 'key', 'unknown')}.hs",
                suggestion="Ensure HS start index ≤ end index",
            )
        )

    return issues


# Container-level validation rules (run when adding to container)
@container_rule("SHAXE")
def validate_shaxe_uniqueness(
    obj: "SHAXE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate SHAXE key uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.key):
        return [
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-DUP-001",
                message=f"Duplicate SHAXE key '{obj.key}' found",
                location=f"SHAXE.{obj.key}",
                suggestion="Use a unique combination of PA, FS, and HS",
            )
        ]
    return []


# Model-level validation rules (run when adding to SD_BASE - cross-container)
@model_rule("SHAXE")
def validate_pa_exists_in_shsec(
    obj: "SHAXE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that PA references an existing part name in SHSEC statements."""
    issues = []

    if not context.full_model:
        return issues

    shsec_container = getattr(context.full_model, "shsec", None)
    if not shsec_container:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-PA-NO-CONTAINER",
                message=f"SHAXE {obj.key} references PA '{obj.pa}' but no SHSEC container exists",
                location=f"SHAXE.{obj.key}.pa",
                suggestion="Add SHSEC statements before adding SHAXE with PA references",
            )
        )
        return issues

    # Check if PA exists in any SHSEC statement
    pa_exists = any(shsec.pa == obj.pa for shsec in shsec_container)

    if not pa_exists:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHAXE-PA-REF-001",
                message=f"SHAXE {obj.key} references non-existent part '{obj.pa}' in SHSEC",
                location=f"SHAXE.{obj.key}.pa",
                suggestion=f"Add SHSEC with PA '{obj.pa}' before referencing it in SHAXE",
            )
        )

    return issues
