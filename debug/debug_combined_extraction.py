from src.pysd.statements import DECAS, CaseBuilder
from src.pysd.validation.rules.decas_rules import collect_load_case_references_from_decas, collect_greco_references_from_decas

# Create the exact DECAS statement from main.py
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,102).with_greco('A'))

print("DECAS statement:", decas_statement)
print("BAS field:", decas_statement.bas)
print("BAS type:", type(decas_statement.bas))

print("\nTesting load case collection:")
try:
    load_cases = collect_load_case_references_from_decas(decas_statement)
    print("✓ Load cases:", load_cases)
except Exception as e:
    print("✗ Load case error:", e)
    import traceback
    traceback.print_exc()

print("\nTesting GRECO collection:")
try:
    greco_refs = collect_greco_references_from_decas(decas_statement)
    print("✓ GRECO refs:", greco_refs)
except Exception as e:
    print("✗ GRECO error:", e)
    import traceback
    traceback.print_exc()

print("\nTesting both together (like in validation):")
try:
    load_cases = collect_load_case_references_from_decas(decas_statement)
    greco_refs = collect_greco_references_from_decas(decas_statement)
    print("✓ Both successful")
    print("  Load cases:", load_cases)
    print("  GRECO refs:", greco_refs)
except Exception as e:
    print("✗ Combined error:", e)
    import traceback
    traceback.print_exc()