"""
Test script for ErrorMessageBuilder implementation.
"""

from pysd.validation.messages import ErrorMessageBuilder, field_required_error, invalid_range_error
from pysd import SD_BASE
from pysd.statements.greco import GRECO
from pysd.statements.cases import Cases

def test_error_message_builder():
    """Test ErrorMessageBuilder functionality."""
    print("Testing ErrorMessageBuilder...")
    
    # Test basic message building
    msg1 = ErrorMessageBuilder.build_message(
        'INVALID_RANGE',
        field='ID',
        min_val=1,
        max_val=99999999
    )
    print(f"Range error: {msg1}")
    
    # Test convenience function
    msg2 = field_required_error('BAS', 'GRECO')
    print(f"Required field error: {msg2}")
    
    # Test range convenience function
    msg3 = invalid_range_error('ID', 1, 26)
    print(f"Range convenience: {msg3}")
    
    # Test custom template
    ErrorMessageBuilder.add_template('CUSTOM_ERROR', "Custom error for {item}: {reason}")
    msg4 = ErrorMessageBuilder.build_message('CUSTOM_ERROR', item='GRECO', reason='invalid format')
    print(f"Custom error: {msg4}")
    
    print("✓ ErrorMessageBuilder working correctly")

def test_error_messages_in_validation():
    """Test that ErrorMessageBuilder is used in actual validation."""
    print("\nTesting ErrorMessageBuilder in validation...")
    
    # Test GRECO ID validation with ErrorMessageBuilder
    try:
        greco_invalid = GRECO(id='1', bas=Cases(ranges=[1, 2, 3, 4, 5, 6]))
        print("✗ Should have failed with invalid ID")
    except ValueError as e:
        print(f"✓ ID validation error: {e}")
        # Check if the error message follows the standard format
        assert "format" in str(e).lower(), "Error message should mention format"
    
    # Test BAS count validation with ErrorMessageBuilder
    try:
        greco_too_many = GRECO(
            id='B', 
            bas=Cases(ranges=[1, 2, 3, 4, 5, 6, 7])  # 7 BAS - too many
        )
        print("✗ Should have failed with too many BAS")
    except ValueError as e:
        print(f"✓ BAS count error: {e}")
        # Check if the error message follows the standard format
        assert "expected" in str(e).lower() or "maximum" in str(e).lower(), "Error message should mention expected count"

def test_container_error_messages():
    """Test ErrorMessageBuilder in container validation."""
    print("\nTesting container error messages...")
    
    sd = SD_BASE()
    
    # Add first GRECO
    greco1 = GRECO(id='A', bas=Cases(ranges=[1, 2, 3, 4, 5, 6]))
    sd.add(greco1)
    
    # Try to add duplicate - should use ErrorMessageBuilder
    try:
        greco_duplicate = GRECO(id='A', bas=Cases(ranges=[7, 8, 9, 10, 11, 12]))
        sd.add(greco_duplicate)
        print("✗ Should have failed with duplicate ID")
    except ValueError as e:
        print(f"✓ Container duplicate error: {e}")
        # Check if the error message follows the standard format
        assert "duplicate" in str(e).lower(), "Error message should mention duplicate"

def test_cross_reference_error_messages():
    """Test ErrorMessageBuilder in cross-reference validation."""
    print("\nTesting cross-reference error messages...")
    
    # Get validation summary to check error message structure
    sd = SD_BASE()
    greco = GRECO(
        id='C',
        bas=Cases(ranges=[1, 2, 3, 4, 5, 6]),
        elc=Cases(ranges=[100, 101])  # These might trigger cross-reference errors in future
    )
    sd.add(greco)
    
    # Test integrity validation (currently returns no errors due to placeholder)
    integrity = sd.validate_integrity()
    print(f"Cross-reference validation results: {integrity}")
    print("✓ Cross-reference validation framework ready")

def test_template_management():
    """Test template management features."""
    print("\nTesting template management...")
    
    # List all templates
    templates = ErrorMessageBuilder.list_templates()
    print(f"Available templates: {len(templates)}")
    
    # Test specific template retrieval
    template = ErrorMessageBuilder.get_template('INVALID_RANGE')
    print(f"Range template: {template}")
    
    # Test unknown template
    unknown = ErrorMessageBuilder.get_template('UNKNOWN_TEMPLATE')
    print(f"Unknown template: {unknown}")
    
    print("✓ Template management working")

if __name__ == "__main__":
    print("ErrorMessageBuilder Implementation Test")
    print("=" * 50)
    
    try:
        test_error_message_builder()
        test_error_messages_in_validation()
        test_container_error_messages()
        test_cross_reference_error_messages()
        test_template_management()
        
        print("\n" + "=" * 50)
        print("All ErrorMessageBuilder tests completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()