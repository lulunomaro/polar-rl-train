"""Preserve new source/errors; execute only single-case offline diagnostic."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parent
n=1
while(R/'attempts'/f'{n:03d}').exists():n+=1
out=R/'attempts'/f'{n:03d}';out.mkdir(parents=True)
p=R/'analyze.py';raw=p.read_bytes();(out/'analyze_source.py').write_bytes(raw);(out/'SOURCE_SHA.json').write_text(json.dumps({'path':str(p),'SHA':hashlib.sha256(raw).hexdigest(),'newphysics':0})+'\n',encoding='utf-8')
protected=[R.parent/'run_manual_first_bar_v1.py',R.parent/'MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py',R.parent/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for p in protected};sys.path.insert(0,str(R))
try:
 import analyze;analyze.main();assert all(sha(Path(p))==h for p,h in before.items());(out/'VALIDATION.json').write_text(json.dumps({'protected_files_unchanged':before,'no_new_physics_Git_agents_H5':True,'raw_producerSHA_reference_no_rehash':True})+'\n',encoding='utf-8')
except BaseException:
 (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
