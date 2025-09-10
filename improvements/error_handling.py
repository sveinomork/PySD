from typing import List, Optional, Dict, Any, Union, Type
from enum import Enum
from dataclasses import dataclass, field
from contextlib import contextmanager
import logging
import traceback

class ErrorCategory(Enum):
    """Categorize errors for better handling strategies"""
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    DATA_INTEGRITY = "data_integrity"
    SYSTEM = "system"
    USER_INPUT = "user_input"

class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"    # System cannot continue
    ERROR = "error"         # Operation failed but system recoverable
    WARNING = "warning"     # Issue detected but operation succeeded
    INFO = "info"          # Informational message

@dataclass
class ErrorDetail:
    """Rich error information"""
    code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    recoverable: bool = True
    trace: Optional[str] = None

class PySDError(Exception):
    """Base exception for PySD with rich error details"""
    
    def __init__(
        self, 
        message: str, 
        error_detail: Optional[ErrorDetail] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.error_detail = error_detail or ErrorDetail(
            code="UNKNOWN",
            message=message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.ERROR
        )
        self.original_exception = original_exception

class ValidationErrorGroup(PySDError):
    """Exception for multiple validation errors"""
    
    def __init__(self, errors: List[ErrorDetail]):
        self.errors = errors
        
        # Categorize by severity
        critical = [e for e in errors if e.severity == ErrorSeverity.CRITICAL]
        error_level = [e for e in errors if e.severity == ErrorSeverity.ERROR]
        
        if critical:
            main_error = critical[0]
            message = f"Critical validation failures: {len(critical)} critical, {len(error_level)} errors"
        elif error_level:
            main_error = error_level[0]
            message = f"Validation failures: {len(error_level)} errors"
        else:
            main_error = errors[0]
            message = f"Validation issues: {len(errors)} total"
        
        super().__init__(message, main_error)

class ErrorRecoveryStrategy:
    """Strategy for recovering from specific error types"""
    
    @staticmethod
    def can_recover(error_detail: ErrorDetail) -> bool:
        """Determine if error is recoverable"""
        return (error_detail.recoverable and 
                error_detail.severity != ErrorSeverity.CRITICAL)
    
    @staticmethod
    def suggest_recovery(error_detail: ErrorDetail) -> List[str]:
        """Suggest recovery actions"""
        strategies = []
        
        if error_detail.category == ErrorCategory.VALIDATION:
            if "duplicate" in error_detail.message.lower():
                strategies.append("Use unique identifiers")
                strategies.append("Check existing items before adding")
            elif "range" in error_detail.message.lower():
                strategies.append("Adjust values to be within valid range")
        
        elif error_detail.category == ErrorCategory.DATA_INTEGRITY:
            strategies.append("Validate data consistency")
            strategies.append("Check cross-references")
        
        strategies.extend(error_detail.suggestions)
        return strategies

class ResilientValidator:
    """Validator with error recovery capabilities"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_history: List[ErrorDetail] = []
        self.recovery_attempts = 0
        
    def validate_with_recovery(
        self, 
        obj: Any, 
        validation_func, 
        max_recovery_attempts: int = 3
    ) -> tuple[bool, List[ErrorDetail]]:
        """Validate with automatic recovery attempts"""
        
        errors = []
        success = False
        
        for attempt in range(max_recovery_attempts + 1):
            try:
                validation_func(obj)
                success = True
                break
                
            except PySDError as e:
                self.logger.warning(f"Validation attempt {attempt + 1} failed: {e}")
                errors.append(e.error_detail)
                
                if not ErrorRecoveryStrategy.can_recover(e.error_detail):
                    self.logger.error(f"Non-recoverable error: {e.error_detail.code}")
                    break
                
                # Attempt recovery
                if attempt < max_recovery_attempts:
                    recovery_success = self._attempt_recovery(obj, e.error_detail)
                    if not recovery_success:
                        self.logger.error(f"Recovery failed for {e.error_detail.code}")
                        break
                        
            except Exception as e:
                error_detail = ErrorDetail(
                    code="UNEXPECTED_ERROR",
                    message=str(e),
                    category=ErrorCategory.SYSTEM,
                    severity=ErrorSeverity.CRITICAL,
                    trace=traceback.format_exc(),
                    recoverable=False
                )
                errors.append(error_detail)
                self.logger.critical(f"Unexpected error: {e}", exc_info=True)
                break
        
        self.error_history.extend(errors)
        return success, errors
    
    def _attempt_recovery(self, obj: Any, error_detail: ErrorDetail) -> bool:
        """Attempt to recover from a specific error"""
        self.recovery_attempts += 1
        
        # Example recovery strategies
        if error_detail.code == "BASCO-ID-001":  # ID range error
            # Try to adjust ID to valid range
            if hasattr(obj, 'id'):
                obj.id = max(1, min(99999999, obj.id))
                return True
                
        elif "DUPLICATE" in error_detail.code:
            # Try to generate unique ID
            if hasattr(obj, 'id'):
                obj.id = obj.id + self.recovery_attempts
                return True
        
        return False

@contextmanager
def error_context(context_info: Dict[str, Any]):
    """Context manager to enrich error information"""
    try:
        yield
    except PySDError as e:
        e.error_detail.context.update(context_info)
        raise
    except Exception as e:
        error_detail = ErrorDetail(
            code="CONTEXT_ERROR",
            message=str(e),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.ERROR,
            context=context_info,
            trace=traceback.format_exc()
        )
        raise PySDError(str(e), error_detail, e)

class ErrorReporter:
    """Enhanced error reporting with categorization"""
    
    def __init__(self):
        self.errors_by_category: Dict[ErrorCategory, List[ErrorDetail]] = {}
        self.errors_by_severity: Dict[ErrorSeverity, List[ErrorDetail]] = {}
    
    def add_error(self, error: ErrorDetail):
        """Add error to categorized collections"""
        # By category
        if error.category not in self.errors_by_category:
            self.errors_by_category[error.category] = []
        self.errors_by_category[error.category].append(error)
        
        # By severity
        if error.severity not in self.errors_by_severity:
            self.errors_by_severity[error.severity] = []
        self.errors_by_severity[error.severity].append(error)
    
    def generate_report(self) -> str:
        """Generate comprehensive error report"""
        lines = ["=== PySD Error Report ===\n"]
        
        # Summary by severity
        lines.append("Summary by Severity:")
        for severity in ErrorSeverity:
            count = len(self.errors_by_severity.get(severity, []))
            if count > 0:
                lines.append(f"  {severity.value.title()}: {count}")
        
        lines.append("")
        
        # Detailed errors by category
        for category, errors in self.errors_by_category.items():
            if errors:
                lines.append(f"=== {category.value.title()} Errors ===")
                for error in errors:
                    lines.append(f"  [{error.code}] {error.message}")
                    if error.suggestions:
                        lines.append(f"    Suggestions: {'; '.join(error.suggestions)}")
                    if error.context:
                        lines.append(f"    Context: {error.context}")
                lines.append("")
        
        return "\n".join(lines)
    
    def get_actionable_items(self) -> List[str]:
        """Get list of actionable recovery suggestions"""
        actionable = []
        
        for category_errors in self.errors_by_category.values():
            for error in category_errors:
                if error.recoverable:
                    strategies = ErrorRecoveryStrategy.suggest_recovery(error)
                    actionable.extend(strategies)
        
        return list(set(actionable))  # Remove duplicates

# Example usage
def example_resilient_validation():
    """Example of using resilient validation"""
    
    logger = logging.getLogger("pysd.validation")
    validator = ResilientValidator(logger)
    reporter = ErrorReporter()
    
    def mock_validation(obj):
        # Mock validation that might fail
        if obj.id < 1:
            raise PySDError(
                "Invalid ID", 
                ErrorDetail(
                    code="BASCO-ID-001",
                    message="ID must be positive",
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.ERROR,
                    suggestions=["Set ID to positive value"]
                )
            )
    
    class MockObject:
        def __init__(self, id: int):
            self.id = id
    
    # Test resilient validation
    obj = MockObject(id=-5)
    
    with error_context({"operation": "BASCO validation", "object_type": "BASCO"}):
        success, errors = validator.validate_with_recovery(obj, mock_validation)
        
        for error in errors:
            reporter.add_error(error)
        
        if not success:
            print(reporter.generate_report())
            print("Actionable items:", reporter.get_actionable_items())

# Integration with existing validation system
class EnhancedValidationContext:
    """Enhanced validation context with error management"""
    
    def __init__(self):
        self.reporter = ErrorReporter()
        self.resilient_validator = ResilientValidator()
    
    def validate_model(self, model: Any) -> bool:
        """Validate model with enhanced error handling"""
        try:
            # Your existing validation logic here
            return True
            
        except Exception as e:
            error_detail = ErrorDetail(
                code="MODEL_VALIDATION_FAILED",
                message=str(e),
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.ERROR,
                recoverable=True
            )
            self.reporter.add_error(error_detail)
            return False
