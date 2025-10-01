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
from ..validation_utils import check_duplicate_ids

if TYPE_CHECKING:
    from ...sdmodel import SD_BASE
    from ...statements.srloc import SRLOC
    from ...statements.srtyp import SRTYP
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("SRLOC")
def validate_srloc_instance(
    statement: "SRLOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual SRLOC statement."""
    issues = []

    # ID length validation (already handled by Pydantic, but we can add context)
    if len(statement.id) > 4:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SRLOC_ID_LENGTH",
                message=f"SRLOC ID '{statement.id}' exceeds maximum length (4 characters)",
                location=f"SRLOC.{statement.id}",
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
                code="SRLOC_LOCATION_GLOBAL",
                message=f"SRLOC {statement.id} applies to entire model (no location specified)",
                location=f"SRLOC.{statement.id}",
                suggestion="Consider specifying location constraints (PA, FS, HS, or LA)",
            )
        )

    # Range validation for rebar types
    if isinstance(statement.st, tuple):
        if statement.st[0] > statement.st[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SRLOC_ST_RANGE_INVALID",
                    message=f"SRLOC {statement.id} has invalid rebar type range {statement.st[0]}-{statement.st[1]}",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )
        elif statement.st[0] == statement.st[1]:
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="SRLOC_ST_RANGE_SINGLE",
                    message=f"SRLOC {statement.id} uses range {statement.st[0]}-{statement.st[1]} for single rebar type",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Consider using single value instead of range",
                )
            )

    return issues


@container_rule("SRLOC")
def validate_srloc_container(
    container: "BaseContainer[SRLOC]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate SRLOC container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs using utility function
    issues.extend(check_duplicate_ids(container, "SRLOC"))

    # Check for consistent rebar type usage using generic filtering
    referenced_types = set()
    for stmt in container.items:
        if hasattr(stmt, "st") and stmt.st is not None:
            referenced_types.add(stmt.st)

    if len(referenced_types) > 20:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="SRLOC_MANY_REBAR_TYPES",
                message=f"Container references {len(referenced_types)} different rebar types",
                location="SRLOC container",
                suggestion="Consider consolidating rebar type definitions",
            )
        )

    #
    return issues


@model_rule("SRLOC")
def validate_reloc_model(
    statement: "SRLOC", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate SRLOC statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check rebar type references
    if isinstance(statement.st, tuple):
        # Range of rebar types
        for st_id in range(statement.st[0], statement.st[1] + 1):
            if hasattr(model, "srtyp") and not model.srtyp.contains(st_id):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="SRLOC_SRTYP_NOT_FOUND",
                        message=f"SRLOC {statement.id} references rebar type {st_id} not found in SRTYP",
                        location=f"SRLOC.{statement.id}",
                        suggestion="Define the referenced rebar type in SRTYP or update the RT reference",
                    )
                )
    else:
        # Single rebar type
        if hasattr(model, "srtyp") and not model.srtyp.has_id(statement.st):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SRLOC_SRTYP_NOT_FOUND",
                    message=f"SRLOC {statement.id} references rebar type {statement.st} not found in SRTYP",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Define the referenced rebar type in SRTYP or update the RT reference",
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
                        code="SRLOC_PART_NO_SHSEC",
                        message=f"SRLOC {statement.id} references part '{statement.pa}' but no SHSEC parts are defined",
                        location=f"SRLOC.{statement.id}",
                        suggestion="Define SHSEC statements with parts before referencing them in SRLOC",
                    )
                )
            else:
                # SHSEC parts exist, but referenced part is not among them
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="SRLOC_PART_NOT_FOUND",
                        message=f"SRLOC {statement.id} references part '{statement.pa}' not found in SHSEC",
                        location=f"SRLOC.{statement.id}",
                        suggestion=f"Use one of the defined parts: {', '.join(sorted(set(valid_parts)))}",
                    )
                )

        # Check naming conventions
        if len(statement.pa) > 8:  # Arbitrary limit
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="SRLOC_PART_NAME_LONG",
                    message=f"SRLOC {statement.id} references long part name '{statement.pa}'",
                    location=f"SRLOC.{statement.id}",
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
                    code="SRLOC_LAREA_INVALID",
                    message=f"SRLOC {statement.id} references invalid location area {statement.la}",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Use positive location area ID",
                )
            )

    # Check section range validity
    if statement.fs is not None:
        if isinstance(statement.fs, tuple) and statement.fs[0] > statement.fs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SRLOC_FS_RANGE_INVALID",
                    message=f"SRLOC {statement.id} has invalid F-section range {statement.fs[0]}-{statement.fs[1]}",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    if statement.hs is not None:
        if isinstance(statement.hs, tuple) and statement.hs[0] > statement.hs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SRLOC_HS_RANGE_INVALID",
                    message=f"SRLOC {statement.id} has invalid H-section range {statement.hs[0]}-{statement.hs[1]}",
                    location=f"SRLOC.{statement.id}",
                    suggestion="Ensure first value is less than or equal to second value",
                )
            )

    return issues
