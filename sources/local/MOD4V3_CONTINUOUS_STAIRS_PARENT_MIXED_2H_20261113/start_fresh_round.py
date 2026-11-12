"""Upload unchanged mixed curriculum, await old safe save, start authorized fresh7200s."""
from pathlib import Path
import json,sys,shlex,time,hashlib,os,traceback
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));E=T/'evidence';REMOTE=P['root']
def put(p,d):
 p=Path(p);tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def read(sf,p):
 try:
  with sf.open(p) as f:return json.loads(f.read())
 except FileNotFoundError:return None
def mkdir(sf,p):
 try:sf.stat(p)
 except FileNotFoundError:mkdir(sf,p.rsplit('/',1)[0]);sf.mkdir(p)
def main():
 c=connect()
 try:
  sf=c.open_sftp();mkdir(sf,REMOTE);files=[(p,'support/'+p.relative_to(T/'support').as_posix()) for p in (T/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
  files += [(T/'PLAN.json','PLAN.json'),(T/'launch.py','launch.py')];manifest={}
  for p,rel in files:
   target=REMOTE+'/'+rel;mkdir(sf,target.rsplit('/',1)[0]);sf.put(str(p),target);manifest[rel]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
  assets={P['parent']:P['parent_sha256']}
  for name,data in P['asset_identity']['actual_training_assets'].items():assets[P['package']+'/assets/'+name]=data['sha256']
  code='import pathlib,hashlib,json;root=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';assets='+repr(assets)+';assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v["sha256"] for k,v in m.items());assert all(hashlib.sha256(pathlib.Path(k).read_bytes()).hexdigest()==v for k,v in assets.items());print(json.dumps({"files_verified":len(m),"parent_and_native_assets_verified":True}))'
  out=json.loads(execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code)));put(E/'UPLOAD_MANIFEST.json',manifest);put(E/'UPLOAD_VERIFIED.json',out)
 finally:c.close()
 print('SOURCE_PARENT_ASSETS_VERIFIED',flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,P['previous_remote_job']+'/SAFE_CLOSED.json');final=read(sf,P['previous_remote_job']+'/FINAL.json')
   if closed:
    if not final:raise RuntimeError('Previous job closed without final checkpoint; inspect original raw error')
    put(E/'PRIOR_FINAL.json',final);put(E/'PRIOR_SAFE_CLOSED.json',closed);break
  finally:c.close()
  time.sleep(2)
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:break
  time.sleep(2)
 c=connect()
 try:out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' train120m_parent_mixed_r1 --kind train --num-envs 2048');put(E/'TRAIN_LAUNCH.json',json.loads(out))
 finally:c.close()
 print('FRESH7200S_LAUNCHED_FROM_ITER24692',flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
