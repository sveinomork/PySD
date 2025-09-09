"""All validation rules for LOADC statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.loadc import LOADC

# Instance-level validation rules
@instance_rule('LOADC')
def validate_loadc_run_number(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate LOADC run number range."""
    # Skip validation if run_number is None (it will be auto-set from alc if needed)
    if obj.run_number is None:
        return []
        
    if not 1 <= obj.run_number <= 99999:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="LOADC-RUN-001",
            message=f"LOADC run number {obj.run_number} out of valid range 1-99999",
            location=f"LOADC.{obj.run_number}",
            suggestion="Use run number between 1 and 99999"
        )]
    return []

@instance_rule('LOADC')
def validate_loadc_alc_range(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate ALC range."""
    issues = []
    if obj.alc and hasattr(obj.alc, 'to_list'):
        # Get all ALC values from the Cases object
        alc_values = obj.alc.to_list()
        for alc_value in alc_values:
            if not 1 <= alc_value <= 99999999:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="LOADC-ALC-RANGE-001",
                    message=f"ALC value {alc_value} outside valid range 1-99999999",
                    location=f"LOADC.{obj.run_number}.alc",
                    suggestion="Use ALC numbers between 1 and 99999999"
                ))
    return issues

@instance_rule('LOADC')
def validate_loadc_olc_range(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate OLC range."""
    issues = []
    if obj.olc and hasattr(obj.olc, 'to_list'):
        # Get all OLC values from the Cases object
        olc_values = obj.olc.to_list()
        for olc_value in olc_values:
            if not 1 <= olc_value <= 99999999:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="LOADC-OLC-RANGE-001",
                    message=f"OLC value {olc_value} outside valid range 1-99999999",
                    location=f"LOADC.{obj.run_number}.olc",
                    suggestion="Use OLC numbers between 1 and 99999999"
                ))
    return issues

@instance_rule('LOADC')
def validate_loadc_ranges_consistency(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that ALC and OLC ranges have same count."""
    issues = []
    if obj.alc and obj.olc and hasattr(obj.alc, 'to_list') and hasattr(obj.olc, 'to_list'):
        alc_count = len(obj.alc.to_list())
        olc_count = len(obj.olc.to_list())
        
        if alc_count != olc_count:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="LOADC-RANGE-MISMATCH-001",
                message=f"ALC range has {alc_count} items but OLC range has {olc_count} items",
                location=f"LOADC.{obj.run_number}",
                suggestion="Ensure ALC and OLC ranges have the same number of items"
            ))
    return issues

# Container-level validation rules
@container_rule('LOADC')
def validate_loadc_uniqueness(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate LOADC run number uniqueness in container."""
    if context.parent_container and context.parent_container.contains(obj.run_number):
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="LOADC-DUP-001",
            message=f"Duplicate LOADC run number {obj.run_number} found",
            location=f"LOADC.{obj.run_number}",
            suggestion="Use a unique LOADC run number"
        )]
    return []

@container_rule('LOADC')
def validate_olc_overlap(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that OLC ranges don't overlap between LOADC statements."""
    issues = []
    
    if not context.parent_container or not obj.olc:
        return issues
    
    obj_olc_start, obj_olc_end = obj.olc
    obj_olc_set = set(range(obj_olc_start, obj_olc_end + 1))
    
    for existing_loadc in context.parent_container:
        if existing_loadc.run_number != obj.run_number and existing_loadc.olc:
            exist_olc_start, exist_olc_end = existing_loadc.olc
            exist_olc_set = set(range(exist_olc_start, exist_olc_end + 1))
            
            overlap = obj_olc_set.intersection(exist_olc_set)
            if overlap:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING.value,
                    code="LOADC-OLC-OVERLAP-001",
                    message=f"OLC range {obj_olc_start}-{obj_olc_end} overlaps with LOADC {existing_loadc.run_number} OLC range {exist_olc_start}-{exist_olc_end}",
                    location=f"LOADC.{obj.run_number}.olc",
                    suggestion="Consider using non-overlapping OLC ranges"
                ))
    
    return issues

# Model-level validation rules (cross-container)
@model_rule('LOADC')
def validate_loadc_usage_in_statements(obj: 'LOADC', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that LOADC OLCs are used in other statements."""
    issues = []
    
    if not context.full_model or not obj.olc:
        return issues
    
    # Check if any BASCO uses this LOADC's OLCs as ELC
    basco_container = getattr(context.full_model, 'basco', None)
    greco_container = getattr(context.full_model, 'greco', None)
    
    olc_start, olc_end = obj.olc
    olc_numbers = set(range(olc_start, olc_end + 1))
    used_olcs = set()
    
    # Check BASCO usage
    if basco_container:
        for basco in basco_container:
            for load_case in basco.load_cases:
                if load_case.lc_type == 'ELC' and load_case.lc_numb in olc_numbers:
                    used_olcs.add(load_case.lc_numb)
    
    # Check GRECO usage
    if greco_container:
        for greco in greco_container:
            if greco.elc:
                elc_numbers = greco.elc.to_list()
                for elc_num in elc_numbers:
                    if elc_num in olc_numbers:
                        used_olcs.add(elc_num)
    
    # Check for unused OLCs
    unused_olcs = olc_numbers - used_olcs
    if len(unused_olcs) > 5:  # Only warn if many are unused
        issues.append(ValidationIssue(
            severity=ValidationSeverity.INFO.value,
            code="LOADC-UNUSED-001",
            message=f"LOADC {obj.run_number} has {len(unused_olcs)} unused OLCs out of {len(olc_numbers)}",
            location=f"LOADC.{obj.run_number}.olc",
            suggestion="Consider reducing OLC range or ensure OLCs are used in BASCO/GRECO"
        ))
    
    return issues