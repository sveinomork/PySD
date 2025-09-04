"""
Specialized container for GRECO statements.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Any
from pydantic import field_validator, model_validator
from .base_container import BaseContainer
from ..validation.core import ValidationIssue
from ..validation.error_codes import ErrorCodes

if TYPE_CHECKING:
    from ..statements.greco import GRECO

class GrecoContainer(BaseContainer):
    """
    Container for GRECO statements with specialized validation.
    
    GRECO-specific rules:
    - IDs must be single uppercase letters A-Z
    - Each GRECO must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)
    - ELC must be defined as OLC in LOADC statements
    - No duplicate IDs allowed
    """
    
    def add(self, item: 'GRECO') -> None:
        """Add GRECO with specialized validation."""
        self._validate_greco_rules(item)
        super().add(item)
    
    def add_batch(self, items: List['GRECO']) -> None:
        """Add multiple GRECO items with batch validation."""
        # Validate each item first
        for item in items:
            self._validate_greco_rules(item)
        
        # Check for duplicates within batch
        seen_ids = set()
        for item in items:
            if item.id in seen_ids:
                raise ValueError(f"Duplicate GRECO ID {item.id} in batch")
            seen_ids.add(item.id)
        
        # Add all items
        for item in items:
            super().add(item)
    
    def _validate_greco_rules(self, item: 'GRECO') -> None:
        """Validate GRECO-specific business rules."""
        issues = []
        
        # Rule 1: ID must be single uppercase letter A-Z (already validated in GRECO model)
        # This is handled by the GRECO Pydantic model validation
        
        # Rule 2: Must have exactly 6 BAS (comment placeholder for future implementation)
        # TODO: Implement BAS count validation
        # Must be exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)
        # if item.bas and len(item.bas.to_list()) != 6:
        #     issues.append(ValidationIssue(
        #         severity='error',
        #         code=ErrorCodes.GRECO_BAS_COUNT_INVALID,
        #         message='GRECO must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)',
        #         location=f'GRECO.{item.id}.bas'
        #     ))
        
        # Rule 3: ELC must be defined as OLC in LOADC (comment placeholder for future implementation)
        # TODO: Implement ELC-OLC cross-reference validation
        # This requires access to the full model to check LOADC statements
        # if item.elc:
        #     # Check that all ELC values exist as OLC in LOADC statements
        #     # This validation will need access to the full SD_BASE model
        #     pass
        
        # Rule 4: Check for duplicate ID in container (handled by parent)
        if self.get_by_id(item.id) is not None:
            issues.append(ValidationIssue(
                severity='error',
                code=ErrorCodes.GRECO_DUPLICATE_ID,
                message=f'GRECO ID {item.id} already exists in container',
                location=f'GRECO.{item.id}'
            ))
        
        # Raise errors if any critical issues found
        errors = [issue for issue in issues if issue.severity == 'error']
        if errors:
            error_messages = [issue.message for issue in errors]
            raise ValueError("GRECO validation failed:\n" + "\n".join(error_messages))
    
    def get_by_id(self, id_value: str) -> Optional['GRECO']:
        """Get GRECO by ID (override to handle string IDs)."""
        for item in self.items:
            if item.id == id_value:
                return item
        return None
    
    def has_id(self, id_value: str) -> bool:
        """Check if GRECO with given ID exists."""
        return self.get_by_id(id_value) is not None
    
    def get_ids(self) -> List[str]:
        """Get all GRECO IDs."""
        return [item.id for item in self.items]
    
    def validate_bas_count_requirement(self) -> List[ValidationIssue]:
        """
        Validate that all GRECO statements have exactly 6 BAS.
        
        Note: This is a placeholder for future implementation.
        The actual business logic needs to be implemented to check
        that each GRECO has exactly 6 BAS (one per load resultant).
        """
        issues = []
        # TODO: Implement actual BAS count validation logic
        # for greco in self.items:
        #     if greco.bas and len(greco.bas.to_list()) != 6:
        #         issues.append(ValidationIssue(
        #             severity='error',
        #             code=ErrorCodes.GRECO_BAS_COUNT_INVALID,
        #             message=f'GRECO {greco.id} must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)',
        #             location=f'GRECO.{greco.id}.bas'
        #         ))
        return issues
    
    def validate_elc_references(self, loadc_container=None) -> List[ValidationIssue]:
        """
        Validate that all ELC values are defined as OLC in LOADC statements.
        
        Note: This is a placeholder for future implementation.
        The actual cross-reference validation needs access to the LOADC container.
        
        Args:
            loadc_container: Container with LOADC statements (for future implementation)
        """
        issues = []
        # TODO: Implement ELC-OLC cross-reference validation
        # for greco in self.items:
        #     if greco.elc and loadc_container:
        #         elc_values = greco.elc.to_list()
        #         for elc_value in elc_values:
        #             # Check if elc_value exists as OLC in any LOADC statement
        #             if not _is_elc_defined_in_loadc(elc_value, loadc_container):
        #                 issues.append(ValidationIssue(
        #                     severity='error',
        #                     code=ErrorCodes.GRECO_ELC_REFERENCE_INVALID,
        #                     message=f'GRECO {greco.id} ELC {elc_value} is not defined as OLC in LOADC',
        #                     location=f'GRECO.{greco.id}.elc'
        #                 ))
        return issues