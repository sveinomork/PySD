from pysd import SD_BASE, ValidationLevel
from pysd.statements import BASCO, LoadCase

model = SD_BASE()
basco = BASCO(id=1001, load_cases=[LoadCase(lc_type='OLC', lc_numb=101, lc_fact=1.0)])

try:
    model.add(basco, validation=True)
    print('No error raised!')
except Exception as e:
    print(f'Error type: {type(e).__name__}')
    print(f'Error message: {str(e)}')