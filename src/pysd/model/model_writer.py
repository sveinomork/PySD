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
    
    @classmethod
    @contextmanager
    def create_writer(cls, output_file: str, validation_enabled: bool = True):
        """Context manager - exact same as SD_BASE.create_writer."""
        from ..sdmodel import SD_BASE
        
        sd_model = SD_BASE(validation_enabled=validation_enabled)
        try:
            yield sd_model
        finally:
            # Same finalization as before
            sd_model._finalize_model()
            
            # Use writer to handle file I/O
            writer = cls(sd_model)
            writer.write_to_file(output_file)