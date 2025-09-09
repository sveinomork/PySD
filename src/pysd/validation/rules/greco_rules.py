"""All validation rules for GRECO statements."""

from typing import List, TYPE_CHECKING
import re
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.greco import GRECO

# Instance-level validation rules (run during object creation)
@instance_rule('GRECO')
def validate_greco_id_format(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate GRECO ID format (A-Z)."""
    if not re.match(r'^[A-Z]$', obj.id):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="GRECO-ID-001",
            message=f"GRECO ID '{obj.id}' must be single uppercase letter A-Z",
            location=f'GRECO.{obj.id}',
            suggestion='Use a single uppercase letter from A to Z'
        )]
    return []

@instance_rule('GRECO')
def validate_greco_bas_count(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate BAS count (≤6)."""
    if obj.bas and len(obj.bas.ranges) > 6:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="GRECO-BAS-001", 
            message=f"GRECO has {len(obj.bas.ranges)} BAS combinations, maximum 6 allowed",
            location=f'GRECO.{obj.id}.bas',
            suggestion='Reduce BAS combinations to 6 or fewer'
        )]
    return []

@instance_rule('GRECO')
def validate_greco_elc_count(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate ELC count (≤12)."""
    if obj.elc and len(obj.elc.ranges) > 12:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="GRECO-ELC-001",
            message=f"GRECO has {len(obj.elc.ranges)} ELC combinations, maximum 12 allowed",
            location=f'GRECO.{obj.id}.elc',
            suggestion='Reduce ELC combinations to 12 or fewer'
        )]
    return []

# Container-level validation rules (run when adding to container)
@container_rule('GRECO')
def validate_greco_uniqueness(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate GRECO ID uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.id):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="GRECO-DUP-001",
            message=f"Duplicate GRECO ID '{obj.id}' found",
            location=f'GRECO.{obj.id}',
            suggestion='Use a unique GRECO ID'
        )]
    return []

# Model-level validation rules (run when adding to SD_BASE - cross-container)
@model_rule('GRECO')
def validate_bas_references_exist(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that all BAS references exist as BASCO statements."""
    issues = []
    
    if not context.full_model or not obj.bas:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        if obj.bas:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="GRECO-BAS-NO-CONTAINER",
                message=f"GRECO {obj.id} has BAS references but no BASCO container exists",
                location=f"GRECO.{obj.id}.bas",
                suggestion="Add BASCO statements before adding GRECO with BAS references"
            ))
        return issues
    
    bas_numbers = obj.bas.to_list()
    for bas_num in bas_numbers:
        if not basco_container.contains(bas_num):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="GRECO-BAS-REF-001",
                message=f"GRECO {obj.id} references non-existent BAS {bas_num}",
                location=f"GRECO.{obj.id}.bas",
                suggestion=f"Add BASCO with ID {bas_num} before referencing it in GRECO"
            ))
    
    return issues

@model_rule('GRECO')
def validate_elc_references_exist(obj: 'GRECO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that all ELC references exist as OLC in LOADC statements."""
    issues = []
    
    if not context.full_model or not obj.elc:
        return issues
    
    loadc_container = getattr(context.full_model, 'loadc', None)
    if not loadc_container:
        if obj.elc:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="GRECO-ELC-NO-CONTAINER",
                message=f"GRECO {obj.id} has ELC references but no LOADC container exists",
                location=f"GRECO.{obj.id}.elc",
                suggestion="Add LOADC statements before adding GRECO with ELC references"
            ))
        return issues
    
    elc_numbers = obj.elc.to_list()
    for elc_num in elc_numbers:
        # Check if ELC exists as OLC in any LOADC
        elc_found = any(loadc.is_olc(elc_num) for loadc in loadc_container)
        
        if not elc_found:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="GRECO-ELC-REF-001",
                message=f"GRECO {obj.id} ELC {elc_num} not found as OLC in LOADC",
                location=f"GRECO.{obj.id}.elc",
                suggestion=f"Add LOADC with OLC {elc_num} before referencing it in GRECO"
            ))
    
    return issues