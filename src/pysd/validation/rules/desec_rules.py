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
    from ...model.base_container import BaseContainer
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
def validate_desec_container(container: 'BaseContainer[DESEC]', context: 'ValidationContext') -> List[ValidationIssue]:
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
    
    # Check if part exists in SHSEC
    if hasattr(model, 'shsec'):
        shsec_parts = []
        for shsec_item in model.shsec.items if hasattr(model.shsec, 'items') else []:
            if hasattr(shsec_item, 'pa'):
                shsec_parts.append(shsec_item.pa)
        
        if statement.pa not in shsec_parts:
            available_parts = ", ".join(shsec_parts[:5])  # Show first 5 parts
            if len(shsec_parts) > 5:
                available_parts += ", ..."
            
            issues.append(ValidationIssue(
                severity="error",
                code="DESEC_PART_NOT_IN_SHSEC",
                message=f"DESEC part '{statement.pa}' not found in SHSEC definitions",
                location=f"DESEC.{statement.pa}",
                suggestion=f"Define part in SHSEC first or use existing parts: {available_parts}"
            ))
    else:
        # No SHSEC container exists at all
        issues.append(ValidationIssue(
            severity="error",
            code="DESEC_NO_SHSEC_CONTAINER",
            message=f"DESEC part '{statement.pa}' requires SHSEC definitions but no SHSEC container exists",
            location=f"DESEC.{statement.pa}",
            suggestion="Add SHSEC statements to define shell sections before using DESEC"
        ))
    
    return issues