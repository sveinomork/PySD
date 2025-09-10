from src.pysd.statements import (
    GRECO, BASCO, LoadCase, DECAS, CaseBuilder, Cases, LOADC
)
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

# Configure validation mode exactly like main.py
set_validation_mode(ValidationMode.STRICT)

print("Creating test model with same setup as main.py...")
sd_model = SD_BASE()

# Add LOADC exactly like main.py
loadc = [
    LOADC(run_number=1, alc=(1,7), olc=(101,107)),
    LOADC(table=True),
    LOADC(pri=True)
]
sd_model.add(loadc)

# add basco's for greco (IDs 211-216)
for i in range(6):
    load_cases = [LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)]
    basco = BASCO(id=211+i, load_cases=load_cases)
    sd_model.add(basco)

# Add GRECO 'A'
greco_support = GRECO(id='A', bas=Cases(ranges=[(211, 216)]))
sd_model.add(greco_support)

# Add BASCO 101 and 102 (but NOT 103)
load_cases = [LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.5) for i in range(101, 107)]
basco = BASCO(id=101, load_cases=load_cases)
sd_model.add(basco)

load_cases2 = [LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.8) for i in range(101, 107)]
basco = BASCO(id=102, load_cases=load_cases2)
sd_model.add(basco)

print("✓ Setup complete")
print("Defined BASCO IDs:", [101, 102] + list(range(211, 217)))
print("Defined LOADC ranges: 101-107")

# Test DECAS with range 101-103 (should fail for 103)
print("\nTesting DECAS with range 101-103...")
try:
    decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,103).with_greco('A'))
    sd_model.add(decas_statement)
    print("✗ DECAS passed validation (SHOULD HAVE FAILED - no BASCO ID=103)")
except Exception as e:
    print("✓ DECAS correctly failed validation")
    print(f"   Reason: {e}")

print("Done.")