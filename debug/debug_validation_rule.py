from src.pysd.statements import DECAS, BASCO, LoadCase, CaseBuilder, GRECO, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode
from src.pysd.validation.rules.decas_rules import validate_decas_model
from src.pysd.validation.core import ValidationContext

# Configure validation mode
set_validation_mode(ValidationMode.STRICT)

# Create a minimal model
sd_model = SD_BASE()

# Add a simple BASCO
basco = BASCO(id=101, load_cases=[LoadCase(lc_type='ELC', lc_numb=101, lc_fact=1.0)])
sd_model.add(basco)

# Add a GRECO 
greco = GRECO(id='A', bas=Cases(ranges=[(211, 216)]))

# Try to add more BASCO for GRECO without triggering error
for i in range(211, 217):
    basco_greco = BASCO(id=i, load_cases=[LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.0)])
    sd_model.add(basco_greco)

sd_model.add(greco)

# Create the DECAS statement that should trigger validation
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

print("Created DECAS:", decas_statement)
print("BAS field:", decas_statement.bas)
print("BAS type:", type(decas_statement.bas))

# Now test the model validation directly
context = ValidationContext(current_object=decas_statement, full_model=sd_model)

try:
    issues = validate_decas_model(decas_statement, context)
    print("Validation issues:", issues)
    for issue in issues:
        print(f"  - {issue.severity}: {issue.code} - {issue.message}")
except Exception as e:
    print("Error in validate_decas_model:", e)
    import traceback
    traceback.print_exc()