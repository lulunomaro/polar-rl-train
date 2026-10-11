"""Read only the complete own410 trace after the actual final closeout."""
from pathlib import Path
D = Path(__file__).resolve().parent
PREV = D.parent / 'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
s = (PREV / 'review_second50_complete_dynamic_family_trace_actual.py').read_text()
s = s.replace('from second50_io import *', 'from entry_io import *')
s = s.replace('SECOND50_OWN_FORMAL_CPU_ACTUAL_', 'ENTRY_OWN_FORMAL_CPU_ACTUAL_')
s = s.replace("own['actual_source_count']==386", "own['actual_source_count']==410")
s = s.replace("source_SHA=own['source_SHA'],controls=own['own']['health']['control_steps']", "source_SHA=SOURCE_SHA,controls=own['own_stage']['health']['control_steps']")
s = s.replace('SECOND50_FULL_TRAINING_TRACE_ACTUAL_', 'ENTRY_FULL_TRAINING_TRACE_ACTUAL_')
s = s.replace('WAVE50_FULL_TRACE_READER_ERROR_', 'ENTRY_FULL_TRACE_READER_ERROR_')
exec(compile(s, '<own410-fulltrace-readonly>', 'exec'), {'__file__': str(D / 'review_entry_complete_dynamic_family_trace_actual.py'), '__name__': '__main__'})
