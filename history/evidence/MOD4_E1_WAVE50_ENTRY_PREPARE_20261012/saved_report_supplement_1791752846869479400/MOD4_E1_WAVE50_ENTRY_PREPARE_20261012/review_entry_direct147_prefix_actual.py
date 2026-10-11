"""Read only the new complete candidate and direct147 original physical prefixes."""
from pathlib import Path
D = Path(__file__).resolve().parent
PREV = D.parent / 'MOD4_E1_WAVE50_SECOND_BOUNDED_20261012'
s = (PREV / 'review_second50_direct146_prefix_actual.py').read_text()
s = s.replace('from second50_io import *', 'from entry_io import *')
s = s.replace('from review_second50_candidate_actual import ', "sys.path.insert(0, str(PREV))\nfrom review_second50_candidate_actual import ")
s = s.replace('SECOND50_CANDIDATE_ACTUAL_REVIEW_', 'ENTRY_CANDIDATE_ACTUAL_REVIEW_')
s = s.replace("PRIOR/'reports/WAVE50_146_COMPLETE_SCOPE_DECISION.json'", "PREV/'reports/WAVE50_147_COMPLETE_OBSERVED_SCOPE_DECISION.json'")
s = s.replace("source['own']['checkpoint']['sha256']==SOURCE_SHA", "source['own']['checkpoint']['sha256']=='a67b955f680dd101cc4480f19c2e95dd86c34423148302fad1d8e925e206d4df'")
s = s.replace('SECOND50_DIRECT146', 'ENTRY_DIRECT147')
s = s.replace('DIRECT146', 'DIRECT147').replace('direct146', 'direct147').replace('source146', 'source147')
exec(compile(s, '<entry-candidate-direct147-readonly>', 'exec'), {'__file__': str(D / 'review_entry_direct147_prefix_actual.py'), '__name__': '__main__'})
