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

if TYPE_CHECKING:
    from ...statements.retyp import RETYP
    from ...containers.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule('RETYP')
def validate_retyp_instance(statement: 'RETYP', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate individual RETYP statement."""
    issues = []
    
    # ID range validation (moved from Pydantic validator)
    if not (1 <= statement.id <= 99999999):
        issues.append(ValidationIssue(
            severity="error",
            code="RETYP_ID_RANGE",
            message=f"RETYP ID {statement.id} must be between 1 and 99999999",
            location=f"RETYP.{statement.id}",
            suggestion="Use an ID value between 1 and 99999999"
        ))
    
    # Label length validation (moved from Pydantic validator)
    if statement.lb is not None and len(statement.lb) > 16:
        issues.append(ValidationIssue(
            severity="error",
            code="RETYP_LABEL_LENGTH",
            message=f"RETYP {statement.id} label '{statement.lb}' exceeds 16 characters",
            location=f"RETYP.{statement.id}",
            suggestion="Use a label with 16 characters or less"
        ))
    
    # Positive values validation (moved from Pydantic validator)
    positive_fields = {
        'ar': 'cross-sectional area',
        'nr': 'number of rebars', 
        'di': 'diameter',
        'cc': 'center distance',
        'c2': 'nominal cover',
        'th': 'thickness',
        'bc': 'bond coefficient'
    }
    
    for field_name, field_desc in positive_fields.items():
        field_value = getattr(statement, field_name, None)
        if field_value is not None and field_value <= 0:
            issues.append(ValidationIssue(
                severity="error",
                code="RETYP_NEGATIVE_VALUE",
                message=f"RETYP {statement.id} {field_desc} ({field_name.upper()}={field_value}) must be positive",
                location=f"RETYP.{statement.id}",
                suggestion=f"Use a positive value for {field_desc}"
            ))
    
    # Offset validation (moved from Pydantic validator) - can be zero or positive
    if statement.os is not None and statement.os < 0:
        issues.append(ValidationIssue(
            severity="error",
            code="RETYP_NEGATIVE_OFFSET",
            message=f"RETYP {statement.id} offset (OS={statement.os}) cannot be negative",
            location=f"RETYP.{statement.id}",
            suggestion="Use zero or positive offset value"
        ))
    
    # Method consistency validation
    has_area_method = statement.ar is not None
    has_count_method = statement.nr is not None and statement.di is not None
    
    if not has_area_method and not has_count_method:
        issues.append(ValidationIssue(
            severity="error",
            code="RETYP_METHOD_MISSING",
            message=f"RETYP {statement.id} must use either area method (AR) or count method (NR+DI)",
            location=f"RETYP.{statement.id}",
            suggestion="Provide either AR parameter or both NR and DI parameters"
        ))
    
   
    
    # Diameter unit validation
    if statement.di is not None:
        if statement.di > 1.0:
            # Likely in mm
            if statement.di > 100:  # Very large diameter
                issues.append(ValidationIssue(
                    severity="warning",
                    code="RETYP_DIAMETER_LARGE",
                    message=f"RETYP {statement.id} has large diameter {statement.di}mm",
                    location=f"RETYP.{statement.id}",
                    suggestion="Verify diameter value and units"
                ))
        else:
            # Likely in m
            if statement.di < 0.005:  # Very small diameter (< 5mm)
                issues.append(ValidationIssue(
                    severity="warning",
                    code="RETYP_DIAMETER_SMALL",
                    message=f"RETYP {statement.id} has small diameter {statement.di}m",
                    location=f"RETYP.{statement.id}",
                    suggestion="Verify diameter value and units"
                ))
    
    # Bond coefficient validation
    if statement.bc is not None:
        if not 0.1 <= statement.bc <= 1.0:
            issues.append(ValidationIssue(
                severity="warning",
                code="RETYP_BOND_COEFFICIENT",
                message=f"RETYP {statement.id} bond coefficient {statement.bc} outside typical range (0.1-1.0)",
                location=f"RETYP.{statement.id}",
                suggestion="Verify bond coefficient value"
            ))
    
    return issues


@container_rule('RETYP')
def validate_retyp_container(container: 'BaseContainer[RETYP]', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate RETYP container for consistency and uniqueness."""
    issues = []
    
    # Check for duplicate IDs
    ids = [stmt.id for stmt in container.items]
    seen_ids = set()
    for stmt_id in ids:
        if stmt_id in seen_ids:
            issues.append(ValidationIssue(
                severity="error",
                code="RETYP_DUPLICATE_ID",
                message=f"Duplicate RETYP ID {stmt_id} found in container",
                location=f"RETYP.{stmt_id}",
                suggestion="Use unique IDs for each RETYP statement"
            ))
        seen_ids.add(stmt_id)
    
    # Check for consistent material references using generic container methods
    materials = set()
    for stmt in container.items:
        if stmt.mp is not None:
            materials.add(stmt.mp)
    
    if len(materials) > 10:  # Arbitrary threshold
        issues.append(ValidationIssue(
            severity="info",
            code="RETYP_MANY_MATERIALS",
            message=f"Container has {len(materials)} different material references",
            location="RETYP container",
            suggestion="Consider consolidating material properties for consistency"
        ))
    
    # Check for mixed methods using generic filtering
    area_method_statements = [stmt for stmt in container.items if stmt.ar is not None]
    count_method_statements = [stmt for stmt in container.items if stmt.nr is not None and stmt.di is not None]
    
    if len(area_method_statements) > 0 and len(count_method_statements) > 0:
        issues.append(ValidationIssue(
            severity="info",
            code="RETYP_MIXED_METHODS",
            message=f"Container uses mixed calculation methods: {len(area_method_statements)} area, {len(count_method_statements)} count",
            location="RETYP container",
            suggestion="Consider standardizing on one calculation method"
        ))
    
    return issues


@model_rule('RETYP')
def validate_retyp_model(statement: 'RETYP', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate RETYP statement against the complete model."""
    issues = []
    
    if context.full_model is None:
        return issues
    
    model = context.full_model
    
    # Check material property references
    if statement.mp is not None:
        # Check if material exists in RMPEC container
        if hasattr(model, 'rmpec') and not model.rmpec.has_id(statement.mp):
            issues.append(ValidationIssue(
                severity="error",
                code="RETYP_MATERIAL_NOT_FOUND",
                message=f"RETYP {statement.id} references material {statement.mp} not found in RMPEC",
                location=f"RETYP.{statement.id}",
                suggestion="Define the referenced material in RMPEC or update the MP reference"
            ))
    
    # Check if this RETYP is referenced by any RELOC statements
    if hasattr(model, 'reloc'):
        # Use generic filtering to find RELOC statements that reference this RETYP
        referencing_relocs = []
        if hasattr(model.reloc, 'items'):
            referencing_relocs = [reloc for reloc in model.reloc.items if hasattr(reloc, 'rt') and reloc.rt == statement.id]
        
        if not referencing_relocs:
            issues.append(ValidationIssue(
                severity="warning",
                code="RETYP_UNUSED",
                message=f"RETYP {statement.id} is not referenced by any RELOC statements",
                location=f"RETYP.{statement.id}",
                suggestion="Remove unused RETYP or add corresponding RELOC statements"
            ))
    
    # Cross-validate with other RETYP statements for consistency
    if hasattr(model, 'retyp'):
        similar_retyps = []
        for other_retyp in model.retyp.items if hasattr(model.retyp, 'items') else []:
            if (other_retyp.id != statement.id and 
                other_retyp.mp == statement.mp and
                abs((other_retyp.di or 0) - (statement.di or 0)) < 0.001):
                similar_retyps.append(other_retyp)
        
        if similar_retyps:
            other_ids = [str(r.id) for r in similar_retyps]
            issues.append(ValidationIssue(
                severity="info",
                code="RETYP_SIMILAR_DEFINITION",
                message=f"RETYP {statement.id} has similar properties to RETYP {', '.join(other_ids)}",
                location=f"RETYP.{statement.id}",
                suggestion="Consider consolidating similar rebar type definitions"
            ))
    
    return issues
