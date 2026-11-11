"""Collect stable actual receipts, logs and replay arrays after this finite round."""
from pathlib import Path
import json,sys,hashlib,time
sys.path.insert(0,r'D:/claude2/fangzhen/tmp')
from step7_remote_access import connect
T=Path(__file__).resolve().parent;P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'));B=P['support'].rsplit('/support',1)[0];E=T/'evidence'
c=connect();s=c.open_sftp();records=[]
def fetch(remote,local):
 local.parent.mkdir(parents=True,exist_ok=True)
 s.get(remote,str(local));records.append(dict(remote_path=remote,local_path=local.relative_to(T).as_posix(),bytes=local.stat().st_size,sha256=hashlib.sha256(local.read_bytes()).hexdigest()))
job=B+'/'+P['training_round']['job']
with s.open(job+'/SAFE_CLOSED.json') as f:assert json.loads(f.read())['scene_closed']
for name in s.listdir(job):
 if name.endswith('.json'):fetch(job+'/'+name,E/'remote_training'/name)
for name in [P['training_round']['job']+'.log',P['training_round']['job']+'_LAUNCH.json']:
 try:s.stat(B+'/'+name)
 except FileNotFoundError:continue
 fetch(B+'/'+name,E/name)
for run in ['paired_landing_r2_b01','paired_landing_r2_b02','paired_landing_r2_b03','paired_flat_r2','paired_rough_level0_r2','paired_rough_level3_r2']:
 for name in sorted(x for x in s.listdir(B+'/'+run) if x.endswith(('.json','.npz'))):
  try:s.stat(B+'/'+run+'/'+name)
  except FileNotFoundError:continue
  fetch(B+'/'+run+'/'+name,E/'remote_evaluations'/run/name)
 for suffix in ['.log','_LAUNCH.json']:
  try:fetch(B+'/'+run+suffix,E/'remote_evaluations'/(run+suffix))
  except FileNotFoundError:pass
s.close();c.close()
(E/'REMOTE_COLLECTION.json').write_text(json.dumps(dict(epoch=time.time(),files=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(records),bytes=sum(x['bytes'] for x in records))))
