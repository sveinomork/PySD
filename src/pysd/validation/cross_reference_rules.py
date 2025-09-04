"""
Cross-reference validation rules for PySD statements.
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING
from .core import ValidationIssue, ValidationRule
from .error_codes import ErrorCodes

if TYPE_CHECKING:
    from ..statements.greco import GRECO
    from ..sdmodel import SD_BASE


class GrecoELCCrossReferenceRule:
    """Validates that GRECO ELC values are defined as OLC in LOADC statements."""
    
    def validate(self, greco: 'GRECO', model: 'SD_BASE') -> List[ValidationIssue]:
        """Validate GRECO ELC cross-references."""
        issues = []
        
        if not greco.elc:
            return issues
        
        # Get ELC values from GRECO
        elc_values = greco.elc.to_list() if hasattr(greco.elc, 'to_list') else []
        
        for elc_value in elc_values:
            if not self._is_elc_defined_in_loadc(elc_value, model):
                issues.append(ValidationIssue(
                    severity='error',
                    code=ErrorCodes.GRECO_ELC_REFERENCE_INVALID,
                    message=f'GRECO {greco.id} ELC {elc_value} is not defined as OLC in LOADC',
                    location=f'GRECO.{greco.id}.elc',
                    suggestion=f'Add LOADC statement with OLC={elc_value} or remove {elc_value} from GRECO {greco.id} ELC'
                ))
        
        return issues
    
    def _is_elc_defined_in_loadc(self, elc_value: int, model: 'SD_BASE') -> bool:
        """
        Check if an ELC value is defined as OLC in any LOADC statement.
        
        TODO: Implement actual LOADC OLC checking logic when LOADC is migrated.
        For now, this is a placeholder that always returns True to avoid false positives.
        """
        # Placeholder implementation - when LOADC is migrated to container:
        # for loadc in model.loadc_container.items:
        #     if hasattr(loadc, 'olc') and elc_value in loadc.get_olc_list():
        #         return True
        # return False
        
        # For now, always return True to avoid validation errors during development
        return True


class GrecoBasCountRule:
    """Validates that GRECO has exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)."""
    
    def validate(self, greco: 'GRECO', model: 'SD_BASE') -> List[ValidationIssue]:
        """Validate GRECO BAS count."""
        issues = []
        
        if not greco.bas:
            return issues
        
        # TODO: Implement actual BAS count validation
        # The business rule requires exactly 6 BAS (one per load resultant)
        # bas_count = len(greco.bas.to_list()) if hasattr(greco.bas, 'to_list') else 0
        # if bas_count != 6:
        #     issues.append(ValidationIssue(
        #         severity='error',
        #         code=ErrorCodes.GRECO_BAS_COUNT_INVALID,
        #         message=f'GRECO {greco.id} must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz), found {bas_count}',
        #         location=f'GRECO.{greco.id}.bas',
        #         suggestion=f'Adjust GRECO {greco.id} BAS to have exactly 6 values'
        #     ))
        
        return issues


# TODO: Add more cross-reference rules as other statements are migrated
# class RelocRetypCrossReferenceRule:
#     """Validates that RELOC RT values reference existing RETYP statements."""
#     pass

# class BascoLoadCaseCrossReferenceRule:
#     """Validates that BASCO load cases reference existing load case definitions."""
#     pass