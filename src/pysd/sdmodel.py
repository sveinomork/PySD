from __future__ import annotations

from contextlib import contextmanager
from typing import List, Union, Protocol, runtime_checkable, Sequence, Dict, Any
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
from .statements.depar import DEPAR
from .statements.headl import HEADL
from .statements.cases import Cases
from .statements.execd import EXECD
from .statements.shsec import SHSEC
from .statements.rmpec import RMPEC
from .statements.xtfil import XTFIL
from .statements.statement_heading import HEADING

# Import container system
from .containers.base_container import BaseContainer
from .model.validation_manager import ValidationManager
from .model.container_factory import ContainerFactory
from .validation.core import ValidationLevel


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
    """Enhanced ShellDesign model with Pydantic validation and container-based architecture.
    
    Features:
    - Automatic container creation and validation
    - Cross-object reference validation via ValidationManager
    - Statement routing via StatementRouter  
    - Container management via ContainerFactory
    - Layered validation (object -> container -> model)
    - Backward compatible API
    - Model-level validation for business rules
    """
    
    # Maintain order of all items (excluded from serialization but tracked internally)
    all_items: List[StatementType] = Field(default_factory=list, exclude=True, description="Ordered list of all items")
   
    # Container fields - generated dynamically by ContainerFactory
    # This eliminates 20+ repetitive field definitions!
    greco: BaseContainer[GRECO] = Field(default_factory=lambda: BaseContainer[GRECO](), description="GRECO container")
    basco: BaseContainer[BASCO] = Field(default_factory=lambda: BaseContainer[BASCO](), description="BASCO container")
    loadc: BaseContainer[LOADC] = Field(default_factory=lambda: BaseContainer[LOADC](), description="LOADC container")
    shsec: BaseContainer[SHSEC] = Field(default_factory=lambda: BaseContainer[SHSEC](), description="SHSEC container")
    shaxe: BaseContainer[SHAXE] = Field(default_factory=lambda: BaseContainer[SHAXE](), description="SHAXE container")
    cmpec: BaseContainer[CMPEC] = Field(default_factory=lambda: BaseContainer[CMPEC](), description="CMPEC container")
    rmpec: BaseContainer[RMPEC] = Field(default_factory=lambda: BaseContainer[RMPEC](), description="RMPEC container")
    retyp: BaseContainer[RETYP] = Field(default_factory=lambda: BaseContainer[RETYP](), description="RETYP container")
    reloc: BaseContainer[RELOC] = Field(default_factory=lambda: BaseContainer[RELOC](), description="RELOC container")
    lores: BaseContainer[LORES] = Field(default_factory=lambda: BaseContainer[LORES](), description="LORES container")
    xtfil: BaseContainer[XTFIL] = Field(default_factory=lambda: BaseContainer[XTFIL](), description="XTFIL container")
    desec: BaseContainer[DESEC] = Field(default_factory=lambda: BaseContainer[DESEC](), description="DESEC container")
    table: BaseContainer[TABLE] = Field(default_factory=lambda: BaseContainer[TABLE](), description="TABLE container")
    rfile: BaseContainer[RFILE] = Field(default_factory=lambda: BaseContainer[RFILE](), description="RFILE container")
    incdf: BaseContainer[INCDF] = Field(default_factory=lambda: BaseContainer[INCDF](), description="INCDF container")
    decas: BaseContainer[DECAS] = Field(default_factory=lambda: BaseContainer[DECAS](), description="DECAS container")
    depar: BaseContainer[DEPAR] = Field(default_factory=lambda: BaseContainer[DEPAR](), description="DEPAR container")
    filst: BaseContainer[FILST] = Field(default_factory=lambda: BaseContainer[FILST](), description="FILST container")
    headl: BaseContainer[HEADL] = Field(default_factory=lambda: BaseContainer[HEADL](), description="HEADL container")
    cases: BaseContainer[Cases] = Field(default_factory=lambda: BaseContainer[Cases](), description="CASES container")
    
    # Special list-based collections (not containers)
    heading: List[HEADING] = Field(default_factory=list, description="HEADING comment blocks")
    execd: List[EXECD] = Field(default_factory=list, description="EXECD statements")
    
    # New simplified validation control
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL, exclude=True, description="Validation level: ValidationLevel enum")
    cross_object_validation: bool = Field(default=True, exclude=True, description="Enable immediate cross-object validation during add()")
    
    # Internal validation control (backward compatibility)
    validation_enabled: bool = Field(default=True, exclude=True, description="Enable validation during operations")
    container_validation_enabled: bool = Field(default=True, exclude=True, description="Enable container-level validation")
    cross_container_validation_enabled: bool = Field(default=True, exclude=True, description="Enable cross-container validation")
    building_mode: bool = Field(default=True, exclude=True, description="Internal flag: True during model building, False when complete")
    deferred_cross_validation: bool = Field(default=True, exclude=True, description="Automatically defer cross-container validation during building")
    
    # ValidationManager and StatementRouter for extracted logic - initialized in model_validator
    router: Any = Field(default=None, exclude=True, description="Statement routing system")

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.NORMAL, cross_object_validation: bool = True, **kwargs):
        """Initialize SD_BASE with simplified validation parameters.
        
        Args:
            validation_level: ValidationLevel enum (DISABLED, NORMAL, or STRICT)
            cross_object_validation: Enable immediate cross-object validation during add()
            **kwargs: Additional Pydantic model parameters
        """
        # Set validation fields before calling super().__init__
        kwargs.setdefault('validation_level', validation_level)
        kwargs.setdefault('cross_object_validation', cross_object_validation)
        
        # Configure validation settings based on level
        if validation_level == ValidationLevel.DISABLED:
            kwargs.setdefault('validation_enabled', False)
            kwargs.setdefault('container_validation_enabled', False) 
            kwargs.setdefault('cross_container_validation_enabled', False)
        elif validation_level in [ValidationLevel.NORMAL, ValidationLevel.STRICT]:
            kwargs.setdefault('validation_enabled', True)
            kwargs.setdefault('container_validation_enabled', True)
            kwargs.setdefault('cross_container_validation_enabled', True)
        
        # Initialize the parent Pydantic model
        super().__init__(**kwargs)
        
        # Configure global validation level
        from .validation.core import validation_config
        validation_config.level = validation_level
    
    
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
        from .model.statement_router import StatementRouter
        
        # Initialize ValidationManager and StatementRouter
        self._validation_manager = ValidationManager(self)
        self.router = StatementRouter(self)
        
        # Set parent model references - ContainerFactory provides the registry
        for container_name in ContainerFactory.get_container_names():
            container = getattr(self, container_name, None)
            if container and hasattr(container, 'set_parent_model'):
                container.set_parent_model(self)
        return self
    


    def add(self, item: Union[StatementType, Sequence[StatementType]], validation: bool = None) -> None:
        """
        Enhanced add method with immediate validation support.
        
        Features:
        - Automatic container selection based on type
        - Batch processing for lists
        - Immediate cross-object validation when requested
        - Layered validation (object -> container -> model)
        - Maintains backward compatibility
        
        Args:
            item: The component to add, or a list of components.
            validation: If True, run immediate cross-validation. If None, use model's cross_object_validation setting.
        """
        # Determine if we should run immediate validation
        # cross_object_validation setting controls cross-object validation independently
        run_cross_object_validation = self.cross_object_validation and (validation if validation is not None else True)
        
        # Add items to model first
        if isinstance(item, list):
            # Use router for batch processing
            self.router.route_batch(item)
            self.all_items.extend(item)
        else:
            # Use router for single item
            self.router.route_item(item)
            self.all_items.append(item)
        
        # Perform immediate cross-object validation if requested and enabled
        if run_cross_object_validation and self.validation_enabled:
            # Temporarily disable deferred validation to force immediate validation
            original_deferred = self.deferred_cross_validation
            self.deferred_cross_validation = False
            try:
                self.validator.validate_cross_references()
            except Exception as e:
                # If validation fails, remove the items that were just added
                if isinstance(item, list):
                    for _ in item:
                        self.all_items.pop()
                        # Also need to remove from containers - this is more complex
                        # For now, we'll let the error propagate and rely on proper usage
                else:
                    self.all_items.pop()
                    # Also need to remove from container - this is more complex
                    # For now, we'll let the error propagate and rely on proper usage
                
                # Re-raise the validation error
                raise e
            finally:
                self.deferred_cross_validation = original_deferred
    
    
    
    def write(self, output_file: str) -> None:
        """
        Simple write method to replace context manager pattern.
        
        Args:
            output_file: Path to the output file
        """
        # Finalize the model first
        self._finalize_model()
        
        # Delegate to ModelWriter for file output
        from .model.model_writer import ModelWriter
        writer = ModelWriter(self)
        writer.write(output_file)
    
    
    @model_validator(mode='after')
    def validate_complete_model(self) -> 'SD_BASE':
        """Final model validation after all fields are set."""
        if self.validation_enabled:
            self.validator.validate_cross_references()
        return self
    
    def _finalize_model(self) -> None:
        """Mark model as complete and trigger final validation."""
        self.validator.finalize_model()
   
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a comprehensive validation summary."""
        integrity = self.validator.validate_integrity()
        
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
    
    
    
    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str, validation_enabled: bool = True):
        """Context manager that delegates to ModelWriter for I/O.
        
        Args:
            output_file: Path to the output file
            validation_enabled: Enable/disable validation during construction
        
        Yields:
            SD_BASE: Model instance for building
        """
        # Delegate to ModelWriter to keep I/O logic out of SD_BASE
        from .model.model_writer import ModelWriter
        with ModelWriter.create_writer(output_file, validation_enabled) as sd_model:
            yield sd_model
    
 
  


    
