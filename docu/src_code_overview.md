# Overview of `src` Directory

This document provides an overview of the `src` directory, focusing on the main components, the validation system, and the process for registering new statements. It also suggests potential improvements and identifies areas of potentially unnecessary code.

## 1. Core Components Overview

The `src/pysd` directory contains the core logic for the ShellDesign model. Key components include:

*   **`SD_BASE` (in `sdmodel.py`):**
    *   The central Pydantic model representing the ShellDesign model.
    *   Acts as a container for all statement types.
    *   Manages global validation settings and orchestrates the routing and writing processes.
    *   Uses `Field(exclude=True)` for internal management attributes (e.g., `all_items`, `validation_enabled`) to prevent their serialization by default.
    *   Initializes `ValidationManager` and `StatementRouter`.

*   **`StatementRouter` (in `model/statement_router.py`):**
    *   Responsible for routing incoming statements (single or batch) to their appropriate `BaseContainer` or internal lists within the `SD_BASE` model.
    *   Employs a registry pattern (`_routing_registry`) to map statement types to container names, significantly reducing `SD_BASE`'s complexity by eliminating large `if/elif` chains.
    *   Designed to make adding new statements require minimal changes.

*   **`ValidationManager` (in `model/validation_manager.py`):**
    *   Centralizes all validation logic, extracted from `SD_BASE` to reduce its complexity.
    *   Handles collecting validation issues, running cross-reference validations, and managing validation settings (e.g., enabling/disabling, deferring validation).
    *   Provides context managers for temporarily altering validation behavior.

*   **`StatementBase` (in `statements/statement_base.py`):**
    *   An abstract base class for all statement types.
    *   Enforces that all statements have an `input` string and an `identifier` property.
    *   Includes a `model_post_init` hook for instance-level validation and building the statement's input string.

*   **`BaseContainer` (in `containers/base_container.py` - inferred):**
    *   A generic container class (e.g., `BaseContainer[GRECO]`) that holds collections of specific statement types.
    *   Used by `SD_BASE` to manage groups of related statements.

*   **Statement Implementations (in `statements/`):**
    *   Each file in this directory (e.g., `basco.py`, `greco.py`) defines a specific statement type.
    *   These classes inherit from `StatementBase` and typically use Pydantic for their own field validation.

*   **Validation System (in `validation/`):**
    *   **`core.py`:** Defines fundamental validation concepts:
        *   `ValidationSeverity` (ERROR, WARNING, INFO)
        *   `ValidationMode` (STRICT, NORMAL, PERMISSIVE, DISABLED)
        *   `ValidationLevel` (DISABLED, NORMAL, STRICT) - used by `SD_BASE` and convertible to `ValidationMode`.
        *   `PySDValidationError`: A custom exception for validation failures.
        *   `ValidationIssue`: A Pydantic model representing a single validation problem.
        *   `ValidationContext`: Carries contextual information during validation.
        *   `ValidationConfig`: A global, thread-safe singleton for managing validation settings (mode, disabled rules, custom thresholds).
    *   **`rule_system.py`:** Implements a rule-based validation system:
        *   `ValidationRegistry`: Stores validation rules.
        *   Decorators (`@instance_rule`, `@container_rule`, `@model_rule`) for registering rules at different levels.
        *   `execute_validation_rules`: Dispatches validation based on object type and level.
    *   **`cross_reference_rules.py`:** Contains specific model-level validation rules that check relationships and consistency between different statement types (e.g., `GrecoELCCrossReferenceRule`, `GrecoBasCountRule`).

## 2. Validation System Details

The validation system is robust and layered, providing fine-grained control over how and when validation occurs:

*   **Levels of Validation:**
    *   **Instance-level:** Performed immediately after a statement object is initialized (`StatementBase.model_post_init`). Focuses on the statement's internal consistency and field validity.
    *   **Container-level:** (Inferred from `StatementBase.validate_cross_references` being called by containers) Rules that validate statements within the context of their specific container (e.g., ensuring uniqueness of IDs within a `GRECO` container).
    *   **Model-level (Cross-reference):** Performed by `ValidationManager` and triggered by `SD_BASE`. These rules check relationships and consistency *between* different statement types or across the entire model. This level of validation can be deferred until the model is fully constructed.

*   **`ValidationConfig`:**
    *   A global, thread-safe singleton that dictates the overall validation behavior.
    *   `mode`: Controls when `PySDValidationError` exceptions are raised (e.g., `STRICT` raises for all issues, `DISABLED` raises for none).
    *   `custom_thresholds`: Allows setting a minimum severity for specific rule codes to trigger an error.
    *   `disabled_rules`: Enables disabling specific validation rules by their unique code.

*   **`ValidationIssue`:**
    *   A Pydantic model that encapsulates all details of a validation problem (severity, code, message, location, suggestion).
    *   Includes a `raise_if_needed()` method that consults the global `ValidationConfig` to determine if an exception should be raised.

*   **`ValidationContext`:**
    *   An object passed to validation rules, providing access to the `current_object` being validated, its `parent_container`, and the `full_model` (`SD_BASE`) when available.
    *   Collects `ValidationIssue`s and can automatically raise errors based on configuration.

*   **Rule Registration:**
    *   Validation rules are defined as functions with a consistent signature (`obj: BaseModel, context: ValidationContext -> List[ValidationIssue]`).
    *   They are registered with the `ValidationRegistry` using decorators (`@instance_rule`, `@container_rule`, `@model_rule`), making it straightforward to add new rules without modifying core dispatch logic.

## 3. Registering New Statements

The system provides a clear, albeit somewhat manual, process for integrating new statement types:

1.  **Create the Statement Class:**
    *   Define a new Pydantic model for the statement in `src/pysd/statements/your_new_statement.py`.
    *   It must inherit from `StatementBase`.
    *   Implement its specific fields, the `identifier` property, and the `_build_input_string` method.

2.  **Import in `src/pysd/statements/__init__.py`:**
    *   Add an `from .your_new_statement import YOUR_NEW_STATEMENT` import.
    *   Include `YOUR_NEW_STATEMENT` in the `__all__` list.

3.  **Add to `StatementRouter`:**
    *   In `src/pysd/model/statement_router.py`, import the new statement class.
    *   Add an entry to the `_routing_registry` dictionary within the `_build_routing_registry` method. This maps the statement type to its corresponding container name (e.g., `YOUR_NEW_STATEMENT: 'your_new_container_name'`).

4.  **Add Container Field to `SD_BASE`:**
    *   In `src/pysd/sdmodel.py`, add a new `BaseContainer` field for the new statement type.
    *   Example: `your_new_container: BaseContainer[YOUR_NEW_STATEMENT] = Field(default_factory=lambda: BaseContainer[YOUR_NEW_STATEMENT](), description="YOUR_NEW_STATEMENT container")`.

5.  **Update `StatementType` Union:**
    *   Add the new statement type to the `StatementType` Union in `src/pysd/sdmodel.py`.

6.  **Add Validation Rules (Optional but Recommended):**
    *   If the new statement requires specific validation, create new rule functions.
    *   Register these rules using the `@instance_rule`, `@container_rule`, or `@model_rule` decorators in `src/pysd/validation/rule_system.py` or a dedicated rules file (e.g., `src/pysd/validation/rules/your_new_statement_rules.py`).

## 4. Suggested Improvements

*   **Dynamic Container Generation in `SD_BASE`:**
    *   **Current Situation:** In `src/pysd/sdmodel.py`, the `SD_BASE` class explicitly defines each `BaseContainer` field for every statement type (e.g., `greco: BaseContainer[GRECO] = Field(...)`, `basco: BaseContainer[BASCO] = Field(...)`, etc.). This leads to significant boilerplate code, especially as new statement types are added. Each new statement requires a manual addition of a `Field` definition in `SD_BASE`.

    *   **Detailed Improvement:** The `ContainerFactory` (located in `src/pysd/model/container_factory.py`, though its content wasn't provided in the initial read, its name suggests its purpose) is ideally positioned to handle this. The improvement would involve:
        1.  **Centralized Container Registry in `ContainerFactory`:** `ContainerFactory` would maintain a registry of all known statement types and their corresponding container names. This could be populated either by explicit registration calls or by introspecting the `src/pysd/statements` directory.
        2.  **Dynamic Pydantic Field Generation:** `ContainerFactory` would expose a method (e.g., `ContainerFactory.generate_container_fields()`) that returns a dictionary of Pydantic `Field` objects. Each entry in this dictionary would correspond to a statement type, with the key being the container's attribute name (e.g., 'greco') and the value being a `Field` instance configured for `BaseContainer[StatementType]`.
        3.  **Integration into `SD_BASE`:** `SD_BASE` would then use Pydantic's `model_rebuild` or a similar mechanism during its initialization (e.g., in a `model_validator` or `__init_subclass__`) to dynamically add these fields. This would replace the numerous hardcoded `Field` definitions with a single, concise call to `ContainerFactory`.

    *   **Benefits:**
        *   **Reduced Boilerplate:** Eliminates dozens of repetitive lines of code in `SD_BASE`, making it much cleaner and easier to read.
        *   **Enhanced Extensibility:** Adding a new statement type would no longer require modifying `SD_BASE` directly. Once the new statement is registered with `ContainerFactory` (or discovered by it), `SD_BASE` would automatically include its container.
        *   **Improved Maintainability:** Changes to how containers are defined or initialized would be centralized within `ContainerFactory`, reducing the risk of inconsistencies across different statement types.
        *   **Reduced Error Surface:** Less manual code means fewer opportunities for typos or copy-paste errors when adding new statement types.
        *   **Single Source of Truth:** `ContainerFactory` would become the definitive place for defining which statement types have dedicated containers and how those containers are structured.

    *   **Conceptual Code Example (Illustrative):**

        ```python
        # In src/pysd/model/container_factory.py (conceptual)
        from typing import Type, Dict, Any
        from pydantic import Field
        from ..containers.base_container import BaseContainer
        # ... import all statement types here or have a mechanism to discover them

        class ContainerFactory:
            _statement_container_map: Dict[Type, str] = {} # Maps StatementType to container attribute name

            @classmethod
            def register_statement_type(cls, statement_type: Type, container_attr_name: str):
                cls._statement_container_map[statement_type] = container_attr_name

            @classmethod
            def generate_container_fields(cls) -> Dict[str, Any]:
                fields = {}
                for statement_type, attr_name in cls._statement_container_map.items():
                    fields[attr_name] = Field(
                        default_factory=lambda st=statement_type: BaseContainer[st](),
                        description=f"{statement_type.__name__} container"
                    )
                return fields

        # In src/pysd/sdmodel.py (conceptual)
        from pydantic import BaseModel, Field, model_validator
        from .model.container_factory import ContainerFactory
        # ... other imports

        class SD_BASE(BaseModel):
            # ... other fields like all_items, heading, execd

            # Dynamically generated container fields
            # This would replace the many explicit container field definitions
            # Pydantic v2 allows dynamic model creation or field addition
            # This might be done in __init_subclass__ or a model_validator
            # For simplicity, illustrating the concept:
            # **ContainerFactory.generate_container_fields() # This is conceptual, Pydantic needs proper integration

            # Example of how it might be integrated (Pydantic v2 approach)
            @model_validator(mode='after')
            def _add_dynamic_container_fields(cls, values):
                if not hasattr(cls, '_dynamic_fields_added'):
                    dynamic_fields = ContainerFactory.generate_container_fields()
                    for name, field_instance in dynamic_fields.items():
                        # This part is highly conceptual and depends on Pydantic's internal API
                        # A more robust solution might involve creating a new Model class
                        # or using Pydantic's __pydantic_fields__ directly if exposed.
                        # For now, assume a mechanism to add fields post-definition.
                        setattr(cls, name, field_instance)
                    cls._dynamic_fields_added = True
                return values

            # ... rest of SD_BASE methods
        ```
        This conceptual example shows how `ContainerFactory` could manage the definitions, and `SD_BASE` would then consume these definitions to build its Pydantic fields dynamically. The exact Pydantic mechanism might vary (e.g., using `create_model` or `__pydantic_init_subclass__` for Pydantic v2).

*   **`StatementRouter.register_statement_type` Implementation:**
    *   **Current:** The `register_statement_type` method in `StatementRouter` is a placeholder that does nothing.
    *   **Improvement:** Implement this method to allow for truly dynamic registration of new statement types at runtime. This would further reduce the need to modify `statement_router.py` for every new statement, enabling plugin-like extensibility.

*   **Robust Rollback in `SD_BASE.add`:**
    *   **Current:** If validation fails during an `add()` operation (especially for batch additions), the code only `pop()`s from `all_items` and notes that removing from containers is "more complex."
    *   **Improvement:** Implement a comprehensive rollback mechanism that ensures all changes made by the `add` operation are reverted from all relevant containers if validation fails. This is crucial for maintaining model consistency.

*   **Complete Placeholder Validation Rules:**
    *   **Current:** `GrecoELCCrossReferenceRule` and `GrecoBasCountRule` in `cross_reference_rules.py` contain `TODO` comments and placeholder logic (e.g., `_is_elc_defined_in_loadc` always returns `True`).
    *   **Improvement:** Fully implement these rules once the referenced statements (like `LOADC`) are migrated and their attributes are accessible. This will ensure complete validation coverage for existing business rules.

*   **Centralized Rule Definition and Organization:**
    *   **Current:** While `rule_system.py` provides a good registration mechanism, the actual rule logic is spread across `cross_reference_rules.py` and potentially within `StatementBase` (for instance-level rules).
    *   **Improvement:** Consider creating a dedicated `rules` subdirectory under `validation` (e.g., `src/pysd/validation/rules/`) where each file contains rules specific to a statement type or a cross-reference concern. This would improve discoverability and organization of validation logic.

*   **Streamlined `SD_BASE` Initialization and Validation Flags:**
    *   **Current:** `SD_BASE`'s `__init__` and `model_validator` handle a lot of setup, and there are multiple validation-related flags (`validation_level`, `cross_object_validation`, `validation_enabled`, `container_validation_enabled`, `cross_container_validation_enabled`).
    *   **Improvement:** Simplify the validation flags by primarily using `validation_level` and deriving the others from it, reducing redundancy and potential for inconsistency. Ensure a clear, well-documented sequence for initialization and setup.

*   **Type Hinting for `StatementType` Union:**
    *   **Current:** The `StatementType` Union in `sdmodel.py` requires manual updates for every new statement.
    *   **Improvement:** If dynamic statement registration is fully implemented, explore ways to dynamically generate or manage this Union to avoid manual updates.

## 5. Potentially Unnecessary Code

*   **`SD_BASE.create_writer` Context Manager:**
    *   **Observation:** This context manager appears to delegate entirely to `ModelWriter.create_writer`.
    *   **Consideration:** If `SD_BASE.create_writer` does not add any specific logic, state management, or unique behavior beyond what `ModelWriter.create_writer` already provides, it might be an unnecessary layer of indirection and could be removed. The user could directly use `ModelWriter.create_writer`.

*   **`StatementRouter.register_statement_type`:**
    *   **Observation:** This method is explicitly marked as a placeholder and currently has no implementation.
    *   **Consideration:** If dynamic statement registration is not a planned feature in the near future, this method could be removed to avoid confusion and unnecessary API surface. If it is a goal, it needs to be fully implemented.

*   **Redundant Validation Flags in `SD_BASE`:**
    *   **Observation:** `SD_BASE` has `validation_level` (an enum) and then several boolean flags (`validation_enabled`, `container_validation_enabled`, `cross_container_validation_enabled`) that are set based on `validation_level`.
    *   **Consideration:** While `validation_level` provides a high-level control, the existence of separate boolean flags might introduce redundancy. The `ValidationManager` also has methods to control these. It might be possible to streamline these flags, perhaps by making the boolean flags properties derived directly from `validation_level` or by centralizing their control entirely within `ValidationManager` to avoid potential inconsistencies.
