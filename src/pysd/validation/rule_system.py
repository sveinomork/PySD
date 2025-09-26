"""
Rule-based validation system with fixed signature pattern.
"""

from typing import Callable, List, Dict, TYPE_CHECKING
from .core import ValidationIssue, ValidationContext

if TYPE_CHECKING:
    from pydantic import BaseModel

# Fixed signature for all validation rules
ValidationRule = Callable[["BaseModel", ValidationContext], List[ValidationIssue]]


class ValidationRegistry:
    """Registry for validation rules with execution at different levels."""

    def __init__(self):
        self._instance_rules: Dict[str, List[ValidationRule]] = {}
        self._container_rules: Dict[str, List[ValidationRule]] = {}
        self._model_rules: Dict[str, List[ValidationRule]] = {}

    def add_instance_rule(self, model_type: str, rule: ValidationRule) -> None:
        """Add validation rule that runs at instance level."""
        if model_type not in self._instance_rules:
            self._instance_rules[model_type] = []
        self._instance_rules[model_type].append(rule)

    def add_container_rule(self, model_type: str, rule: ValidationRule) -> None:
        """Add validation rule that runs at container level."""
        if model_type not in self._container_rules:
            self._container_rules[model_type] = []
        self._container_rules[model_type].append(rule)

    def add_model_rule(self, model_type: str, rule: ValidationRule) -> None:
        """Add validation rule that runs at SD_BASE level."""
        if model_type not in self._model_rules:
            self._model_rules[model_type] = []
        self._model_rules[model_type].append(rule)

    def get_instance_rules(self, model_type: str) -> List[ValidationRule]:
        """Get all instance-level rules for a model type."""
        return self._instance_rules.get(model_type, [])

    def get_container_rules(self, model_type: str) -> List[ValidationRule]:
        """Get all container-level rules for a model type."""
        return self._container_rules.get(model_type, [])

    def get_model_rules(self, model_type: str) -> List[ValidationRule]:
        """Get all model-level rules for a model type."""
        return self._model_rules.get(model_type, [])


# Global registry
validation_registry = ValidationRegistry()


def instance_rule(model_type: str):
    """Decorator to register instance-level validation rules."""

    def decorator(func: ValidationRule) -> ValidationRule:
        validation_registry.add_instance_rule(model_type, func)
        return func

    return decorator


def container_rule(model_type: str):
    """Decorator to register container-level validation rules."""

    def decorator(func: ValidationRule) -> ValidationRule:
        validation_registry.add_container_rule(model_type, func)
        return func

    return decorator


def model_rule(model_type: str):
    """Decorator to register model-level validation rules."""

    def decorator(func: ValidationRule) -> ValidationRule:
        validation_registry.add_model_rule(model_type, func)
        return func

    return decorator


def execute_validation_rules(
    obj: "BaseModel", context: ValidationContext, level: str = "instance"
) -> List[ValidationIssue]:
    """Execute validation rules for an object at the specified level."""
    model_type = type(obj).__name__

    if level == "instance":
        rules = validation_registry.get_instance_rules(model_type)
    elif level == "container":
        rules = validation_registry.get_container_rules(model_type)
    elif level == "model":
        rules = validation_registry.get_model_rules(model_type)
    else:
        return []

    all_issues = []
    for rule in rules:
        try:
            issues = rule(obj, context)
            all_issues.extend(issues)
        except Exception as e:
            # Enhanced error handling with more context
            import traceback

            error_details = traceback.format_exc()
            all_issues.append(
                ValidationIssue(
                    severity="error",
                    code="RULE-EXEC-001",
                    message=f"Validation rule execution failed: {e}\nRule: {rule.__name__ if hasattr(rule, '__name__') else str(rule)}\nDetails: {error_details}",
                    location=f"{model_type}.{getattr(obj, 'id', 'unknown')}",
                )
            )

    return all_issues
