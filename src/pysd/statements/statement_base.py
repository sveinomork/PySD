from abc import ABC,abstractmethod
from typing import Any
from pydantic import BaseModel, Field
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext
from .registry import register_statement


class StringBuilderHelper:
    """Helper class for hybrid string building approach."""
    
    def __init__(self, statement_name: str):
        self.input = f"{statement_name}"  
    
    def add_param(self, key: str, value: Any, skip_if: Any = None) -> None:
        """
        Add a parameter to the input string manually.

        Args:
            key: The parameter name (will be uppercased)
            value: The value to append
            skip_if: If provided, skip adding if value == skip_if

        Automatically handles tuple formatting (range or CSV).
        """
        if value is None:
            return
        if skip_if is not None and value == skip_if:
            return

        if isinstance(value, tuple):
            if len(value) == 2:
                val_str = f"{value[0]}-{value[1]}"
            else:
                val_str = ",".join(str(v) for v in value)
        else:
            val_str = str(value)

        self.input += f" {key.upper()}={val_str}"


class StatementBase(BaseModel, ABC):
    input: str = Field(default="", init=False)
    # General optional trailing comment for all statements. When set, builders
    # should append it as "% <comment>" at the end of the line.
    comment: str | None = Field(default=None, description="Optional trailing comment to append as '% <text>'.")
    
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass
   
    @property
    def statement_name(self) -> str:
        """Use the class name as identifier (e.g., SHSEC)."""
        return self.__class__.__name__.upper()
    
    @abstractmethod
    def _build_input_string(self) -> None:
        pass

    def _build_identifier(self, field_order: list[str] = None, add_hash: bool = False) -> str:
        """
        Build a unique identifier string from specified fields in order.
        
        Args:
            field_order: List of field names in the order they should appear (optional)
            add_hash: If True, add a hash of the object at the end
            
        Returns:
            String identifier like "YE_1_10_1_5" or "YE_1_10_1_5_ABC123" with hash
            
        Examples:
            pa="Ye", fs=(1,10), hs=(1,5) with field_order=["pa", "fs", "hs"] 
            -> "YE_1_10_1_5"
            
            _build_identifier(add_hash=True) -> uses all non-None fields + hash
        """
        parts = []
        
        # If no field_order specified, use all non-None fields in alphabetical order
        if field_order is None:
            field_order = sorted([f for f in self.__dict__.keys() 
                                 if not f.startswith('_') and f not in {'input'} 
                                 and getattr(self, f) is not None
                                 and not (isinstance(getattr(self, f), bool) and getattr(self, f) is False)
                                 and not (isinstance(getattr(self, f), list) and len(getattr(self, f)) == 0)])
        
        for field_name in field_order:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                
                if value is None:
                    continue
                    
                # Handle different value types
                if isinstance(value, str):
                    parts.append(value.upper())
                elif isinstance(value, tuple):
                    # Convert tuple (1,10) to "1_10"
                    parts.extend(str(v) for v in value)
                elif isinstance(value, (list, set)):
                    # Convert list/set to individual elements
                    parts.extend(str(v) for v in value)
                else:
                    # Convert other types to string
                    parts.append(str(value))
        
        # Join all parts with underscores
        identifier = "_".join(parts)
        
        # Add hash if requested
        if add_hash:
            import hashlib
            # Create hash from the object's string representation
            obj_hash = hashlib.md5(str(self).encode()).hexdigest()[:6].upper()
            identifier += f"_{obj_hash}"
        
        return identifier

    def _build_string_generic(
        self,
        exclude: set[str] | None = None,
        default_values: dict[str, Any] | None = None,
       
        field_order: list[str] | None = None,
        bool_flags: set[str] | None = None,
        special_formatting: dict[str, callable] | None = None,
        float_precision: int = 6,
        comment: str | None = None,
    ) -> str:
        """
        Enhanced generic string builder for statement-like models.

        Args:
            exclude: Fields to exclude from output
            default_values: Skip fields that match these default values  
            field_order: Order of fields (remaining fields added at end)
            bool_flags: Boolean fields that output as "KEY=" when True
            special_formatting: Dict of field -> formatting function
            float_precision: Decimal places for float formatting

        Rules:
        - Skips None fields.
        - Skips fields listed in `exclude`.
        - Skips fields that match a default value in `default_values`.
        - Tuples of length 2 are joined with "-" (range).
        - Tuples of length 3+ are joined with "," (coordinates).
        - Boolean flags output as "KEY=" when True, skipped when False.
        - Special formatting functions can override default formatting.
        """
        exclude = exclude or set()
        exclude = exclude.union({"input", "identifier", "name"})  # Always exclude internal fields
        default_values = default_values or {}
        bool_flags = bool_flags or set()
        special_formatting = special_formatting or {}
        parts = [self.statement_name]

        # Get all fields to process
        all_fields = list(self.__dict__.keys())
        
        # Order fields: specified order first, then remaining
        if field_order:
            ordered_fields = [f for f in field_order if f in all_fields]
            remaining_fields = [f for f in all_fields if f not in field_order]
            fields_to_process = ordered_fields + remaining_fields
        else:
            fields_to_process = all_fields

        for field in fields_to_process:
            value = getattr(self, field, None)
            
            if field in exclude:
                continue
            if value is None:
                continue
            if field in default_values and value == default_values[field]:
                continue

            # Handle special formatting
            if field in special_formatting:
                formatted = special_formatting[field](value)
                if formatted:  # Only add if formatter returns non-empty
                    parts.append(formatted)
            # Handle boolean flags
            elif field in bool_flags and value is True:
                parts.append(f"{field.upper()}=")
            elif field in bool_flags and value is False:
                continue  # Skip False boolean flags
            # Handle regular values
            elif isinstance(value, float):
                parts.append(f"{field.upper()}={value:.{float_precision}g}")
            elif isinstance(value, tuple):
                if len(value) == 2:
                    # Handle ranges like (1,4) -> "1-4"
                    val_str = f"{value[0]}-{value[1]}"
                else:
                    # Handle vectors like (1.0, 0.0, 0.0) with float precision
                    formatted_values = []
                    for v in value:
                        if isinstance(v, float):
                            formatted_values.append(f"{v:.{float_precision}g}")
                        else:
                            formatted_values.append(str(v))
                    val_str = ",".join(formatted_values)
                parts.append(f"{field.upper()}={val_str}")
            else:
                parts.append(f"{field.upper()}={value}")

        # If no explicit comment provided, fall back to the instance's comment attribute
        if comment is None:
            comment = getattr(self, "comment", None)

        # Add comment if provided (explicit or from attribute)
        if comment:
            parts.append(f"% {comment}")

        return " ".join(parts)
    
    def start_string(self) -> None:
        """Initialize an empty input string with the class name."""
        self.input = self.statement_name
    
    def _get_string_builder(self) -> "StringBuilderHelper":
        """Get a string builder helper for hybrid building approach."""
        return StringBuilderHelper(self.statement_name)

    def add_param(self, key: str, value: Any, skip_if: Any = None) -> None:
        """
        Add a parameter to the input string manually.

        Args:
            key: The parameter name (will be uppercased)
            value: The value to append
            skip_if: If provided, skip adding if value == skip_if

        Automatically handles tuple formatting (range or CSV).
        """
        if value is None:
            return
        if skip_if is not None and value == skip_if:
            return

        if isinstance(value, tuple):
            if len(value) == 2:
                val_str = f"{value[0]}-{value[1]}"
            else:
                val_str = ",".join(str(v) for v in value)
        else:
            val_str = str(value)

        self.input += f" {key.upper()}={val_str}"
    
    def add_comment(self, comment: str, prefix: str = "%") -> None:
        """
        Add a comment to the input string.
        
        Args:
            comment: The comment text
            prefix: Comment prefix (default: "%")
        """
        if comment:
            self.input += f" {prefix} {comment}"
    
    
    
    
    
    
    def model_post_init(self, __context) -> None:
        """Execute INSTANCE-level validation and build input string."""
        # 1. Execute ONLY instance-level validation
        self._execute_instance_validation()
        
        # 2. Build input string
        self._build_input_string()
        # 3. Append trailing comment if provided and not already present
        self._append_comment_if_needed()
    
    def _execute_instance_validation(self) -> None:
        """Execute instance-level validation rules."""
        context = ValidationContext(current_object=self)
        # Only instance-level rules - no full model context yet
        issues = execute_validation_rules(self, context, level='instance')
        
        for issue in issues:
            context.add_issue(issue)
    
    def _append_comment_if_needed(self) -> None:
        """Ensure trailing comment is appended if the instance has a comment.
        Avoid duplicate insertion if already present (e.g., generic builder added it).
        """
        c = getattr(self, 'comment', None)
        if c:
            marker = f"% {c}"
            if marker not in self.input:
                self.input += f" {marker}"
    
    def validate_cross_references(self, context: ValidationContext) -> None:
        """
        Execute container and model-level validation rules.
        Called by containers when full model context is available.
        """
        if context.full_model is None:
            # Only container-level validation possible
            issues = execute_validation_rules(self, context, level='container')
        else:
            # Both container and model-level validation
            issues = execute_validation_rules(self, context, level='container')
            issues.extend(execute_validation_rules(self, context, level='model'))
        
        for issue in issues:
            context.add_issue(issue)

    def __str__(self) -> str:
        return self.input

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Skip the abstract base class itself
        if cls is StatementBase:
            return
        # Allow opting out per class if ever needed
        if getattr(cls, "_exclude_from_registry", False):
            return
        # Register this concrete Statement subclass
        register_statement(cls)