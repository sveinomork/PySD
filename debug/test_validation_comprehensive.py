from src.pysd.statements import DECAS, BASCO, LoadCase, CaseBuilder, GRECO, Cases
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

# Configure validation mode
set_validation_mode(ValidationMode.STRICT)

print("Creating SD_BASE model...")
sd_model = SD_BASE()

# Add the same BASCO statements as in main.py
print("Adding BASCO statements...")

# From main.py: only BASCO with ID 101 for load cases 101-106
load_cases = [LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.5) for i in range(101, 107)]
basco = BASCO(id=101, load_cases=load_cases)
sd_model.add(basco)

# From main.py: BASCO statements for GRECO (IDs 211-216)
for i in range(6):
    load_cases = [LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)]
    basco = BASCO(id=211+i, load_cases=load_cases)
    sd_model.add(basco)

# Add GRECO 'A'
greco_support = GRECO(id='A', bas=Cases(ranges=[(211, 216)]))
sd_model.add(greco_support)

print("✓ Setup complete. Testing DECAS validation...")

# Test 1: DECAS with range 101-112 (should fail for 107-112)
print("\nTest 1: DECAS with range 101-112")
try:
    decas1 = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))
    sd_model.add(decas1)
    print("✗ DECAS 101-112 passed validation (SHOULD HAVE FAILED)")
except Exception as e:
    print("✓ DECAS 101-112 correctly failed validation")
    print(f"   Reason: {e}")

# Test 2: DECAS with range 400-409 (should fail for all)
print("\nTest 2: DECAS with range 400-409")
try:
    decas2 = DECAS(ls='ULS', bas="400-409")
    sd_model.add(decas2)
    print("✗ DECAS 400-409 passed validation (SHOULD HAVE FAILED)")
except Exception as e:
    print("✓ DECAS 400-409 correctly failed validation")
    print(f"   Reason: {e}")

# Test 3: Valid DECAS with only defined load case
print("\nTest 3: DECAS with valid range 101-101")
try:
    decas3 = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,101).with_greco('A'))
    sd_model.add(decas3)
    print("✓ DECAS 101-101 correctly passed validation")
except Exception as e:
    print(f"✗ DECAS 101-101 failed validation (SHOULD HAVE PASSED): {e}")

print("\nValidation testing complete!")