from src.pysd.statements import DECAS, CaseBuilder

# Create the DECAS statement
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

print("DECAS statement:", decas_statement)
print("BAS field:", decas_statement.bas)
print("BAS field type:", type(decas_statement.bas))

# Manually trace through the collection logic
field_value = decas_statement.bas
load_cases = []

print("\nTracing collection logic:")
print("field_value:", field_value)
print("field_value type:", type(field_value))

# Check if it has ranges
if hasattr(field_value, 'ranges') and field_value.ranges:
    print("Found ranges:", field_value.ranges)
    for start, end in field_value.ranges:
        print(f"  Range: {start} to {end}")
        range_list = list(range(start, end + 1))
        print(f"  Range list: {range_list}")
        load_cases.extend(range_list)
    print("Load cases after ranges:", load_cases)

# Check if it's a string
elif isinstance(field_value, str):
    print("It's a string:", field_value)
    # This shouldn't happen for Cases objects
else:
    print("Unknown type")

print("Final load_cases before set:", load_cases)
print("Types in load_cases:", [type(x) for x in load_cases])

try:
    result = list(set(load_cases))
    print("Result after set conversion:", result)
except Exception as e:
    print("Error in set conversion:", e)
    print("Items that can't be hashed:")
    for item in load_cases:
        try:
            hash(item)
        except Exception as ex:
            print(f"  {item} (type: {type(item)}) - {ex}")