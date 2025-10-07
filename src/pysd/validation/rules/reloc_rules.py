"""
Validation rules for RELOC statements.

Implements three levels of validation:
1. Instance-level: Individual RELOC statement validation
2. Container-level: RELOC container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (rebar type references, etc.)
"""

from typing import List, TYPE_CHECKING, cast

from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.reloc import RELOC
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext
    from ...sdmodel import SD_BASE


@instance_rule("RELOC")
def validate_reloc_instance(
    statement: "RELOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual RELOC statement."""
    issues = []

    # ID length validation (already handled by Pydantic, but we can add context)
    if len(statement.id) > 4:
        issues.append(
            ValidationIssue(
                severity="error",
                code="RELOC_ID_LENGTH",
                message=f"RELOC ID '{statement.id}' exceeds maximum length (4 characters)",
                location=f"RELOC.{statement.id}",
                suggestion="Use a shorter ID",
            )
        )

    # Angle validation (additional context beyond Pydantic)
    if abs(statement.al) > 90:
        issues.append(
            ValidationIssue(
                severity="error",
                code="RELOC_ANGLE_RANGE",
                message=f"RELOC {statement.id} angle {statement.al} outside valid range (-90 to +90)",
                location=f"RELOC.{statement.id}",
                suggestion="Use angle between -90 and +90 degrees",
            )
        )

    # Cover validation
    if statement.cov is not None:
        if statement.cov < 10:  # Very small cover
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="RELOC_COVER_SMALL",
                    message=f"RELOC {statement.id} has small cover {statement.cov}mm",
                    location=f"RELOC.{statement.id}",
                    suggestion="Verify cover requirements for structural adequacy",
                )
            )
        elif statement.cov > 200:  # Very large cover
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="RELOC_COVER_LARGE",
                    message=f"RELOC {statement.id} has large cover {statement.cov}mm",
                    location=f"RELOC.{statement.id}",
                    suggestion="Verify cover value and units",
                )
            )

    # Location definition validation
    has_location_alt1 = any([statement.pa, statement.fs, statement.hs])
    has_location_alt2 = statement.la is not None

    if not has_location_alt1 and not has_location_alt2:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="RELOC_LOCATION_GLOBAL",
                message=f"RELOC {statement.id} applies to entire model (no location specified)",
                location=f"RELOC.{statement.id}",
                suggestion="Consider specifying location constraints (PA, FS, HS, or LA)",
            )
        )

    # Range validation for rebar types
    if isinstance(statement.rt, tuple):
        if statement.rt[0] > statement.rt[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_RT_RANGE_INVALID",
                    message=f"RELOC {statement.id} has invalid rebar type range {statement.rt[0]}-{statement.rt[1]}",
                    location=f"RELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )
        elif statement.rt[0] == statement.rt[1]:
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="RELOC_RT_RANGE_SINGLE",
                    message=f"RELOC {statement.id} uses range {statement.rt[0]}-{statement.rt[1]} for single rebar type",
                    location=f"RELOC.{statement.id}",
                    suggestion="Consider using single value instead of range",
                )
            )

    return issues


@container_rule("RELOC")
def validate_reloc_container(
    container: "BaseContainer[RELOC]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate RELOC container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs
    ids = [stmt.id for stmt in container.items]
    seen_ids = set()
    for stmt_id in ids:
        if stmt_id in seen_ids:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_DUPLICATE_ID",
                    message=f"Duplicate RELOC ID '{stmt_id}' found in container",
                    location=f"RELOC.{stmt_id}",
                    suggestion="Use unique IDs for each RELOC statement",
                )
            )
        seen_ids.add(stmt_id)

    # Check for consistent rebar type usage using generic filtering
    referenced_types = set()
    for stmt in container.items:
        if hasattr(stmt, "rt") and stmt.rt is not None:
            referenced_types.add(stmt.rt)

    if len(referenced_types) > 20:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="RELOC_MANY_REBAR_TYPES",
                message=f"Container references {len(referenced_types)} different rebar types",
                location="RELOC container",
                suggestion="Consider consolidating rebar type definitions",
            )
        )

    # Check for face distribution
    face_counts = {0: 0, 1: 0, 2: 0}
    for stmt in container.items:
        face_counts[stmt.fa] = face_counts.get(stmt.fa, 0) + 1

    if face_counts[0] == len(container.items):
        issues.append(
            ValidationIssue(
                severity="info",
                code="RELOC_ALL_CENTER",
                message="All RELOC statements use center face (FA=0)",
                location="RELOC container",
                suggestion="Consider if face-specific reinforcement is needed",
            )
        )

    # Check for angle distribution
    angles = [stmt.al for stmt in container.items]
    if all(angle == 0.0 for angle in angles):
        issues.append(
            ValidationIssue(
                severity="info",
                code="RELOC_ALL_ZERO_ANGLE",
                message="All RELOC statements use zero angle (AL=0)",
                location="RELOC container",
                suggestion="Consider if directional reinforcement is needed",
            )
        )

    return issues


@model_rule("RELOC")
def validate_reloc_model(
    statement: "RELOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate RELOC statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check rebar type references
    if isinstance(statement.rt, tuple):
        # Range of rebar types
        for rt_id in range(statement.rt[0], statement.rt[1] + 1):
            if hasattr(model, "retyp") and not model.retyp.has_id(rt_id):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="RELOC_RETYP_NOT_FOUND",
                        message=f"RELOC {statement.id} references rebar type {rt_id} not found in RETYP",
                        location=f"RELOC.{statement.id}",
                        suggestion="Define the referenced rebar type in RETYP or update the RT reference",
                    )
                )
    else:
        # Single rebar type
        if hasattr(model, "retyp") and not model.retyp.has_id(statement.rt):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_RETYP_NOT_FOUND",
                    message=f"RELOC {statement.id} references rebar type {statement.rt} not found in RETYP",
                    location=f"RELOC.{statement.id}",
                    suggestion="Define the referenced rebar type in RETYP or update the RT reference",
                )
            )

    # Check part references against SHSEC
    if statement.pa is not None:
        # Get all part names from SHSEC container (clean iteration)
        valid_parts = [shsec.pa for shsec in model.shsec]

        # ALWAYS validate part references - fail if part doesn't exist
        if statement.pa not in valid_parts:
            if not valid_parts:
                # No SHSEC parts defined at all
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="RELOC_PART_NO_SHSEC",
                        message=f"RELOC {statement.id} references part '{statement.pa}' but no SHSEC parts are defined",
                        location=f"RELOC.{statement.id}",
                        suggestion="Define SHSEC statements with parts before referencing them in RELOC",
                    )
                )
            else:
                # SHSEC parts exist, but referenced part is not among them
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="RELOC_PART_NOT_FOUND",
                        message=f"RELOC {statement.id} references part '{statement.pa}' not found in SHSEC",
                        location=f"RELOC.{statement.id}",
                        suggestion=f"Use one of the defined parts: {', '.join(sorted(set(valid_parts)))}",
                    )
                )

        # Check naming conventions
        if len(statement.pa) > 8:  # Arbitrary limit
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="RELOC_PART_NAME_LONG",
                    message=f"RELOC {statement.id} references long part name '{statement.pa}'",
                    location=f"RELOC.{statement.id}",
                    suggestion="Consider using shorter part names for clarity",
                )
            )

    # Check location area references
    if statement.la is not None:
        # Could validate against LAREA statements if available
        if statement.la <= 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_LAREA_INVALID",
                    message=f"RELOC {statement.id} references invalid location area {statement.la}",
                    location=f"RELOC.{statement.id}",
                    suggestion="Use positive location area ID",
                )
            )

    # Check section range validity
    if statement.fs is not None:
        if isinstance(statement.fs, tuple) and statement.fs[0] > statement.fs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_FS_RANGE_INVALID",
                    message=f"RELOC {statement.id} has invalid F-section range {statement.fs[0]}-{statement.fs[1]}",
                    location=f"RELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    if statement.hs is not None:
        if isinstance(statement.hs, tuple) and statement.hs[0] > statement.hs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="RELOC_HS_RANGE_INVALID",
                    message=f"RELOC {statement.id} has invalid H-section range {statement.hs[0]}-{statement.hs[1]}",
                    location=f"RELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    return issues
