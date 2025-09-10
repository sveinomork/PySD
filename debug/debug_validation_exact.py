from src.pysd.statements import DECAS, BASCO, LoadCase, CaseBuilder, GRECO, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode
from src.pysd.validation.core import ValidationContext
from src.pysd.validation.rule_system import execute_validation_rules

# Configure validation mode
set_validation_mode(ValidationMode.STRICT)

# Create a simple DECAS statement
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

# Create a mock model
sd_model = SD_BASE()

# Add a simple BASCO
basco = BASCO(id=101, load_cases=[LoadCase(lc_type='ELC', lc_numb=101, lc_fact=1.0)])
sd_model.add(basco)

print("Starting validation test...")

# Create context exactly like SD_BASE does
context = ValidationContext(
    current_object=decas_statement,
    full_model=sd_model
)

print("Created context successfully")

# Call execute_validation_rules exactly like SD_BASE does
try:
    validation_issues = execute_validation_rules(decas_statement, context, level='model')
    print("Validation completed successfully!")
    print(f"Number of issues: {len(validation_issues)}")
    for issue in validation_issues:
        print(f"  - {issue.severity}: {issue.code} - {issue.message}")
except Exception as e:
    print(f"Validation failed: {e}")
    import traceback
    traceback.print_exc()