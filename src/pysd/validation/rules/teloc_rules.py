"""
Validation rules for SRLOC statements.

Implements three levels of validation:
1. Instance-level: Individual SRLOC statement validation
2. Container-level: SRLOC container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (rebar type references, etc.)
"""

from typing import List, TYPE_CHECKING, cast
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...sdmodel import SD_BASE
    from ...statements.teloc import TELOC
    from ...statements.tetyp import TETYP
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("TELOC")
def validate_teloc_instance(
    statement: "TELOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual TELOC statement."""
    issues = []

    # ID length validation (already handled by Pydantic, but we can add context)
    if len(statement.id) > 4:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TELOC_ID_LENGTH",
                message=f"TELOC ID '{statement.id}' exceeds maximum length (4 characters)",
                location=f"TELOC.{statement.id}",
                suggestion="Use a shorter ID",
            )
        )

    # Location definition validation
    has_location_alt1 = any([statement.pa, statement.fs, statement.hs])
    has_location_alt2 = statement.la is not None

    if not has_location_alt1 and not has_location_alt2:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="TELOC_LOCATION_GLOBAL",
                message=f"TELOC {statement.id} applies to entire model (no location specified)",
                location=f"TELOC.{statement.id}",
                suggestion="Consider specifying location constraints (PA, FS, HS, or LA)",
            )
        )

    # Range validation for rebar types
    if isinstance(statement.st, tuple):
        if statement.st[0] > statement.st[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TELOC_ST_RANGE_INVALID",
                    message=f"TELOC {statement.id} has invalid rebar type range {statement.st[0]}-{statement.st[1]}",
                    location=f"TELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )
        elif statement.st[0] == statement.st[1]:
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="TELOC_ST_RANGE_SINGLE",
                    message=f"TELOC {statement.id} uses range {statement.st[0]}-{statement.st[1]} for single rebar type",
                    location=f"TELOC.{statement.id}",
                    suggestion="Consider using single value instead of range",
                )
            )

    return issues


@container_rule("TELOC")
def validate_teloc_container(
    container: "BaseContainer[TELOC]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate TELOC container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs
    ids = [stmt.id for stmt in container.items]
    seen_ids = set()
    for stmt_id in ids:
        if stmt_id in seen_ids:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TELOC_DUPLICATE_ID",
                    message=f"Duplicate TELOC ID '{stmt_id}' found in container",
                    location=f"TELOC.{stmt_id}",
                    suggestion="Use unique IDs for each TELOC statement",
                )
            )
        seen_ids.add(stmt_id)

    # Check for consistent rebar type usage using generic filtering
    referenced_types = set()
    for stmt in container.items:
        if hasattr(stmt, "st") and stmt.tt is not None:
            referenced_types.add(stmt.tt)

    if len(referenced_types) > 20:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="TELOC_MANY_REBAR_TYPES",
                message=f"Container references {len(referenced_types)} different rebar types",
                location="TELOC container",
                suggestion="Consider consolidating rebar type definitions",
            )
        )

    #
    return issues


@model_rule("TELOC")
def validate_reloc_model(
    statement: "TELOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate TELOC statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check rebar type references
    if isinstance(statement.tt, tuple):
        # Range of rebar types
        for st_id in range(statement.tt[0], statement.st[1] + 1):
            if hasattr(model, "tetyp") and not model.tetyp.contains(st_id):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TELOC_TETYP_NOT_FOUND",
                        message=f"TELOC {statement.id} references rebar type {st_id} not found in TETYP",
                        location=f"TELOC.{statement.id}",
                        suggestion="Define the referenced rebar type in TETYP or update the RT reference",
                    )
                )
    else:
        # Single rebar type
        if hasattr(model, "tetyp") and not model.tetyp.has_id(statement.tt):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TELOC_TETYP_NOT_FOUND",
                    message=f"TELOC {statement.id} references rebar type {statement.tt} not found in TETYP",
                    location=f"TELOC.{statement.id}",
                    suggestion="Define the referenced rebar type in TETYP or update the RT reference",
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
                        code="TELOC_PART_NO_SHSEC",
                        message=f"TELOC {statement.id} references part '{statement.pa}' but no SHSEC parts are defined",
                        location=f"TELOC.{statement.id}",
                        suggestion="Define SHSEC statements with parts before referencing them in TELOC",
                    )
                )
            else:
                # SHSEC parts exist, but referenced part is not among them
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TELOC_PART_NOT_FOUND",
                        message=f"TELOC {statement.id} references part '{statement.pa}' not found in SHSEC",
                        location=f"TELOC.{statement.id}",
                        suggestion=f"Use one of the defined parts: {', '.join(sorted(set(valid_parts)))}",
                    )
                )

        # Check naming conventions
        if len(statement.pa) > 8:  # Arbitrary limit
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="TELOC_PART_NAME_LONG",
                    message=f"TELOC {statement.id} references long part name '{statement.pa}'",
                    location=f"TELOC.{statement.id}",
                    suggestion="Consider using shorter part names for clarity",
                )
            )

    # Check section range validity
    if statement.fs is not None:
        if isinstance(statement.fs, tuple) and statement.fs[0] > statement.fs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TELOC_FS_RANGE_INVALID",
                    message=f"TELOC {statement.id} has invalid F-section range {statement.fs[0]}-{statement.fs[1]}",
                    location=f"TELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    if statement.hs is not None:
        if isinstance(statement.hs, tuple) and statement.hs[0] > statement.hs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TELOC_HS_RANGE_INVALID",
                    message=f"TELOC {statement.id} has invalid H-section range {statement.hs[0]}-{statement.hs[1]}",
                    location=f"TELOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    return issues
