"""At the next complete saved boundary, continue with Rough-v1 retention; no extra training budget."""
from pathlib import Path
import sys,json,time,hashlib,shlex,os,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T))
from remote_run import connect,execute
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));REMOTE=P['root'];OLD=R/P['previous_stage'];JOB=P['previous_remote_job']
def put(p,d):
 p=Path(p);tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def read(sf,p):
 try:
  with sf.open(p) as f:return json.loads(f.read())
 except FileNotFoundError:return None
def mkdir(sf,p):
 try:sf.stat(p)
 except FileNotFoundError:mkdir(sf,p.rsplit('/',1)[0]);sf.mkdir(p)
def call(c,code):return execute(c,shlex.quote(P['python'])+' -c '+shlex.quote(code))
def main():
 c=connect()
 try:
  sf=c.open_sftp();mkdir(sf,REMOTE);manifest={}
  files=[(p,'support/'+p.relative_to(T/'support').as_posix()) for p in (T/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
  files += [(T/'launch.py','launch.py')]
  for p,rel in files:
   dst=REMOTE+'/'+rel;mkdir(sf,dst.rsplit('/',1)[0]);sf.put(str(p),dst);manifest[rel]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  verification=json.loads(call(c,'import pathlib,hashlib,json; b=pathlib.Path('+repr(REMOTE)+');m='+repr(manifest)+';actual={k:hashlib.sha256((b/k).read_bytes()).hexdigest() for k in m};assert all(actual[k]==m[k]["sha256"] for k in m);print(json.dumps({"files":len(m),"all_equal":True}))'))
  put(T/'evidence/UPLOAD_MANIFEST.json',manifest);put(T/'evidence/UPLOAD_VERIFIED.json',verification)
  progress=read(sf,JOB+'/LATEST_PROGRESS.json');assert progress
  boundary=(int(progress['training_elapsed_seconds']//300)+1)*300
  assert boundary<7200
  put(T/'evidence/SWITCH_REQUEST.json',dict(epoch=time.time(),target_training_seconds=boundary,previous_job=JOB,mixture=dict(continuous_stairs=.5,rough_v1=.3,flat=.2)))
 finally:c.close()
 print('WAIT_SAVED_BOUNDARY '+str(boundary),flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();receipt=read(sf,JOB+'/PERIODIC_'+format(int(boundary/60),'03d')+'M.json')
   if receipt:
    with sf.open(JOB+'/REQUEST_STOP','w') as f:f.write('Human requested Rough-v1 retention; continue same7200s budget from final complete PPO.\n')
    put(T/'evidence/STOP_AFTER_SAVED_BOUNDARY.json',dict(epoch=time.time(),receipt=receipt));break
   error=read(sf,JOB+'/ERROR.json')
   if error:raise RuntimeError('Old job failed before saved boundary: '+str(error))
  finally:c.close()
  time.sleep(2)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();closed=read(sf,JOB+'/SAFE_CLOSED.json');final=read(sf,JOB+'/FINAL.json')
   if closed:
    if not final:raise RuntimeError('Old job closed without final PPO')
    consumed=final['elapsed_seconds'];assert 0<consumed<7200
    parent=JOB+'/model_final.pt';digest=execute(c,'sha256sum -- '+shlex.quote(parent)).split()[0]
    P.update(parent=parent,parent_sha256=digest,cumulative_training_seconds_before=consumed)
    P['training_round']['seconds']=int(7200-consumed)
    put(T/'PLAN.json',P);sf.put(str(T/'PLAN.json'),REMOTE+'/PLAN.json')
    sf.get(parent,str(T/'weights/parent_phase1_boundary.pt'))
    assert hashlib.sha256((T/'weights/parent_phase1_boundary.pt').read_bytes()).hexdigest()==digest
    put(T/'evidence/PHASE1_FINAL.json',final);put(T/'evidence/PHASE1_SAFE_CLOSED.json',closed)
    put(OLD/'evidence/RETENTION_HANDOFF.json',dict(next_stage=T.relative_to(R).as_posix(),consumed_training_seconds=consumed,remaining_training_seconds=P['training_round']['seconds'],total_budget_seconds=7200,parent_sha256=digest))
    break
  finally:c.close()
  time.sleep(2)
 def idle():
  while True:
   c=connect()
   try:owners=execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits').strip()
   finally:c.close()
   if not owners:return
   time.sleep(2)
 idle()
 c=connect()
 try:
  out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' probe2048_retention_r1 --kind probe --num-envs 2048');put(T/'evidence/PROBE_LAUNCH.json',json.loads(out))
 finally:c.close()
 print('RETENTION_PROBE_LAUNCHED',flush=True)
 while True:
  c=connect()
  try:
   sf=c.open_sftp();probe=REMOTE+'/probe2048_retention_r1';closed=read(sf,probe+'/SAFE_CLOSED.json')
   if closed:
    mkdir_local=T/'evidence/probe2048_retention_r1';mkdir_local.mkdir(exist_ok=True)
    for item in sf.listdir_attr(probe):
     if item.filename.endswith('.json'):sf.get(probe+'/'+item.filename,str(mkdir_local/item.filename))
    sf.get(REMOTE+'/probe2048_retention_r1.log',str(T/'evidence/probe2048_retention_r1.log'))
    result=read(sf,probe+'/ROUGH_PROBE.json');complete=read(sf,probe+'/PROBE_COMPLETE.json');error=read(sf,probe+'/ERROR.json')
    if error or not complete or not result:raise RuntimeError('Retention probe failed: '+str(error))
    if result['done_totals'].get('numerical',0) or result['done_totals'].get('mimic',0):raise RuntimeError('Native probe nonfinite/mimic failure: '+str(result['done_totals']))
    put(T/'evidence/PROBE_ACCEPTED.json',dict(epoch=time.time(),result=result,scope='Functional2048env/noPPO; same per-environment2mm closure reset; not graduation'))
    break
  finally:c.close()
  time.sleep(5)
 idle()
 c=connect()
 try:
  out=execute(c,shlex.quote(P['python'])+' '+shlex.quote(REMOTE+'/launch.py')+' train_retention_r1 --kind train --num-envs 2048');put(T/'evidence/TRAIN_LAUNCH.json',json.loads(out))
 finally:c.close()
 put(T/'evidence/SWITCH_COMPLETE.json',dict(epoch=time.time(),remaining_training_seconds=P['training_round']['seconds'],previous_training_seconds=consumed,parent_sha256=digest,whole_budget_seconds=7200,training_launched=True))
 print('RETENTION_TRAIN_LAUNCHED '+str(P['training_round']['seconds']),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put(T/'evidence/SWITCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
