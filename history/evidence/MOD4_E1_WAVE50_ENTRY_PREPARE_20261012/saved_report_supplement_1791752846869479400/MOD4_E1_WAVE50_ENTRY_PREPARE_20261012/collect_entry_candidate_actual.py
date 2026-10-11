"""Reuse actual twohost collector; only this entry candidate and ownfinal label change."""
from pathlib import Path
D=Path(__file__).resolve().parent;W=D.parent
s=(W/'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012/collect_second50_candidate_actual.py').read_text()
s=s.replace('from second50_io import *',"from entry_io import *\nROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012'")
s=s.replace('e1_WAVE50_second_bounded_observation_PASSED','e1_WAVE50_entry_observation_PASSED').replace('SECOND50_CANDIDATE_COLLECTED_','ENTRY_CANDIDATE_COLLECTED_')
exec(compile(s,'<entry410-actual-only-twohost-collection>','exec'),{'__file__':str(D/'collect_entry_candidate_actual.py'),'__name__':'__main__'})
