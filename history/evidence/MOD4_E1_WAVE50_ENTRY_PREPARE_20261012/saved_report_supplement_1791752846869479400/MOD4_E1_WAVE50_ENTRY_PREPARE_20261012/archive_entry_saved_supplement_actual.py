"""Archive only new saved evidence after the already recorded entry410 stage."""
from pathlib import Path
D = Path(__file__).resolve().parent
PREV = D.parent / 'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
s = (PREV / 'archive_final147_saved_supplement_actual.py').read_text()
s = s.replace('from second50_io import *', 'from entry_io import *')
s = s.replace('for folder in (D,PRIOR):', 'for folder in (D,):')
s = s.replace('Append Wave50 own386 complete final, trace and candidate147 actual review evidence', 'Append Wave50 entry410 actual preflight, formal and monitor evidence')
s = s.replace('SAVED_DELTA_GIT_ERROR_', 'ENTRY_SAVED_DELTA_GIT_ERROR_')
exec(compile(s, '<entry410-ordinary-evidence-supplement>', 'exec'), {'__file__': str(D / 'archive_entry_saved_supplement_actual.py'), '__name__': '__main__'})
