from src.pysd.statements.cases import Cases, normalize_cases

# Test different string inputs to see how they're normalized
test_inputs = ["101", "101-106", "400-409"]

for input_str in test_inputs:
    print(f"\nInput: '{input_str}'")
    try:
        cases = normalize_cases(input_str)
        print(f"  Result: {cases}")
        print(f"  Type: {type(cases)}")
        print(f"  Ranges: {cases.ranges}")
        print(f"  Ranges type: {type(cases.ranges)}")
        if cases.ranges:
            print(f"  First range: {cases.ranges[0]} (type: {type(cases.ranges[0])})")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()