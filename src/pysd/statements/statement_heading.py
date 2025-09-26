from __future__ import annotations
from typing import Optional, Literal, overload
from pydantic import Field, model_validator
from .statement_base import StatementBase


@overload
def HEADING(
    *,
    statement: str,
    description: Optional[str] = None,
    comment: Optional[str] = None,
    line_length: int = 60,
) -> "HEADING":
    """Create a default style heading with statement name."""
    ...


@overload
def HEADING(
    *,
    bas_id: str,
    description: Optional[str] = None,
    comment: Optional[str] = None,
    line_length: int = 60,
) -> "HEADING":
    """Create a bas style heading for BASCO groups."""
    ...


class HEADING(StatementBase):
    """
    Creates formatted heading sections in the output file.

    Supports two styles:
    - **Default style**: Clean, bordered sections for major headings
    - **Bas style**: Compact format for BASCO group headers

    ### Usage with @overload
    ```python
    # Default style - automatically selected when using 'statement'
    HEADING(statement="LOAD CASES", description="Define all load combinations")

    # Bas style - automatically selected when using 'bas_id'
    HEADING(bas_id="A", description="Main load combination group")
    ```

    ### Examples
    ```python
    # Default style with multiline description and comments
    HEADING(
        statement="MATERIALS",
        description="Concrete properties\\nSteel reinforcement\\nMaterial factors",
        comment="Updated 2025-09-11\\nReviewed by SOM"
    )
    # Output:
    # % ════════════════════════════════════════════════════════════
    # %                       🏗️ MATERIALS 🏗️
    # % ────────────────────────────────────────────────────────────
    # % 📝 Concrete properties
    # % 📝 Steel reinforcement
    # % 📝 Material factors
    # % 💬 Updated 2025-09-11
    # % 💬 Reviewed by SOM
    # % ════════════════════════════════════════════════════════════

    # Bas style for BASCO groups
    HEADING(bas_id="B", description="Secondary load group", comment="Per ASCE 7-16")
    # Output:
    # % ⚡ Bas: B    Secondary load group (Per ASCE 7-16)

    # Custom line length
    HEADING(statement="ANALYSIS", description="Results and verification", line_length=80)
    ```
    """

    statement: Optional[str] = Field(
        None, description="Statement name or section title (will be uppercase)"
    )
    bas_id: Optional[str] = Field(
        None, description="BASCO group ID (automatically uses bas style)"
    )
    description: Optional[str] = Field(
        None, description="Optional description (use \\n for multiple lines)"
    )
    comment: Optional[str] = Field(
        None, description="Optional comment (use \\n for multiple lines)"
    )
    line_length: int = Field(60, description="Length of the border lines")
    heading_type: Literal["default", "bas"] = Field(
        "default", description="Heading style type"
    )

    def model_post_init(self, __context) -> None:
        """Execute INSTANCE-level validation but skip _build_input_string (done in validator)."""
        # 1. Execute ONLY instance-level validation
        self._execute_instance_validation()

        # Note: _build_input_string is called from validate_and_set_heading_type
        # after heading_type is properly set

    @model_validator(mode="after")
    def validate_and_set_heading_type(self) -> "HEADING":
        """Validate that either statement or bas_id is provided, and set heading_type."""
        if self.statement is not None and self.bas_id is not None:
            raise ValueError(
                "Cannot specify both 'statement' and 'bas_id'. Use one or the other."
            )

        if self.statement is None and self.bas_id is None:
            raise ValueError("Must specify either 'statement' or 'bas_id'.")

        # If bas_id is provided, automatically set heading_type to "bas"
        if self.bas_id is not None:
            object.__setattr__(self, "heading_type", "bas")

        # Now that heading_type is set correctly, build the input string
        self._build_input_string()

        return self

    @property
    def identifier(self) -> str:
        """Get unique identifier for this heading."""
        return self._build_identifier(field_order=["heading_type"], add_hash=True)

    def _get_emoji(self) -> str:
        """Auto-select emoji based on statement content or default for bas style."""
        if self.statement is None:  # bas style
            return "⚡"

        statement_lower = self.statement.lower()
        if any(word in statement_lower for word in ["load", "force", "basco", "greco"]):
            return "⚡"
        elif any(
            word in statement_lower
            for word in ["material", "concrete", "steel", "cmpec", "rmpec"]
        ):
            return "🏗️"
        elif any(
            word in statement_lower
            for word in ["geometry", "section", "desec", "shaxe"]
        ):
            return "📐"
        elif any(
            word in statement_lower for word in ["analysis", "result", "table", "xtfil"]
        ):
            return "📊"
        elif any(
            word in statement_lower for word in ["reinforcement", "retyp", "reloc"]
        ):
            return "🔩"
        elif any(word in statement_lower for word in ["model", "basic", "setup"]):
            return "🏛️"
        else:
            return "📋"

    def _build_input_string(self) -> None:
        """Build heading with selected style type."""
        if self.heading_type == "bas":
            self._build_bas_style()
        else:
            self._build_default_style()

    def _build_bas_style(self) -> None:
        """Build compact BASCO-style heading: % emoji Bas: ID    description"""
        # For bas style, always use load emoji ⚡ since it's for BASCO combinations
        emoji = "⚡"

        # Format: % emoji Bas: bas_id    description
        parts = [f"% {emoji} Bas: {self.bas_id}"]

        if self.description:
            # For bas style, only use first line of description to keep it compact
            first_desc_line = self.description.split("\\n")[0]
            parts.append(f"   {first_desc_line}")

        if self.comment:
            # Add comment on same line in parentheses for compact style
            first_comment_line = self.comment.split("\\n")[0]
            parts.append(f"({first_comment_line})")

        self.input = " ".join(parts)

    def _build_default_style(self) -> None:
        """Build clean style heading with multiline support."""
        emoji = self._get_emoji()
        title = f"{emoji} {self.statement.upper()} {emoji}"

        lines = []

        # Top border
        lines.append("% " + "═" * self.line_length)

        # Title line (centered)
        lines.append(f"% {title:^{self.line_length}}")

        # Add separator if we have description or comment
        if self.description or self.comment:
            lines.append("% " + "─" * self.line_length)

        # Description (multiline support)
        if self.description:
            desc_lines = self.description.split("\\n")
            for desc_line in desc_lines:
                lines.append(f"% 📝 {desc_line}")

        # Comment (multiline support)
        if self.comment:
            comment_lines = self.comment.split("\\n")
            for comment_line in comment_lines:
                lines.append(f"% 💬 {comment_line}")

        # Bottom border
        lines.append("% " + "═" * self.line_length)

        self.input = "\n".join(lines)

    def __str__(self) -> str:
        return self.input
