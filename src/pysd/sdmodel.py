from __future__ import annotations

from typing import List, Union, Sequence, Any
from pydantic import BaseModel, Field, model_validator

# Note: No per-statement runtime imports needed; auto-registry handles discovery

# Import container system
from .model.validation_manager import ValidationManager
from .model.container_factory import ContainerFactory
from .validation.core import ValidationLevel

from .types import StatementType


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
   
    # ✅ PHASE 3 COMPLETE: All container fields are now created dynamically!
    # No more manual container field definitions - they're auto-generated from ContainerFactory
   
    #  validation control
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL, exclude=True, description="Validation level: ValidationLevel enum")
    cross_object_validation: bool = Field(default=True, exclude=True, description="Enable immediate cross-object validation during add()")
    
    # ValidationManager and StatementRouter for extracted logic - initialized in model_validator
    router: Any = Field(default=None, exclude=True, description="Statement routing system")

    # === 1. CONSTRUCTION & INITIALIZATION ===
    
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
        
        # Initialize the parent Pydantic model
        super().__init__(**kwargs)
        
        # Configure global validation level
        from .validation.core import validation_config
        validation_config.level = validation_level
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Dynamically inject container fields from ContainerFactory."""
        super().__init_subclass__(**kwargs)
        
        # Inject all container fields dynamically
        from .model.container_factory import ContainerFactory
        ContainerFactory.inject_container_fields(cls)
    
    @model_validator(mode='after')
    def setup_container_parent_references(self) -> 'SD_BASE':
        """Set parent model references for all containers and initialize router."""
        # Import here to avoid circular imports
        from .model.statement_router import StatementRouter
        from .containers.base_container import BaseContainer
        
        # Initialize ValidationManager and StatementRouter
        self._validation_manager = ValidationManager(self)
        self.router = StatementRouter(self)
        
        # Create all container fields dynamically
        self._create_dynamic_containers()
        
        # Set parent model references - ContainerFactory provides the registry
        for container_name in ContainerFactory.get_container_names():
            container = getattr(self, container_name, None)
            # Type hint for IDE support - container should be BaseContainer
            if container is not None and isinstance(container, BaseContainer):
                container.set_parent_model(self)
        return self
    
    # === 2. PROPERTIES & ACCESS ===
    
    @property
    def validator(self) -> ValidationManager:
        """Get or create the validation manager."""
        if not hasattr(self, '_validation_manager') or self._validation_manager is None:
            self._validation_manager = ValidationManager(self)
        return self._validation_manager
    
    def __getattr__(self, name: str):
        """Dynamic container access - provides containers on-demand."""
        from .model.container_factory import ContainerFactory
        
        # Handle both 'basco_container' and 'basco' naming schemes
        if name.endswith('_container'):
            # Extract the base name (e.g., 'basco_container' -> 'basco')
            base_name = name[:-10]  # Remove '_container' suffix
        else:
            # Direct base name (e.g., 'basco')
            base_name = name
        
        # Check if it's a valid container
        if ContainerFactory.is_valid_container(base_name):
            # Create the containers if they don't exist yet
            if not hasattr(self, '_dynamic_containers'):
                self._dynamic_containers = {}
            
            # Check both naming schemes in our storage
            container_key = f'{base_name}_container'
            base_key = base_name
            
            if container_key not in self._dynamic_containers and base_key not in self._dynamic_containers:
                containers = ContainerFactory.create_containers()
                # Store with both naming schemes for backward compatibility
                for base_name_key, container in containers.items():
                    self._dynamic_containers[base_name_key] = container  # 'basco'
                    self._dynamic_containers[f'{base_name_key}_container'] = container  # 'basco_container'
            
            # Return the container using the requested naming scheme
            if name in self._dynamic_containers:
                return self._dynamic_containers[name]
            elif container_key in self._dynamic_containers:
                return self._dynamic_containers[container_key]
            elif base_key in self._dynamic_containers:
                return self._dynamic_containers[base_key]
        
        # Not a container, raise normal AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # === 3. CORE FUNCTIONALITY ===
    
    def add(self, item: Union[StatementType, Sequence[StatementType]], validation: bool = None) -> None:
        """Enhanced add method with immediate validation support.
        
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
        if run_cross_object_validation and self.validator.validation_enabled:
            # Temporarily disable deferred validation to force immediate validation
            original_deferred = self.validator.deferred_cross_validation
            self.validator.disable_deferred_validation()
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
                if original_deferred:
                    self.validator.enable_deferred_validation()
    
    def write(self, output_file: str) -> None:
        """Simple write method - delegates to ModelWriter for I/O.
        
        Args:
            output_file: Path to the output file
        """
        from .model.model_writer import ModelWriter
        ModelWriter.write_model(self, output_file)
    
    # === 4. VALIDATION ===
    
    @model_validator(mode='after')
    def validate_complete_model(self) -> 'SD_BASE':
        """Final model validation after all fields are set."""
        if self.validator.validation_enabled:
            self.validator.validate_cross_references()
        return self
    
    # === 5. INTERNAL/PRIVATE METHODS ===
    
    def _create_dynamic_containers(self) -> None:
        """Create all container fields dynamically based on ContainerFactory registry."""
        from .model.container_factory import ContainerFactory
        
        # Store containers in a private dict to avoid Pydantic validation issues
        self._dynamic_containers = ContainerFactory.create_containers()
    
    def _finalize_model(self) -> None:
        """Mark model as complete and trigger final validation."""
        self.validator.finalize_model_and_validation()

