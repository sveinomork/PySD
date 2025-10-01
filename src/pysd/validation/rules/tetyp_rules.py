"""
Validation rules for TETYP statements.

Implements three levels of validation:
1. Instance-level: Individual TETYP statement validation
2. Container-level: TETYP container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (material references, etc.)
"""

from typing import List, TYPE_CHECKING, cast
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule
from ..validation_utils import (
    check_duplicate_ids,
    check_positive_values,
    check_unused_definition,
)

if TYPE_CHECKING:
    from ...sdmodel import SD_BASE
    from ...statements.tetyp import TETYP
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule("TETYP")
def validate_TETYP_instance(
    statement: "TETYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual TETYP statement."""
    issues = []

    # ID range validation - kept inline as it's simple
    if not (1 <= statement.id <= 99999999):
        issues.append(
            ValidationIssue(
                severity="error",
                code="TETYP_ID_RANGE",
                message=f"TETYP ID {statement.id} must be between 1 and 99999999",
                location=f"TETYP.{statement.id}",
                suggestion="Use an ID value between 1 and 99999999",
            )
        )

    # Positive values validation using utility function
    positive_fields = {
        "ar": "cross-sectional area",
        "nr": "number of rebars",
        "eo": "initial strain",
        "os": "offset",
    }
    issues.extend(check_positive_values(statement, "TETYP", positive_fields))

    # Method consistency validation
    has_area_method = statement.ar is not None

    if not has_area_method:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TETYP_METHOD_MISSING",
                message=f"TETYP {statement.id} must use either area method (AR)",
                location=f"TETYP.{statement.id}",
                suggestion="Provide either AR parameter or both NR and DI parameters",
            )
        )

    return issues


@container_rule("TETYP")
def validate_TETYP_container(
    container: "BaseContainer[TETYP]", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate TETYP container for consistency and uniqueness."""
    issues = []

    # Check for duplicate IDs using utility function
    issues.extend(check_duplicate_ids(container, "TETYP"))

    # Check for consistent material references using generic container methods
    materials = set()
    for stmt in container.items:
        if stmt.mp is not None:
            materials.add(stmt.mp)

    if len(materials) > 10:  # Arbitrary threshold
        issues.append(
            ValidationIssue(
                severity="info",
                code="TETYP_MANY_MATERIALS",
                message=f"Container has {len(materials)} different material references",
                location="TETYP container",
                suggestion="Consider consolidating material properties for consistency",
            )
        )

    return issues


@model_rule("TETYP")
def validate_TETYP_model(
    statement: "TETYP", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate TETYP statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check material property references
    if statement.mp is not None:
        # With container ID normalization, we can directly check contains on the TEMAT container
        if hasattr(model, "temat") and not model.temat.contains(statement.mp):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TETYP_MATERIAL_NOT_FOUND",
                    message=f"TETYP {statement.id} references material {statement.mp} not found in TEMAT",
                    location=f"TETYP.{statement.id}",
                    suggestion="Define the referenced material in TEMAT or update the MP reference",
                )
            )

    # Check if this TETYP is referenced by any TELOC statements using utility function
    issues.extend(check_unused_definition(statement, "TETYP", model, "teloc", "rt"))

    return issues
