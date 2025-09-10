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

print("✓ Setup complete. Testing valid DECAS...")

# Test with a valid single BASCO ID
print("\nTest: DECAS with valid BASCO ID 101")
try:
    decas_valid = DECAS(ls='ULS', bas="101")
    sd_model.add(decas_valid)
    print("✓ DECAS with valid load case 101 passed validation")
except Exception as e:
    print(f"✗ DECAS with valid load case failed: {e}")

print("\nValidation testing complete!")