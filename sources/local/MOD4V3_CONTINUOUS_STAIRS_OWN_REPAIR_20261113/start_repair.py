"""Verify the restored own recipe with no PPO, then start one bounded40-minute repair."""
from pathlib import Path
import sys,json,hashlib,time,shlex,traceback,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T))
from remote_run import P,REMOTE,connect,execute
from native_cache_lifecycle import cleanup_closed_cache

def put(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(path)
def read(sf,path):
 try:
  with sf.open(path) as f:return json.loads(f.read())
 except FileNotFoundError:return None
def mkdir(sf,path):
 try:sf.stat(path)
 except FileNotFoundError:mkdir(sf,path.rsplit('/',1)[0]);sf.mkdir(path)
def idle():
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:return
  time.sleep(2)
def main():
 manifest={};c=connect()
 try:
  sf=c.open_sftp();mkdir(sf,REMOTE)
  files=[(x,'support/'+x.relative_to(T/'support').as_posix()) for x in (T/'support').rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc']
  files.extend([(T/'PLAN.json','PLAN.json'),(T/'launch.py','launch.py')])
  for source,rel in files:
   target=REMOTE+'/'+rel;mkdir(sf,target.rsplit('/',1)[0]);sf.put(str(source),target);manifest[rel]={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bytes':source.stat().st_size}
  assets={P['parent']:P['parent_sha256']}
  for name,data in P['asset_identity']['actual_training_assets'].items():assets[P['package']+'/assets/'+name]=data['sha256']
  code='import pathlib,hashlib,json;root=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';a='+repr(assets)+';assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v["sha256"] for k,v in m.items());assert all(hashlib.sha256(pathlib.Path(k).read_bytes()).hexdigest()==v for k,v in a.items());print(json.dumps({"verified_source_files":len(m),"parent_and_existing_assets_verified":True}))'
  verified=json.loads(execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code)))
  put(E/'UPLOAD_MANIFEST.json',manifest);put(E/'UPLOAD_VERIFIED.json',verified)
 finally:c.close()
 name='probe2048_own_repair_r3';job=REMOTE+'/'+name
 for filename in ('continuous_stair_env.py','continuous_stair_checks.py','scut_rough_scut_v1_env.py'):
  dest=E/'probe_r3_source'/filename;dest.parent.mkdir(exist_ok=True);shutil.copy2(T/'support/mod4v3_ppo_v1'/filename,dest)
 idle();c=connect()
 try:put(E/'PROBE_R2_CLOSED_CACHE_CLEANUP.json',cleanup_closed_cache(c,REMOTE,REMOTE+'/probe2048_own_repair_r2',P['python']))
 finally:c.close()
 c=connect()
 try:receipt=json.loads(execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' '+name+' --kind probe --num-envs 2048'));put(E/'PROBE_LAUNCH.json',receipt)
 finally:c.close()
 print('OWN_RECIPE_NATIVE_PROBE_STARTED',flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,job+'/SAFE_CLOSED.json')
   if not closed:
    code='from pathlib import Path;import json;p=Path("/proc/'+str(int(receipt['pid']))+'/status");print(json.dumps(p.exists() and "State:\\tZ" not in p.read_text()))'
    if not json.loads(execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code))) and not read(sf,job+'/SAFE_CLOSED.json'):
     sf.get(job+'.log',str(E/(name+'_hard_exit.log')));raise RuntimeError('Probe process ended without closure receipt; inspect preserved raw log')
   if closed:
    dest=E/name;dest.mkdir(exist_ok=True)
    for item in sf.listdir_attr(job):
     if item.filename.endswith('.json'):sf.get(job+'/'+item.filename,str(dest/item.filename))
    sf.get(job+'.log',str(E/(name+'.log')))
    result=read(sf,job+'/ROUGH_PROBE.json');error=read(sf,job+'/ERROR.json');complete=read(sf,job+'/PROBE_COMPLETE.json');restore=read(sf,job+'/RESTORE.json')
    if error or not result or not complete:raise RuntimeError('Own recipe functional probe failed: '+json.dumps(error,ensure_ascii=False))
    assert result['flat_six_tasks_verified'] and result['own_stair_shaping_enabled'] and result['terrain_name_filter_verified']
    assert restore['iteration']==24692 and restore['optimizer_entries']==17
    group=result['samples'][-1]['terrain']['course_groups'];assert group['continuous_stairs']==1024 and group['retained_rough']==614 and group['flat']==410
    put(E/'PROBE_ACCEPTED.json',{'epoch':time.time(),'accepted_probe':name,'no_optimizer_update':True,'actual_groups':group,'flat_preservation':result['samples'][-1]['terrain']['flat_preservation'],'reported_per_environment_resets':result['done_totals'],'scope':'Own stair shaping, original speed reward, six flat commands, ground reset exclusion and actual terrain filtering;600steps; no global zero-reset requirement','restore':restore});break
  finally:c.close()
  time.sleep(5)
 idle();c=connect()
 try:put(E/'PROBE_CLOSED_CACHE_CLEANUP.json',cleanup_closed_cache(c,REMOTE,job,P['python']))
 finally:c.close()
 c=connect()
 try:receipt=json.loads(execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' train040m_own_repair_r1 --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt)
 finally:c.close()
 print('OWN_RECIPE40M_TRAIN_STARTED',flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(E/'LAUNCH_ERROR.json',{'epoch':time.time(),'traceback':traceback.format_exc()});raise
