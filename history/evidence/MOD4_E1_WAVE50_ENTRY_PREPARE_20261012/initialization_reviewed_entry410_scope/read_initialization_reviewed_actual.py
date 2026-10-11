from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'read_entry_actual.py').read_text()
s=s.replace('from entry_io import *',"from entry_io import *\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'")
s=s.replace('supervise_wave50_entry_scope_once','supervise_wave50_entry_scope_once_v2').replace("'ENTRY_ACTUAL_'","'INITIALIZATION_REVIEWED_ACTUAL_'").replace('ACTUAL_READER_ERROR_','INITIALIZATION_ACTUAL_READER_ERROR_')
exec(compile(s,'<readonly410-actual-stage>','exec'),{'__file__':str(D/'read_entry_actual.py'),'__name__':'__main__'})
