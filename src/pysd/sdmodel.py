from __future__ import annotations

from contextlib import contextmanager
from typing import List, Union, Protocol, runtime_checkable, Sequence, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator

# Import all statement types for runtime use
from .statements.rfile import RFILE
from .statements.shaxe import SHAXE
from .statements.desec import DESEC
from .statements.cmpec import CMPEC
from .statements.loadc import LOADC
from .statements.lores import LORES
from .statements.basco import BASCO
from .statements.greco import GRECO
from .statements.filst import FILST
from .statements.retyp import RETYP
from .statements.reloc import RELOC
from .statements.decas import DECAS
from .statements.table import TABLE
from .statements.incdf import INCDF
from .statements.execd import EXECD
from .statements.shsec import SHSEC
from .statements.rmpec import RMPEC
from .statements.xtfil import XTFIL
from .statements.headl import HEADL
from .statements.depar import DEPAR

# Import container system
from .containers import GrecoContainer, BascoContainer, LoadcContainer, ShsecContainer
from .validation.core import ValidationContext, ValidationIssue, ValidationMode, ValidationSeverity
from .validation.rule_system import execute_validation_rules
from .validation.error_codes import ErrorCodes


# Define a protocol that all statement classes implement
@runtime_checkable
class StatementProtocol(Protocol):
    """Protocol that all statement classes must implement."""
    input: str  # All statements have an input string

# Type alias for all supported statement types using the protocol
StatementType = Union[
    RFILE, SHAXE, DESEC, CMPEC, LOADC, LORES, BASCO, GRECO, 
    FILST, RETYP, RELOC, DECAS, TABLE, INCDF, EXECD, SHSEC, 
    RMPEC, XTFIL, HEADL
]


class SD_BASE(BaseModel):
    """
    Enhanced ShellDesign model with Pydantic validation and container-based architecture.
    
    Features:
    - Automatic container creation and validation
    - Cross-object reference validation
    - Layered validation (object -> container -> model)
    - Backward compatible API
    - Model-level validation for business rules
    """
    
    # Maintain order of all items (excluded from serialization but tracked internally)
    all_items: List[StatementType] = Field(default_factory=list, exclude=True, description="Ordered list of all items")
   
    # Collections for type-specific access  
    rfile: List[RFILE] = Field(default_factory=list, description="RFILE statements")
    incdf: List[INCDF] = Field(default_factory=list, description="INCDF statements")
    headl: List[HEADL] = Field(default_factory=list, description="HEADL statements")
    shaxe: Dict[str, SHAXE] = Field(default_factory=dict, description="SHAXE statements (key: PA_FS_HS)")
    shsec: ShsecContainer = Field(default_factory=ShsecContainer, description="SHSEC statements with validation")
    xtfil: Dict[str, XTFIL] = Field(default_factory=dict, description="XTFIL statements (key: FN_PA_FS_HS)")
  
    filst: List[FILST] = Field(default_factory=list, description="FILST statements")
    desec: Dict[str, DESEC] = Field(default_factory=dict, description="DESEC statements")
    
    # Enhanced containers with validation
    greco: GrecoContainer = Field(default_factory=GrecoContainer, description="GRECO statements with validation")
    basco: BascoContainer = Field(default_factory=BascoContainer, description="BASCO statements with validation")
    loadc: LoadcContainer = Field(default_factory=LoadcContainer, description="LOADC statements with validation")
    lores: List[LORES] = Field(default_factory=list, description="LORES statements")
    table: List[TABLE] = Field(default_factory=list, description="TABLE statements")
    execd: List[EXECD] = Field(default_factory=list, description="EXECD statements")
    decas: List[DECAS] = Field(default_factory=list, description="DECAS statements")
    cmpec: Dict[int, CMPEC] = Field(default_factory=dict, description="CMPEC statements")
    rmpec: Dict[int, RMPEC] = Field(default_factory=dict, description="RMPEC statements")
    retyp: Dict[int, RETYP] = Field(default_factory=dict, description="RETYP statements")
   
    reloc: Dict[str, RELOC] = Field(default_factory=dict, description="RELOC statements")
    depar: Optional[DEPAR] = Field(None, description="DEPAR statement (singleton)")
    
    # Validation settings
    validation_enabled: bool = Field(default=True, exclude=True, description="Enable validation during operations")
    


    def add(self, item: Union[StatementType, Sequence[StatementType]]) -> None:
        """
        Enhanced add method with automatic container routing and validation.
        
        Features:
        - Automatic container selection based on type
        - Batch processing for lists
        - Layered validation (object -> container -> model)
        - Cross-object reference validation
        - Maintains backward compatibility
        
        Args:
            item: The component to add, or a list of components.
        """
        if isinstance(item, list):
            self._add_batch(item)
            return

        # Route to appropriate container/collection
        self._route_item(item)
        
        # Add to the master list to maintain order
        if isinstance(item, EXECD):
            # Remove any existing EXECD items and add at end
            self.all_items = [x for x in self.all_items if not isinstance(x, EXECD)]
        
        self.all_items.append(item)
        
        # Perform model-level cross-object validation
        if self.validation_enabled:
            self._validate_cross_references()
    
    def _route_item(self, item: StatementType) -> None:
        """Route item to appropriate container or collection with validation."""
        
        # Container-based routing with validation
        if isinstance(item, GRECO):
            self.greco.add(item)
        elif isinstance(item, BASCO):
            self.basco.add(item)
        elif isinstance(item, LOADC):
            self.loadc.add(item)
        elif isinstance(item, SHSEC):
            self.shsec.add(item)
        
        # Dictionary-based routing for other statements
        # TODO: Add new statement types here or migrate to containers
        
        else:  
            raise TypeError(f"Unsupported type for add(): {type(item).__name__}")
    
    def _add_batch(self, items: List[StatementType]) -> None:
        """Add multiple items with optimized batch validation."""
        
        # Group items by type for batch processing
        grouped_items = {}
        for item in items:
            item_type = type(item)
            if item_type not in grouped_items:
                grouped_items[item_type] = []
            grouped_items[item_type].append(item)
        
        # Process each group using containers
        for item_type, type_items in grouped_items.items():
            if item_type == GRECO:
                self.greco.add_batch(type_items)
            elif item_type == BASCO:
                self.basco.add_batch(type_items)
            elif item_type == LOADC:
                self.loadc.add_batch(type_items)
            elif item_type == SHSEC:
                self.shsec.add_batch(type_items)
            else:
                # Fall back to individual processing for non-container types
                for item in type_items:
                    self._route_item(item)
        
        # Add all to master list
        self.all_items.extend(items)
        
        # Model-level cross-object validation
        if self.validation_enabled:
            self._validate_cross_references()
    
    def _validate_cross_references(self) -> None:
        """Perform model-level cross-object validation."""
        issues = self._collect_validation_issues()
        
        # Check for critical errors
        errors = [issue for issue in issues if issue.severity == 'error']
        if errors:
            error_messages = [f"[{error.code}] {error.message}" for error in errors]
            raise ValueError("Model validation failed:\n" + "\n".join(error_messages))
    
    def _collect_validation_issues(self) -> List[ValidationIssue]:
        """Collect all validation issues from model-level validation using the rule system."""
        issues = []
        
        # Execute model-level validation for all statement types using the rule system
        all_statements = []
        all_statements.extend(self.greco.items)
        all_statements.extend(self.basco.items)
        all_statements.extend(self.loadc.items)
        all_statements.extend(self.shsec.items)
        
        for statement in all_statements:
            context = ValidationContext(
                statement=statement,
                container=self,
                mode=ValidationMode.STRICT,
                severity=ValidationSeverity.ERROR
            )
            try:
                execute_validation_rules(statement, context, level='model')
            except Exception as e:
                # Convert any validation errors to issues
                statement_type = type(statement).__name__
                statement_id = getattr(statement, 'id', getattr(statement, 'key', 'unknown'))
                issues.append(ValidationIssue(
                    code=f"{statement_type.upper()}_MODEL_ERROR",
                    message=f"{statement_type} {statement_id} model validation failed: {str(e)}",
                    severity="error"
                ))
        
        return issues
    
    @model_validator(mode='after')
    def validate_complete_model(self) -> 'SD_BASE':
        """Final model validation after all fields are set."""
        if self.validation_enabled:
            self._validate_cross_references()
        return self
    def get_all_ids(self, statement_type: type) -> List[Union[int, str]]:
        """Get all IDs for a specific statement type."""
        if statement_type == GRECO:
            return self.greco.get_ids()
        elif statement_type == BASCO:
            return self.basco.get_ids()
        elif statement_type == LOADC:
            return self.loadc.get_keys()  # LOADC uses keys, not IDs
        elif statement_type == SHSEC:
            return self.shsec.get_keys()  # SHSEC uses keys, not IDs
        elif statement_type == RETYP:
            return list(self.retyp.keys())
        # Add more as needed
        return []
    
    def validate_integrity(self) -> Dict[str, List[str]]:
        """Comprehensive integrity validation returning all issues by severity."""
        issues_by_severity = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        try:
            # Collect all validation issues
            all_issues = self._collect_validation_issues()
            
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
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a comprehensive validation summary."""
        integrity = self.validate_integrity()
        
        return {
            'validation_enabled': self.validation_enabled,
            'total_items': len(self.all_items),
            'containers': {
                'greco': len(self.greco),
                'basco': len(self.basco),
                'loadc': len(self.loadc),
                'shsec': len(self.shsec),
            },
            'integrity_issues': integrity,
            'has_errors': len(integrity['errors']) > 0,
            'has_warnings': len(integrity['warnings']) > 0
        }
    
    def disable_validation(self) -> None:
        """Disable validation for batch operations."""
        self.validation_enabled = False
    
    def enable_validation(self) -> None:
        """Re-enable validation and perform full model validation."""
        self.validation_enabled = True
        self._validate_cross_references()
    
    @contextmanager
    def validation_disabled(self):
        """Context manager to temporarily disable validation."""
        original_state = self.validation_enabled
        self.validation_enabled = False
        try:
            yield
        finally:
            self.validation_enabled = original_state
            if original_state:  # Only validate if it was originally enabled
                self._validate_cross_references()
    
    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str, validation_enabled: bool = True):
        """
        Enhanced context manager with validation control.
        
        Args:
            output_file: Output file path
            validation_enabled: Enable/disable validation during construction
        """
        sd_model = cls(validation_enabled=validation_enabled)
        try:
            yield sd_model
        finally:
            # Re-enable validation for final check if it was disabled
            if not validation_enabled:
                sd_model.validation_enabled = True
                sd_model._validate_cross_references()
            
            # Write to file
            with open(output_file, "w", encoding="utf-8") as f:
                for item in sd_model.all_items:
                    f.write(str(item) + "\n")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export model to dictionary for serialization."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SD_BASE':
        """Import model from dictionary."""
        return cls.model_validate(data)
              


    
