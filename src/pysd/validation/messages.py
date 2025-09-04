"""
Standardized error message builder for PySD validation.
"""

from typing import Dict

class ErrorMessageBuilder:
    """Builds standardized error messages for validation."""
    
    TEMPLATES = {
        'REQUIRED_FIELD': "{field} is required for {statement_type}",
        'INVALID_RANGE': "{field} must be between {min_val} and {max_val}",
        'INVALID_LENGTH': "{field} must be max {max_length} characters",
        'INVALID_FORMAT': "{field} must match format: {format_desc}",
        'MUTUAL_EXCLUSION': "Cannot specify both {field1} and {field2}",
        'MISSING_DEPENDENCY': "{field} requires {dependency_field} to be specified",
        'INVALID_REFERENCE': "{field} references non-existent {ref_type} {ref_value}",
        'DUPLICATE_ID': "Duplicate {statement_type} ID {id_value} found",
        'INVALID_COUNT': "{field} must have exactly {expected_count} items, found {actual_count}",
        'INVALID_TYPE': "{field} must be of type {expected_type}",
        'CROSS_REFERENCE_MISSING': "{statement_type} {source_id} references non-existent {target_type} {target_id}",
        'BUSINESS_RULE_VIOLATION': "{rule_description}",
    }
    
    @classmethod
    def build_message(cls, template_key: str, **kwargs) -> str:
        """
        Build a standardized error message.
        
        Args:
            template_key: Key for the message template
            **kwargs: Arguments to fill the template
            
        Returns:
            Formatted error message
            
        Example:
            ErrorMessageBuilder.build_message(
                'INVALID_RANGE',
                field='ID',
                min_val=1,
                max_val=99999999
            )
            # Returns: "ID must be between 1 and 99999999"
        """
        template = cls.TEMPLATES.get(template_key, "Validation error: {error}")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Error building message for {template_key}: Missing argument {e}"
    
    @classmethod
    def add_template(cls, key: str, template: str) -> None:
        """Add a new message template."""
        cls.TEMPLATES[key] = template
    
    @classmethod
    def get_template(cls, key: str) -> str:
        """Get a message template by key."""
        return cls.TEMPLATES.get(key, "Unknown template: {error}")
    
    @classmethod
    def list_templates(cls) -> Dict[str, str]:
        """Get all available templates."""
        return cls.TEMPLATES.copy()


# Convenience functions for common error types
def field_required_error(field: str, statement_type: str) -> str:
    """Generate a field required error message."""
    return ErrorMessageBuilder.build_message(
        'REQUIRED_FIELD',
        field=field,
        statement_type=statement_type
    )

def invalid_range_error(field: str, min_val: int, max_val: int) -> str:
    """Generate an invalid range error message."""
    return ErrorMessageBuilder.build_message(
        'INVALID_RANGE',
        field=field,
        min_val=min_val,
        max_val=max_val
    )

def invalid_length_error(field: str, max_length: int) -> str:
    """Generate an invalid length error message."""
    return ErrorMessageBuilder.build_message(
        'INVALID_LENGTH',
        field=field,
        max_length=max_length
    )

def cross_reference_error(statement_type: str, source_id: str, target_type: str, target_id: str) -> str:
    """Generate a cross-reference error message."""
    return ErrorMessageBuilder.build_message(
        'CROSS_REFERENCE_MISSING',
        statement_type=statement_type,
        source_id=source_id,
        target_type=target_type,
        target_id=target_id
    )

def duplicate_id_error(statement_type: str, id_value: str) -> str:
    """Generate a duplicate ID error message."""
    return ErrorMessageBuilder.build_message(
        'DUPLICATE_ID',
        statement_type=statement_type,
        id_value=id_value
    )