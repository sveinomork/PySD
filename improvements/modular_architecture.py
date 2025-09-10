# Suggested file structure refactor:

"""
src/pysd/
├── core/
│   ├── __init__.py
│   ├── base.py           # BaseStatement, common interfaces
│   ├── containers.py     # Container abstractions
│   └── protocols.py      # Type protocols
├── model/
│   ├── __init__.py
│   ├── builder.py        # Model building logic
│   ├── manager.py        # SD_BASE core functionality
│   └── serialization.py  # Import/export logic
├── validation/
│   ├── __init__.py
│   ├── core.py          # Current core
│   ├── engine.py        # Validation execution
│   ├── rules/           # Rule definitions
│   └── strategies.py    # Recovery strategies
└── statements/          # Keep existing structure
"""

# Example modular design:

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, List, Dict, Any

# === Core Module ===
class StatementProtocol(Protocol):
    """Protocol for all statements"""
    identifier: Any
    input: str

T = TypeVar('T', bound=StatementProtocol)

class ContainerProtocol(Protocol[T]):
    """Protocol for containers"""
    def add(self, item: T) -> None: ...
    def get_by_id(self, id_val: Any) -> T | None: ...
    def contains(self, id_val: Any) -> bool: ...

# === Model Module ===
class ModelManager:
    """Manages model state and operations"""
    
    def __init__(self):
        self._containers: Dict[type, ContainerProtocol] = {}
        self._validation_enabled = True
    
    def register_container(self, statement_type: type, container: ContainerProtocol):
        """Register container for statement type"""
        self._containers[statement_type] = container
    
    def add_statement(self, statement: StatementProtocol) -> None:
        """Add statement to appropriate container"""
        statement_type = type(statement)
        container = self._containers.get(statement_type)
        if container:
            container.add(statement)
        else:
            raise ValueError(f"No container registered for {statement_type}")

class ModelBuilder:
    """Builds and configures models"""
    
    def __init__(self):
        self.manager = ModelManager()
        self._setup_containers()
    
    def _setup_containers(self):
        """Setup default containers"""
        from ..containers import StandardContainer
        from ..statements import BASCO, GRECO  # etc
        
        self.manager.register_container(BASCO, StandardContainer[BASCO]())
        self.manager.register_container(GRECO, StandardContainer[GRECO]())
        # etc...
    
    def build(self) -> 'SD_BASE':
        """Build complete model"""
        return SD_BASE(manager=self.manager)

# === Validation Module ===
class ValidationEngine:
    """Centralized validation execution"""
    
    def __init__(self):
        self._rules_by_level = {
            'instance': {},
            'container': {},
            'model': {}
        }
    
    def register_rule(self, level: str, statement_type: type, rule):
        """Register validation rule"""
        if level not in self._rules_by_level:
            raise ValueError(f"Invalid level: {level}")
        
        if statement_type not in self._rules_by_level[level]:
            self._rules_by_level[level][statement_type] = []
        
        self._rules_by_level[level][statement_type].append(rule)
    
    def validate(self, obj: Any, level: str, context: Any) -> List[Any]:
        """Execute validation for object at specified level"""
        statement_type = type(obj)
        rules = self._rules_by_level.get(level, {}).get(statement_type, [])
        
        issues = []
        for rule in rules:
            try:
                rule_issues = rule(obj, context)
                issues.extend(rule_issues)
            except Exception as e:
                # Handle rule execution errors
                issues.append(self._create_rule_error(rule, e))
        
        return issues
    
    def _create_rule_error(self, rule, exception):
        """Create error for rule execution failure"""
        return {
            'code': 'RULE_EXECUTION_ERROR',
            'message': f'Rule {rule} failed: {exception}',
            'severity': 'error'
        }

# === Refactored SD_BASE ===
class SD_BASE:
    """Simplified SD_BASE using modular components"""
    
    def __init__(self, manager: ModelManager = None):
        self.manager = manager or ModelManager()
        self.validation_engine = ValidationEngine()
        self._setup_validation()
    
    def _setup_validation(self):
        """Setup validation rules"""
        from ..validation.rules import load_all_rules
        load_all_rules(self.validation_engine)
    
    def add(self, statement: StatementProtocol | List[StatementProtocol]) -> None:
        """Add statement(s) to model"""
        if isinstance(statement, list):
            for stmt in statement:
                self._add_single(stmt)
        else:
            self._add_single(statement)
    
    def _add_single(self, statement: StatementProtocol) -> None:
        """Add single statement"""
        # Instance validation
        instance_issues = self.validation_engine.validate(
            statement, 'instance', None
        )
        self._handle_issues(instance_issues)
        
        # Add to container
        self.manager.add_statement(statement)
        
        # Model-level validation
        model_issues = self.validation_engine.validate(
            statement, 'model', self
        )
        self._handle_issues(model_issues)
    
    def _handle_issues(self, issues: List[Any]) -> None:
        """Handle validation issues based on severity"""
        errors = [i for i in issues if i.get('severity') == 'error']
        if errors and self.manager._validation_enabled:
            from ..validation.core import ValidationErrorGroup, ErrorDetail
            error_details = [
                ErrorDetail(
                    code=i.get('code', 'UNKNOWN'),
                    message=i.get('message', 'Unknown error'),
                    category='validation',
                    severity='error'
                ) for i in errors
            ]
            raise ValidationErrorGroup(error_details)

# === Usage Example ===
def create_model_example():
    """Example of using modular architecture"""
    
    # Build model with automatic container setup
    builder = ModelBuilder()
    model = builder.build()
    
    # Add statements - routing and validation handled automatically
    from ..statements import BASCO, LoadCase
    
    basco = BASCO(
        id=101,
        load_cases=[
            LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.0)
        ]
    )
    
    model.add(basco)  # Automatic validation and routing
    
    return model

# === Plugin System Example ===
class PluginManager:
    """Plugin system for extensions"""
    
    def __init__(self):
        self._plugins = {}
    
    def register_plugin(self, name: str, plugin):
        """Register plugin"""
        self._plugins[name] = plugin
    
    def get_plugin(self, name: str):
        """Get plugin by name"""
        return self._plugins.get(name)
    
    def apply_plugins(self, model: SD_BASE):
        """Apply all plugins to model"""
        for plugin in self._plugins.values():
            if hasattr(plugin, 'apply_to_model'):
                plugin.apply_to_model(model)

class CustomValidationPlugin:
    """Example plugin for custom validation rules"""
    
    def apply_to_model(self, model: SD_BASE):
        """Add custom validation rules"""
        def custom_basco_rule(obj, context):
            # Custom validation logic
            return []
        
        model.validation_engine.register_rule(
            'instance', 
            BASCO, 
            custom_basco_rule
        )

# === Configuration System ===
class Configuration:
    """Configuration management"""
    
    def __init__(self):
        self._config = {
            'validation': {
                'mode': 'strict',
                'cache_enabled': True,
                'max_cache_size': 1000
            },
            'performance': {
                'batch_size': 100,
                'enable_threading': False
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

# Global configuration instance
config = Configuration()
