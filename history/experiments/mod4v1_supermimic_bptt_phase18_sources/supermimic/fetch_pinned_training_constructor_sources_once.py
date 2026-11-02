"""Fetchonlynew-goalconstructorPython/metadatafromalreadyactiveprojectroots. NoPT/raw/SDK/GO/Cwrites."""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;T=R.parent/'mod4v1_experts_fulldr_rm70_20261101';sys.path.insert(0,str(T));from project_connector import connect72
D=T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';out=R/'discovery';index=R/'reports/PINNED_CONSTRUCTOR_SOURCE_FETCH_V1.json';assert not index.exists();entries=[];c=connect72();s=c.open_sftp()
try:
 for pair,roles in((1,['E0','CURB_PROTECTED878']),(2,['E2','CURB_INDEPENDENT113']),(3,['E3','SLOPE135']),(4,['W35','SLOPE_INDEPENDENT50'])):
  f=D/('PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json'if pair==1 else'PAIR'+str(pair)+'_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json');closed=json.loads(Path(json.loads(f.read_bytes())['path']).read_bytes());base=closed['root']
  for role in roles:
   root=base+'/roles/'+role;paths=['original_run_manifest.json','E1_CANONICAL_SOURCE_METADATA.json','lib/mod4v1_fresh_dr_guard.py']
   if role in('E0','E2','E3','W35'):paths+=['runtime/isaac/mod4/train_mod4v1_'+role.lower()+'.py','runtime/isaac/mod4/mod4_task.py','runtime/isaac/mod4/observations.py','runtime/isaac/mod4/rescue_training.py']
   for rel in paths:
    try:
     with s.open(root+'/'+rel,'rb')as z:raw=z.read(1000000)
    except FileNotFoundError:continue
    assert len(raw)<1000000;p=out/role/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);entries.append(dict(role=role,remote=root+'/'+rel,local=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
finally:s.close();c.close()
index.parent.mkdir(parents=True,exist_ok=True);index.write_text(json.dumps(dict(kind='SOURCE_ONLY_PINNED_ORIGINAL_NATIVE_CONSTRUCTORS_NO_MODELS',files=entries,PT_raw_SDK_C_GO_operations=0),indent=2),encoding='utf-8');print(index);print(json.dumps(entries,indent=2))
