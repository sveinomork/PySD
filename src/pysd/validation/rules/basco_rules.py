"""All validation rules for BASCO statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.basco import BASCO

# Instance-level validation rules
@instance_rule('BASCO')
def validate_basco_id_range(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate BASCO ID range."""
    if not 1 <= obj.id <= 99999999:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-ID-001",
            message=f"BASCO ID {obj.id} out of valid range 1-99999999",
            location=f"BASCO.{obj.id}",
            suggestion="Use ID between 1 and 99999999"
        )]
    return []

@instance_rule('BASCO')
def validate_basco_load_cases_count(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate load cases count."""
    if not obj.load_cases:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-LOADCASES-001",
            message="BASCO must have at least one load case",
            location=f"BASCO.{obj.id}",
            suggestion="Add at least one load case"
        )]
    elif len(obj.load_cases) > 300:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-LOADCASES-002",
            message=f"BASCO has {len(obj.load_cases)} load cases, maximum 300 allowed",
            location=f"BASCO.{obj.id}",
            suggestion="Reduce number of load cases to 300 or fewer"
        )]
    return []

@instance_rule('BASCO')
def validate_basco_text_length(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate text length."""
    if obj.txt and len(obj.txt) > 80:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-TXT-001",
            message=f"BASCO text length {len(obj.txt)} exceeds maximum 80 characters",
            location=f"BASCO.{obj.id}.txt",
            suggestion="Reduce text description to 80 characters or fewer"
        )]
    return []

@instance_rule('BASCO')
def validate_load_factor_ranges(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate load factor ranges."""
    issues = []
    for i, load_case in enumerate(obj.load_cases):
        if abs(load_case.lc_fact) > 999.0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="BASCO-FACTOR-001",
                message=f"Load factor {load_case.lc_fact} exceeds recommended range ±999.0",
                location=f"BASCO.{obj.id}.load_cases[{i}]",
                suggestion="Consider reducing load factor to avoid numerical issues"
            ))
    return issues

# Container-level validation rules
@container_rule('BASCO')
def validate_basco_uniqueness(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate BASCO ID uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.id):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-DUP-001",
            message=f"Duplicate BASCO ID {obj.id} found",
            location=f"BASCO.{obj.id}",
            suggestion="Use a unique BASCO ID"
        )]
    return []

# Model-level validation rules (cross-container)
@model_rule('BASCO')
def validate_bas_references_exist(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that BAS references exist in BASCO container."""
    issues = []
    
    if not context.full_model:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        return issues
    
    for i, load_case in enumerate(obj.load_cases):
        if load_case.lc_type == 'BAS' and load_case.lc_numb != obj.id:
            if not basco_container.contains(load_case.lc_numb):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="BASCO-BAS-REF-001",
                    message=f"BASCO {obj.id} references non-existent BAS {load_case.lc_numb}",
                    location=f"BASCO.{obj.id}.load_cases[{i}]",
                    suggestion=f"Add BASCO with ID {load_case.lc_numb}"
                ))
    return issues

@model_rule('BASCO')
def validate_elc_references_exist(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that ELC references can only be used when GRECO statements exist."""
    issues = []
    
    if not context.full_model:
        return issues
    
    greco_container = getattr(context.full_model, 'greco', None)
    if greco_container is None:
        return issues
    
    for i, load_case in enumerate(obj.load_cases):
        if load_case.lc_type == 'ELC':
            # Check if any GRECO statements exist in the model
            has_greco = len(list(greco_container)) > 0
            
            if not has_greco:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="BASCO-ELC-REF-001",
                    message=f"BASCO {obj.id} ELC {load_case.lc_numb} cannot be used without GRECO statements",
                    location=f"BASCO.{obj.id}.load_cases[{i}]",
                    suggestion=f"Add GRECO statement or use OLC instead of ELC"
                ))
            else:
                # If GRECO exists, ELC should reference the same numbers as OLC
                loadc_container = getattr(context.full_model, 'loadc', None)
                if loadc_container is not None:
                    # Check if ELC number exists as OLC in any LOADC
                    olc_found = any(loadc.is_olc(load_case.lc_numb) for loadc in loadc_container)
                    
                    if not olc_found:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR.value,
                            code="BASCO-ELC-REF-002",
                            message=f"BASCO {obj.id} ELC {load_case.lc_numb} not found as OLC in LOADC",
                            location=f"BASCO.{obj.id}.load_cases[{i}]",
                            suggestion=f"Add LOADC with OLC {load_case.lc_numb} or use existing OLC number"
                        ))
    return issues

@model_rule('BASCO')
def validate_olc_references_exist(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that OLC references exist in LOADC container."""
    issues = []
    
    if not context.full_model:
        return issues
    
    loadc_container = getattr(context.full_model, 'loadc', None)
    if loadc_container is None:
        return issues
    
    for i, load_case in enumerate(obj.load_cases):
        if load_case.lc_type == 'OLC':
            # Check if OLC exists in any LOADC
            olc_found = any(loadc.is_olc(load_case.lc_numb) for loadc in loadc_container)
            
            if not olc_found:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="BASCO-OLC-REF-001",
                    message=f"BASCO {obj.id} OLC {load_case.lc_numb} not found in LOADC",
                    location=f"BASCO.{obj.id}.load_cases[{i}]",
                    suggestion=f"Add LOADC with OLC {load_case.lc_numb}"
                ))
    return issues

@model_rule('BASCO')
def validate_no_circular_bas_references(obj: 'BASCO', context: ValidationContext) -> List[ValidationIssue]:
    """Validate no circular BAS references exist."""
    issues = []
    
    if not context.full_model:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        return issues
    
    # Check for circular references using depth-first search
    visited = set()
    rec_stack = set()
    
    def has_cycle(current_id: int) -> bool:
        if current_id in rec_stack:
            return True  # Back edge found = cycle
        if current_id in visited:
            return False
        
        visited.add(current_id)
        rec_stack.add(current_id)
        
        current_basco = basco_container.get_by_id(current_id)
        if current_basco:
            for load_case in current_basco.load_cases:
                if load_case.lc_type == 'BAS':
                    if has_cycle(load_case.lc_numb):
                        return True
        
        rec_stack.remove(current_id)
        return False
    
    if has_cycle(obj.id):
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="BASCO-CIRCULAR-001",
            message=f"Circular BAS reference detected starting from BASCO {obj.id}",
            location=f"BASCO.{obj.id}",
            suggestion="Remove circular BAS references to avoid infinite loops"
        ))
    
    return issues