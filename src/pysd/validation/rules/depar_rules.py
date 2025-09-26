"""
Validation rules for DEPAR (Design Parameters) statements.

This module contains validation logic for DEPAR statement parameters.
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationSeverity
from ..rule_system import object_rule, model_rule, ValidationContext

if TYPE_CHECKING:
    from ...statements.depar import DEPAR


# Object-level validation rules (validate individual DEPAR objects)
@object_rule("DEPAR")
def validate_depar_parameters(obj: "DEPAR") -> List[ValidationIssue]:
    """Validate DEPAR parameter ranges and consistency."""
    issues = []

    # Validate positive integer parameters
    if obj.n_lay is not None and obj.n_lay <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="DEPAR-NLAY-001",
                message=f"N_LAY must be positive, got {obj.n_lay}",
                location="DEPAR.n_lay",
                suggestion="Use a positive number of integration layers (typically 5-20)",
            )
        )

    if obj.n_ite is not None and obj.n_ite <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="DEPAR-NITE-001",
                message=f"N_ITE must be positive, got {obj.n_ite}",
                location="DEPAR.n_ite",
                suggestion="Use a positive maximum number of iterations (typically 100-10000)",
            )
        )

    # Validate stress deviation parameters
    if obj.d_sig is not None:
        if isinstance(obj.d_sig, tuple):
            if len(obj.d_sig) != 2:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR.value,
                        code="DEPAR-DSIG-001",
                        message=f"D_SIG tuple must have exactly 2 values, got {len(obj.d_sig)}",
                        location="DEPAR.d_sig",
                        suggestion="Use format (absolute_deviation, relative_deviation)",
                    )
                )
            elif obj.d_sig[0] <= 0 or obj.d_sig[1] <= 0:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR.value,
                        code="DEPAR-DSIG-002",
                        message=f"D_SIG values must be positive, got {obj.d_sig}",
                        location="DEPAR.d_sig",
                        suggestion="Use positive values for stress deviation criteria",
                    )
                )
        elif obj.d_sig <= 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="DEPAR-DSIG-003",
                    message=f"D_SIG must be positive, got {obj.d_sig}",
                    location="DEPAR.d_sig",
                    suggestion="Use positive value for stress deviation criterion",
                )
            )

    # Validate tolerance parameters
    for tol_name, tol_value in [
        ("t_tol", obj.t_tol),
        ("p_tol", obj.p_tol),
        ("z_tol", obj.z_tol),
    ]:
        if tol_value is not None and tol_value < 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code=f"DEPAR-{tol_name.upper()}-001",
                    message=f"{tol_name.upper()} must be non-negative, got {tol_value}",
                    location=f"DEPAR.{tol_name}",
                    suggestion="Use non-negative tolerance values",
                )
            )

    # Validate percentage tolerance
    if obj.p_tol is not None and obj.p_tol > 100:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="DEPAR-PTOL-002",
                message=f"P_TOL is unusually high at {obj.p_tol}%",
                location="DEPAR.p_tol",
                suggestion="Typical percentage tolerances are 0-50%",
            )
        )

    # Validate modulus of elasticity
    if obj.e_mod is not None and obj.e_mod <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="DEPAR-EMOD-001",
                message=f"E_MOD must be positive, got {obj.e_mod}",
                location="DEPAR.e_mod",
                suggestion="Use positive modulus of elasticity in kPa (typical range: 1e6 - 1e8)",
            )
        )

    # Validate Poisson's ratio
    if obj.p_rat is not None and not (-1 <= obj.p_rat <= 0.5):
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="DEPAR-PRAT-001",
                message=f"P_RAT must be between -1 and 0.5, got {obj.p_rat}",
                location="DEPAR.p_rat",
                suggestion="Use valid Poisson ratio (typical range: 0-0.5 for most materials)",
            )
        )

    return issues


# Model-level validation rules (validate DEPAR in model context)
@model_rule("DEPAR")
def validate_depar_model_consistency(
    obj: "DEPAR", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate DEPAR consistency within the model."""
    issues = []

    if not context.full_model:
        return issues

    # Check if multiple DEPAR statements exist (typically only one should be used)
    existing_depars = getattr(context.full_model, "depar", None)
    if existing_depars and hasattr(existing_depars, "items"):
        other_depars = [d for d in existing_depars.items if d is not obj]
        if len(other_depars) > 0:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING.value,
                    code="DEPAR-DUP-001",
                    message=f"Model already has {len(other_depars)} other DEPAR statement(s), typically only one is needed",
                    location="DEPAR",
                    suggestion="Consider consolidating multiple DEPAR statements into one",
                )
            )

    return issues
