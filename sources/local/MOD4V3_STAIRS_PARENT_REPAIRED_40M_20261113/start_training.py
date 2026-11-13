"""Upload this new authorized recipe, validate it once, then launch the bounded40m run."""
from pathlib import Path
import sys,json,time,hashlib,shlex,subprocess,os,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T))
from remote_run import connect,execute,P,REMOTE
from native_cache_lifecycle import cleanup_closed_cache
E=T/'evidence'
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(sf,p):
 try:
  with sf.open(p) as f:return json.loads(f.read())
 except FileNotFoundError:return None

def idle():
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:return
  time.sleep(3)

def main():
 c=connect();manifest={}
 try:
  sf=c.open_sftp();execute(c,'mkdir -p '+shlex.quote(REMOTE));created={REMOTE}
  files=[(p,'support/'+p.relative_to(T/'support').as_posix()) for p in (T/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
  files += [(T/'PLAN.json','PLAN.json'),(T/'launch.py','launch.py')]
  for source,rel in files:
   target=REMOTE+'/'+rel;parent=target.rsplit('/',1)[0]
   if parent not in created:execute(c,'mkdir -p '+shlex.quote(parent));created.add(parent)
   sf.put(str(source),target);manifest[rel]=dict(sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size)
  assets={P['parent']:P['parent_sha256']}
  for name,data in P['asset_identity']['actual_training_assets'].items():assets[P['package']+'/assets/'+name]=data['sha256']
  code='import pathlib,hashlib,json;root=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';a='+repr(assets)+';assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v["sha256"] for k,v in m.items());assert all(hashlib.sha256(pathlib.Path(k).read_bytes()).hexdigest()==v for k,v in a.items());print(json.dumps({"verified_source_files":len(m),"parent_and_existing_assets_verified":True}))'
  put(E/'UPLOAD_MANIFEST.json',manifest);put(E/'UPLOAD_VERIFIED.json',json.loads(execute(c,shlex.quote(P['python'])+' -B -c '+shlex.quote(code))))
 finally:c.close()
 idle();name='probe2048_parent_repaired_r1';job=REMOTE+'/'+name;c=connect()
 try:receipt=json.loads(execute(c,shlex.quote(P['python'])+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+name+' --kind probe --num-envs 2048'));put(E/'PROBE_LAUNCH.json',receipt)
 finally:c.close()
 print('REPAIRED_PARENT_NATIVE_PROBE_STARTED',flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,job+'/SAFE_CLOSED.json')
   if closed:
    dest=E/name;dest.mkdir(exist_ok=True)
    for item in sf.listdir_attr(job):
     if item.filename.endswith('.json'):sf.get(job+'/'+item.filename,str(dest/item.filename))
    sf.get(job+'.log',str(E/(name+'.log')))
    result=read(sf,job+'/ROUGH_PROBE.json');error=read(sf,job+'/ERROR.json');complete=read(sf,job+'/PROBE_COMPLETE.json');restore=read(sf,job+'/RESTORE.json')
    if error or not result or not complete:raise RuntimeError('Functional probe failed: '+json.dumps(error,ensure_ascii=False))
    assert result['flat_six_tasks_verified'] and result['stair_repair_probe']['height_reference_verified'] and result['stair_repair_probe']['retained_height_reference_verified']
    assert restore['iteration']==24692 and restore['optimizer_entries']==17
    group=result['samples'][-1]['terrain']['course_groups'];assert (group['continuous_stairs'],group['retained_rough'],group['flat'])==(819,717,512)
    put(E/'PROBE_ACCEPTED.json',dict(epoch=time.time(),accepted_probe=name,no_optimizer_update=True,actual_groups=group,flat_preservation=result['samples'][-1]['terrain']['flat_preservation'],reported_per_environment_resets=result['done_totals'],stair_repair_probe=result['stair_repair_probe'],restore=restore));break
   code='from pathlib import Path;import json;p=Path("/proc/'+str(int(receipt['pid']))+'/status");print(json.dumps(p.exists() and "State:\\tZ" not in p.read_text()))'
   if not json.loads(execute(c,shlex.quote(P['python'])+' -B -c '+shlex.quote(code))):raise RuntimeError('Native probe ended without SAFE_CLOSED; preserve raw evidence')
  finally:c.close()
  time.sleep(5)
 idle();c=connect()
 try:put(E/'PROBE_CLOSED_CACHE_CLEANUP.json',cleanup_closed_cache(c,REMOTE,job,P['python']))
 finally:c.close()
 c=connect()
 try:receipt=json.loads(execute(c,shlex.quote(P['python'])+' -B '+shlex.quote(REMOTE+'/launch.py')+' train040m_parent_repaired_r1 --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt)
 finally:c.close()
 with (T/'validation.log').open('wb') as out,(T/'validation_error.log').open('wb') as err:
  child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/'validate_launch.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 put(E/'VALIDATOR_LAUNCH.json',dict(epoch=time.time(),pid=child.pid));print('REPAIRED_PARENT40M_TRAIN_STARTED',json.dumps(receipt),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
