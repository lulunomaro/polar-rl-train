"""Existing authorized SSH transport, isolated new Linux job, no old run mutation."""
from pathlib import Path
import json,sys,hashlib,shlex,time,argparse
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R.parent/'tmp'))
from step7_remote_access import connect
P=json.loads((T/'PLAN.json').read_text());REMOTE=P['root']
def execute(c,cmd,timeout=50):
 i,o,e=c.exec_command(cmd,timeout=timeout);out=o.read().decode('utf8',errors='replace');err=e.read().decode('utf8',errors='replace');status=o.channel.recv_exit_status()
 if status:raise RuntimeError('Remote exit '+str(status)+'\n'+out[-4000:]+'\n'+err[-4000:])
 return out

def upload():
 c=connect()
 try:
  sf=c.open_sftp();created=set()
  def mkdir(path):
   if path in created:return
   try:sf.stat(path)
   except FileNotFoundError:
    parent=path.rsplit('/',1)[0]
    if parent:mkdir(parent)
    sf.mkdir(path)
   created.add(path)
  mkdir(REMOTE)
  pairs=[]
  for part in ['support','dependencies']:
   pairs += [(p,part+'/'+p.relative_to(T/part).as_posix()) for p in (T/part).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
  pairs += [(T/'PLAN.json','PLAN.json'),(T/'launch.py','launch.py')]
  D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant/MOD4v3_HW300N60_R3'
  pairs += [(p,'native_package/'+p.name) for p in D.iterdir() if p.is_file()]
  pairs += [(p,'native_package/assets/'+p.name) for p in (D/'assets').iterdir() if p.is_file()]
  pairs += [(p,'native_package/legacy/'+p.relative_to(D/'legacy').as_posix()) for p in (D/'legacy').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
  pairs += [(D/'mjcf/scene.xml','native_package/mjcf/scene.xml'),(R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/weights/selected_flat_speed_candidate.pt','parent.pt')]
  manifest={}
  for src,rel in pairs:
   dst=REMOTE+'/'+rel;mkdir(dst.rsplit('/',1)[0]);sf.put(str(src),dst);manifest[rel]=dict(source=src.relative_to(R).as_posix(),bytes=src.stat().st_size,sha256=hashlib.sha256(src.read_bytes()).hexdigest())
  (T/'evidence/UPLOAD_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  code='import pathlib,json,hashlib; base=pathlib.Path('+repr(REMOTE)+'); expected='+repr(manifest)+'; actual={k:hashlib.sha256((base/k).read_bytes()).hexdigest() for k in expected}; assert all(actual[k]==expected[k]["sha256"] for k in expected); print(json.dumps(dict(files=len(actual),all_hashes_verified=True)))'
  out=execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code));(T/'evidence/UPLOAD_VERIFIED.json').write_text(out,encoding='utf8');print(out,flush=True)
 finally:c.close()
def launch(name,kind):
 c=connect()
 try:
  out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' '+shlex.quote(name)+' --kind '+kind+' --num-envs 2048');(T/'evidence'/(name+'_LAUNCH.json')).write_text(out,encoding='utf8');print(out,flush=True)
 finally:c.close()
def status(name):
 c=connect()
 try:
  code='import pathlib,json; b=pathlib.Path('+repr(REMOTE+'/'+name)+'); out={"job_exists":b.exists()};\nfor n in ["STARTUP.json","PROBE_COMPLETE.json","ROUGH_PROBE.json","FIRST_UPDATE.json","LATEST_PROGRESS.json","FINAL.json","ERROR.json","SAFE_CLOSED.json"]:\n p=b/n\n if p.exists():out[n]=json.loads(p.read_text())\nprint(json.dumps(out))'
  out=execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code));print(out,flush=True)
  sf=c.open_sftp()
  try:
   with sf.open(REMOTE+'/'+name+'.log') as f:log=f.read().decode('utf8',errors='replace')
   (T/'evidence'/(name+'.log')).write_text(log,encoding='utf8');print('LOG_TAIL\n'+log[-3500:],flush=True)
  except FileNotFoundError:pass
 finally:c.close()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['upload','probe','train','status']);a.add_argument('--name');v=a.parse_args()
 if v.action=='upload':upload()
 elif v.action=='probe':launch(v.name or 'probe2048_r1','probe')
 elif v.action=='train':launch(v.name or 'train120m_r1','train')
 else:status(v.name or 'probe2048_r1')
