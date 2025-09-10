from src.pysd.statements import (
    GRECO, BASCO, LoadCase, DECAS, CaseBuilder, Cases
)
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

# Configure global validation mode for the entire script
set_validation_mode(ValidationMode.STRICT)

# Create a simple model to test DECAS validation
sd_model = SD_BASE()

# Add BASCO statements first (required for GRECO)
basco_statements = [
    BASCO(
        id=i, 
        load_cases=[LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.0)]
    )
    for i in range(211, 217)
]
for basco in basco_statements:
    sd_model.add(basco)

# Add a GRECO statement with ID 'A' (not 'B')
greco_support = GRECO(
    id='A',
    bas=Cases(ranges=[(211, 216)])
)
sd_model.add(greco_support)

# Add a DECAS statement that references non-existent GRECO 'B'
print("Adding DECAS with GRECO 'B' reference...")
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,102).with_greco('B'))
print(f"DECAS statement: {decas_statement}")
print(f"DECAS bas field: {decas_statement.bas}")
print(f"DECAS bas greco: {decas_statement.bas.greco if hasattr(decas_statement.bas, 'greco') else 'No greco attr'}")

try:
    sd_model.add(decas_statement)
    print("✓ DECAS added successfully (validation did not catch the issue)")
except Exception as e:
    print(f"✗ DECAS validation failed: {e}")

# Try to validate the model
print("\nValidating model...")
try:
    validation_result = sd_model.validate_model()
    print(f"Validation result: {validation_result}")
    
    if hasattr(validation_result, 'issues'):
        print(f"Number of issues: {len(validation_result.issues)}")
        for issue in validation_result.issues:
            print(f"  - {issue.severity}: {issue.code} - {issue.message}")
    elif hasattr(validation_result, 'errors'):
        print(f"Number of errors: {len(validation_result.errors)}")
        for error in validation_result.errors:
            print(f"  - ERROR: {error}")
    else:
        print("No validation result issues found")
    
except Exception as e:
    print(f"Validation error: {e}")

print(f"\nModel items: {len(sd_model.all_items)} total")
for item in sd_model.all_items:
    print(f"  - {item.__class__.__name__}: {item}")