from src.pysd.statements import DECAS, CaseBuilder

# Create the DECAS statement
decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))

print("Testing getattr calls like in SD_BASE:")
print("getattr(statement, 'id', None):", getattr(decas_statement, 'id', None))
print("getattr(statement, 'key', None):", getattr(decas_statement, 'key', None))

# Test the nested getattr like in the error handling
try:
    statement_id = getattr(decas_statement, 'id', getattr(decas_statement, 'key', 'unknown'))
    print("statement_id:", statement_id)
    print("statement_id type:", type(statement_id))
    
    # Test if we can format this into a string like in the error message
    location_string = f"DECAS.{statement_id}"
    print("location_string:", location_string)
    
except Exception as e:
    print("Error in getattr chain:", e)
    import traceback
    traceback.print_exc()