from src.pysd.statements import DECAS
from src.pysd.validation.rules.decas_rules import collect_load_case_references_from_decas

# Test the problematic case
decas_statement = DECAS(ls='ULS', bas="101")

print("DECAS statement:", decas_statement)
print("BAS field:", decas_statement.bas)
print("BAS type:", type(decas_statement.bas))

try:
    load_cases = collect_load_case_references_from_decas(decas_statement)
    print("Collected load cases:", load_cases)
except Exception as e:
    print("Error in collection:", e)
    import traceback
    traceback.print_exc()