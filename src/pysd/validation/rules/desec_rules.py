"""
Validation rules for DESEC statements.

Implements three levels of validation:
1. Instance-level: Individual DESEC statement validation
2. Container-level: DESEC container validation (part consistency, etc.)
3. Model-level: Cross-container validation (part references, etc.)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.desec import DESEC
    from ...containers.desec_container import DesecContainer
    from ..core import ValidationContext


@instance_rule('DESEC')
def validate_desec_instance(statement: 'DESEC', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate individual DESEC statement."""
    issues = []
    
    # Check thickness values
    if statement.th and statement.th < 0:
        issues.append(ValidationIssue(
            severity="error",
            code="DESEC_NEGATIVE_THICKNESS",
            message=f"Negative thickness {statement.th} in DESEC {statement.pa}",
            location=f"DESEC.{statement.pa}",
            suggestion="Thickness must be non-negative"
        ))
    
    if statement.th and statement.th > 5.0:
        issues.append(ValidationIssue(
            severity="warning",
            code="DESEC_LARGE_THICKNESS",
            message=f"Very large thickness {statement.th}m in DESEC {statement.pa}",
            location=f"DESEC.{statement.pa}",
            suggestion="Verify thickness value and units"
        ))
    
    # Check section ranges
    if statement.fs and isinstance(statement.fs, tuple):
        if statement.fs[0] > statement.fs[1]:
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_INVALID_FS_RANGE",
                message=f"Invalid F-section range {statement.fs} in DESEC {statement.pa}",
                location=f"DESEC.{statement.pa}",
                suggestion="F-section start must be <= end"
            ))
        if statement.fs[0] < 1:
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_INVALID_FS_START",
                message=f"F-section start {statement.fs[0]} < 1 in DESEC {statement.pa}",
                location=f"DESEC.{statement.pa}",
                suggestion="Section numbers must be positive"
            ))
    
    if statement.hs and isinstance(statement.hs, tuple):
        if statement.hs[0] > statement.hs[1]:
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_INVALID_HS_RANGE",
                message=f"Invalid H-section range {statement.hs} in DESEC {statement.pa}",
                location=f"DESEC.{statement.pa}",
                suggestion="H-section start must be <= end"
            ))
        if statement.hs[0] < 1:
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_INVALID_HS_START",
                message=f"H-section start {statement.hs[0]} < 1 in DESEC {statement.pa}",
                location=f"DESEC.{statement.pa}",
                suggestion="Section numbers must be positive"
            ))
    
    # Check coordinate ranges
    large_coord_limit = 1000.0  # meters
    for coord_name, coord_value in [('X', statement.x), ('Y', statement.y), ('Z', statement.z)]:
        if coord_value and abs(coord_value) > large_coord_limit:
            issues.append(ValidationIssue(
                severity="warning",
                code="DESEC_LARGE_COORDINATE",
                message=f"Large {coord_name}-coordinate {coord_value}m in DESEC {statement.pa}",
                location=f"DESEC.{statement.pa}",
                suggestion="Verify coordinate value and units"
            ))
    
    return issues


@container_rule('DESEC')
def validate_desec_container(container: 'DesecContainer', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate DESEC container for consistency."""
    issues = []
    
    # Check for duplicate part names
    part_names = [item.pa for item in container.items]
    seen_parts = set()
    for part_name in part_names:
        if part_name in seen_parts:
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_DUPLICATE_PART",
                message=f"Duplicate part name '{part_name}' in DESEC container",
                location=f"DESEC.{part_name}",
                suggestion="Use unique part names for each DESEC statement"
            ))
        seen_parts.add(part_name)
    
    # Check for consistent thickness definitions
    parts_with_thickness = container.get_with_thickness()
    parts_without_thickness = [item for item in container.items if item.th == 0.0]
    
    if len(parts_with_thickness) > 0 and len(parts_without_thickness) > 0:
        issues.append(ValidationIssue(
            severity="info",
            code="DESEC_MIXED_THICKNESS",
            message=f"Mixed thickness definitions: {len(parts_with_thickness)} with thickness, {len(parts_without_thickness)} without",
            location="DESEC container",
            suggestion="Consider consistent thickness definition approach"
        ))
    
    return issues


@model_rule('DESEC')
def validate_desec_model(statement: 'DESEC', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate DESEC statement against the complete model."""
    issues = []
    
    if context.full_model is None:
        return issues
    
    model = context.full_model
    
    # Check if part is referenced by XTFIL
    if hasattr(model, 'xtfil'):
        xtfil_parts = []
        for xtfil_item in model.xtfil.items if hasattr(model.xtfil, 'items') else []:
            if hasattr(xtfil_item, 'pa'):
                xtfil_parts.append(xtfil_item.pa)
        
        if statement.pa not in xtfil_parts:
            issues.append(ValidationIssue(
                severity="info",
                code="DESEC_PART_NO_XTFIL",
                message=f"DESEC part '{statement.pa}' not referenced by any XTFIL statement",
                location=f"DESEC.{statement.pa}",
                suggestion="Consider adding XTFIL statement for plotting or remove unused DESEC"
            ))
    
    # Check consistency with LOADC for design cases
    if hasattr(model, 'loadc') and len(model.loadc.items) > 0:
        if statement.th == 0.0:
            issues.append(ValidationIssue(
                severity="warning",
                code="DESEC_NO_THICKNESS_WITH_LOADC",
                message=f"DESEC part '{statement.pa}' has no thickness but LOADC defined",
                location=f"DESEC.{statement.pa}",
                suggestion="Consider defining thickness for design calculations"
            ))
    
    return issues