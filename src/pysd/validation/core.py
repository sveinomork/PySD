"""
Core validation framework components.
"""

from __future__ import annotations
from typing import Protocol, TypeVar, List, Optional, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod
from enum import Enum

T = TypeVar("T", bound=BaseModel)


class ValidationSeverity(Enum):
    """Validation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationLevel(Enum):
    """Validation levels for SD_BASE models."""

    DISABLED = "disabled"  # All validation disabled
    NORMAL = "normal"  # Standard validation level
    STRICT = "strict"  # Strictest validation level


class PySDValidationError(ValueError):
    """
    Custom validation error with severity-aware raising.

    This error will only be raised based on the global validation level
    and the severity of the validation issue.
    """

    def __init__(
        self,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        code: Optional[str] = None,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
        validation_issues: Optional[List["ValidationIssue"]] = None,
    ):
        super().__init__(message)
        self.severity = severity
        self.code = code
        self.location = location
        self.suggestion = suggestion
        self.validation_issues = validation_issues or []

    @classmethod
    def from_validation_issue(cls, issue: "ValidationIssue") -> "PySDValidationError":
        """Create a PySDValidationError from a ValidationIssue."""
        return cls(
            message=issue.message,
            severity=ValidationSeverity(issue.severity),
            code=issue.code,
            location=issue.location,
            suggestion=issue.suggestion,
            validation_issues=[issue],
        )

    @classmethod
    def from_validation_issues(
        cls, issues: List["ValidationIssue"]
    ) -> "PySDValidationError":
        """Create a PySDValidationError from multiple ValidationIssues."""
        if not issues:
            return cls("No validation issues provided")

        # Use the most severe issue as the main error
        error_issues = [
            i for i in issues if i.severity == ValidationSeverity.ERROR.value
        ]
        main_issue = error_issues[0] if error_issues else issues[0]

        message = f"Validation failed with {len(issues)} issue(s): {main_issue.message}"

        return cls(
            message=message,
            severity=ValidationSeverity(main_issue.severity),
            code=main_issue.code,
            location=main_issue.location,
            suggestion=main_issue.suggestion,
            validation_issues=issues,
        )


class ValidationConfig:
    """Simple global validation configuration."""

    def __init__(self):
        self._level = ValidationLevel.NORMAL

    @property
    def level(self) -> ValidationLevel:
        """Get current validation level."""
        return self._level

    @level.setter
    def level(self, value: ValidationLevel) -> None:
        """Set validation level."""
        self._level = value

    def should_raise_for_severity(self, severity: ValidationSeverity) -> bool:
        """Determine if an error should be raised for the given severity."""
        if self._level == ValidationLevel.DISABLED:
            return False
        elif self._level == ValidationLevel.STRICT:
            return True  # Raise for all severities
        elif self._level == ValidationLevel.NORMAL:
            return severity == ValidationSeverity.ERROR
        return False


# Global validation configuration instance
validation_config = ValidationConfig()


class ValidationIssue(BaseModel):
    """Represents a validation issue with smart error raising."""

    severity: str  # 'error', 'warning', 'info'
    code: str
    message: str
    location: str
    suggestion: Optional[str] = None

    def raise_if_needed(self) -> None:
        """Raise PySDValidationError if global config requires it."""
        severity_enum = ValidationSeverity(self.severity)

        # Check if we should raise based on global config
        if validation_config.should_raise_for_severity(severity_enum):
            raise PySDValidationError.from_validation_issue(self)


class ValidationContext(BaseModel):
    """Context for validation operations with smart error handling."""

    model_config = {"arbitrary_types_allowed": True}

    current_object: Optional[BaseModel] = None
    parent_container: Optional[object] = None
    full_model: Optional[BaseModel] = None  # Will be SD_BASE when available

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue and optionally raise error."""
        if not hasattr(self, "_issues"):
            self._issues = []
        self._issues.append(issue)

        # Automatically raise if configured to do so
        issue.raise_if_needed()

    def get_issues(self) -> List[ValidationIssue]:
        """Get all validation issues."""
        return getattr(self, "_issues", [])

    def raise_if_errors(self) -> None:
        """Raise exception if there are any validation errors."""
        error_issues = [
            issue
            for issue in self.get_issues()
            if ValidationSeverity(issue.severity) == ValidationSeverity.ERROR
        ]
        if error_issues:
            raise PySDValidationError.from_validation_issues(error_issues)


class ValidationRule(Protocol):
    """Protocol for validation rules."""

    def validate(
        self, obj: BaseModel, context: ValidationContext
    ) -> List[ValidationIssue]:
        """Validate an object and return issues."""
        ...


# Convenience functions for common validation patterns
def set_validation_level(level: Union[ValidationLevel, str]) -> None:
    """Set global validation level."""
    if isinstance(level, str):
        level = ValidationLevel(level)
    validation_config.level = level


def get_validation_level() -> ValidationLevel:
    """Get current validation level."""
    return validation_config.level
