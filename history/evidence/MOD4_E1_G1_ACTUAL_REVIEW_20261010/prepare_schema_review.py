"""Preserve original failed reader; handle absent aggregate resets only if all episode rows are unchanged."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
p=D/'review_actual.py';s=p.read_text(encoding='utf8')
s=s.replace("assert sum(increments)==p['resets']", "assert sum(increments)==p['resets'] if 'resets' in p else sum(increments)==0")
s=s.replace("if not age:assert p['resets']>0", "if not age:assert p.get('resets',0)>0")
s=s.replace("trial_id='E1-G1-CPU-REVIEW-01'", "trial_id='E1-G1-CPU-REVIEW-02-OPTIONAL-RESET-FIELD'")
out=D/'review_actual_schema_checked.py';assert not out.exists();out.write_text(s,encoding='utf8')
(D/'reports/READER_PREPARATION_REJECTIONS.json').write_text(json.dumps(dict(epoch=time.time(),attempts=[dict(id='E1-G1-CPU-REVIEW-01',result='retained_failed',error='KeyError resets on spin schema; original traceback and reader retained'),dict(id='E1-G1-READER-PREPARE-01',result='rejected_before_write',error='PowerShell inline quoting OpenError; requested new file was not created'),dict(id='E1-G1-READER-EXEC-02',result='never_ran',error='requested new reader file did not yet exist')],production_and_GPU_and_canonical_unchanged=True,fix='absence of aggregate resets accepted only when all independent episode delta rows prove zero; original tolerances unchanged'),indent=2),encoding='utf8')
