"""
Simple ValidationManager - extracted from SD_BASE to reduce complexity.

Focus: Just move validation logic out of sdmodel.py to make it smaller.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List
from contextlib import contextmanager

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE
    from ..validation.core import ValidationIssue


class ValidationManager:
    """
    Validation manager that handles all validation logic and internal state.

    This class now manages its own internal validation state instead of
    storing it on the SD_BASE model, providing a cleaner separation of concerns.
    """

    def __init__(self, model: "SD_BASE"):
        self.model = model

        # Internal validation state (moved from SD_BASE)
        self._validation_enabled: bool = True
        self._container_validation_enabled: bool = True
        self._cross_container_validation_enabled: bool = True
        self._building_mode: bool = True
        self._deferred_cross_validation: bool = True

        # Initialize state based on model's high-level settings
        self._configure_from_model_settings()

    def _configure_from_model_settings(self) -> None:
        """Configure internal state based on model's validation_level and settings."""
        from ..validation.core import ValidationLevel

        if self.model.validation_level == ValidationLevel.DISABLED:
            self._validation_enabled = False
            self._container_validation_enabled = False
            self._cross_container_validation_enabled = False
        elif self.model.validation_level in [
            ValidationLevel.NORMAL,
            ValidationLevel.STRICT,
        ]:
            self._validation_enabled = True
            self._container_validation_enabled = True
            self._cross_container_validation_enabled = True

    # Properties to access internal state (backward compatibility)
    @property
    def validation_enabled(self) -> bool:
        return self._validation_enabled

    @property
    def container_validation_enabled(self) -> bool:
        return self._container_validation_enabled

    @property
    def cross_container_validation_enabled(self) -> bool:
        return self._cross_container_validation_enabled

    @property
    def building_mode(self) -> bool:
        return self._building_mode

    @property
    def deferred_cross_validation(self) -> bool:
        return self._deferred_cross_validation

    def should_run_cross_validation(self) -> bool:
        """Check if cross-container validation should run."""
        from ..validation.core import validation_config

        # Skip validation if disabled globally
        if validation_config.level == "disabled" or not self._validation_enabled:
            return False

        # SMART DEFERRAL: Skip cross-container validation during building mode
        if (
            self._building_mode
            and self._deferred_cross_validation
            and self._cross_container_validation_enabled
        ):
            return False

        # Skip cross-container validation if specifically disabled
        if not self._cross_container_validation_enabled:
            return False

        return True

    def collect_validation_issues(self) -> List["ValidationIssue"]:
        """Collect all validation issues - moved from SD_BASE."""
        from ..validation.core import ValidationContext, ValidationIssue
        from ..validation.rule_system import execute_validation_rules

        issues = []

        # Get all statements from all containers dynamically
        # This ensures all registered statement types participate in validation
        from ..model.container_factory import ContainerFactory

        all_statements = []
        for container_name in ContainerFactory.get_container_names():
            if hasattr(self.model, container_name):
                container = getattr(self.model, container_name)
                if hasattr(container, "items"):
                    all_statements.extend(container.items)

        for statement in all_statements:
            context = ValidationContext(current_object=statement, full_model=self.model)
            try:
                validation_issues = execute_validation_rules(
                    statement, context, level="model"
                )
                issues.extend(validation_issues)
            except Exception as e:
                # Convert any validation errors to issues
                statement_type = type(statement).__name__
                statement_id = getattr(
                    statement, "id", getattr(statement, "key", "unknown")
                )
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code=f"{statement_type.upper()}_MODEL_ERROR",
                        message=f"{statement_type} {statement_id} model validation failed: {str(e)}",
                        location=f"{statement_type}.{statement_id}",
                    )
                )

        return issues

    def validate_cross_references(self) -> None:
        """Run cross-reference validation - moved from SD_BASE."""
        from ..validation.core import validation_config

        if not self.should_run_cross_validation():
            return

        issues = self.collect_validation_issues()

        # Check for critical errors based on validation mode
        if validation_config.level == "permissive":
            critical_errors = [
                issue
                for issue in issues
                if issue.severity == "error" and "CRITICAL" in issue.code
            ]
        else:
            critical_errors = [issue for issue in issues if issue.severity == "error"]

        if critical_errors:
            error_messages = [
                f"[{error.code}] {error.message}" for error in critical_errors
            ]
            raise ValueError("Model validation failed:\n" + "\n".join(error_messages))

    def finalize_model(self) -> None:
        """Finalize model and run deferred validation."""
        self._building_mode = False  # Exit building mode

        # If we deferred cross-container validation, run it now
        if (
            self._deferred_cross_validation
            and self._cross_container_validation_enabled
            and self._validation_enabled
        ):
            self.validate_cross_references()

    def finalize_model_and_validation(self) -> None:
        """Complete model finalization with full validation - used by I/O operations."""
        # This is the method that ModelWriter should call
        self.finalize_model()

    def validate_integrity(self) -> dict:
        """Validate integrity - moved from SD_BASE."""
        issues_by_severity = {"errors": [], "warnings": [], "info": []}

        try:
            all_issues = self.collect_validation_issues()

            # Group by severity
            for issue in all_issues:
                severity_key = issue.severity + "s"  # 'error' -> 'errors'
                if severity_key in issues_by_severity:
                    issue_msg = f"[{issue.code}] {issue.message}"
                    if issue.suggestion:
                        issue_msg += f" Suggestion: {issue.suggestion}"
                    issues_by_severity[severity_key].append(issue_msg)

        except Exception as e:
            issues_by_severity["errors"].append(f"Validation system error: {str(e)}")

        return issues_by_severity

    def disable_container_validation(self) -> None:
        """Disable container-level validation only."""
        self._container_validation_enabled = False

    def enable_container_validation(self) -> None:
        """Enable container-level validation."""
        self._container_validation_enabled = True

    def disable_cross_container_validation(self) -> None:
        """Disable cross-container validation only."""
        self._cross_container_validation_enabled = False

    def enable_cross_container_validation(self) -> None:
        """Enable cross-container validation."""
        self._cross_container_validation_enabled = True

    def disable_deferred_validation(self) -> None:
        """Disable automatic deferral - validate immediately during building."""
        self._deferred_cross_validation = False

    def enable_deferred_validation(self) -> None:
        """Enable automatic deferral (default behavior)."""
        self._deferred_cross_validation = True

    def disable_validation(self) -> None:
        """Disable validation for batch operations."""
        self._validation_enabled = False

    def enable_validation(self) -> None:
        """Re-enable validation and perform full model validation."""
        self._validation_enabled = True
        # Trigger cross-reference validation
        self.validate_cross_references()

    @contextmanager
    def container_validation_disabled(self):
        """Context manager to temporarily disable container validation."""
        original_state = self._container_validation_enabled
        self._container_validation_enabled = False
        try:
            yield
        finally:
            self._container_validation_enabled = original_state

    @contextmanager
    def cross_validation_disabled(self):
        """Context manager to temporarily disable cross-container validation."""
        original_state = self._cross_container_validation_enabled
        self._cross_container_validation_enabled = False
        try:
            yield
        finally:
            self._cross_container_validation_enabled = original_state

    @contextmanager
    def immediate_validation(self):
        """Context manager to temporarily disable deferred validation."""
        original_state = self.model.deferred_cross_validation
        self.model.deferred_cross_validation = False
        try:
            yield
        finally:
            self.model.deferred_cross_validation = original_state

    @contextmanager
    def validation_disabled(self):
        """Context manager to temporarily disable validation."""
        original_state = self.model.validation_enabled
        self.model.validation_enabled = False
        try:
            yield
        finally:
            self.model.validation_enabled = original_state
            if original_state:  # Only validate if it was originally enabled
                self.validate_cross_references()
