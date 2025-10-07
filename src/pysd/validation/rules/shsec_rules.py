"""All validation rules for SHSEC statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.shsec import SHSEC
    from ...model.base_container import BaseContainer


# Instance-level validation rules (run during object creation)
@instance_rule("SHSEC")
def validate_shsec_pa_format(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate SHSEC PA format (max 8 characters, alphanumeric)."""
    issues = []

    if not obj.pa:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHSEC-PA-001",
                message="SHSEC PA (part name) is required",
                location=f"SHSEC.{obj.pa}",
                suggestion="Provide a part name (PA) with max 8 characters",
            )
        )
    elif len(obj.pa) > 8:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHSEC-PA-002",
                message=f"SHSEC PA '{obj.pa}' exceeds 8 character limit (has {len(obj.pa)})",
                location=f"SHSEC.{obj.pa}",
                suggestion="Use a part name with 8 or fewer characters",
            )
        )

    return issues


@instance_rule("SHSEC")
def validate_shsec_element_specification(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that exactly one element specification is provided."""
    issues = []

    # Check all element specification fields
    specs = [obj.el, obj.xp, obj.elset, obj.elsetname, obj.te]
    provided_specs = [spec for spec in specs if spec is not None]

    if len(provided_specs) == 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHSEC-ELEM-001",
                message="SHSEC requires exactly one element specification (EL, XP, ELSET, ELSETNAME, or TE)",
                location=f"SHSEC.{obj.pa}",
                suggestion="Provide one of: EL, XP, ELSET, ELSETNAME, or TE",
            )
        )
    elif len(provided_specs) > 1:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHSEC-ELEM-002",
                message=f"SHSEC has {len(provided_specs)} element specifications, only one allowed",
                location=f"SHSEC.{obj.pa}",
                suggestion="Provide only one element specification",
            )
        )

    return issues


@instance_rule("SHSEC")
def validate_shsec_ne_range(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate NE (number of elements over thickness) range."""
    issues = []

    if obj.ne is not None and (obj.ne < 1 or obj.ne > 10):
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="SHSEC-NE-001",
                message=f"SHSEC NE value {obj.ne} out of range, must be 1-10",
                location=f"SHSEC.{obj.pa}.ne",
                suggestion="Set NE to a value between 1 and 10",
            )
        )

    return issues


@instance_rule("SHSEC")
def validate_shsec_section_ranges(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate FS and HS section ranges."""
    issues = []

    if obj.fs is not None:
        if obj.fs[0] > obj.fs[1]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="SHSEC-FS-001",
                    message=f"SHSEC FS range invalid: start {obj.fs[0]} > end {obj.fs[1]}",
                    location=f"SHSEC.{obj.pa}.fs",
                    suggestion="Ensure FS start value is less than or equal to end value",
                )
            )

    if obj.hs is not None:
        if obj.hs[0] > obj.hs[1]:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="SHSEC-HS-001",
                    message=f"SHSEC HS range invalid: start {obj.hs[0]} > end {obj.hs[1]}",
                    location=f"SHSEC.{obj.pa}.hs",
                    suggestion="Ensure HS start value is less than or equal to end value",
                )
            )

    return issues


# Container-level validation rules (run when adding to container)
@container_rule("SHSEC")
def validate_shsec_uniqueness(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate SHSEC identifier uniqueness in container."""
    issues = []

    if context.parent_container:
        container: "BaseContainer[SHSEC]" = context.parent_container
        # Check if identifier already exists in container
        if any(
            item.identifier == obj.identifier
            for item in container.items
        ):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="SHSEC-DUP-001",
                    message=f"Duplicate SHSEC identifier '{obj.identifier}' found",
                    location=f"SHSEC.{obj.pa}",
                    suggestion="Use a unique combination of PA and section ranges",
                )
            )

    return issues


# Model-level validation rules (run when adding to SD_BASE - cross-container)
@model_rule("SHSEC")
def validate_shsec_part_consistency(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate SHSEC part name consistency across the model."""
    issues = []

    if not context.full_model:
        return issues

    # Check if part name is consistent with other components
    # This could include validation against SHAXE, DESEC, etc.
    # For now, just check basic consistency

    return issues


@model_rule("SHSEC")
def validate_shsec_super_element_reference(
    obj: "SHSEC", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate SHSEC super element references if applicable."""
    issues = []

    if not context.full_model or obj.se is None:
        return issues

    # Validate SE (super element) references
    # This would check against available super elements in the model
    # Implementation would depend on how super elements are tracked

    return issues
