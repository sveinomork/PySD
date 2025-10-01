"""
Validation rules for RETYP statements.

Implements three levels of validation:
1. Instance-level: Individual RETYP statement validation
2. Container-level: RETYP container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (material references, etc.)
"""

from typing import List, TYPE_CHECKING, cast

from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule
from ..validation_utils import (
    check_duplicate_ids,
    check_positive_values,
    check_label_length,
    check_material_reference,
    check_unused_definition,
)

if TYPE_CHECKING:
    from ...sdmodel import SD_BASE
    from ...statements.srtyp import SRTYP
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("SRTYP")
def validate_srtyp_instance(
    statement: "SRTYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual SRTYP statement."""
    issues = []

    # ID range validation - kept inline as it's simple
    if not (1 <= statement.id <= 99999999):
        issues.append(
            ValidationIssue(
                severity="error",
                code="SRTYP_ID_RANGE",
                message=f"SRTYP ID {statement.id} must be between 1 and 99999999",
                location=f"SRTYP.{statement.id}",
                suggestion="Use an ID value between 1 and 99999999",
            )
        )

    # Label length validation using utility function
    issues.extend(check_label_length(statement, "SRTYP", max_length=16))

    # Positive values validation using utility function
    positive_fields = {
        "ar": "cross-sectional area",
        "nr": "number of rebars",
        "di": "diameter",
        "c1": "center distance",
        "c2": "nominal cover",
    }
    issues.extend(check_positive_values(statement, "SRTYP", positive_fields))

    # Method consistency validation
    has_area_method = statement.ar is not None
    has_count_method = statement.nr is not None and statement.di is not None

    if not has_area_method and not has_count_method:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SRTYP_METHOD_MISSING",
                message=f"SRTYP {statement.id} must use either area method (AR) or count method (NR+DI)",
                location=f"SRTYP.{statement.id}",
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
                        code="SRTYP_DIAMETER_LARGE",
                        message=f"SRTYP {statement.id} has large diameter {statement.di}mm",
                        location=f"SRTYP.{statement.id}",
                        suggestion="Verify diameter value and units",
                    )
                )
        else:
            # Likely in m
            if statement.di < 0.005:  # Very small diameter (< 5mm)
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="SRTYP_DIAMETER_SMALL",
                        message=f"SRTYP {statement.id} has small diameter {statement.di}m",
                        location=f"SRTYP.{statement.id}",
                        suggestion="Verify diameter value and units",
                    )
                )

    return issues


@container_rule("SRTYP")
def validate_retyp_container(
    container: "BaseContainer[SRTYP]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate SRTYP container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs using utility function
    issues.extend(check_duplicate_ids(container, "SRTYP"))

    # Check for consistent material references using generic container methods
    materials = set()
    for stmt in container.items:
        if stmt.mp is not None:
            materials.add(stmt.mp)

    if len(materials) > 10:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="SRTYP_MANY_MATERIALS",
                message=f"Container has {len(materials)} different material references",
                location="SRTYP container",
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
                code="SRTYP_MIXED_METHODS",
                message=f"Container uses mixed calculation methods: {len(area_method_statements)} area, {len(count_method_statements)} count",
                location="SRTYP container",
                suggestion="Consider standardizing on one calculation method",
            )
        )

    return issues


@model_rule("SRTYP")
def validate_srtyp_model(
    statement: "SRTYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate SRTYP statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check material property references using utility function
    issues.extend(check_material_reference(statement, "SRTYP", model, "rmpec"))

    # Check if this SRTYP is referenced by any SRLOC statements using utility function
    issues.extend(check_unused_definition(statement, "SRTYP", model, "srloc", "rt"))

    # Cross-validate with other SRTYP statements for consistency
    if hasattr(model, "srtyp"):
        similar_srtips = []
        for other_srtip in model.srtyp.items if hasattr(model.srtyp, "items") else []:
            if (
                other_srtip.id != statement.id
                and other_srtip.mp == statement.mp
                and abs((other_srtip.di or 0) - (statement.di or 0)) < 0.001
            ):
                similar_srtips.append(other_srtip)

        if similar_srtips:
            other_ids = [str(r.id) for r in similar_srtips]
            issues.append(
                ValidationIssue(
                    severity="info",
                    code="SRTYP_SIMILAR_DEFINITION",
                    message=f"SRTYP {statement.id} has similar properties to SRTYP {', '.join(other_ids)}",
                    location=f"SRTYP.{statement.id}",
                    suggestion="Consider consolidating similar rebar type definitions",
                )
            )

    return issues
