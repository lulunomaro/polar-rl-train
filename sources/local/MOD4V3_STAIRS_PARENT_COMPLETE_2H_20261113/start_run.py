"""Upload isolated repaired source, validate frozen2048x600, then launch authorized2h once."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T))
from remote_run import connect,execute,P,REMOTE
E=T/'evidence';PROBE=REMOTE+'/probe2048_r1';JOB=REMOTE+'/train120m_parent_r1'
def put(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');os.replace(tmp,path)
try:
 assert not (E/'TRAIN_LAUNCH.json').exists()
 provenance=json.loads((T/'PROVENANCE.json').read_text(encoding='utf8'))
 files=[T/'PLAN.json',T/'launch.py',T/'teacher_success_full_episode_demos.pt']+[p for p in (T/'support').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 c=connect()
 try:
  create="from pathlib import Path;import json,os;root=Path("+repr(REMOTE)+");assert not root.exists();root.mkdir();assert str(root.resolve()).startswith('/mnt/mod4_windows_data/MOD4_training_data/rl_candidates/');print(json.dumps(dict(root=str(root.resolve()),created=True)))"
  receipt=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(create)));put(E/'REMOTE_DIRECTORY.json',receipt)
  sf=c.open_sftp();made={REMOTE};index={}
  def mkdir(path):
   if path in made:return
   parent=path.rsplit('/',1)[0]
   if parent not in made:mkdir(parent)
   try:sf.mkdir(path)
   except OSError:sf.stat(path)
   made.add(path)
  for p in files:
   rel=p.relative_to(T).as_posix();dest=REMOTE+'/'+rel;mkdir(dest.rsplit('/',1)[0]);sf.put(str(p),dest);index[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
  with sf.open(REMOTE+'/UPLOADED_INPUT_SHA256.json','w') as f:f.write(json.dumps(index))
  code="from pathlib import Path;import json,hashlib,shutil;root=Path("+repr(REMOTE)+");source=Path("+repr(provenance['source_parent_remote'])+");expected="+repr(P['parent_sha256'])+";assert hashlib.sha256(source.read_bytes()).hexdigest()==expected;shutil.copyfile(source,root/'frozen_best_parent.pt');files=json.loads((root/'UPLOADED_INPUT_SHA256.json').read_text());assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in files.items());print(json.dumps(dict(parent_sha256=expected,verified_inputs=len(files),root=str(root.resolve()))))"
  verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'UPLOADED_INPUTS.json',dict(files=index,verified=verified))
  result=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' probe2048_r1 --kind probe --num-envs 2048'));put(E/'PROBE_LAUNCH.json',result);print('FROZEN_PROBE_STARTED '+str(result['pid']),flush=True)
 finally:c.close()
 while True:
  c=connect()
  try:
   sf=c.open_sftp()
   try:items=sf.listdir_attr(PROBE)
   except FileNotFoundError:items=[]
   local=E/'probe';local.mkdir(exist_ok=True)
   for item in items:
    if item.filename.endswith('.json'):
     try:sf.get(PROBE+'/'+item.filename,str(local/item.filename))
     except FileNotFoundError:pass
   closed=(local/'SAFE_CLOSED.json').exists()
   if closed:
    sf.get(REMOTE+'/probe2048_r1.log',str(E/'probe2048_r1.log'))
    if execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip():closed=False
  finally:c.close()
  if closed:break
  time.sleep(5)
 assert not (local/'ERROR.json').exists(),'Probe failed; original error retained'
 assert (local/'PROBE_COMPLETE.json').exists()
 probe=json.loads((local/'ROUGH_PROBE.json').read_text());scope=json.loads((local/'TEACHER_KEEP_SCOPE.json').read_text())
 assert probe['no_optimizer_update'] and probe['num_envs']==2048 and probe['steps']==600
 assert probe['done_totals'].get('numerical',0)==0
 assert scope['ascent_parent_keep']==0 and scope['retained_parent_keep']==scope['retained_envs']
 put(E/'ADMISSION.json',dict(epoch=time.time(),frozen_probe_complete=True,probe=probe,teacher_keep_scope=scope,new_training_seconds=7200,automatic_extension=False));print('FROZEN_PROBE_PASSED',flush=True)
 c=connect()
 try:
  result=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' train120m_parent_r1 --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',result)
 finally:c.close()
 with (T/'monitor.log').open('wb') as out,(T/'monitor_error.log').open('wb') as err:
  monitor=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/'monitor_run.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 put(E/'MONITOR_LAUNCH.json',dict(epoch=time.time(),pid=monitor.pid,interval_seconds=300,full_checkpoints=True,independent_checkpoint_evaluations=True))
 print('TWO_HOUR_TRAINING_LAUNCHED '+json.dumps(dict(remote_pid=result['pid'],job=JOB,monitor_pid=monitor.pid,budget_seconds=7200)),flush=True)
except BaseException:
 put(E/'LAUNCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),scope='No automatic repeat, no old experiment overwritten'))
 raise
