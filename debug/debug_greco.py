from src.pysd.statements import DECAS, CaseBuilder
from src.pysd.validation.rules.decas_rules import collect_greco_references_from_decas

# Create the same DECAS statement that should fail
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,102).with_greco('B'))

print("DECAS statement:", decas_statement)
print("DECAS bas field:", decas_statement.bas)
print("DECAS bas type:", type(decas_statement.bas))

# Check if bas has greco attribute
if hasattr(decas_statement.bas, 'greco'):
    print("DECAS bas.greco:", decas_statement.bas.greco)
else:
    print("DECAS bas does not have greco attribute")

# Check attributes of bas
print("DECAS bas attributes:", [attr for attr in dir(decas_statement.bas) if not attr.startswith('_')])

# Test the collection function
greco_refs = collect_greco_references_from_decas(decas_statement)
print("Collected GRECO references:", greco_refs)