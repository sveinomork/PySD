from src.pysd.statements import DECAS, CaseBuilder

# Create the DECAS statement
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

print("DECAS attributes:")
for attr in dir(decas_statement):
    if not attr.startswith('_'):
        value = getattr(decas_statement, attr)
        print(f"  {attr}: {value} (type: {type(value)})")

print("\nDirect getattr test:")
print("id attribute:", getattr(decas_statement, 'id', 'unknown'))

# Check if any attributes contain Cases objects
print("\nChecking for Cases objects in attributes:")
for attr in dir(decas_statement):
    if not attr.startswith('_') and not callable(getattr(decas_statement, attr)):
        value = getattr(decas_statement, attr)
        if hasattr(value, '__class__') and 'Cases' in str(type(value)):
            print(f"  {attr} contains Cases object: {value}")
            
            # Try to hash this attribute
            try:
                hash(value)
                print(f"    -> {attr} is hashable")
            except Exception as e:
                print(f"    -> {attr} is NOT hashable: {e}")