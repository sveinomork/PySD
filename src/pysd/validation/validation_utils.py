"""
Common validation utilities to reduce code duplication.

This module provides reusable validation functions that can be used
across different validation rule files to maintain DRY principles.
"""

from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.base_container import BaseContainer

from .core import ValidationIssue


def check_duplicate_ids(
    container: "BaseContainer",
    statement_type: str,
    error_code_suffix: str = "DUPLICATE_ID",
) -> List[ValidationIssue]:
    """
    Generic duplicate ID checker for any container.

    Args:
        container: Container with items having 'id' attribute
        statement_type: Name for error messages (e.g., "RETYP", "SRTYP")
        error_code_suffix: Suffix for error code (default: "DUPLICATE_ID")

    Returns:
        List of ValidationIssue objects for any duplicate IDs found

    Example:
        >>> issues = check_duplicate_ids(container, "RETYP")
        >>> # Returns issues for any duplicate RETYP IDs
    """
    issues = []
    seen_ids = set()

    for item in container.items:
        if item.id in seen_ids:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"Duplicate {statement_type} ID {item.id} found in container",
                    location=f"{statement_type}.{item.id}",
                    suggestion=f"Use unique IDs for each {statement_type} statement",
                )
            )
        seen_ids.add(item.id)

    return issues


def check_id_range(
    container: "BaseContainer",
    statement_type: str,
    min_id: int,
    max_id: int,
    error_code_suffix: str = "ID_RANGE",
) -> List[ValidationIssue]:
    """
    Check if all IDs in container are within acceptable range.

    Args:
        container: Container with items having 'id' attribute
        statement_type: Name for error messages (e.g., "RETYP")
        min_id: Minimum allowed ID (inclusive)
        max_id: Maximum allowed ID (inclusive)
        error_code_suffix: Suffix for error code (default: "ID_RANGE")

    Returns:
        List of ValidationIssue objects for any IDs out of range

    Example:
        >>> issues = check_id_range(container, "RETYP", 1, 99999999)
        >>> # Returns issues for any RETYP IDs outside [1, 99999999]
    """
    issues = []

    for item in container.items:
        if not (min_id <= item.id <= max_id):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} ID {item.id} must be between {min_id} and {max_id}",
                    location=f"{statement_type}.{item.id}",
                    suggestion=f"Use an ID value between {min_id} and {max_id}",
                )
            )

    return issues


def check_positive_values(
    statement: Any,
    statement_type: str,
    field_descriptions: Dict[str, str],
    error_code_suffix: str = "NEGATIVE_VALUE",
) -> List[ValidationIssue]:
    """
    Check that specified fields have positive values (> 0).

    Args:
        statement: Statement object to validate
        statement_type: Name for error messages (e.g., "RETYP")
        field_descriptions: Dict mapping field names to human-readable descriptions
                          e.g., {"ar": "cross-sectional area", "nr": "number of rebars"}
        error_code_suffix: Suffix for error code (default: "NEGATIVE_VALUE")

    Returns:
        List of ValidationIssue objects for any non-positive values

    Example:
        >>> fields = {"ar": "cross-sectional area", "nr": "number of rebars"}
        >>> issues = check_positive_values(stmt, "RETYP", fields)
        >>> # Returns issues for any ar or nr values <= 0
    """
    issues = []

    for field_name, field_desc in field_descriptions.items():
        field_value = getattr(statement, field_name, None)
        if field_value is not None and field_value <= 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} {statement.id} {field_desc} ({field_name.upper()}={field_value}) must be positive",
                    location=f"{statement_type}.{statement.id}",
                    suggestion=f"Use a positive value for {field_desc}",
                )
            )

    return issues


def check_non_negative_values(
    statement: Any,
    statement_type: str,
    field_descriptions: Dict[str, str],
    error_code_suffix: str = "NEGATIVE_VALUE",
) -> List[ValidationIssue]:
    """
    Check that specified fields have non-negative values (>= 0).

    Args:
        statement: Statement object to validate
        statement_type: Name for error messages (e.g., "RETYP")
        field_descriptions: Dict mapping field names to human-readable descriptions
                          e.g., {"os": "offset"}
        error_code_suffix: Suffix for error code (default: "NEGATIVE_VALUE")

    Returns:
        List of ValidationIssue objects for any negative values

    Example:
        >>> fields = {"os": "offset"}
        >>> issues = check_non_negative_values(stmt, "RETYP", fields)
        >>> # Returns issues for any os values < 0
    """
    issues = []

    for field_name, field_desc in field_descriptions.items():
        field_value = getattr(statement, field_name, None)
        if field_value is not None and field_value < 0:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} {statement.id} {field_desc} ({field_name.upper()}={field_value}) cannot be negative",
                    location=f"{statement_type}.{statement.id}",
                    suggestion=f"Use zero or positive value for {field_desc}",
                )
            )

    return issues


def check_label_length(
    statement: Any,
    statement_type: str,
    max_length: int = 16,
    label_field: str = "lb",
    error_code_suffix: str = "LABEL_LENGTH",
) -> List[ValidationIssue]:
    """
    Check that label field does not exceed maximum length.

    Args:
        statement: Statement object to validate
        statement_type: Name for error messages (e.g., "RETYP")
        max_length: Maximum allowed label length (default: 16)
        label_field: Name of the label field (default: "lb")
        error_code_suffix: Suffix for error code (default: "LABEL_LENGTH")

    Returns:
        List of ValidationIssue objects if label exceeds max length

    Example:
        >>> issues = check_label_length(stmt, "RETYP", max_length=16)
        >>> # Returns issues if stmt.lb is longer than 16 characters
    """
    issues = []
    label_value = getattr(statement, label_field, None)

    if label_value is not None and len(label_value) > max_length:
        issues.append(
            ValidationIssue(
                severity="error",
                code=f"{statement_type}_{error_code_suffix}",
                message=f"{statement_type} {statement.id} label '{label_value}' exceeds {max_length} characters",
                location=f"{statement_type}.{statement.id}",
                suggestion=f"Use a label with {max_length} characters or less",
            )
        )

    return issues


def check_material_reference(
    statement: Any,
    statement_type: str,
    model: Any,
    container_name: str,
    material_field: str = "mp",
    error_code_suffix: str = "MATERIAL_NOT_FOUND",
) -> List[ValidationIssue]:
    """
    Check that material reference exists in specified container.

    Args:
        statement: Statement object to validate
        statement_type: Name for error messages (e.g., "RETYP")
        model: Full model object (SD_BASE instance)
        container_name: Name of container to check (e.g., "rmpec", "temat")
        material_field: Name of material field to validate (default: "mp")
        error_code_suffix: Suffix for error code (default: "MATERIAL_NOT_FOUND")

    Returns:
        List of ValidationIssue objects if material reference not found

    Example:
        >>> issues = check_material_reference(stmt, "RETYP", model, "rmpec")
        >>> # Returns issues if stmt.mp not found in model.rmpec
    """
    issues = []
    material_id = getattr(statement, material_field, None)

    if material_id is not None:
        container = getattr(model, container_name, None)
        if container is None:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} {statement.id} references material {material_id}, but {container_name.upper()} container not found",
                    location=f"{statement_type}.{statement.id}",
                    suggestion=f"Define {container_name.upper()} container with material {material_id}",
                )
            )
        elif not container.has_id(material_id):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} {statement.id} references material {material_id} not found in {container_name.upper()}",
                    location=f"{statement_type}.{statement.id}",
                    suggestion=f"Define the referenced material in {container_name.upper()} or update the {material_field.upper()} reference",
                )
            )

    return issues


def check_unused_definition(
    statement: Any,
    statement_type: str,
    model: Any,
    referencing_container: str,
    reference_field: str,
    error_code_suffix: str = "UNUSED",
) -> List[ValidationIssue]:
    """
    Check if a definition is referenced by any other statements.

    Args:
        statement: Statement object to validate
        statement_type: Name for error messages (e.g., "RETYP")
        model: Full model object (SD_BASE instance)
        referencing_container: Name of container that should reference this (e.g., "reloc")
        reference_field: Field name in referencing statements (e.g., "rt")
        error_code_suffix: Suffix for error code (default: "UNUSED")

    Returns:
        List of ValidationIssue objects (warning) if definition is unused

    Example:
        >>> issues = check_unused_definition(stmt, "RETYP", model, "reloc", "rt")
        >>> # Returns warning if no RELOC statements have rt == stmt.id
    """
    issues = []
    container = getattr(model, referencing_container, None)

    if container is not None and hasattr(container, "items"):
        referencing_items = [
            item
            for item in container.items
            if hasattr(item, reference_field)
            and getattr(item, reference_field) == statement.id
        ]

        if not referencing_items:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code=f"{statement_type}_{error_code_suffix}",
                    message=f"{statement_type} {statement.id} is not referenced by any {referencing_container.upper()} statements",
                    location=f"{statement_type}.{statement.id}",
                    suggestion=f"Remove unused {statement_type} or add corresponding {referencing_container.upper()} statements",
                )
            )

    return issues
