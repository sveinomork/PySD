from src.pysd.statements import DECAS, CaseBuilder
from src.pysd.validation.rules.decas_rules import collect_load_case_references_from_decas

# Create the problematic DECAS statement
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

print("DECAS statement:", decas_statement)
print("DECAS bas field:", decas_statement.bas)
print("DECAS bas type:", type(decas_statement.bas))

# Check if bas has ranges attribute
if hasattr(decas_statement.bas, 'ranges'):
    print("DECAS bas.ranges:", decas_statement.bas.ranges)
else:
    print("DECAS bas does not have ranges attribute")

# Check attributes of bas
print("DECAS bas attributes:", [attr for attr in dir(decas_statement.bas) if not attr.startswith('_')])

try:
    # Test the collection function
    load_cases = collect_load_case_references_from_decas(decas_statement)
    print("Collected load cases:", load_cases)
except Exception as e:
    print("Error in collection:", e)
    import traceback
    traceback.print_exc()