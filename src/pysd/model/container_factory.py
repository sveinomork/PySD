"""Container Factory - Dynamic container creation and management.

This module eliminates the 20+ repetitive container field definitions
from SD_BASE and makes adding new statement types trivial.

Focus: Replace boilerplate with clean, dynamic container creation.
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Type, TYPE_CHECKING
from pydantic import Field

# Ensure all statements are imported so auto-registry is populated
from .. import statements as _statements  # noqa: F401  (import for side effects)
from ..statements.registry import STATEMENT_CLASSES as _AUTO_REG
from .base_container import BaseContainer

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from ..sdmodel import SD_BASE


class ContainerFactory:
    """
    Factory for creating and managing all model containers.

    This eliminates the need for 20+ repetitive field definitions
    in SD_BASE and centralizes container management.
    """

    # Unified statement registry - single source of truth for ALL statements
    # In auto mode, this is synthesized from STATEMENT_CLASSES (via _build_auto_statement_registry).
    # A manual registry can be supplied here if ever needed (kept empty by default).
    _statement_registry: dict[str, dict] = {}

    USE_AUTO_REGISTRY: bool = True  # default to auto registry

    @classmethod
    def _build_auto_statement_registry(cls) -> dict[str, dict]:
        """
        Build the same structure as _statement_registry but from STATEMENT_CLASSES.
        Maps lowercased class names to {'type': class, 'description': ...}
        """
        auto = {}
        for cls_name, cls_type in _AUTO_REG.items():
            container_name = cls_name.lower()
            auto[container_name] = {
                "type": cls_type,
                "description": f"{cls_name} statements",
            }
        # If you have non-StatementBase special cases, add them here if needed
        return auto

    @classmethod
    def _get_active_registry(cls) -> dict[str, dict]:
        return (
            cls._build_auto_statement_registry()
            if cls.USE_AUTO_REGISTRY
            else cls._statement_registry
        )

    @classmethod
    def _get_container_types_dict(cls) -> Dict[str, Type]:
        """Helper: name -> concrete statement class (filters out None)."""
        reg = cls._get_active_registry()
        return {
            name: info["type"]
            for name, info in reg.items()
            if info.get("type") is not None
        }

    @classmethod
    def get_routing_registry(cls) -> Dict[Type, str]:
        """Generate StatementRouter registry - ALL statements route to containers now!"""
        reg = cls._get_active_registry()
        # Simple container routing for ALL statements - direct container name
        routing: Dict[Type, str] = {}
        for name, info in reg.items():
            t = info.get("type")
            if t is not None:
                routing[t] = name
        return routing

    @classmethod
    def get_container_registry(cls) -> Dict[str, Type]:
        """Get ALL statements (now all are container-based for consistency)."""
        return cls._get_container_types_dict()

    @classmethod
    def get_all_statement_types(cls) -> list[Type]:
        """Get all statement types for StatementType union generation."""
        reg = cls._get_active_registry()
        return [info["type"] for info in reg.values() if info.get("type") is not None]

    @classmethod
    def get_all_imports(cls) -> Dict[str, str]:
        """Generate import statements for all statement types."""
        imports: Dict[str, str] = {}
        reg = cls._get_active_registry()
        # All statement imports (no more container vs list distinction)
        for info in reg.values():
            t = info.get("type")
            if t is None:
                continue
            module_name = t.__module__.split(".")[-1]
            imports[t.__name__] = f"from .statements.{module_name} import {t.__name__}"
        return imports

    @classmethod
    def create_container_fields(cls) -> Dict[str, Any]:
        """
        Generate all Pydantic field declarations for containers.

        This replaces 20+ manual field definitions with dynamic generation.

        Returns:
            Dict mapping field names to Pydantic Field objects
        """
        fields: Dict[str, Any] = {}
        for container_name, statement_type in cls._get_container_types_dict().items():
            # Create the field definition with proper type hints
            fields[container_name] = Field(
                default_factory=lambda st=statement_type: BaseContainer[st](),
                description=f"{statement_type.__name__} container",
            )
        return fields

    @classmethod
    def inject_container_fields(cls, model_class: Type) -> None:
        """
        Dynamically inject container fields into a model class.

        This allows SD_BASE to get all container fields without manual definition.
        """
        container_fields = cls.create_container_fields()
        container_types = cls._get_container_types_dict()
        for field_name, field_def in container_fields.items():
            # Add field to model annotations and fields
            model_class.__annotations__[field_name] = (
                f"BaseContainer[{container_types[field_name].__name__}]"
            )
            setattr(model_class, field_name, field_def)

        # Rebuild the model to recognize new fields
        model_class.model_rebuild()

    @classmethod
    def create_containers(cls) -> Dict[str, BaseContainer]:
        """
        Create all container instances.

        This can be used for runtime container creation if needed.

        Returns:
            Dict mapping container names to BaseContainer instances
        """
        containers: Dict[str, BaseContainer] = {}
        for container_name, statement_type in cls._get_container_types_dict().items():
            containers[container_name] = BaseContainer[statement_type]()
        return containers

    @classmethod
    def get_container_types(cls) -> Dict[str, Type]:
        """Get mapping of container names to their statement types."""
        return cls._get_container_types_dict().copy()

    @classmethod
    def get_container_names(cls) -> list[str]:
        """Get list of all container names - ALL statements are containers now!"""
        return list(cls._get_active_registry().keys())

    @classmethod
    def is_valid_container(cls, container_name: str) -> bool:
        """Check if a container name is valid."""
        return container_name in cls._get_active_registry()

    @classmethod
    def get_statement_type(cls, container_name: str) -> Type | None:
        """Get the statement type for a container name."""
        return cls._get_container_types_dict().get(container_name)

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
        # Manual extension path (primarily for manual registry mode)
        if not cls.USE_AUTO_REGISTRY:
            cls._statement_registry[container_name] = {
                "type": statement_type,
                "description": f"{statement_type.__name__} statements",
            }
            return
        raise NotImplementedError(
            "Add new statements by defining a new StatementBase subclass; it will auto-register."
        )

    @classmethod
    def setup_container_parent_references(cls, model: "SD_BASE") -> None:
        """
        Set up parent model references for all containers using unified registry.

        Much simpler now - ALL statements use containers!

        Args:
            model: The SD_BASE model instance
        """
        logger.debug("ContainerFactory.setup_container_parent_references called")

        # Get ALL container names (no more filtering needed)
        container_names = cls.get_container_names()

        logger.debug(f"Registry has {len(container_names)} containers: {container_names}")

        for container_name in container_names:
            container = getattr(model, container_name, None)
            if container:
                logger.debug(
                    f"Found container {container_name}, has set_parent_model: {hasattr(container, 'set_parent_model')}"
                )
                if hasattr(container, "set_parent_model"):
                    container.set_parent_model(model)
                    logger.debug(f"Set parent for container: {container_name}")
            else:
                logger.debug(f"Container {container_name} not found on model")

    @classmethod
    def debug_compare_manual_vs_auto(cls) -> dict:
        """
        Compare current manual _statement_registry against auto-registered statements.
        Returns a dict with sets for diff inspection (no side effects).
        """
        manual = set(cls._statement_registry.keys())
        auto = {
            name.lower() for name in _AUTO_REG.keys()
        }  # class names -> container names
        return {
            "manual_container_names": manual,
            "auto_container_names": auto,
            "only_in_manual": sorted(manual - auto),
            "only_in_auto": sorted(auto - manual),
        }
