"""Save/close the superseded run, verify the one-term reward change, start fresh40m."""
from pathlib import Path
import json,sys,time,hashlib,shlex,subprocess,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T))
from remote_run import connect,execute,P,REMOTE
from native_cache_lifecycle import cleanup_closed_cache
OLD=R/P['previous_stage'];oldplan=json.loads((OLD/'PLAN.json').read_text(encoding='utf8'));OLDROOT=oldplan['root'];OLDJOB=OLDROOT+'/train040m_parent_repaired_r1';E=T/'evidence'
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def read(sf,p):
 try:
  with sf.open(p) as f:return json.loads(f.read())
 except FileNotFoundError:return None

def main():
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,OLDJOB+'/SAFE_CLOSED.json');final=read(sf,OLDJOB+'/FINAL.json')
   if closed:
    if not final:raise RuntimeError('Previous run closed without complete final checkpoint')
    digest=execute(c,'sha256sum -- '+shlex.quote(OLDJOB+'/model_final.pt')).split()[0];assert digest==final['checkpoint']['SHA']
    put(E/'PREVIOUS_RUN_SAFE_STOP.json',dict(closed=closed,final=final,final_SHA_verified=digest));break
  finally:c.close()
  time.sleep(3)
 while True:
  c=connect()
  try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
  finally:c.close()
  if not owners:break
  time.sleep(3)
 c=connect()
 try:
  put(E/'PREVIOUS_CLOSED_CACHE_CLEANUP.json',cleanup_closed_cache(c,OLDROOT,OLDJOB,P['python']))
  sf=c.open_sftp();execute(c,'mkdir -p '+shlex.quote(REMOTE));created={REMOTE};manifest={}
  files=[(p,'support/'+p.relative_to(T/'support').as_posix()) for p in (T/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']+[(T/'PLAN.json','PLAN.json'),(T/'launch.py','launch.py')]
  for p,rel in files:
   dest=REMOTE+'/'+rel;parent=dest.rsplit('/',1)[0]
   if parent not in created:execute(c,'mkdir -p '+shlex.quote(parent));created.add(parent)
   sf.put(str(p),dest);manifest[rel]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
  assets={P['parent']:P['parent_sha256']}
  for name,d in P['asset_identity']['actual_training_assets'].items():assets[P['package']+'/assets/'+name]=d['sha256']
  code='import pathlib,hashlib,json;root=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';a='+repr(assets)+';assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v["sha256"] for k,v in m.items());assert all(hashlib.sha256(pathlib.Path(k).read_bytes()).hexdigest()==v for k,v in a.items());print(json.dumps({"verified_source_files":len(m),"original_parent_and_assets_verified":True}))'
  put(E/'UPLOAD_MANIFEST.json',manifest);put(E/'UPLOAD_VERIFIED.json',json.loads(execute(c,shlex.quote(P['python'])+' -B -c '+shlex.quote(code))))
 finally:c.close()
 prior=OLD/'evidence/probe2048_parent_repaired_r1/ROUGH_PROBE.json';proof=json.loads(prior.read_text(encoding='utf8'));assert proof['num_envs']==2048 and proof['no_optimizer_update'] and proof['stair_repair_probe']['height_reference_verified']
 put(E/'REUSED_PRELAUNCH_EVIDENCE.json',dict(source=str(prior),source_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),num_envs=2048,steps=600,same_original_parent=True,same_assets_controller_DR_and403525_distribution=True,only_reward_term_removed='0.8*advance',reason='A removed bounded positive scalar reward does not change frozen-policy physics; reuse actual same-plant source proof and verify new reward zero in first update/ongoing checkpoints',prior_done_totals=proof['done_totals']))
 c=connect()
 try:receipt=json.loads(execute(c,shlex.quote(P['python'])+' -B '+shlex.quote(REMOTE+'/launch.py')+' train040m_no_progress_parent_r1 --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt)
 finally:c.close()
 with (T/'validation.log').open('wb') as out,(T/'validation_error.log').open('wb') as err:
  child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/'validate_launch.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 put(E/'VALIDATOR_LAUNCH.json',dict(epoch=time.time(),pid=child.pid));print('NO_PROGRESS_PARENT40M_TRAIN_STARTED',json.dumps(receipt),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
