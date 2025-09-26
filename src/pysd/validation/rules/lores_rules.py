"""
Validation rules for LORES statements.

Implements three levels of validation:
1. Instance-level: Individual LORES statement validation
2. Container-level: LORES container validation (consistency)
3. Model-level: Cross-container validation (load case references, etc.)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.lores import LORES
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("LORES")
def validate_lores_instance(
    statement: "LORES", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual LORES statement."""
    issues = []

    # Mode validation (should be caught by Pydantic but add context)
    manual_mode = statement.lc is not None and statement.part is not None
    sin_mode = statement.sin
    pri_olc_mode = statement.pri_olc
    pri_alc_mode = statement.pri_alc

    modes = [manual_mode, sin_mode, pri_olc_mode, pri_alc_mode]
    if sum(modes) != 1:
        issues.append(
            ValidationIssue(
                severity="error",
                code="LORES_MODE_INVALID",
                message="Exactly one mode must be used: (lc, part), sin, pri_olc, or pri_alc",
                location="LORES statement",
                suggestion="Specify only one operational mode",
            )
        )

    # Manual mode validation
    if manual_mode:
        if statement.lc and (statement.lc < 1 or statement.lc > 9999):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="LORES_LC_RANGE",
                    message=f"Load case {statement.lc} outside typical range (1-9999)",
                    location=f"LORES.{statement.lc}",
                    suggestion="Use a valid load case number",
                )
            )

        if len(statement.resultants) == 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="LORES_NO_RESULTANTS",
                    message="Manual mode requires at least one load resultant value",
                    location=f"LORES.{statement.lc}",
                    suggestion="Provide 1-6 load resultant values",
                )
            )

        # Check for very large resultant values
        for i, value in enumerate(statement.resultants):
            if abs(value) > 1e10:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="LORES_LARGE_RESULTANT",
                        message=f"Very large resultant value {value:.2E} at position {i + 1}",
                        location=f"LORES.{statement.lc}",
                        suggestion="Verify units and magnitude of load resultant",
                    )
                )

    return issues


@container_rule("LORES")
def validate_lores_container(
    container: "BaseContainer[LORES]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate LORES container for consistency."""
    issues = []

    # Check for conflicting modes using generic filtering
    # Manual definitions: LORES statements with explicit load case definitions
    manual_statements = [
        stmt for stmt in container.items if hasattr(stmt, "lc") and stmt.lc is not None
    ]
    # SIN statements: LORES statements that generate SIN files
    sin_statements = [
        stmt
        for stmt in container.items
        if hasattr(stmt, "sin") and stmt.sin is not None
    ]

    if len(sin_statements) > 1:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="LORES_MULTIPLE_SIN",
                message=f"Multiple SIN file generation statements ({len(sin_statements)})",
                location="LORES container",
                suggestion="Typically only one SIN generation statement is needed",
            )
        )

    if len(manual_statements) > 0 and len(sin_statements) > 0:
        issues.append(
            ValidationIssue(
                severity="info",
                code="LORES_MIXED_MODES",
                message=f"Container has both manual definitions ({len(manual_statements)}) and SIN generation ({len(sin_statements)})",
                location="LORES container",
                suggestion="Verify if both modes are intended",
            )
        )

    # Check for duplicate load case definitions using generic grouping
    load_case_groups = {}
    for stmt in manual_statements:
        if hasattr(stmt, "lc") and stmt.lc is not None:
            lc_id = stmt.lc
            if lc_id not in load_case_groups:
                load_case_groups[lc_id] = []
            load_case_groups[lc_id].append(stmt)

    lc_part_combinations = set()
    for stmt in manual_statements:
        combo = (stmt.lc, stmt.part)
        if combo in lc_part_combinations:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="LORES_DUPLICATE_LC_PART",
                    message=f"Duplicate definition for LC={stmt.lc} PART={stmt.part}",
                    location=f"LORES.{stmt.lc}",
                    suggestion="Remove duplicate load case/part combinations",
                )
            )
        lc_part_combinations.add(combo)

    return issues


@model_rule("LORES")
def validate_lores_model(
    statement: "LORES", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate LORES statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = context.full_model

    # Check if load case references exist in LOADC
    if statement.lc is not None and hasattr(model, "loadc"):
        # Check if the load case is defined in LOADC statements
        loadc_olcs = []
        for loadc_item in model.loadc.items if hasattr(model.loadc, "items") else []:
            if hasattr(loadc_item, "olc"):
                if hasattr(loadc_item.olc, "to_list"):
                    loadc_olcs.extend(loadc_item.olc.to_list())
                elif isinstance(loadc_item.olc, (list, tuple)):
                    loadc_olcs.extend(loadc_item.olc)
                else:
                    loadc_olcs.append(loadc_item.olc)

        if loadc_olcs and statement.lc not in loadc_olcs:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="LORES_LC_NOT_IN_LOADC",
                    message=f"LORES load case {statement.lc} not found in LOADC definitions",
                    location=f"LORES.{statement.lc}",
                    suggestion="Verify load case exists in LOADC or add corresponding LOADC statement",
                )
            )

    # Check for consistency with GRECO statements
    if hasattr(model, "greco") and statement.lc is not None:
        greco_items = model.greco.items if hasattr(model.greco, "items") else []
        if greco_items:
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="LORES_WITH_GRECO",
                    message=f"LORES load case {statement.lc} defined with GRECO statements present",
                    location=f"LORES.{statement.lc}",
                    suggestion="Ensure LORES load resultants are compatible with GRECO support system",
                )
            )

    return issues
