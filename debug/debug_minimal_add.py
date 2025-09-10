from src.pysd.statements import DECAS, BASCO, LoadCase, CaseBuilder
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

# Configure validation mode
set_validation_mode(ValidationMode.STRICT)

print("Creating SD_BASE model...")
sd_model = SD_BASE()

print("Adding BASCO...")
try:
    basco = BASCO(id=101, load_cases=[LoadCase(lc_type='ELC', lc_numb=101, lc_fact=1.0)])
    sd_model.add(basco)
    print("✓ BASCO added successfully")
except Exception as e:
    print(f"✗ BASCO failed: {e}")

print("Adding DECAS...")
try:
    decas_statement = DECAS(ls='ULS', bas=CaseBuilder.create().add_range(101,112).with_greco('A'))
    sd_model.add(decas_statement)
    print("✓ DECAS added successfully")
except Exception as e:
    print(f"✗ DECAS failed: {e}")
    import traceback
    traceback.print_exc()

print("Done.")