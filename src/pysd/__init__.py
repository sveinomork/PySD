"""
PySD - Python library for ShellDesign (SD) modeling and analysis.

This package provides tools for creating, manipulating, and analyzing 
ShellDesign models with full type support and comprehensive documentation.

Main Components:
    SD_BASE: Core model container class
    StatementType: Union type of all supported statement types  
    StatementProtocol: Protocol that all statement classes implement
    statements: Module containing all statement implementations
    create_axes_based_on_3_points_in_plane: Geometric utility function

Example:
    >>> from pysd import SD_BASE, statements
    >>> with SD_BASE.create_writer("model.dat") as sd:
    ...     sd.add(statements.HEADL("My Model"))
    ...     sd.add(statements.FILST())
"""

from .sdmodel import SD_BASE, StatementType, StatementProtocol
from .helpers import create_axes_based_on_3_points_in_plane
from . import statements

__version__ = "0.1.0"
__all__ = [
    "SD_BASE",
    "StatementType", 
    "StatementProtocol",
    "statements",
    "create_axes_based_on_3_points_in_plane"
]
