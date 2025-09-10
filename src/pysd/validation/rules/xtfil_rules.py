"""
Validation rules for XTFIL statements.

Implements three levels of validation:
1. Instance-level: Individual XTFIL statement validation
2. Container-level: XTFIL container validation (filename uniqueness, etc.)
3. Model-level: Cross-container validation (part references, etc.)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.xtfil import XTFIL
    from ...containers.xtfil_container import XtfilContainer
    from ..core import ValidationContext


@instance_rule('XTFIL')
def validate_xtfil_instance(statement: 'XTFIL', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate individual XTFIL statement."""
    issues = []
    
    # Validate plot items
    valid_plot_items = {
        'AX', 'FH', 'TH',  # From OLC-file
        'RE', 'RC', 'TE', 'ST',  # From DEC-file
        'ND', 'DF', 'PF', 'PM', 'PS',  # Design cases
        'PE', 'CS', 'RS', 'TS', 'SC', 'CW', 'TW',  # Design calculations
        'CZ', 'CT', 'MS', 'LF'  # Results
    }
    
    for item in statement.plot_items:
        if item not in valid_plot_items:
            issues.append(ValidationIssue(
                severity="error",
                code="XTFIL_INVALID_PLOT_ITEM",
                message=f"Invalid plot item '{item}' in XTFIL {statement.fn}",
                location=f"XTFIL.{statement.fn}",
                suggestion=f"Use valid plot items: {', '.join(sorted(valid_plot_items))}"
            ))
    
    return issues


@container_rule('XTFIL')
def validate_xtfil_container(container: 'XtfilContainer', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate XTFIL container for consistency and uniqueness."""
    issues = []
    
    # Check for duplicate filenames
    filenames = [item.fn for item in container.items]
    seen_filenames = set()
    for filename in filenames:
        if filename in seen_filenames:
            issues.append(ValidationIssue(
                severity="error",
                code="XTFIL_DUPLICATE_FILENAME",
                message=f"Duplicate filename '{filename}' in XTFIL container",
                location=f"XTFIL.{filename}",
                suggestion="Use unique filenames for each XTFIL statement"
            ))
        seen_filenames.add(filename)
    
    return issues


@model_rule('XTFIL')
def validate_xtfil_model(statement: 'XTFIL', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate XTFIL statement against the complete model."""
    issues = []
    
    if context.full_model is None:
        return issues
    
    model = context.full_model
    
    # Check if structural part exists in DESEC statements
    if hasattr(model, 'desec'):
        desec_parts = []
        for desec_item in model.desec.items if hasattr(model.desec, 'items') else []:
            if hasattr(desec_item, 'pa'):
                desec_parts.append(desec_item.pa)
        
        if desec_parts and statement.pa not in desec_parts:
            available_parts = ", ".join(desec_parts[:5])  # Show first 5 parts
            if len(desec_parts) > 5:
                available_parts += ", ..."
            
            issues.append(ValidationIssue(
                severity="error",
                code="XTFIL_PART_NOT_IN_DESEC",
                message=f"XTFIL part '{statement.pa}' not found in DESEC definitions",
                location=f"XTFIL.{statement.fn}",
                suggestion=f"Define part in DESEC first or use existing parts: {available_parts}"
            ))
    
    return issues
