"""
Core validation framework components with global severity control.
"""

from __future__ import annotations
from typing import Protocol, TypeVar, List, Optional, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod
from enum import Enum
import threading

T = TypeVar('T', bound=BaseModel)

class ValidationSeverity(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationMode(Enum):
    """Global validation modes."""
    STRICT = "strict"      # All errors raise exceptions
    NORMAL = "normal"      # Only ERROR severity raises exceptions
    PERMISSIVE = "permissive"  # Only critical errors raise exceptions
    DISABLED = "disabled"  # No validation errors raise exceptions

class ValidationLevel(Enum):
    """Validation levels for SD_BASE models."""
    DISABLED = "disabled"  # All validation disabled
    NORMAL = "normal"      # Standard validation level
    STRICT = "strict"      # Strictest validation level
    
    def to_validation_mode(self) -> ValidationMode:
        """Convert ValidationLevel to ValidationMode."""
        mapping = {
            ValidationLevel.DISABLED: ValidationMode.DISABLED,
            ValidationLevel.NORMAL: ValidationMode.NORMAL,
            ValidationLevel.STRICT: ValidationMode.STRICT
        }
        return mapping[self]

class PySDValidationError(ValueError):
    """
    Custom validation error with severity-aware raising.
    
    This error will only be raised based on the global validation mode
    and the severity of the validation issue.
    """
    
    def __init__(
        self, 
        message: str, 
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        code: Optional[str] = None,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
        validation_issues: Optional[List['ValidationIssue']] = None
    ):
        super().__init__(message)
        self.severity = severity
        self.code = code
        self.location = location
        self.suggestion = suggestion
        self.validation_issues = validation_issues or []
    
    @classmethod
    def from_validation_issue(cls, issue: 'ValidationIssue') -> 'PySDValidationError':
        """Create a PySDValidationError from a ValidationIssue."""
        return cls(
            message=issue.message,
            severity=ValidationSeverity(issue.severity),
            code=issue.code,
            location=issue.location,
            suggestion=issue.suggestion,
            validation_issues=[issue]
        )
    
    @classmethod
    def from_validation_issues(cls, issues: List['ValidationIssue']) -> 'PySDValidationError':
        """Create a PySDValidationError from multiple ValidationIssues."""
        if not issues:
            return cls("No validation issues provided")
        
        # Use the most severe issue as the main error
        error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR.value]
        main_issue = error_issues[0] if error_issues else issues[0]
        
        message = f"Validation failed with {len(issues)} issue(s): {main_issue.message}"
        
        return cls(
            message=message,
            severity=ValidationSeverity(main_issue.severity),
            code=main_issue.code,
            location=main_issue.location,
            suggestion=main_issue.suggestion,
            validation_issues=issues
        )

class ValidationConfig:
    """Global validation configuration with thread-safe access."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._mode = ValidationMode.NORMAL
                    cls._instance._custom_thresholds = {}
                    cls._instance._disabled_rules = set()
        return cls._instance
    
    @property
    def mode(self) -> ValidationMode:
        """Get current validation mode."""
        return self._mode
    
    @mode.setter
    def mode(self, value: ValidationMode) -> None:
        """Set validation mode."""
        self._mode = value
    
    def should_raise_for_severity(self, severity: ValidationSeverity) -> bool:
        """Determine if an error should be raised for the given severity."""
        if self._mode == ValidationMode.DISABLED:
            return False
        elif self._mode == ValidationMode.STRICT:
            return True  # Raise for all severities
        elif self._mode == ValidationMode.NORMAL:
            return severity == ValidationSeverity.ERROR
        elif self._mode == ValidationMode.PERMISSIVE:
            # Only raise for critical system errors (you can customize this logic)
            return severity == ValidationSeverity.ERROR and self._is_critical_error()
        return False
    
    def _is_critical_error(self) -> bool:
        """Determine if this is a critical error that should always raise."""
        # You can customize this logic based on error codes or other criteria
        return True
    
    def set_custom_threshold(self, rule_code: str, min_severity: ValidationSeverity) -> None:
        """Set custom severity threshold for specific rule codes."""
        self._custom_thresholds[rule_code] = min_severity
    
    def should_raise_for_code(self, code: str, severity: ValidationSeverity) -> bool:
        """Check if error should be raised for specific code and severity."""
        if code in self._custom_thresholds:
            threshold = self._custom_thresholds[code]
            severity_levels = [ValidationSeverity.INFO, ValidationSeverity.WARNING, ValidationSeverity.ERROR]
            return severity_levels.index(severity) >= severity_levels.index(threshold)
        return self.should_raise_for_severity(severity)
    
    def disable_rule(self, rule_code: str) -> None:
        """Disable a specific validation rule."""
        self._disabled_rules.add(rule_code)
    
    def enable_rule(self, rule_code: str) -> None:
        """Enable a specific validation rule."""
        self._disabled_rules.discard(rule_code)
    
    def is_rule_enabled(self, rule_code: str) -> bool:
        """Check if a validation rule is enabled."""
        return rule_code not in self._disabled_rules

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
        
        # Check if rule is disabled
        if not validation_config.is_rule_enabled(self.code):
            return
        
        # Check if we should raise based on global config
        if validation_config.should_raise_for_code(self.code, severity_enum):
            raise PySDValidationError.from_validation_issue(self)

class ValidationContext(BaseModel):
    """Context for validation operations with smart error handling."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    current_object: Optional[BaseModel] = None
    parent_container: Optional[object] = None  # Use object instead of 'BaseContainer' to avoid forward ref
    full_model: Optional[BaseModel] = None  # Will be SD_BASE when available
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue and optionally raise error."""
        if not hasattr(self, '_issues'):
            self._issues = []
        self._issues.append(issue)
        
        # Automatically raise if configured to do so
        issue.raise_if_needed()
    
    def get_issues(self) -> List[ValidationIssue]:
        """Get all validation issues."""
        return getattr(self, '_issues', [])
    
    def raise_if_errors(self) -> None:
        """Raise exception if there are any validation errors."""
        error_issues = [issue for issue in self.get_issues() 
                       if ValidationSeverity(issue.severity) == ValidationSeverity.ERROR]
        if error_issues:
            raise PySDValidationError.from_validation_issues(error_issues)

class ValidationRule(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, obj: BaseModel, context: ValidationContext) -> List[ValidationIssue]:
        """Validate an object and return issues."""
        ...

# Convenience functions for common validation patterns
def validate_with_mode(func):
    """Decorator to wrap validation functions with mode-aware error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PySDValidationError as e:
            if validation_config.should_raise_for_severity(e.severity):
                raise
            # Otherwise, just log or handle silently
            return None
    return wrapper

def set_validation_mode(mode: Union[ValidationMode, str]) -> None:
    """Set global validation mode."""
    if isinstance(mode, str):
        mode = ValidationMode(mode)
    validation_config.mode = mode

def get_validation_mode() -> ValidationMode:
    """Get current validation mode."""
    return validation_config.mode

def disable_validation_rule(rule_code: str) -> None:
    """Disable a specific validation rule globally."""
    validation_config.disable_rule(rule_code)

def enable_validation_rule(rule_code: str) -> None:
    """Enable a specific validation rule globally."""
    validation_config.enable_rule(rule_code)

def set_rule_severity_threshold(rule_code: str, min_severity: Union[ValidationSeverity, str]) -> None:
    """Set minimum severity for a rule to raise errors."""
    if isinstance(min_severity, str):
        min_severity = ValidationSeverity(min_severity)
    validation_config.set_custom_threshold(rule_code, min_severity)

# Context managers for temporary validation mode changes
class validation_mode_context:
    """Context manager for temporary validation mode changes."""
    
    def __init__(self, mode: Union[ValidationMode, str]):
        if isinstance(mode, str):
            mode = ValidationMode(mode)
        self.new_mode = mode
        self.old_mode = None
    
    def __enter__(self):
        self.old_mode = validation_config.mode
        validation_config.mode = self.new_mode
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        validation_config.mode = self.old_mode

# Convenient context managers
def strict_validation():
    """Context manager for strict validation mode."""
    return validation_mode_context(ValidationMode.STRICT)

def permissive_validation():
    """Context manager for permissive validation mode."""
    return validation_mode_context(ValidationMode.PERMISSIVE)

def no_validation():
    """Context manager for disabled validation mode."""
    return validation_mode_context(ValidationMode.DISABLED)