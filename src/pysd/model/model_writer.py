"""
Simple ModelWriter - extracts ONLY the I/O logic from SD_BASE.

Goal: Move file writing logic out of sdmodel.py to make it shorter.
No new features - just the original functionality extracted.
"""

from __future__ import annotations
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE

class ModelWriter:
    """Simple writer that extracts file I/O from SD_BASE."""
    
    def __init__(self, model: 'SD_BASE'):
        self.model = model
    
    def write_to_file(self, output_file: str) -> None:
        """Write model to file - exact same logic as before."""
        with open(output_file, "w", encoding="utf-8") as f:
            for item in self.model.all_items:
                f.write(str(item) + "\n")
    
    def write(self, output_file: str) -> None:
        """Simple write method for new API - delegates to write_to_file."""
        self.write_to_file(output_file)
    
    @classmethod
    def write_model(cls, model: 'SD_BASE', output_file: str) -> None:
        """Write a model to file with finalization - convenience method.
        
        Args:
            model: SD_BASE model to write
            output_file: Path to output file
        """
        # Finalize the model first
        model._finalize_model()
        
        # Write using ModelWriter
        writer = cls(model)
        writer.write_to_file(output_file)
    
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
            validation_level = ValidationLevel.NORMAL if validation_level else ValidationLevel.DISABLED
        
        sd_model = SD_BASE(validation_level=validation_level)
        try:
            yield sd_model
        finally:
            # Same finalization as before
            sd_model._finalize_model()
            
            # Use writer to handle file I/O
            writer = cls(sd_model)
            writer.write_to_file(output_file)