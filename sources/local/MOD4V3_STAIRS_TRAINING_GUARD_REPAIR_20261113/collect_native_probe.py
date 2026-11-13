from pathlib import Path
import sys,json,shlex,hashlib
T=Path(__file__).resolve().parent;P=T.parent/'MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113';sys.path.insert(0,str(P))
from remote_run import connect,execute
plan=json.loads((T/'PLAN.json').read_text(encoding='utf8'));root=plan['root'];dest=T/'evidence/native_probe_r1';dest.mkdir(exist_ok=True);c=connect()
try:
 sftp=c.open_sftp()
 for a in sftp.listdir_attr(root+'/native_probe_r1'):
  if a.filename.endswith('.json') or a.filename.endswith('.txt'):sftp.get(root+'/native_probe_r1/'+a.filename,str(dest/a.filename))
 sftp.get(root+'/native_probe_r1.log',str(dest/'native.log'));sftp.close()
 code='import hashlib,pathlib,json;p=pathlib.Path('+repr(plan['parent'])+');print(json.dumps({"checkpoint_sha256":hashlib.sha256(p.read_bytes()).hexdigest()}))'
 after=json.loads(execute(c,shlex.quote(plan['python'])+' -B -c '+shlex.quote(code)))
 assert after['checkpoint_sha256']==plan['parent_sha256']
 (dest/'WEIGHT_UNCHANGED.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf8')
finally:c.close()
p=dest/'ROUGH_PROBE.json'
if p.exists():
 d=json.loads(p.read_text(encoding='utf8'));print(json.dumps({k:d[k] for k in ['no_optimizer_update','num_envs','steps','simulation_seconds','max_closure_m','done_totals','stair_repair_probe','policy35_critic78_actions6'] if k in d},ensure_ascii=False))
 print('COMPLETE', (dest/'PROBE_COMPLETE.json').exists(),'CLOSED',(dest/'SAFE_CLOSED.json').exists())
