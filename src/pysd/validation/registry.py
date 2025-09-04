# validation/registry.py
from typing import Callable, List
from .context import ValidationContext, ValidationIssue

_RULES: List[Callable[[ValidationContext], List[ValidationIssue]]] = []

def register_rule(fn: Callable[[ValidationContext], List[ValidationIssue]]):
    _RULES.append(fn)
    return fn

def run_registered_rules(ctx: ValidationContext):
    issues: List[ValidationIssue] = []
    for rule in _RULES:
        issues.extend(rule(ctx))
    # Raise with aggregated message if any errors:
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        lines = [f"[{e.rule_id}] {e.loc}: {e.message}" for e in errors]
        raise ValueError("Validation failed:\n" + "\n".join(lines))