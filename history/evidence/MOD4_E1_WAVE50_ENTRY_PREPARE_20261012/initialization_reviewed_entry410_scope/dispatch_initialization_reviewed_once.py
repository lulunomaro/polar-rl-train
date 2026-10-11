"""Dispatch only the new410 source; failed398 controller is never resumed."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'verify_reset_ast_and_dispatch_entry_once.py').read_text()
s=s.replace('from entry_io import *',"from entry_io import *\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'")
s=s.replace('ENTRY_TARGET_CPU_PASSED.json','INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json').replace('source_count']==398','source_count']==410') if False else s.replace('ENTRY_TARGET_CPU_PASSED.json','INITIALIZATION_REVIEWED_TARGET_CPU_PASSED.json')
s=s.replace("cpu['source_count']==398","cpu['source_count']==410").replace('source_count=398','source_count=410')
for name in ('DISPATCH_REQUESTED','RESET_AST_AND_STRICT_RESTORE_CPU_ACTUAL','DISPATCH_ACTUAL_RECEIPT','DISPATCH_ERROR'):s=s.replace(name,'INITIALIZATION_REVIEWED_'+name)
for name in ('supervise_wave50_entry_scope_once','wave50_entry_current_state','wave50_entry_full_checkpoint','wave50_entry_full_pose_reset','wave50_entry_runtime'):s=s.replace(name,name+'_v2')
exec(compile(s,'<independent410-unique-dispatch>','exec'),{'__file__':str(D/'verify_reset_ast_and_dispatch_entry_once.py'),'__name__':'__main__'})
