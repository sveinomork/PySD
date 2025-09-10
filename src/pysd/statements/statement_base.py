




from abc import ABC,abstractmethod
from pydantic import BaseModel, Field
from ..validation.rule_system import execute_validation_rules
from ..validation.core import ValidationContext


class StatementBase(BaseModel, ABC):
    input: str = Field(default="", init=False)
    
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass
    
    @abstractmethod
    def _build_input_string(self) -> None:
        pass
    
    def model_post_init(self, __context) -> None:
        """Execute INSTANCE-level validation and build input string."""
        # 1. Execute ONLY instance-level validation
        self._execute_instance_validation()
        
        # 2. Build input string
        self._build_input_string()
    
    def _execute_instance_validation(self) -> None:
        """Execute instance-level validation rules."""
        context = ValidationContext(current_object=self)
        # Only instance-level rules - no full model context yet
        issues = execute_validation_rules(self, context, level='instance')
        
        for issue in issues:
            context.add_issue(issue)
    
    def validate_cross_references(self, context: ValidationContext) -> None:
        """
        Execute container and model-level validation rules.
        Called by containers when full model context is available.
        """
        if context.full_model is None:
            # Only container-level validation possible
            issues = execute_validation_rules(self, context, level='container')
        else:
            # Both container and model-level validation
            issues = execute_validation_rules(self, context, level='container')
            issues.extend(execute_validation_rules(self, context, level='model'))
        
        for issue in issues:
            context.add_issue(issue)

    def __str__(self) -> str:
        return self.input