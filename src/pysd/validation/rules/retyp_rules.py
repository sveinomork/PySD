"""
Validation rules for RETYP statements.

Implements three levels of validation:
1. Instance-level: Individual RETYP statement validation
2. Container-level: RETYP container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (material references, etc.)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule
from ..validation_utils import (
    check_duplicate_ids,
    check_positive_values,
    check_non_negative_values,
    check_label_length,
    check_material_reference,
    check_unused_definition,
)

if TYPE_CHECKING:
    from ...statements.retyp import RETYP
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("RETYP")
def validate_retyp_instance(
    statement: "RETYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual RETYP statement."""
    issues = []

    # ID range validation (instance-level)
    if not (1 <= statement.id <= 99999999):
        issues.append(
            ValidationIssue(
                severity="error",
                code="RETYP_ID_RANGE",
                message=f"RETYP ID {statement.id} must be between 1 and 99999999",
                location=f"RETYP.{statement.id}",
                suggestion="Use an ID value between 1 and 99999999",
            )
        )

    # Label length validation using utility function
    issues.extend(check_label_length(statement, "RETYP", max_length=16))

    # Positive values validation using utility function
    positive_fields = {
        "ar": "cross-sectional area",
        "nr": "number of rebars",
        "di": "diameter",
        "cc": "center distance",
        "c2": "nominal cover",
        "th": "thickness",
        "bc": "bond coefficient",
    }
    issues.extend(check_positive_values(statement, "RETYP", positive_fields))

    # Offset validation using utility function - can be zero or positive
    non_negative_fields = {"os": "offset"}
    issues.extend(
        check_non_negative_values(
            statement, "RETYP", non_negative_fields, error_code_suffix="NEGATIVE_OFFSET"
        )
    )

    # Method consistency validation
    has_area_method = statement.ar is not None
    has_count_method = statement.nr is not None and statement.di is not None

    if not has_area_method and not has_count_method:
        issues.append(
            ValidationIssue(
                severity="error",
                code="RETYP_METHOD_MISSING",
                message=f"RETYP {statement.id} must use either area method (AR) or count method (NR+DI)",
                location=f"RETYP.{statement.id}",
                suggestion="Provide either AR parameter or both NR and DI parameters",
            )
        )

    # Diameter unit validation
    if statement.di is not None:
        if statement.di > 1.0:
            # Likely in mm
            if statement.di > 100:  # Very large diameter
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="RETYP_DIAMETER_LARGE",
                        message=f"RETYP {statement.id} has large diameter {statement.di}mm",
                        location=f"RETYP.{statement.id}",
                        suggestion="Verify diameter value and units",
                    )
                )
        else:
            # Likely in m
            if statement.di < 0.005:  # Very small diameter (< 5mm)
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="RETYP_DIAMETER_SMALL",
                        message=f"RETYP {statement.id} has small diameter {statement.di}m",
                        location=f"RETYP.{statement.id}",
                        suggestion="Verify diameter value and units",
                    )
                )

    # Bond coefficient validation
    if statement.bc is not None:
        if not 0.1 <= statement.bc <= 1.0:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="RETYP_BOND_COEFFICIENT",
                    message=f"RETYP {statement.id} bond coefficient {statement.bc} outside typical range (0.1-1.0)",
                    location=f"RETYP.{statement.id}",
                    suggestion="Verify bond coefficient value",
                )
            )

    return issues


@container_rule("RETYP")
def validate_retyp_container(
    container: "BaseContainer[RETYP]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate RETYP container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs using utility function
    issues.extend(check_duplicate_ids(container, "RETYP"))

    # Check for consistent material references using generic container methods
    materials = set()
    for stmt in container.items:
        if stmt.mp is not None:
            materials.add(stmt.mp)

    if len(materials) > 10:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="RETYP_MANY_MATERIALS",
                message=f"Container has {len(materials)} different material references",
                location="RETYP container",
                suggestion="Consider consolidating material properties for consistency",
            )
        )

    # Check for mixed methods using generic filtering
    area_method_statements = [stmt for stmt in container.items if stmt.ar is not None]
    count_method_statements = [
        stmt for stmt in container.items if stmt.nr is not None and stmt.di is not None
    ]

    if len(area_method_statements) > 0 and len(count_method_statements) > 0:
        issues.append(
            ValidationIssue(
                severity="info",
                code="RETYP_MIXED_METHODS",
                message=f"Container uses mixed calculation methods: {len(area_method_statements)} area, {len(count_method_statements)} count",
                location="RETYP container",
                suggestion="Consider standardizing on one calculation method",
            )
        )

    return issues


@model_rule("RETYP")
def validate_retyp_model(
    statement: "RETYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate RETYP statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = context.full_model

    # Check material property references using utility function
    issues.extend(check_material_reference(statement, "RETYP", model, "rmpec"))

    # Check if this RETYP is referenced by any RELOC statements using utility function
    issues.extend(check_unused_definition(statement, "RETYP", model, "reloc", "rt"))

    # Cross-validate with other RETYP statements for consistency
    if hasattr(model, "retyp"):
        similar_retyps = []
        for other_retyp in model.retyp.items if hasattr(model.retyp, "items") else []:
            if (
                other_retyp.id != statement.id
                and other_retyp.mp == statement.mp
                and abs((other_retyp.di or 0) - (statement.di or 0)) < 0.001
            ):
                similar_retyps.append(other_retyp)

        if similar_retyps:
            other_ids = [str(r.id) for r in similar_retyps]
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="RETYP_SIMILAR_DEFINITION",
                    message=f"RETYP {statement.id} has similar properties to RETYP {', '.join(other_ids)}",
                    location=f"RETYP.{statement.id}",
                    suggestion="Consider consolidating similar rebar type definitions",
                )
            )

    return issues
