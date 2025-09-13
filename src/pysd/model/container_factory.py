"""
Container Factory - Dynamic container creation and management.

This module eliminates the 20+ repetitive container field definitions
from SD_BASE and makes adding new statement types trivial.

Focus: Replace boilerplate with clean, dynamic container creation.
"""

from __future__ import annotations
from typing import Dict, Any, Type, TYPE_CHECKING
from pydantic import Field

if TYPE_CHECKING:
    from ..sdmodel import SD_BASE

# Import all statement types for container creation
from ..statements.greco import GRECO
from ..statements.basco import BASCO
from ..statements.loadc import LOADC
from ..statements.shsec import SHSEC
from ..statements.shaxe import SHAXE
from ..statements.cmpec import CMPEC
from ..statements.rmpec import RMPEC
from ..statements.retyp import RETYP
from ..statements.reloc import RELOC
from ..statements.lores import LORES
from ..statements.xtfil import XTFIL
from ..statements.desec import DESEC
from ..statements.table import TABLE
from ..statements.rfile import RFILE
from ..statements.incdf import INCDF
from ..statements.decas import DECAS
from ..statements.depar import DEPAR
from ..statements.filst import FILST
from ..statements.headl import HEADL
from ..statements.cases import Cases

from ..containers.base_container import BaseContainer


class ContainerFactory:
    """
    Factory for creating and managing all model containers.
    
    This eliminates the need for 20+ repetitive field definitions
    in SD_BASE and centralizes container management.
    """
    
    # Registry of all container types - single source of truth
    _container_registry = {
        'greco': GRECO,
        'basco': BASCO,
        'loadc': LOADC,
        'shsec': SHSEC,
        'shaxe': SHAXE,
        'cmpec': CMPEC,
        'rmpec': RMPEC,
        'retyp': RETYP,
        'reloc': RELOC,
        'lores': LORES,
        'xtfil': XTFIL,
        'desec': DESEC,
        'table': TABLE,
        'rfile': RFILE,
        'incdf': INCDF,
        'decas': DECAS,
        'depar': DEPAR,
        'filst': FILST,
        'headl': HEADL,
        'cases': Cases,
    }
    
    @classmethod
    def create_container_fields(cls) -> Dict[str, Any]:
        """
        Generate all Pydantic field declarations for containers.
        
        This replaces 20+ manual field definitions with dynamic generation.
        
        Returns:
            Dict mapping field names to Pydantic Field objects
        """
        fields = {}
        
        for container_name, statement_type in cls._container_registry.items():
            # Create the field definition
            fields[container_name] = Field(
                default_factory=lambda st=statement_type: BaseContainer[st](),
                description=f"{statement_type.__name__} container"
            )
        
        return fields
    
    @classmethod
    def create_containers(cls) -> Dict[str, BaseContainer]:
        """
        Create all container instances.
        
        This can be used for runtime container creation if needed.
        
        Returns:
            Dict mapping container names to BaseContainer instances
        """
        containers = {}
        
        for container_name, statement_type in cls._container_registry.items():
            containers[container_name] = BaseContainer[statement_type]()
        
        return containers
    
    @classmethod
    def get_container_types(cls) -> Dict[str, Type]:
        """Get mapping of container names to their statement types."""
        return cls._container_registry.copy()
    
    @classmethod
    def get_container_names(cls) -> list[str]:
        """Get list of all container names."""
        return list(cls._container_registry.keys())
    
    @classmethod
    def is_valid_container(cls, container_name: str) -> bool:
        """Check if a container name is valid."""
        return container_name in cls._container_registry
    
    @classmethod
    def get_statement_type(cls, container_name: str) -> Type | None:
        """Get the statement type for a container name."""
        return cls._container_registry.get(container_name)
    
    @classmethod
    def add_container_type(cls, container_name: str, statement_type: Type) -> None:
        """
        Add a new container type to the registry.
        
        This makes adding new statement types easy - just call this method
        and the container will be automatically created everywhere.
        
        Args:
            container_name: Name of the container field (e.g., 'new_statement')
            statement_type: The statement class type (e.g., NEW_STATEMENT)
        """
        cls._container_registry[container_name] = statement_type
    
    @classmethod
    def setup_container_parent_references(cls, model: 'SD_BASE') -> None:
        """
        Set up parent model references for all containers.
        
        This replaces the manual setup in SD_BASE model_validator.
        
        Args:
            model: The SD_BASE model instance
        """
        print(f"DEBUG: ContainerFactory.setup_container_parent_references called")  # DEBUG
        # Include all container names from our registry plus any others that might exist
        all_container_names = list(cls._container_registry.keys())
        print(f"DEBUG: Registry has {len(all_container_names)} containers: {all_container_names}")  # DEBUG
        
        for container_name in all_container_names:
            container = getattr(model, container_name, None)
            if container:
                print(f"DEBUG: Found container {container_name}, has set_parent_model: {hasattr(container, 'set_parent_model')}")  # DEBUG
                if hasattr(container, 'set_parent_model'):
                    container.set_parent_model(model)
                    print(f"DEBUG: Set parent for {container_name}")  # DEBUG
            else:
                print(f"DEBUG: Container {container_name} not found on model")  # DEBUG