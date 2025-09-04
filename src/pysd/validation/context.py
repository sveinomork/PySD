# validation/context.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ValidationIssue:
    loc: str       # e.g., "Reloc[id='X11']"
    message: str
    severity: str  # "error" | "warn" | "info"
    rule_id: str

@dataclass
class ValidationContext:
    model: "SDBase"
    config: Dict[str, Any] = None

    def error(self, loc: str, message: str, rule_id: str) -> ValidationIssue:
        return ValidationIssue(loc=loc, message=message, severity="error", rule_id=rule_id)