from src.pysd.statements import (
    GRECO, BASCO, LoadCase, DECAS, CaseBuilder, Cases
)
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

# Configure validation mode exactly like main.py
set_validation_mode(ValidationMode.STRICT)

print("Creating SD_BASE model...")
sd_model = SD_BASE()

print("Adding BASCO statements exactly like main.py...")

# add basco's for greco (IDs 211-216)
for i in range(6):
    load_cases = [LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1)]
    basco = BASCO(id=211+i, load_cases=load_cases)
    sd_model.add(basco)

# Add GRECO 'A'
greco_support = GRECO(id='A', bas=Cases(ranges=[(211, 216)]))
sd_model.add(greco_support)

# Create and add BASCO entries for 101-106
load_cases = [LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.5) for i in range(101, 107)]
basco = BASCO(id=101, load_cases=load_cases)
sd_model.add(basco)

# Add BASCO 102 like in main.py
load_cases2 = [LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.8) for i in range(101, 107)]
basco = BASCO(id=102, load_cases=load_cases2)
sd_model.add(basco)

print("✓ All BASCO and GRECO added successfully")

print("Adding DECAS exactly like main.py...")
try:
    decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,102).with_greco('A'))
    sd_model.add(decas_statement)
    print("✓ DECAS added successfully")
except Exception as e:
    print(f"✗ DECAS failed: {e}")
    import traceback
    traceback.print_exc()

print("Done.")