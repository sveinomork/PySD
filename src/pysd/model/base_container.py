from typing import List, Protocol, runtime_checkable, Self, Union, Any, TypeVar, Generic, Optional, Iterator, TYPE_CHECKING
from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE


@runtime_checkable
class HasIdentifier(Protocol):
    """Protocol for objects that have an identifier property."""
    @property
    def identifier(self) -> Union[int, str]:
        """Get unique identifier for this object."""
        ...


T = TypeVar('T', bound=HasIdentifier)


class BaseContainer(BaseModel, Generic[T]):
    """
    Universal container for all statement types with rule-based validation.
    
    This container works with any statement that has an `identifier` property,
    provides unique ID validation, and integrates with the rule-based validation system.
    
    The container automatically runs container-level validation rules when items are added
    or when explicitly validated.
    
    Examples:
        # For BASCO statements
        basco_container = BaseContainer[BASCO](items=[basco1, basco2])
        
        # For GRECO statements  
        greco_container = BaseContainer[GRECO](items=[greco1, greco2])
        
        # Add items with automatic validation
        greco_container.add(GRECO(id='A', bas=...))  # Runs container rules
        
        # Manual validation (useful for batch operations)
        greco_container.validate()
    """
    model_config = {'arbitrary_types_allowed': True}
    
    items: List[T] = Field(default_factory=list, description="List of items with unique identifiers")
    parent_model: Optional[Any] = Field(default=None, exclude=True, description="Reference to parent model for validation settings")
    
    def _normalize_id(self, value: Union[int, str, float, None]) -> str:
        """Normalize identifier values to a canonical string form.
        
        - Coerces whole-number floats (e.g., 1.0) to int first
        - Converts ints to string
        - Leaves strings as-is
        - Treats None as empty string (shouldn't normally happen for identifiers)
        """
        if value is None:
            return ""
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)
    
    @model_validator(mode='after')
    def validate_unique_identifiers(self) -> Self:
        """Ensure all item identifiers are unique."""
        # Skip validation if container validation is disabled
        if not self._is_container_validation_enabled():
            return self
            
        seen_ids: set[str] = set()
        for item in self.items:
            item_id = self._normalize_id(item.identifier)
            if item_id in seen_ids:
                raise ValueError(f"Duplicate identifier found: {item_id}")
            seen_ids.add(item_id)
        return self
    
    def set_parent_model(self, parent_model: 'SD_BASE') -> None:
        """Set the parent model for validation control."""
        self.parent_model = parent_model
    
    def _is_container_validation_enabled(self) -> bool:
        """Check if container validation is enabled."""
        # Check global validation config
        from ..validation.core import validation_config
        if validation_config.level == 'disabled':
            return False
        
        # Check parent model settings if available
        if self.parent_model and hasattr(self.parent_model, 'container_validation_enabled'):
            return self.parent_model.container_validation_enabled
        
        return True  # Default to enabled
    
    def add(self, item: T) -> None:
        """Add an item to the container with validation."""
        # Check for duplicate identifiers (unless validation is disabled)
        if self._is_container_validation_enabled():
            item_id = self._normalize_id(item.identifier)
            for existing in self.items:
                if self._normalize_id(existing.identifier) == item_id:
                    raise ValueError(f"Item with identifier {item_id} already exists")
        
        # Add the item
        self.items.append(item)
        
        # Run container-level validation rules
        self.validate_container()
    
    def add_batch(self, items: List[T]) -> None:
        """Add multiple items with batch validation."""
        # Add all items first (with individual duplicate checks)
        if self._is_container_validation_enabled():
            for item in items:
                item_id = self._normalize_id(item.identifier)
                for existing in self.items:
                    if self._normalize_id(existing.identifier) == item_id:
                        raise ValueError(f"Item with identifier {item_id} already exists")
        
        # Add items to the container
        self.items.extend(items)
        
        # Run container validation once at the end
        self.validate_container()
    
    def validate_container(self) -> None:
        """Run container-level validation rules."""
        if not self.items:
            return
        
        # Skip validation if container validation is disabled
        if not self._is_container_validation_enabled():
            return
        
        # Run container-level validation rules using the validation system
        from ..validation.rule_system import execute_validation_rules
        from ..validation.core import ValidationContext, validation_config
        
        # Skip validation if disabled globally
        if validation_config.level == 'disabled':
            return
        
        # Determine statement type from first item
        if self.items:
            # Create validation context
            context = ValidationContext()
            context.parent_container = self
            
            # Execute container-level validation rules
            issues = execute_validation_rules(self, context, level='container')
            
            # Handle validation issues based on global mode
            errors = [issue for issue in issues if issue.severity == 'error']
            if errors:
                if validation_config.level in ['strict', 'normal']:
                    error_messages = [f"[{error.code}] {error.message}" for error in errors]
                    raise ValueError("Container validation failed:\n" + "\n".join(error_messages))
                # In permissive mode, just log warnings (for now, we'll raise them)
        
        # Also do basic unique identifier validation
        seen_ids: set[str] = set()
        for item in self.items:
            item_id = self._normalize_id(item.identifier)
            if item_id in seen_ids:
                raise ValueError(f"Duplicate identifier found: {item_id}")
            seen_ids.add(item_id)
    
    def validate(self) -> None:
        """Explicitly run all validation (useful for batch operations)."""
        self.validate_container()
    
    def get_by_id(self, id_value: Union[int, str, float]) -> Optional[T]:
        """Get an item by identifier with flexible type matching."""
        target = self._normalize_id(id_value)
        for item in self.items:
            if self._normalize_id(item.identifier) == target:
                return item
        return None
    
    def get_ids(self) -> List[Union[int, str]]:
        """Get a list of all identifiers in the container."""
        return [item.identifier for item in self.items]
    
    def contains(self, id_value: Union[int, str, float]) -> bool:
        """Check if container contains an item with the given identifier."""
        return self.get_by_id(id_value) is not None
    
    def has_id(self, id_value: Union[int, str, float]) -> bool:
        """Check if container contains an item with the given identifier (alias for contains)."""
        return self.contains(id_value)
    
    def remove_by_id(self, id_value: Union[int, str, float]) -> bool:
        """Remove an item by identifier. Returns True if item was found and removed."""
        target = self._normalize_id(id_value)
        for i, item in enumerate(self.items):
            if self._normalize_id(item.identifier) == target:
                del self.items[i]
                # Re-validate after removal
                self.validate_container()
                return True
        return False
    
    def clear(self) -> None:
        """Remove all items from the container."""
        self.items.clear()
    
    def filter(self, predicate) -> List[T]:
        """Filter items based on a predicate function."""
        return [item for item in self.items if predicate(item)]
    
    def find_first(self, predicate) -> Optional[T]:
        """Find the first item that matches the predicate."""
        for item in self.items:
            if predicate(item):
                return item
        return None
    
    # Specialized query methods that work with identifiers
    def get_by_attribute(self, attr_name: str, value: Any) -> List[T]:
        """Get all items where an attribute equals the given value."""
        return [item for item in self.items if getattr(item, attr_name, None) == value]
    
    def get_by_range(self, attr_name: str, min_val: Union[int, float], max_val: Union[int, float]) -> List[T]:
        """Get all items where a numeric attribute is within the given range."""
        result = []
        for item in self.items:
            val = getattr(item, attr_name, None)
            if val is not None and min_val <= val <= max_val:
                result.append(item)
        return result
    
    def group_by(self, attr_name: str) -> dict[Any, List[T]]:
        """Group items by the value of a given attribute."""
        groups = {}
        for item in self.items:
            key = getattr(item, attr_name, None)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return groups
    
    def __len__(self) -> int:
        """Return the number of items in the container."""
        return len(self.items)
    
    def __iter__(self) -> Iterator[T]:
        """Allow iteration over items in the container."""
        return iter(self.items)
    
    def __getitem__(self, index: int) -> T:
        """Get item by index."""
        return self.items[index]
    
    def __bool__(self) -> bool:
        """Return True if container has items."""
        return len(self.items) > 0