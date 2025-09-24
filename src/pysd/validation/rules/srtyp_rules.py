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
    from ...statements.srtyp import SRTYP
    from ...containers.base_container import BaseContainer
    from ..core import ValidationContext


@instance_rule('SRTYP')
def validate_srtyp_instance(statement: 'SRTYP', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate individual SRTYP statement."""
    issues = []
    
    # ID range validation (moved from Pydantic validator)
    if not (1 <= statement.id <= 99999999):
        issues.append(ValidationIssue(
            severity="error",
            code="SRTYP_ID_RANGE",
            message=f"SRTYP ID {statement.id} must be between 1 and 99999999",
            location=f"SRTYP.{statement.id}",
            suggestion="Use an ID value between 1 and 99999999"
        ))
    
    # Label length validation (moved from Pydantic validator)
    if statement.lb is not None and len(statement.lb) > 16:
        issues.append(ValidationIssue(
            severity="error",
            code="SRTYP_LABEL_LENGTH",
            message=f"SRTYP {statement.id} label '{statement.lb}' exceeds 16 characters",
            location=f"SRTYP.{statement.id}",
            suggestion="Use a label with 16 characters or less"
        ))
    
    # Positive values validation (moved from Pydantic validator)
    positive_fields = {
        'ar': 'cross-sectional area',
        'nr': 'number of rebars', 
        'di': 'diameter',
        'c1': 'center distance',
        'c2': 'nominal cover'
    }
    
    for field_name, field_desc in positive_fields.items():
        field_value = getattr(statement, field_name, None)
        if field_value is not None and field_value <= 0:
            issues.append(ValidationIssue(
                severity="error",
                code="SRTYP_NEGATIVE_VALUE",
                message=f"SRTYP {statement.id} {field_desc} ({field_name.upper()}={field_value}) must be positive",
                location=f"SRTYP.{statement.id}",
                suggestion=f"Use a positive value for {field_desc}"
            ))

    
    # Method consistency validation
    has_area_method = statement.ar is not None
    has_count_method = statement.nr is not None and statement.di is not None
    
    if not has_area_method and not has_count_method:
        issues.append(ValidationIssue(
            severity="error",
            code="SRTYP_METHOD_MISSING",
            message=f"SRTYP {statement.id} must use either area method (AR) or count method (NR+DI)",
            location=f"SRTYP.{statement.id}",
            suggestion="Provide either AR parameter or both NR and DI parameters"
        ))
    
   
    
    # Diameter unit validation
    if statement.di is not None:
        if statement.di > 1.0:
            # Likely in mm
            if statement.di > 100:  # Very large diameter
                issues.append(ValidationIssue(
                    severity="warning",
                    code="SRTYP_DIAMETER_LARGE",
                    message=f"SRTYP {statement.id} has large diameter {statement.di}mm",
                    location=f"SRTYP.{statement.id}",
                    suggestion="Verify diameter value and units"
                ))
        else:
            # Likely in m
            if statement.di < 0.005:  # Very small diameter (< 5mm)
                issues.append(ValidationIssue(
                    severity="warning",
                    code="SRTYP_DIAMETER_SMALL",
                    message=f"SRTYP {statement.id} has small diameter {statement.di}m",
                    location=f"SRTYP.{statement.id}",
                    suggestion="Verify diameter value and units"
                ))
    
    
    
    return issues


@container_rule('SRTYP')
def validate_retyp_container(container: 'BaseContainer[SRTYP]', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate SRTYP container for consistency and uniqueness."""
    issues = []
    
    # Check for duplicate IDs
    ids = [stmt.id for stmt in container.items]
    seen_ids = set()
    for stmt_id in ids:
        if stmt_id in seen_ids:
            issues.append(ValidationIssue(
                severity="error",
                code="SRTYP_DUPLICATE_ID",
                message=f"Duplicate SRTYP ID {stmt_id} found in container",
                location=f"SRTYP.{stmt_id}",
                suggestion="Use unique IDs for each SRTYP statement"
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
            code="SRTYP_MANY_MATERIALS",
            message=f"Container has {len(materials)} different material references",
            location="SRTYP container",
            suggestion="Consider consolidating material properties for consistency"
        ))
    
    # Check for mixed methods using generic filtering
    area_method_statements = [stmt for stmt in container.items if stmt.ar is not None]
    count_method_statements = [stmt for stmt in container.items if stmt.nr is not None and stmt.di is not None]
    
    if len(area_method_statements) > 0 and len(count_method_statements) > 0:
        issues.append(ValidationIssue(
            severity="info",
            code="SRTYP_MIXED_METHODS",
            message=f"Container uses mixed calculation methods: {len(area_method_statements)} area, {len(count_method_statements)} count",
            location="SRTYP container",
            suggestion="Consider standardizing on one calculation method"
        ))
    
    return issues


@model_rule('SRTYP')
def validate_srtyp_model(statement: 'SRTYP', context: 'ValidationContext') -> List[ValidationIssue]:
    """Validate SRTYP statement against the complete model."""
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
                code="SRTYP_MATERIAL_NOT_FOUND",
                message=f"SRTYP {statement.id} references material {statement.mp} not found in RMPEC",
                location=f"SRTYP.{statement.id}",
                suggestion="Define the referenced material in RMPEC or update the MP reference"
            ))

    # Check if this SRTYP is referenced by any SRTLOC statements
    if hasattr(model, 'srloc'):
        # Use generic filtering to find SRTLOC statements that reference this SRTYP
        referencing_srlocs = []
        if hasattr(model.srloc, 'items'):
            referencing_srlocs = [srloc for srloc in model.srloc.items if hasattr(srloc, 'rt') and srloc.rt == statement.id]

        if not referencing_srlocs:
            issues.append(ValidationIssue(
                severity="warning",
                code="SRTYP_UNUSED",
                message=f"SRTYP {statement.id} is not referenced by any SRTLOC statements",
                location=f"SRTYP.{statement.id}",
                suggestion="Remove unused SRTYP or add corresponding SRTLOC statements"
            ))

    # Cross-validate with other SRTYP statements for consistency
    if hasattr(model, 'srtyp'):
        similar_srtips = []
        for other_srtip in model.srtyp.items if hasattr(model.srtyp, 'items') else []:
            if (other_srtip.id != statement.id and 
                other_srtip.mp == statement.mp and
                abs((other_srtip.di or 0) - (statement.di or 0)) < 0.001):
                similar_srtips.append(other_srtip)

        if similar_srtips:
            other_ids = [str(r.id) for r in similar_srtips]
            issues.append(ValidationIssue(
                severity="info",
                code="SRTYP_SIMILAR_DEFINITION",
                message=f"SRTYP {statement.id} has similar properties to SRTYP {', '.join(other_ids)}",
                location=f"SRTYP.{statement.id}",
                suggestion="Consider consolidating similar rebar type definitions"
            ))
    
    return issues
