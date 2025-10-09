"""
Validation rules for XTFIL statements.

Implements three levels of validation:
1. Instance-level: Individual XTFIL statement validation
2. Container-level: XTFIL container validation (filename uniqueness, etc.)
3. Model-level: Cross-container validation (part references, etc.)
"""

from typing import List, TYPE_CHECKING, cast
from ..core import ValidationIssue
from ..rule_system import model_rule

if TYPE_CHECKING:
    from ...sdmodel import SD_BASE
    from ...statements.xtfil import XTFIL
    from ...model.base_container import BaseContainer
    from ..core import ValidationContext


@model_rule("XTFIL")
def validate_xtfil_model(
    statement: "XTFIL", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate XTFIL statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = cast("SD_BASE", context.full_model)

    # Check if structural part exists in DESEC statements
    if hasattr(model, "desec"):
        desec_parts = []
        for desec_item in model.desec.items if hasattr(model.desec, "items") else []:
            if hasattr(desec_item, "pa"):
                desec_parts.append(desec_item.pa)

        if desec_parts and statement.pa not in desec_parts:
            available_parts = ", ".join(desec_parts[:5])  # Show first 5 parts
            if len(desec_parts) > 5:
                available_parts += ", ..."

            issues.append(
                ValidationIssue(
                    severity="error",
                    code="XTFIL_PART_NOT_IN_DESEC",
                    message=f"XTFIL part '{statement.pa}' not found in DESEC definitions",
                    location=f"XTFIL.{statement.fn}",
                    suggestion=f"Define part in DESEC first or use existing parts: {available_parts}",
                )
            )

    return issues
