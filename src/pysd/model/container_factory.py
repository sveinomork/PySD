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
    
    # Unified statement registry - single source of truth for ALL statements
    # ALL statements now use container storage for consistency and simplicity
    _statement_registry = {
        # Container-based statements
        'greco': {
            'type': GRECO,
            'description': 'GRECO statements for load case definitions'
        },
        'basco': {
            'type': BASCO,
            'description': 'BASCO statements for basic controls'
        },
        'loadc': {
            'type': LOADC,
            'description': 'LOADC statements for load case control'
        },
        'shsec': {
            'type': SHSEC,
            'description': 'SHSEC statements for shell sections'
        },
        'shaxe': {
            'type': SHAXE,
            'description': 'SHAXE statements for shell axis definitions'
        },
        'cmpec': {
            'type': CMPEC,
            'description': 'CMPEC statements for composite sections'
        },
        'rmpec': {
            'type': RMPEC,
            'description': 'RMPEC statements for removing composite sections'
        },
        'retyp': {
            'type': RETYP,
            'description': 'RETYP statements for element type changes'
        },
        'reloc': {
            'type': RELOC,
            'description': 'RELOC statements for element relocation'
        },
        'lores': {
            'type': LORES,
            'description': 'LORES statements for load result processing'
        },
        'xtfil': {
            'type': XTFIL,
            'description': 'XTFIL statements for external file operations'
        },
        'desec': {
            'type': DESEC,
            'description': 'DESEC statements for design sections'
        },
        'table': {
            'type': TABLE,
            'description': 'TABLE statements for tabular data'
        },
        'rfile': {
            'type': RFILE,
            'description': 'RFILE statements for result file operations'
        },
        'incdf': {
            'type': INCDF,
            'description': 'INCDF statements for include file operations'
        },
        'decas': {
            'type': DECAS,
            'description': 'DECAS statements for design case definitions'
        },
        'depar': {
            'type': DEPAR,
            'description': 'DEPAR statements for design parameters'
        },
        'filst': {
            'type': FILST,
            'description': 'FILST statements for file listings'
        },
        'headl': {
            'type': HEADL,
            'description': 'HEADL statements for heading lines'
        },
        'cases': {
            'type': Cases,
            'description': 'CASES for case range definitions'
        },
        
        # Previously list-based, now container-based for consistency!
        'heading': {
            'type': None,  # Will be imported later to avoid circular imports
            'description': 'HEADING comment blocks'
        },
        'execd': {
            'type': None,  # Will be imported later to avoid circular imports
            'description': 'EXECD execution statements'
        }
    }
    
    # Backward compatibility - keep old name as alias  
    _container_registry = {name: info['type'] 
                          for name, info in _statement_registry.items() 
                          if info['type'] is not None}

    
    @classmethod
    def get_routing_registry(cls) -> Dict[Type, str]:
        """Generate StatementRouter registry - ALL statements route to containers now!"""
        # Import here to avoid circular imports
        from ..statements.statement_heading import HEADING
        from ..statements.execd import EXECD
        
        # Update the None types with actual imports
        cls._statement_registry['heading']['type'] = HEADING
        cls._statement_registry['execd']['type'] = EXECD
        
        # Simple container routing for ALL statements - no more list complexity!
        routing = {}
        for name, info in cls._statement_registry.items():
            if info['type'] is not None:
                routing[info['type']] = name  # Direct container name, no '_list' suffix!
        
        return routing
    
    @classmethod
    def get_container_registry(cls) -> Dict[str, Type]:
        """Get ALL statements (now all are container-based for consistency)."""
        # Import here to avoid circular imports
        from ..statements.statement_heading import HEADING
        from ..statements.execd import EXECD
        
        # Update the None types
        cls._statement_registry['heading']['type'] = HEADING
        cls._statement_registry['execd']['type'] = EXECD
        
        return {name: info['type'] 
                for name, info in cls._statement_registry.items() 
                if info['type'] is not None}
    
    @classmethod
    def get_all_statement_types(cls) -> list[Type]:
        """Get all statement types for StatementType union generation."""
        # Import here to avoid circular imports
        from ..statements.statement_heading import HEADING
        from ..statements.execd import EXECD
        
        # Update the None types
        cls._statement_registry['heading']['type'] = HEADING
        cls._statement_registry['execd']['type'] = EXECD
        
        types = []
        for info in cls._statement_registry.values():
            if info['type'] is not None:
                types.append(info['type'])
        
        return types
    
    @classmethod
    def get_all_imports(cls) -> Dict[str, str]:
        """Generate import statements for all statement types."""
        imports = {}
        
        # All statement imports (no more container vs list distinction)
        for name, info in cls._statement_registry.items():
            if info['type'] is not None:
                statement_type = info['type']
                module_name = statement_type.__module__.split('.')[-1]
                imports[statement_type.__name__] = f"from .statements.{module_name} import {statement_type.__name__}"
            elif name == 'heading':
                imports['HEADING'] = "from .statements.statement_heading import HEADING"
            elif name == 'execd':
                imports['EXECD'] = "from .statements.execd import EXECD"
        
        return imports
    

    
    @classmethod
    def create_container_fields(cls) -> Dict[str, Any]:
        """
        Generate all Pydantic field declarations for containers.
        
        This replaces 20+ manual field definitions with dynamic generation.
        ALL statements now use containers for consistency!
        
        Returns:
            Dict mapping field names to Pydantic Field objects
        """
        # Import here to avoid circular imports
        from ..statements.statement_heading import HEADING
        from ..statements.execd import EXECD
        
        # Update the None types
        cls._statement_registry['heading']['type'] = HEADING
        cls._statement_registry['execd']['type'] = EXECD
        
        fields = {}
        
        # Create container fields for ALL statements
        for name, info in cls._statement_registry.items():
            if info['type'] is not None:
                statement_type = info['type']
                fields[name] = Field(
                    default_factory=lambda st=statement_type: BaseContainer[st](),
                    description=info['description']
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
        """Get list of all container names - ALL statements are containers now!"""
        return list(cls._statement_registry.keys())
    
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
        Set up parent model references for all containers using unified registry.
        
        Much simpler now - ALL statements use containers!
        
        Args:
            model: The SD_BASE model instance
        """
        print("DEBUG: ContainerFactory.setup_container_parent_references called")  # DEBUG
        
        # Get ALL container names (no more filtering needed)
        container_names = cls.get_container_names()
        
        print(f"DEBUG: Registry has {len(container_names)} containers: {container_names}")  # DEBUG
        
        for container_name in container_names:
            container = getattr(model, container_name, None)
            if container:
                print(f"DEBUG: Found container {container_name}, has set_parent_model: {hasattr(container, 'set_parent_model')}")  # DEBUG
                if hasattr(container, 'set_parent_model'):
                    container.set_parent_model(model)
                    print(f"DEBUG: Set parent for {container_name}")  # DEBUG
            else:
                print(f"DEBUG: Container {container_name} not found on model")  # DEBUG