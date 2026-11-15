"""Upload unique frozen inputs and run the no-update native2048-env admission."""
from pathlib import Path
import sys,json,hashlib,shlex,time,traceback
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
E=T/'evidence';c=connect()
def put(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
try:
 sf=c.open_sftp()
 def mkdir(x):
  try:sf.stat(x)
  except FileNotFoundError:mkdir(x.rsplit('/',1)[0]);sf.mkdir(x)
 try:sf.stat(REMOTE);raise RuntimeError('New root already exists; inspect and resume explicitly')
 except FileNotFoundError:pass
 mkdir(REMOTE)
 files=[T/x for x in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt','teacher_movement_balanced_demos.pt','high_stance_comprehensive_anchors.pt','rearward_reference_dataset.pt']]+[x for x in (T/'support').rglob('*')if x.is_file()and'__pycache__'not in x.parts and x.suffix!='.pyc']
 index={}
 for x in files:
  rel=x.relative_to(T).as_posix();dst=REMOTE+'/'+rel;mkdir(dst.rsplit('/',1)[0]);sf.put(str(x),dst);index[rel]=hashlib.sha256(x.read_bytes()).hexdigest()
 sf.put(str(T/'weights/parent_comprehensive.pt'),P['parent']);index['parent_comprehensive.pt']=P['parent_sha256']
 code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d="+repr(index)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());package=Path("+repr(P['package'])+");assets="+repr(P['asset_identity']['actual_training_assets'])+";assert all(hashlib.sha256((package/'assets'/k).read_bytes()).hexdigest()==v['sha256']for k,v in assets.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256=d['parent_comprehensive.pt'],mod4v3_asset_hashes_verified=True)))"
 verification=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'UPLOADED_INPUTS.json',dict(verification=verification,files=index))
 receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' probe_scut_pitch_brake_2h --kind probe --num-envs2048'.replace('--num-envs2048','--num-envs 2048')));put(E/'NATIVE_PROBE_LAUNCH.json',receipt);print('NATIVE_PROBE_LAUNCHED',receipt['pid'],flush=True)
 job=REMOTE+'/probe_scut_pitch_brake_2h';lastset=set()
 while True:
  try:names=set(sf.listdir(job))
  except FileNotFoundError:names=set()
  for name in names-lastset:
   if name.endswith('.json'):sf.get(job+'/'+name,str(E/('native_probe_'+name)))
  lastset=names
  if 'SAFE_CLOSED.json'in names:break
  time.sleep(5)
 for name in names:
  if name.endswith('.json'):sf.get(job+'/'+name,str(E/('native_probe_'+name)))
 sf.get(REMOTE+'/probe_scut_pitch_brake_2h.log',str(E/'NATIVE_PROBE.log'))
 if 'ERROR.json'in names:raise RuntimeError('Native probe failed; preserve original ERROR and log; no optimizer launched')
 result=json.loads((E/'native_probe_ROUGH_PROBE.json').read_text());assert result['passed']and result['no_optimizer_updates']
 print('NATIVE_PROBE_PASSED',json.dumps(result),flush=True)
finally:c.close()
