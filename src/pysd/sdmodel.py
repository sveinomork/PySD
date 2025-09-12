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
from src.pysd.model.validation_manager import ValidationManager


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
    
    # ValidationManager and StatementRouter for extracted logic - initialized in model_validator
    router: Any = Field(default=None, exclude=True, description="Statement routing system")
    
    @property
    def validator(self) -> ValidationManager:
        """Get or create the validation manager."""
        if not hasattr(self, '_validation_manager') or self._validation_manager is None:
            self._validation_manager = ValidationManager(self)
        return self._validation_manager
    
    @model_validator(mode='after')
    def setup_container_parent_references(self) -> 'SD_BASE':
        """Set parent model references for all containers and initialize router."""
        # Import here to avoid circular imports
        from src.pysd.model.statement_router import StatementRouter
        
        # Initialize ValidationManager and StatementRouter
        self._validation_manager = ValidationManager(self)
        self.router = StatementRouter(self)
            
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
            # Use router for batch processing
            self.router.route_batch(item)
            self.all_items.extend(item)
        else:
            # Use router for single item
            self.router.route_item(item)
            self.all_items.append(item)
        
        # Perform model-level cross-object validation
        if self.validation_enabled:
            self.validator.validate_cross_references()
    
    # _route_item method removed - functionality moved to StatementRouter
    
    # _add_batch method removed - functionality moved to StatementRouter
    
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
        self.validator.finalize_model()
    
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
    

    
    @model_validator(mode='after')
    def validate_complete_model(self) -> 'SD_BASE':
        """Final model validation after all fields are set."""
        if self.validation_enabled:
            self.validator.validate_cross_references()
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
        return self.validator.validate_integrity()
    
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
              


    
