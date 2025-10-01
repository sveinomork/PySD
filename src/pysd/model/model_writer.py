"""
Simple ModelWriter - extracts ONLY the I/O logic from SD_BASE.

Goal: Move file writing logic out of sdmodel.py to make it shorter.
No new features - just the original functionality extracted.
"""

from __future__ import annotations
import os
from pathlib import Path
from contextlib import contextmanager
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE


class ModelWriter:
    """Simple writer that extracts file I/O from SD_BASE."""

    def __init__(self, model: "SD_BASE"):
        self.model = model

    @staticmethod
    def validate_output_path(output_file: Union[str, Path]) -> Path:
        """Validate and resolve output file path.

        Args:
            output_file: Path to validate (str or Path)

        Returns:
            Path: Resolved absolute path

        Raises:
            ValueError: If parent directory doesn't exist or path is invalid
            PermissionError: If path is not writable
            TypeError: If output_file is not a string or Path
        """
        # Type validation
        if not isinstance(output_file, (str, Path)):
            raise TypeError(
                f"output_file must be str or Path, got {type(output_file).__name__}"
            )

        # Convert to Path and resolve to absolute path
        try:
            path = Path(output_file).resolve()
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid path '{output_file}': {e}") from e

        # Validate parent directory exists
        parent = path.parent
        if not parent.exists():
            raise ValueError(
                f"Parent directory does not exist: {parent}\n"
                f"Create it first or provide a valid path."
            )

        # Check write permissions
        if path.exists():
            # File exists - check if we can write to it
            if not os.access(path, os.W_OK):
                raise PermissionError(f"No write permission for existing file: {path}")
        else:
            # File doesn't exist - check if we can write to parent directory
            if not os.access(parent, os.W_OK):
                raise PermissionError(
                    f"No write permission for directory: {parent}"
                )

        return path

    def write_to_file(self, output_file: Union[str, Path]) -> Path:
        """Write model to file with path validation.

        Args:
            output_file: Path to the output file

        Returns:
            Path: Resolved absolute path where file was written

        Raises:
            ValueError: If parent directory doesn't exist
            PermissionError: If path is not writable
        """
        # Validate path first
        validated_path = self.validate_output_path(output_file)

        # Write to file
        with open(validated_path, "w", encoding="utf-8") as f:
            for item in self.model.all_items:
                f.write(str(item) + "\n")

        return validated_path

    def write(self, output_file: Union[str, Path]) -> Path:
        """Simple write method for new API - delegates to write_to_file.

        Returns:
            Path: Resolved absolute path where file was written
        """
        return self.write_to_file(output_file)

    @classmethod
    def write_model(cls, model: "SD_BASE", output_file: Union[str, Path]) -> Path:
        """Write a model to file with finalization and path validation.

        Args:
            model: SD_BASE model to write
            output_file: Path to output file

        Returns:
            Path: Resolved absolute path where file was written

        Raises:
            ValueError: If parent directory doesn't exist
            PermissionError: If path is not writable
        """
        # Finalize the model first
        model._finalize_model()

        # Write using ModelWriter
        writer = cls(model)
        return writer.write_to_file(output_file)

    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str, validation_level=None):
        """Context manager for creating models with proper I/O handling.

        Args:
            output_file: Path to the output file
            validation_level: ValidationLevel enum (DISABLED, NORMAL, STRICT) or boolean for backward compatibility

        Yields:
            SD_BASE: Model instance for building
        """
        from ..sdmodel import SD_BASE
        from ..validation.core import ValidationLevel

        # Handle backward compatibility - convert boolean to ValidationLevel
        if validation_level is None:
            validation_level = ValidationLevel.NORMAL
        elif isinstance(validation_level, bool):
            validation_level = (
                ValidationLevel.NORMAL if validation_level else ValidationLevel.DISABLED
            )

        sd_model = SD_BASE(validation_level=validation_level)
        try:
            yield sd_model
        finally:
            # Same finalization as before
            sd_model._finalize_model()

            # Use writer to handle file I/O
            writer = cls(sd_model)
            writer.write_to_file(output_file)
