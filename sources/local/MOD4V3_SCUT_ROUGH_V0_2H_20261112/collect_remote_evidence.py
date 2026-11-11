"""Collect actual closed training/evaluation evidence and verify executed source hashes."""
from pathlib import Path
import json,sys,hashlib,time
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=Path(__file__).resolve().parent;P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'));B=P['support'].rsplit('/support',1)[0];E=T/'evidence'
c=connect();s=c.open_sftp();records=[]
def fetch(remote,local):
 local.parent.mkdir(parents=True,exist_ok=True);s.get(remote,str(local));records.append(dict(remote_path=remote,local_path=local.relative_to(T).as_posix(),bytes=local.stat().st_size,sha256=hashlib.sha256(local.read_bytes()).hexdigest()))
job=B+'/'+P['training_round']['job']
with s.open(job+'/SAFE_CLOSED.json','rb') as f:assert json.loads(f.read())['scene_closed']
for name in s.listdir(job):
 if name.endswith('.json'):fetch(job+'/'+name,E/'remote_training'/name)
for name in (P['training_round']['job']+'.log',P['training_round']['job']+'_LAUNCH.json'):fetch(B+'/'+name,E/name)
evals=json.loads((E/'EVALUATIONS_COMPLETE.json').read_text(encoding='utf-8'))
for run in evals['evaluations']:
 for name in s.listdir(B+'/'+run):
  if name.endswith(('.json','.npz')):fetch(B+'/'+run+'/'+name,E/'remote_evaluations'/run/name)
 for suffix in ('.log','_LAUNCH.json'):fetch(B+'/'+run+suffix,E/(run+suffix))
manifest=json.loads((E/'UPLOADED_MANIFEST.json').read_text(encoding='utf-8'));verified=[]
for rel,expected in manifest.items():
 with s.open(B+'/'+rel,'rb') as f:payload=f.read()
 digest=hashlib.sha256(payload).hexdigest();assert digest==expected,rel
 local=T/rel;assert hashlib.sha256(local.read_bytes()).hexdigest()==expected,rel
 verified.append(dict(path=rel,sha256=digest,remote_matches_launch=True,local_matches_launch=True))
for name in ('checkpoint_unified_replay.py','checkpoint_remaining_replay.py','FINAL_MODELS_TEMPLATE.json'):
 with s.open(B+'/'+name,'rb') as f:payload=f.read()
 assert payload==(T/name).read_bytes(),name
 verified.append(dict(path=name,sha256=hashlib.sha256(payload).hexdigest(),local_matches_executed=True))
s.close();c.close()
(E/'EXECUTED_SOURCE_VERIFIED.json').write_text(json.dumps(dict(files=verified),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(E/'REMOTE_COLLECTION.json').write_text(json.dumps(dict(epoch=time.time(),files=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(records),bytes=sum(x['bytes'] for x in records),verified_executed_sources=len(verified))))
