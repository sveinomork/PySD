from __future__ import annotations

from contextlib import contextmanager
from typing import List, Union, Protocol, runtime_checkable, Sequence, Dict, Any
from pydantic import BaseModel, Field, model_validator

# Import all statement types for runtime use
from src.pysd.statements.rfile import RFILE
from src.pysd.statements.shaxe import SHAXE
from src.pysd.statements.desec import DESEC
from src.pysd.statements.cmpec import CMPEC
from src.pysd.statements.loadc import LOADC
from src.pysd.statements.lores import LORES
from src.pysd.statements.basco import BASCO
from src.pysd.statements.greco import GRECO
from src.pysd.statements.filst import FILST
from src.pysd.statements.retyp import RETYP
from src.pysd.statements.reloc import RELOC
from src.pysd.statements.decas import DECAS
from src.pysd.statements.table import TABLE
from src.pysd.statements.incdf import INCDF
from src.pysd.statements.depar import DEPAR
from src.pysd.statements.headl import HEADL
from src.pysd.statements.cases import Cases
from src.pysd.statements.execd import EXECD
from src.pysd.statements.shsec import SHSEC
from src.pysd.statements.rmpec import RMPEC
from src.pysd.statements.xtfil import XTFIL
from src.pysd.statements.statement_heading import HEADING

# Import container system
from src.pysd.containers.base_container import BaseContainer
from src.pysd.validation.core import ValidationContext, ValidationIssue, validation_config
from src.pysd.validation.rule_system import execute_validation_rules


# Define a protocol that all statement classes implement
@runtime_checkable
class StatementProtocol(Protocol):
    """Protocol that all statement classes must implement."""
    input: str  # All statements have an input string

# Type alias for all supported statement types using the protocol
StatementType = Union[
    RFILE, SHAXE, DESEC, CMPEC, LOADC, LORES, BASCO, GRECO, 
    FILST, RETYP, RELOC, DECAS, TABLE, INCDF, EXECD, SHSEC, 
    RMPEC, XTFIL, HEADL, HEADING
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
    headl: BaseContainer[HEADL] = Field(default_factory=lambda: BaseContainer[HEADL](), description="HEADL container with validation")
    heading: List[HEADING] = Field(default_factory=list, description="HEADING comment blocks")
    
    filst: BaseContainer[FILST] = Field(default_factory=lambda: BaseContainer[FILST](), description="FILST container with validation")
    cases: BaseContainer[Cases] = Field(default_factory=lambda: BaseContainer[Cases](), description="CASES container with validation")
    
    # Enhanced containers with validation
    rfile: BaseContainer[RFILE] = Field(default_factory=lambda: BaseContainer[RFILE](), description="RFILE container with validation")
    incdf: BaseContainer[INCDF] = Field(default_factory=lambda: BaseContainer[INCDF](), description="INCDF container with validation")
    
    # Enhanced containers with validation
    greco: BaseContainer[GRECO] = Field(default_factory=lambda: BaseContainer[GRECO](), description="GRECO container with validation")
    basco: BaseContainer[BASCO] = Field(default_factory=lambda: BaseContainer[BASCO](), description="BASCO container with validation")
    loadc: BaseContainer[LOADC] = Field(default_factory=lambda: BaseContainer[LOADC](), description="LOADC container with validation")
    shsec: BaseContainer[SHSEC] = Field(default_factory=lambda: BaseContainer[SHSEC](), description="SHSEC container with validation")
    shaxe: BaseContainer[SHAXE] = Field(default_factory=lambda: BaseContainer[SHAXE](), description="SHAXE container with validation")
    cmpec: BaseContainer[CMPEC] = Field(default_factory=lambda: BaseContainer[CMPEC](), description="CMPEC container with validation")
    rmpec: BaseContainer[RMPEC] = Field(default_factory=lambda: BaseContainer[RMPEC](), description="RMPEC container with validation")
    retyp: BaseContainer[RETYP] = Field(default_factory=lambda: BaseContainer[RETYP](), description="RETYP container with validation")
    reloc: BaseContainer[RELOC] = Field(default_factory=lambda: BaseContainer[RELOC](), description="RELOC container with validation")
    lores: BaseContainer[LORES] = Field(default_factory=lambda: BaseContainer[LORES](), description="LORES container with validation")
    xtfil: BaseContainer[XTFIL] = Field(default_factory=lambda: BaseContainer[XTFIL](), description="XTFIL container with validation")
    desec: BaseContainer[DESEC] = Field(default_factory=lambda: BaseContainer[DESEC](), description="DESEC container with validation")
    table: BaseContainer[TABLE] = Field(default_factory=lambda: BaseContainer[TABLE](), description="TABLE container with validation")
   
    execd: List[EXECD] = Field(default_factory=list, description="EXECD statements")
    decas: BaseContainer[DECAS] = Field(default_factory=lambda: BaseContainer[DECAS](), description="DECAS container with validation")
    depar: BaseContainer[DEPAR] = Field(default_factory=lambda: BaseContainer[DEPAR](), description="DEPAR container with validation")
    
    # Enhanced validation control with automatic deferral
    validation_enabled: bool = Field(default=True, exclude=True, description="Enable validation during operations")
    container_validation_enabled: bool = Field(default=True, exclude=True, description="Enable container-level validation")
    cross_container_validation_enabled: bool = Field(default=True, exclude=True, description="Enable cross-container validation")
    building_mode: bool = Field(default=True, exclude=True, description="Internal flag: True during model building, False when complete")
    deferred_cross_validation: bool = Field(default=True, exclude=True, description="Automatically defer cross-container validation during building")
    
    @model_validator(mode='after')
    def setup_container_parent_references(self) -> 'SD_BASE':
        """Set parent model references for all containers."""
        # Set parent model reference for all BaseContainer instances
        for field_name in ['rfile', 'incdf', 'greco', 'basco', 'loadc', 'shsec', 'shaxe', 
                          'cmpec', 'rmpec', 'retyp', 'reloc', 'lores', 'xtfil', 'desec', 'table', 'decas', 'depar']:
            container = getattr(self, field_name, None)
            if container and hasattr(container, 'set_parent_model'):
                container.set_parent_model(self)
        return self
    


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
        elif isinstance(item, SHAXE):
            self.shaxe.add(item)
        elif isinstance(item, CMPEC):
            self.cmpec.add(item)
        elif isinstance(item, RMPEC):
            self.rmpec.add(item)
        elif isinstance(item, RETYP):
            self.retyp.add(item)
        elif isinstance(item, RELOC):
            self.reloc.add(item)
        elif isinstance(item, LORES):
            self.lores.add(item)
        elif isinstance(item, XTFIL):
            self.xtfil.add(item)
        elif isinstance(item, DESEC):
            self.desec.add(item)
        elif isinstance(item, TABLE):
            self.table.add(item)
        elif isinstance(item, RFILE):
            self.rfile.add(item)
        elif isinstance(item, INCDF):
            self.incdf.add(item)
        elif isinstance(item, DECAS):
            self.decas.add(item)
        elif isinstance(item, DEPAR):
            self.depar.add(item)
        
        # Container-based routing for simple statements
        elif isinstance(item, FILST):
            self.filst.add(item)
        elif isinstance(item, HEADL):
            self.headl.add(item)
        elif isinstance(item, Cases):
            self.cases.add(item)
        elif isinstance(item, HEADING):
            self.heading.append(item)
        elif isinstance(item, EXECD):
            self.execd.append(item)
        
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
            elif item_type == SHAXE:
                self.shaxe.add_batch(type_items)
            elif item_type == CMPEC:
                self.cmpec.add_batch(type_items)
            elif item_type == RMPEC:
                self.rmpec.add_batch(type_items)
            elif item_type == RETYP:
                self.retyp.add_batch(type_items)
            elif item_type == RELOC:
                self.reloc.add_batch(type_items)
            elif item_type == LORES:
                self.lores.add_batch(type_items)
            elif item_type == XTFIL:
                self.xtfil.add_batch(type_items)
            elif item_type == DESEC:
                self.desec.add_batch(type_items)
            elif item_type == TABLE:
                self.table.add_batch(type_items)
            else:
                # Fall back to individual processing for non-container types
                for item in type_items:
                    self._route_item(item)
        
        # Add all to master list
        self.all_items.extend(items)
        
        # Model-level cross-object validation
        if self.validation_enabled:
            self._validate_cross_references()
    
    # Validation control methods
    def disable_container_validation(self) -> None:
        """Disable container-level validation only."""
        self.container_validation_enabled = False
    
    def enable_container_validation(self) -> None:
        """Enable container-level validation."""
        self.container_validation_enabled = True
    
    def disable_cross_container_validation(self) -> None:
        """Disable cross-container validation only."""
        self.cross_container_validation_enabled = False
    
    def enable_cross_container_validation(self) -> None:
        """Enable cross-container validation."""
        self.cross_container_validation_enabled = True
    
    @contextmanager
    def container_validation_disabled(self):
        """Context manager to temporarily disable container validation."""
        original_state = self.container_validation_enabled
        self.container_validation_enabled = False
        try:
            yield
        finally:
            self.container_validation_enabled = original_state
    
    @contextmanager
    def cross_validation_disabled(self):
        """Context manager to temporarily disable cross-container validation."""
        original_state = self.cross_container_validation_enabled
        self.cross_container_validation_enabled = False
        try:
            yield
        finally:
            self.cross_container_validation_enabled = original_state
    
    def _finalize_model(self) -> None:
        """Mark model as complete and trigger final validation."""
        self.building_mode = False  # Exit building mode
        
        # If we deferred cross-container validation, run it now
        if (self.deferred_cross_validation and 
            self.cross_container_validation_enabled and 
            self.validation_enabled):
            self._validate_cross_references()
    
    def disable_deferred_validation(self) -> None:
        """Disable automatic deferral - validate immediately during building."""
        self.deferred_cross_validation = False
    
    def enable_deferred_validation(self) -> None:
        """Enable automatic deferral (default behavior)."""
        self.deferred_cross_validation = True
    
    @contextmanager
    def immediate_validation(self):
        """Context manager to temporarily disable deferred validation."""
        original_state = self.deferred_cross_validation
        self.deferred_cross_validation = False
        try:
            yield
        finally:
            self.deferred_cross_validation = original_state
    
    def _validate_cross_references(self) -> None:
        """Perform model-level cross-object validation with automatic deferral."""
        # Skip validation if disabled globally
        if validation_config.mode.value == 'disabled' or not self.validation_enabled:
            return
        
        # SMART DEFERRAL: Skip cross-container validation during building mode if deferred validation is enabled
        if (self.building_mode and 
            self.deferred_cross_validation and 
            self.cross_container_validation_enabled):
            # Silently defer cross-container validation - no error, no noise
            return
            
        # Skip cross-container validation if specifically disabled
        if not self.cross_container_validation_enabled:
            return
            
        issues = self._collect_validation_issues()
        
        # Check for critical errors based on validation mode
        if validation_config.mode.value == 'permissive':
            # In permissive mode, only raise for critical errors, not reference errors
            critical_errors = [issue for issue in issues if issue.severity == 'error' and 'CRITICAL' in issue.code]
        else:
            # In normal/strict mode, raise for all errors
            critical_errors = [issue for issue in issues if issue.severity == 'error']
            
        if critical_errors:
            error_messages = [f"[{error.code}] {error.message}" for error in critical_errors]
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
        all_statements.extend(self.shaxe.items)
        all_statements.extend(self.cmpec.items)
        all_statements.extend(self.rmpec.items)
        all_statements.extend(self.retyp.items)
        all_statements.extend(self.reloc.items)
        all_statements.extend(self.lores.items)  # Add LORES container
        all_statements.extend(self.xtfil.items)  # Add XTFIL container
        all_statements.extend(self.desec.items)  # Add DESEC container
        all_statements.extend(self.table.items)  # Add TABLE container
        all_statements.extend(self.rfile.items)  # RFILE is now a container
        all_statements.extend(self.incdf.items)  # INCDF is now a container
        all_statements.extend(self.decas.items)  # DECAS is now a container
        all_statements.extend(self.depar.items)  # DEPAR is now a container
        all_statements.extend(self.filst)
        
        for statement in all_statements:
            context = ValidationContext(
                current_object=statement,
                full_model=self
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
        elif statement_type == SHAXE:
            return self.shaxe.get_ids()
        elif statement_type == CMPEC:
            return self.cmpec.get_ids()
        elif statement_type == RMPEC:
            return self.rmpec.get_ids()
        elif statement_type == RETYP:
            return self.retyp.get_ids()
        elif statement_type == RELOC:
            return self.reloc.get_ids()
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
                'shaxe': len(self.shaxe),
                'cmpec': len(self.cmpec),
                'rmpec': len(self.rmpec),
                'retyp': len(self.retyp),
                'reloc': len(self.reloc),
                'lores': len(self.lores),
                'xtfil': len(self.xtfil),
                'desec': len(self.desec),
                'table': len(self.table),
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
        """Enhanced context manager with automatic validation management.
        
        Args:
            output_file: Path to the output file
            validation_enabled: Enable/disable validation during construction
        
        Yields:
            SD_BASE: Model instance for building
        """
        sd_model = cls(validation_enabled=validation_enabled)
        try:
            yield sd_model
        finally:
            # AUTOMATIC FINALIZATION: Trigger final validation and mark as complete
            sd_model._finalize_model()
            
            # Write the model to file
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
              


    
