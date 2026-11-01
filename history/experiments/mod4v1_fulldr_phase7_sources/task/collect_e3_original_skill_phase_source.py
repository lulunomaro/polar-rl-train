"""Smallsource-only original E3 recovery acceptance/phase contract, owncompletedcase. No model/SDK."""
from pathlib import Path
import json,hashlib
from project_connector import connect72
R=Path(__file__).resolve().parent;root=json.loads((R/'reports/E3_1cd_no_update_final_20261102_031620/COLLECTION.json').read_bytes())['remote_root'];D=R/'skill_contracts/E3_ORIGINAL_PHASE_SOURCE_V1';assert not D.exists();D.mkdir(parents=True);c=connect72();s=c.open_sftp();rows=[]
try:
 for rel in('job0/runtime/isaac/mod4/e3_public_recovery_phase_v1.py','job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py','runtime/isaac/mod4/e3_public_recovery_phase_v1.py','runtime/isaac/mod4/e3_recovery_runtime_v1.py','e3/runtime/isaac/mod4/e3_public_recovery_phase_v1.py'):
  try:
   st=s.stat(root+'/'+rel);assert st.st_size<2000000
   with s.open(root+'/'+rel,'rb')as f:raw=f.read()
  except FileNotFoundError:rows.append({'path':root+'/'+rel,'present':False});continue
  p=D/Path(rel).name
  if p.exists():assert p.read_bytes()==raw
  else:p.write_bytes(raw)
  rows.append({'path':root+'/'+rel,'present':True,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'local_copy':str(p)})
finally:s.close();c.close()
v={'kind':'SOURCE_ONLY_ORIGINAL_E3_PHASE_SKILL_DEFINITION_NOT_NEW_GRADUATION_GATE','rows':rows,'PT_SDK_budget_or_raw_access':False,'source_executed':False};(D/'READ_RECEIPT.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
