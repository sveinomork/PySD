from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Sequence
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

    def add_raw(self, raw: str) -> None:
        """
        Add a raw string segment to the input.

        Args:
            raw: The raw string to append
        """
        if raw:
            self.input += raw

    def append_comment(self, comment: str, prefix: str = "%") -> None:
        """
        Add a comment to the input string.

        Args:
            comment: The comment text
            prefix: Comment prefix (default: "%")
        """
        if comment:
            self.input += f" {prefix} {comment}"


class StatementBase(BaseModel, ABC):
    input: str = Field(default="", init=False)
    # General optional trailing comment for all statements. When set, builders
    # should append it as "% <comment>" at the end of the line.
    comment: str | None = Field(
        default=None, description="Optional trailing comment to append as '% <text>'."
    )

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

    def _build_identifier(
        self, field_order: list[str] = None, add_hash: bool = False
    ) -> str:
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
            field_order = sorted(
                [
                    f
                    for f in self.__dict__.keys()
                    if not f.startswith("_")
                    and f not in {"input"}
                    and getattr(self, f) is not None
                    and not (
                        isinstance(getattr(self, f), bool) and getattr(self, f) is False
                    )
                    and not (
                        isinstance(getattr(self, f), list)
                        and len(getattr(self, f)) == 0
                    )
                ]
            )

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
        field_order: Sequence[str],
        *,
        exclude: Optional[set[str]] = None,
        float_precision: int = 6,
        comment: Optional[str] = None,
        special_formatting: Optional[Dict[str, Callable[[Any], str]]] = None,
        # NEW: configurable tuple separators
        tuple_separators: Optional[Dict[int, str]] = None,
        field_tuple_separators: Optional[Dict[str, Dict[int, str]]] = None,
    ) -> str:
        """
        Generic string builder:
        - Scalars formatted normally (floats use float_precision).
        - Tuples/lists formatted using separators:
          default: length==2 -> '-', otherwise ',',
          override with tuple_separators {length: sep},
          override per-field with field_tuple_separators {field: {length: sep}}
        - special_formatting takes precedence and can return a fully formatted token.
        """
        exclude = exclude or set()
        special_formatting = special_formatting or {}

        helper = StringBuilderHelper(self.statement_name)

        def fmt_number(v: Any) -> str:
            if isinstance(v, float):
                # Avoid scientific notation for typical magnitudes
                s = f"{v:.{float_precision}f}".rstrip("0").rstrip(".")
                return s if s else "0"
            return str(v)

        def fmt_sequence(field: str, seq: Sequence[Any]) -> str:
            # Default separator policy
            sep = "-" if len(seq) == 2 else ","
            # Global override
            if tuple_separators and len(seq) in tuple_separators:
                sep = tuple_separators[len(seq)]
            # Per-field override
            if field_tuple_separators and field in field_tuple_separators:
                per = field_tuple_separators[field]
                if len(seq) in per:
                    sep = per[len(seq)]
            return sep.join(fmt_number(x) for x in seq)

        for name in field_order:
            if name in exclude:
                continue

            value = getattr(self, name, None)
            if value is None:
                continue

            # Custom formatter wins
            if name in special_formatting:
                token = special_formatting[name](value)
                # Ensure there is exactly one separating space before the token
                if token and not token.startswith(" "):
                    token = " " + token
                helper.add_raw(token)
                continue

            # Sequences/tuples
            if isinstance(value, (tuple, list)):
                helper.add_param(name, fmt_sequence(name, value))
                continue

            # Scalars
            helper.add_param(name, fmt_number(value))

        # Append trailing comment if provided or instance has comment attribute
        final_comment = comment if comment is not None else getattr(self, "comment", None)
        if final_comment:
            helper.append_comment(final_comment)

        return helper.input

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

    def add_raw(self, raw: str) -> None:
        """
        Add a raw string segment to the input.

        Args:
            raw: The raw string to append
        """
        if raw:
            self.input += raw

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
        issues = execute_validation_rules(self, context, level="instance")

        for issue in issues:
            context.add_issue(issue)

    def _append_comment_if_needed(self) -> None:
        """Ensure trailing comment is appended if the instance has a comment.
        Avoid duplicate insertion if already present (e.g., generic builder added it).
        """
        c = getattr(self, "comment", None)
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
            issues = execute_validation_rules(self, context, level="container")
        else:
            # Both container and model-level validation
            issues = execute_validation_rules(self, context, level="container")
            issues.extend(execute_validation_rules(self, context, level="model"))

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
