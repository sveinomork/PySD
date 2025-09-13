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
    Simple validation manager that handles the validation logic
    previously embedded in SD_BASE.
    
    Goal: Reduce sdmodel.py complexity, not add features.
    """
    
    def __init__(self, model: 'SD_BASE'):
        self.model = model
    
    def should_run_cross_validation(self) -> bool:
        """Check if cross-container validation should run."""
        from ..validation.core import validation_config
        
        # Skip validation if disabled globally
        if validation_config.mode.value == 'disabled' or not self.model.validation_enabled:
            return False
        
        # SMART DEFERRAL: Skip cross-container validation during building mode
        if (self.model.building_mode and 
            self.model.deferred_cross_validation and 
            self.model.cross_container_validation_enabled):
            return False
            
        # Skip cross-container validation if specifically disabled
        if not self.model.cross_container_validation_enabled:
            return False
            
        return True
    
    def collect_validation_issues(self) -> List['ValidationIssue']:
        """Collect all validation issues - moved from SD_BASE."""
        from ..validation.core import ValidationContext, ValidationIssue
        from ..validation.rule_system import execute_validation_rules
        
        issues = []
        
        # Get all statements from all containers
        all_statements = []
        all_statements.extend(self.model.greco.items)
        all_statements.extend(self.model.basco.items)
        all_statements.extend(self.model.loadc.items)
        all_statements.extend(self.model.shsec.items)
        all_statements.extend(self.model.shaxe.items)
        all_statements.extend(self.model.cmpec.items)
        all_statements.extend(self.model.rmpec.items)
        all_statements.extend(self.model.retyp.items)
        all_statements.extend(self.model.reloc.items)
        all_statements.extend(self.model.lores.items)
        all_statements.extend(self.model.xtfil.items)
        all_statements.extend(self.model.desec.items)
        all_statements.extend(self.model.table.items)
        all_statements.extend(self.model.rfile.items)
        all_statements.extend(self.model.incdf.items)
        all_statements.extend(self.model.decas.items)
        all_statements.extend(self.model.depar.items)
        all_statements.extend(self.model.filst.items)
        
        for statement in all_statements:
            context = ValidationContext(
                current_object=statement,
                full_model=self.model
            )
            try:
                validation_issues = execute_validation_rules(statement, context, level='model')
                issues.extend(validation_issues)
            except Exception as e:
                # Convert any validation errors to issues
                statement_type = type(statement).__name__
                statement_id = getattr(statement, 'id', getattr(statement, 'key', 'unknown'))
                issues.append(ValidationIssue(
                    severity="error",
                    code=f"{statement_type.upper()}_MODEL_ERROR",
                    message=f"{statement_type} {statement_id} model validation failed: {str(e)}",
                    location=f"{statement_type}.{statement_id}"
                ))
        
        return issues
    
    def validate_cross_references(self) -> None:
        """Run cross-reference validation - moved from SD_BASE."""
        from ..validation.core import validation_config
        
        if not self.should_run_cross_validation():
            return
            
        issues = self.collect_validation_issues()
        
        # Check for critical errors based on validation mode
        if validation_config.mode.value == 'permissive':
            critical_errors = [issue for issue in issues if issue.severity == 'error' and 'CRITICAL' in issue.code]
        else:
            critical_errors = [issue for issue in issues if issue.severity == 'error']
            
        if critical_errors:
            error_messages = [f"[{error.code}] {error.message}" for error in critical_errors]
            raise ValueError("Model validation failed:\n" + "\n".join(error_messages))
    
    def finalize_model(self) -> None:
        """Finalize model and run deferred validation."""
        self.model.building_mode = False  # Exit building mode
        
        # If we deferred cross-container validation, run it now
        if (self.model.deferred_cross_validation and 
            self.model.cross_container_validation_enabled and 
            self.model.validation_enabled):
            self.validate_cross_references()
    
    def validate_integrity(self) -> dict:
        """Validate integrity - moved from SD_BASE."""
        issues_by_severity = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        try:
            all_issues = self.collect_validation_issues()
            
            # Group by severity
            for issue in all_issues:
                severity_key = issue.severity + 's'  # 'error' -> 'errors'
                if severity_key in issues_by_severity:
                    issue_msg = f"[{issue.code}] {issue.message}"
                    if issue.suggestion:
                        issue_msg += f" Suggestion: {issue.suggestion}"
                    issues_by_severity[severity_key].append(issue_msg)
        
        except Exception as e:
            issues_by_severity['errors'].append(f"Validation system error: {str(e)}")
        
        return issues_by_severity
    
    # =============================================================================
    # Validation Control Methods (moved from SD_BASE)
    # =============================================================================
    
    def disable_container_validation(self) -> None:
        """Disable container-level validation only."""
        self.model.container_validation_enabled = False
    
    def enable_container_validation(self) -> None:
        """Enable container-level validation."""
        self.model.container_validation_enabled = True
    
    def disable_cross_container_validation(self) -> None:
        """Disable cross-container validation only."""
        self.model.cross_container_validation_enabled = False
    
    def enable_cross_container_validation(self) -> None:
        """Enable cross-container validation."""
        self.model.cross_container_validation_enabled = True
    
    def disable_deferred_validation(self) -> None:
        """Disable automatic deferral - validate immediately during building."""
        self.model.deferred_cross_validation = False
    
    def enable_deferred_validation(self) -> None:
        """Enable automatic deferral (default behavior)."""
        self.model.deferred_cross_validation = True
    
    def disable_validation(self) -> None:
        """Disable validation for batch operations."""
        self.model.validation_enabled = False
    
    def enable_validation(self) -> None:
        """Re-enable validation and perform full model validation."""
        self.model.validation_enabled = True
        # Trigger cross-reference validation
        self.validate_cross_references()
    
    @contextmanager
    def container_validation_disabled(self):
        """Context manager to temporarily disable container validation."""
        original_state = self.model.container_validation_enabled
        self.model.container_validation_enabled = False
        try:
            yield
        finally:
            self.model.container_validation_enabled = original_state
    
    @contextmanager
    def cross_validation_disabled(self):
        """Context manager to temporarily disable cross-container validation."""
        original_state = self.model.cross_container_validation_enabled
        self.model.cross_container_validation_enabled = False
        try:
            yield
        finally:
            self.model.cross_container_validation_enabled = original_state
    
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