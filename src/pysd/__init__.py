"""
PySD - Python library for ShellDesign (SD) modeling and analysis.

This package provides tools for creating, manipulating, and analyzing 
ShellDesign models with full type support and comprehensive documentation.

Main Components:
    SD_BASE: Core model container class with enum-based validation levels
    ValidationLevel: Enum for type-safe validation configuration (DISABLED, NORMAL, STRICT)
    StatementType: Union type of all supported statement types  
    StatementProtocol: Protocol that all statement classes implement
    statements: Module containing all statement implementations
    create_axes_based_on_3_points_in_plane: Geometric utility function

Example:
    >>> from pysd import SD_BASE, ValidationLevel, statements
    >>> model = SD_BASE(validation_level=ValidationLevel.NORMAL)
    >>> model.add(statements.LOADC(run_number=1, alc=1, olc=110))
    >>> model.write("model.inp")
"""

from .sdmodel import SD_BASE, StatementType, StatementProtocol
from .validation.core import ValidationLevel
from .helpers import create_axes_based_on_3_points_in_plane
from . import statements

__version__ = "0.1.0"
__all__ = [
    "SD_BASE",
    "StatementType", 
    "StatementProtocol",
    "ValidationLevel",
    "statements",
    "create_axes_based_on_3_points_in_plane"
]
