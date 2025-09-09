"""All validation rules for CASES statements."""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.cases import CASES

# Instance-level validation rules
@instance_rule('CASES')
def validate_cases_bas_ids(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CASES BAS ID ranges."""
    issues = []
    
    for i, bas_id in enumerate(obj.bas_ids):
        if not 1 <= bas_id <= 99999999:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="CASES-BAS-RANGE-001",
                message=f"BAS ID {bas_id} out of valid range 1-99999999",
                location=f"CASES.bas_ids[{i}]",
                suggestion="Use BAS IDs between 1 and 99999999"
            ))
    
    # Check for duplicate BAS IDs within the same CASES
    if len(obj.bas_ids) != len(set(obj.bas_ids)):
        duplicates = [x for x in obj.bas_ids if obj.bas_ids.count(x) > 1]
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CASES-BAS-DUP-001",
            message=f"Duplicate BAS IDs found: {list(set(duplicates))}",
            location="CASES.bas_ids",
            suggestion="Remove duplicate BAS IDs from the CASES statement"
        ))
    
    return issues

@instance_rule('CASES')
def validate_cases_bas_count(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CASES BAS count limits."""
    if not obj.bas_ids:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CASES-BAS-COUNT-001",
            message="CASES must have at least one BAS ID",
            location="CASES.bas_ids",
            suggestion="Add at least one BAS ID to the CASES statement"
        )]
    
    # Check maximum count (typical ShellDesign limit)
    if len(obj.bas_ids) > 1000:
        return [ValidationIssue(
            severity=ValidationSeverity.WARNING.value,
            code="CASES-BAS-COUNT-002",
            message=f"CASES has {len(obj.bas_ids)} BAS IDs, consider if this is necessary",
            location="CASES.bas_ids",
            suggestion="Consider grouping BAS IDs or using ranges if possible"
        )]
    
    return []

@instance_rule('CASES')
def validate_cases_text_length(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CASES text length."""
    if obj.txt and len(obj.txt) > 80:
        return [ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CASES-TXT-001",
            message=f"CASES text length {len(obj.txt)} exceeds maximum 80 characters",
            location="CASES.txt",
            suggestion="Reduce text description to 80 characters or fewer"
        )]
    return []

# Container-level validation rules
@container_rule('CASES')
def validate_cases_bas_overlap(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that BAS IDs don't overlap between different CASES."""
    issues = []
    
    if not context.parent_container:
        return issues
    
    obj_bas_set = set(obj.bas_ids)
    
    for existing_cases in context.parent_container:
        if existing_cases != obj:  # Don't compare with self
            existing_bas_set = set(existing_cases.bas_ids)
            overlap = obj_bas_set.intersection(existing_bas_set)
            
            if overlap:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING.value,
                    code="CASES-BAS-OVERLAP-001",
                    message=f"BAS IDs {sorted(list(overlap))} are used in multiple CASES statements",
                    location="CASES.bas_ids",
                    suggestion="Consider if BAS IDs should be unique across CASES or if overlap is intentional"
                ))
    
    return issues

# Model-level validation rules (cross-container)
@model_rule('CASES')
def validate_cases_bas_references_exist(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that all BAS IDs in CASES exist as BASCO statements."""
    issues = []
    
    if not context.full_model:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        if obj.bas_ids:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="CASES-BAS-NO-CONTAINER",
                message="CASES has BAS references but no BASCO container exists",
                location="CASES.bas_ids",
                suggestion="Add BASCO statements before adding CASES with BAS references"
            ))
        return issues
    
    missing_bas = []
    for bas_id in obj.bas_ids:
        if not basco_container.contains(bas_id):
            missing_bas.append(bas_id)
    
    if missing_bas:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.ERROR.value,
            code="CASES-BAS-REF-001",
            message=f"CASES references non-existent BAS IDs: {missing_bas}",
            location="CASES.bas_ids",
            suggestion=f"Add BASCO statements with IDs {missing_bas} before referencing them in CASES"
        ))
    
    return issues

@model_rule('CASES')
def validate_cases_coverage(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate CASES coverage against available BASCO statements."""
    issues = []
    
    if not context.full_model:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        return issues
    
    # Get all BASCO IDs in the model
    all_basco_ids = set(basco.id for basco in basco_container)
    
    # Check if all CASES together cover all BASCO statements
    cases_container = getattr(context.full_model, 'cases', None)
    if cases_container:
        all_cases_bas_ids = set()
        for cases in cases_container:
            all_cases_bas_ids.update(cases.bas_ids)
        
        uncovered_basco = all_basco_ids - all_cases_bas_ids
        if len(uncovered_basco) > 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO.value,
                code="CASES-COVERAGE-001",
                message=f"BASCO statements {sorted(list(uncovered_basco))} are not covered by any CASES",
                location="CASES",
                suggestion="Consider adding these BASCO IDs to CASES statements if they should be included in analysis"
            ))
    
    return issues

@model_rule('CASES')
def validate_cases_basco_dependencies(obj: 'CASES', context: ValidationContext) -> List[ValidationIssue]:
    """Validate that CASES includes all BAS dependencies."""
    issues = []
    
    if not context.full_model:
        return issues
    
    basco_container = getattr(context.full_model, 'basco', None)
    if not basco_container:
        return issues
    
    # For each BAS in CASES, check if it references other BAS that should also be in CASES
    missing_dependencies = set()
    
    for bas_id in obj.bas_ids:
        basco = basco_container.get_by_id(bas_id)
        if basco:
            for load_case in basco.load_cases:
                if load_case.lc_type == 'BAS' and load_case.lc_numb not in obj.bas_ids:
                    missing_dependencies.add(load_case.lc_numb)
    
    if missing_dependencies:
        issues.append(ValidationIssue(
            severity=ValidationSeverity.WARNING.value,
            code="CASES-DEP-001",
            message=f"CASES includes BAS that reference other BAS not in CASES: {sorted(list(missing_dependencies))}",
            location="CASES.bas_ids",
            suggestion=f"Consider adding BAS {sorted(list(missing_dependencies))} to CASES for complete dependency coverage"
        ))
    
    return issues