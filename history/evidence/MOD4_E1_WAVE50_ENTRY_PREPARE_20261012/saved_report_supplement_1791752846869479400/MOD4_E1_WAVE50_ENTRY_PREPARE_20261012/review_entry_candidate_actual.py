"""Reuse whole unchanged50/legacy protocol; exact own410 CPU binding is required."""
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent
s=(W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012/review_second50_candidate_actual.py').read_text()
s=s.replace('from second50_io import *',"from entry_io import *\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'")
s=s.replace('SECOND50_CANDIDATE_COLLECTED_','ENTRY_CANDIDATE_COLLECTED_').replace('SECOND50_OWN_FORMAL_CPU_ACTUAL_','ENTRY_OWN_FORMAL_CPU_ACTUAL_').replace("cpu['actual_source_count']==386","cpu['actual_source_count']==410").replace('SECOND50_CANDIDATE_ACTUAL_REVIEW_','ENTRY_CANDIDATE_ACTUAL_REVIEW_')
exec(compile(s,'<entry410-full-raw-unchanged-protocol-review>','exec'),{'__file__':str(D/'review_entry_candidate_actual.py'),'__name__':'__main__'})
