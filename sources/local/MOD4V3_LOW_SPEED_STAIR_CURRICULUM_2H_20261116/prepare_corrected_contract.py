"""Freeze and verify isolated inputs; native admission consumes no PPO optimizer steps."""
from pathlib import Path
import sys,json,hashlib,shlex,time,traceback
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
E=T/'evidence'
def put(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=connect()
try:
 sf=c.open_sftp()
 def mkdir(x):
  try:sf.stat(x)
  except FileNotFoundError:mkdir(x.rsplit('/',1)[0]);sf.mkdir(x)
 try:sf.stat(REMOTE);raise RuntimeError('Unique candidate root already exists; inspect existing attempt')
 except FileNotFoundError:pass
 mkdir(REMOTE)
 files=[T/x for x in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt']]+[x for x in (T/'support').rglob('*')if x.is_file()and'__pycache__'not in x.parts and x.suffix!='.pyc']
 index={}
 for x in files:
  rel=x.relative_to(T).as_posix();dst=REMOTE+'/'+rel;mkdir(dst.rsplit('/',1)[0]);sf.put(str(x),dst);index[rel]=hashlib.sha256(x.read_bytes()).hexdigest()
 sf.put(str(T/'weights/parent_comprehensive.pt'),P['parent']);index['parent_comprehensive.pt']=P['parent_sha256']
 code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d="+repr(index)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());package=Path("+repr(P['package'])+");assets="+repr(P['asset_identity']['actual_training_assets'])+";assert all(hashlib.sha256((package/'assets'/k).read_bytes()).hexdigest()==v['sha256']for k,v in assets.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256=d['parent_comprehensive.pt'],mod4v3_asset_hashes_verified=True)))"
 verification=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'UPLOADED_INPUTS_R6.json',dict(verification=verification,files=index))
 receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+P['probe_job']+' --kind probe --num-envs 4'));put(E/'NATIVE_PROBE_R6_LAUNCH.json',receipt);print('NATIVE_PROBE_LAUNCHED',receipt['pid'],flush=True)
 job=REMOTE+'/'+P['probe_job'];lastset=set();deadline=time.time()+1800
 while True:
  try:names=set(sf.listdir(job))
  except FileNotFoundError:names=set()
  for name in names-lastset:
   if name.endswith('.json'):sf.get(job+'/'+name,str(E/('native_probe_r6_'+name)))
  lastset=names
  if 'SAFE_CLOSED.json'in names:break
  if time.time()>deadline:raise RuntimeError('Probe exceeded1800seconds; inspect its existing PID without automatic restart')
  time.sleep(5)
 for name in names:
  if name.endswith('.json'):sf.get(job+'/'+name,str(E/('native_probe_r6_'+name)))
 sf.get(REMOTE+'/'+P['probe_job']+'.log',str(E/'NATIVE_PROBE_R6.log'))
 if 'ERROR.json'in names:raise RuntimeError('Native probe failed; original error retained; no PPO launched')
 result=json.loads((E/'native_probe_r6_ROUGH_PROBE.json').read_text());assert result['passed']and result['no_optimizer_updates']
 print('NATIVE_PROBE_PASSED',json.dumps(result),flush=True)
except Exception:
 put(E/'PREPARE_R6_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_PPO_launched=True));raise
finally:c.close()
