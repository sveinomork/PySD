"""
Validation rules for DECAS (Design Case) statements.

Implements three levels of validation:
1. Instance-level: Individual DECAS statement validation
2. Container-level: DECAS container validation (uniqueness, consistency)
3. Model-level: Cross-container validation (GRECO references, load case references)
"""

from typing import List, TYPE_CHECKING
from ..core import ValidationIssue
from ..rule_system import instance_rule, container_rule, model_rule

if TYPE_CHECKING:
    from ...statements.decas import DECAS
    from ..core import ValidationContext


@instance_rule("DECAS")
def validate_decas_instance(
    statement: "DECAS", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate individual DECAS statement."""
    issues = []

    # Validate load scenario
    if statement.ls not in ["ULS", "SLS", "ALS", "FLS"]:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="DECAS_LS_UNKNOWN",
                message=f"DECAS uses unknown load scenario '{statement.ls}'. Common values: ULS, SLS, ALS, FLS",
                location=f"DECAS.{statement.ls}",
                suggestion="Verify the load scenario abbreviation",
            )
        )

    # Validate BAS format if it's a string
    if isinstance(statement.bas, str):
        # Check for valid range format (e.g., "400-409", "101-102")
        if "-" in statement.bas:
            try:
                parts = statement.bas.split("-")
                if len(parts) == 2:
                    start, end = int(parts[0]), int(parts[1])
                    if start > end:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                code="DECAS_BAS_RANGE_INVALID",
                                message=f"DECAS has invalid load case range '{statement.bas}' (start > end)",
                                location=f"DECAS.{statement.ls}",
                                suggestion="Ensure first value is less than or equal to second value",
                            )
                        )
                    elif start <= 0 or end <= 0:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                code="DECAS_BAS_RANGE_NEGATIVE",
                                message=f"DECAS has invalid load case range '{statement.bas}' (negative values)",
                                location=f"DECAS.{statement.ls}",
                                suggestion="Use positive load case numbers",
                            )
                        )
            except ValueError:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="DECAS_BAS_FORMAT_INVALID",
                        message=f"DECAS has invalid BAS format '{statement.bas}'",
                        location=f"DECAS.{statement.ls}",
                        suggestion="Use format like '101-102' or valid CaseBuilder expression",
                    )
                )

    return issues


@container_rule("DECAS")
def validate_decas_container(
    container, context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate DECAS container for consistency."""
    issues = []

    # Check for duplicate load scenarios
    scenarios = [stmt.ls for stmt in container]
    scenario_counts = {}
    for scenario in scenarios:
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

    for scenario, count in scenario_counts.items():
        if count > 1:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="DECAS_DUPLICATE_SCENARIO",
                    message=f"Multiple DECAS statements found for scenario '{scenario}' ({count} occurrences)",
                    location=f"DECAS container",
                    suggestion="Consider consolidating or verify if multiple cases are intentional",
                )
            )

    # Check for common load scenarios
    common_scenarios = {"ULS", "SLS"}
    defined_scenarios = set(scenarios)
    missing_common = common_scenarios - defined_scenarios

    if missing_common:
        issues.append(
            ValidationIssue(
                severity="info",
                code="DECAS_MISSING_COMMON_SCENARIOS",
                message=f"Common load scenarios not defined: {', '.join(missing_common)}",
                location="DECAS container",
                suggestion="Consider adding missing scenarios if applicable to your analysis",
            )
        )

    return issues


def collect_load_case_references_from_decas(instance: "DECAS") -> list[int]:
    """
    Extract all load case numbers referenced in a DECAS instance.

    Args:
        instance: DECAS instance to examine

    Returns:
        List of load case numbers
    """
    load_cases = []

    # Check all Case fields for load case references
    case_fields = ["ilc", "olc", "plc", "elc", "bas"]

    for field_name in case_fields:
        field_value = getattr(instance, field_name, None)
        if field_value is not None:
            # Handle Cases objects - extract ranges
            if hasattr(field_value, "ranges") and field_value.ranges:
                for range_item in field_value.ranges:
                    if isinstance(range_item, tuple):
                        # Range like (101, 106)
                        start, end = range_item
                        load_cases.extend(range(start, end + 1))
                    else:
                        # Single number like 101
                        load_cases.append(range_item)

            # Handle string representations that might contain ranges
            elif isinstance(field_value, str):
                # Look for range patterns like "101-106", "400-409"
                import re

                # Match patterns like "101-106" or "400-409:A"
                range_matches = re.findall(r"(\d+)-(\d+)", field_value)
                for start_str, end_str in range_matches:
                    start, end = int(start_str), int(end_str)
                    load_cases.extend(range(start, end + 1))

                # Also match single numbers (but avoid double-counting from ranges)
                single_matches = re.findall(r"\b(\d+)\b", field_value)
                # Convert range matches to actual ranges for overlap checking
                range_sets = []
                for start_str, end_str in range_matches:
                    start, end = int(start_str), int(end_str)
                    range_sets.append(set(range(start, end + 1)))

                for num_str in single_matches:
                    num = int(num_str)
                    # Check if this number is already covered by a range
                    is_in_range = any(num in range_set for range_set in range_sets)
                    if not is_in_range:
                        load_cases.append(num)

    return list(set(load_cases))  # Remove duplicates


def collect_greco_references_from_decas(instance: "DECAS") -> list[str]:
    """
    Extract all GRECO references from a DECAS instance.

    Args:
        instance: DECAS instance to examine

    Returns:
        List of GRECO reference strings
    """
    greco_refs = []

    # Check all Case fields for GRECO references
    case_fields = ["ilc", "olc", "plc", "elc", "bas"]

    for field_name in case_fields:
        field_value = getattr(instance, field_name, None)
        if field_value is not None:
            # Handle Cases objects - check the 'greco' attribute
            if hasattr(field_value, "greco") and field_value.greco:
                greco_refs.append(field_value.greco)

            # Handle string representations that might contain GRECO references
            elif isinstance(field_value, str):
                # Look for GRECO patterns like ":A", ":B", etc.
                import re

                greco_matches = re.findall(r":([A-Z])", field_value)
                greco_refs.extend(greco_matches)

    return list(set(greco_refs))  # Remove duplicates


@model_rule("DECAS")
def validate_decas_model(
    statement: "DECAS", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate DECAS statement against the complete model."""
    issues = []

    if context.full_model is None:
        return issues

    model = context.full_model

    # Collect GRECO references from this DECAS statement
    try:
        greco_refs = collect_greco_references_from_decas(statement)
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to extract GRECO references from DECAS: {e}", exc_info=True)
        
        issues.append(
            ValidationIssue(
                severity="error",
                code="DECAS_GRECO_EXTRACTION_ERROR",
                message=f"Failed to extract GRECO references: {e}",
                location=f"DECAS.{statement.ls}",
            )
        )
        return issues

    if greco_refs:
        # Get all defined GRECO IDs using container access
        defined_greco_ids = []
        if hasattr(model, "greco") and hasattr(model.greco, "items"):
            for item in model.greco.items:
                if hasattr(item, "id") and item.id:
                    defined_greco_ids.append(item.id)

        # Check each referenced GRECO ID
        for greco_id in greco_refs:
            if greco_id not in defined_greco_ids:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="DECAS_GRECO_NOT_FOUND",
                        message=f"DECAS {statement.ls} references GRECO '{greco_id}' not found in model",
                        location=f"DECAS.{statement.ls}",
                        suggestion=f"Define GRECO '{greco_id}' or use one of: {', '.join(defined_greco_ids) if defined_greco_ids else 'None defined'}",
                    )
                )

    # Collect load case references from this DECAS statement
    try:
        referenced_load_cases = collect_load_case_references_from_decas(statement)
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to extract load case references from DECAS: {e}", exc_info=True)
        
        issues.append(
            ValidationIssue(
                severity="error",
                code="DECAS_LOAD_CASE_EXTRACTION_ERROR",
                message=f"Failed to extract load case references: {e}",
                location=f"DECAS.{statement.ls}",
            )
        )
        return issues

    if referenced_load_cases:
        # Get all defined load case IDs from BASCO statements only
        # DECAS should only reference load cases that have explicit BASCO definitions
        defined_load_cases = set()

        # Check BASCO containers
        if hasattr(model, "basco") and hasattr(model.basco, "items"):
            for item in model.basco.items:
                if hasattr(item, "id") and item.id:
                    defined_load_cases.add(item.id)

        # Note: We intentionally do NOT include LOADC ranges here
        # DECAS should only reference load cases with explicit BASCO definitions

        # Check for missing load cases
        missing_cases = [
            lc for lc in referenced_load_cases if lc not in defined_load_cases
        ]

        if missing_cases:
            # Limit the number of missing cases shown to avoid spam
            if len(missing_cases) <= 10:
                missing_list = missing_cases
            else:
                missing_list = missing_cases[:10] + ["..."]

            issues.append(
                ValidationIssue(
                    severity="error",
                    code="DECAS_LOAD_CASES_NOT_FOUND",
                    message=f"DECAS {statement.ls} references undefined load cases: {missing_list}",
                    location=f"DECAS.{statement.ls}",
                    suggestion=f"Define missing load cases as BASCO statements. Defined BASCO IDs: {sorted(list(defined_load_cases)) if defined_load_cases else 'None'}",
                )
            )

    return issues
