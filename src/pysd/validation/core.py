"""
Core validation framework components.
"""

from __future__ import annotations
from typing import Protocol, TypeVar, List, Optional, TYPE_CHECKING
from pydantic import BaseModel
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..containers.base_container import BaseContainer

T = TypeVar('T', bound=BaseModel)

class ValidationIssue(BaseModel):
    """Represents a validation issue."""
    
    severity: str  # 'error', 'warning', 'info'
    code: str
    message: str
    location: str
    suggestion: Optional[str] = None

class ValidationContext(BaseModel):
    """Context for validation operations."""
    
    current_object: Optional[BaseModel] = None
    parent_container: Optional[BaseContainer] = None
    full_model: Optional[BaseModel] = None  # Will be SD_BASE when available
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        if not hasattr(self, '_issues'):
            self._issues = []
        self._issues.append(issue)
    
    def get_issues(self) -> List[ValidationIssue]:
        """Get all validation issues."""
        return getattr(self, '_issues', [])

class ValidationRule(Protocol):
    """Protocol for validation rules."""
    
    def validate(self, obj: BaseModel, context: ValidationContext) -> List[ValidationIssue]:
        """Validate an object and return issues."""
        ...