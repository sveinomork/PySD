"""All validation rules for RFILE statements."""

import os
from pathlib import Path
from typing import List, TYPE_CHECKING
from ..core import ValidationIssue, ValidationContext, ValidationSeverity
from ..rule_system import instance_rule, model_rule

if TYPE_CHECKING:
    from ...statements.rfile import RFILE


# Instance-level validation rules (run during object creation)
@instance_rule("RFILE")
def validate_rfile_file_existence(
    obj: "RFILE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that the RFILE referenced file actually exists on the filesystem."""
    issues = []

    # Construct the full file path based on RFILE parameters
    # Format: PRE/FNM.SUF or just FNM.SUF if no PRE
    try:
        if obj.pre:
            # Use Path to handle Windows/Unix path separators correctly
            full_path = Path(obj.pre) / f"{obj.fnm}.{obj.suf}"
        else:
            full_path = Path(f"{obj.fnm}.{obj.suf}")

        # Check if file exists
        if not full_path.exists():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="RFILE-FILE-001",
                    message=f"RFILE referenced file does not exist: {full_path}",
                    location=f"RFILE.{obj.fnm}",
                    suggestion=f"Create the file {full_path} or verify the path is correct",
                )
            )
        # Additional check: if file exists but is not readable
        elif not full_path.is_file():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR.value,
                    code="RFILE-FILE-002",
                    message=f"RFILE path exists but is not a file: {full_path}",
                    location=f"RFILE.{obj.fnm}",
                    suggestion=f"Ensure {full_path} is a valid file, not a directory",
                )
            )
        # Check if file is readable
        elif not os.access(full_path, os.R_OK):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING.value,
                    code="RFILE-FILE-003",
                    message=f"RFILE referenced file may not be readable: {full_path}",
                    location=f"RFILE.{obj.fnm}",
                    suggestion=f"Check file permissions for {full_path}",
                )
            )

    except (OSError, PermissionError) as e:
        # Handle cases where path access fails
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-FILE-004",
                message=f"RFILE file path validation failed: {str(e)}",
                location=f"RFILE.{obj.fnm}",
                suggestion="Check if the path is valid and accessible",
            )
        )

    return issues


@instance_rule("RFILE")
def validate_rfile_fnm_format(
    obj: "RFILE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate RFILE FNM format (filename)."""
    issues = []

    if not obj.fnm:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-FNM-001",
                message="RFILE FNM (filename) is required",
                location=f"RFILE.{obj.fnm}",
                suggestion="Provide a filename (FNM)",
            )
        )
    elif len(obj.fnm.strip()) == 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-FNM-002",
                message="RFILE FNM (filename) cannot be empty",
                location=f"RFILE.{obj.fnm}",
                suggestion="Provide a non-empty filename (FNM)",
            )
        )

    return issues


@instance_rule("RFILE")
def validate_rfile_file_dependencies(
    obj: "RFILE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate RFILE file dependencies (LFI requires TFI)."""
    issues = []

    # L-file requires T-file
    if obj.lfi is not None and obj.tfi is None:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-DEP-001",
                message="RFILE LFI (L-file) requires TFI (T-file) to be specified",
                location="RFILE.lfi",
                suggestion="Provide TFI parameter when using LFI",
            )
        )

    return issues


@instance_rule("RFILE")
def validate_rfile_unit_factors(
    obj: "RFILE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate RFILE unit conversion factors."""
    issues = []

    # Length unit factor should be positive
    if obj.lun <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-LUN-001",
                message=f"RFILE LUN (length unit factor) must be positive, got {obj.lun}",
                location="RFILE.lun",
                suggestion="Use a positive number for length unit conversion",
            )
        )

    # Force unit factor should be positive
    if obj.fun <= 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR.value,
                code="RFILE-FUN-001",
                message=f"RFILE FUN (force unit factor) must be positive, got {obj.fun}",
                location="RFILE.fun",
                suggestion="Use a positive number for force unit conversion",
            )
        )

    # Common unit factor values validation (warning)
    common_length_units = [1, 10, 100, 1000, 25.4, 304.8]  # mm, cm, m, mm, inch, ft
    if obj.lun not in common_length_units:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="RFILE-LUN-002",
                message=f"RFILE LUN {obj.lun} is not a common unit factor",
                location="RFILE.lun",
                suggestion=f"Common values: {common_length_units}",
            )
        )

    return issues


# Model-level validation rules (run when adding to SD_BASE)
@model_rule("RFILE")
def validate_rfile_uniqueness(
    obj: "RFILE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate RFILE uniqueness in model (typically only one RFILE per model)."""
    issues = []

    if not context.full_model:
        return issues

    # Check if model already has other RFILE statements (excluding the current one)
    existing_rfiles = getattr(context.full_model, "rfile", [])
    other_rfiles = [rf for rf in existing_rfiles if rf is not obj]

    if len(other_rfiles) > 0:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.WARNING.value,
                code="RFILE-DUP-001",
                message=f"Model already has {len(other_rfiles)} other RFILE statement(s), typically only one is needed",
                location=f"RFILE.{obj.fnm}",
                suggestion="Consider if multiple RFILE statements are necessary",
            )
        )

    return issues
