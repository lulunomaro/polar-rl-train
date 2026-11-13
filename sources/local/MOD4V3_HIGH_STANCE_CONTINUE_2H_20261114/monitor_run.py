"""Watch only this authorized run; collect full PTs and inspect every five training minutes."""
from pathlib import Path
import sys,json,time,hashlib,os,subprocess,shlex,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
JOB=REMOTE+'/train120m_height_continue_r1';E=T/'evidence';W=T/'weights';W.mkdir(exist_ok=True);(E/'training').mkdir(exist_ok=True);(E/'inspections').mkdir(exist_ok=True);(E/'checkpoint_evals').mkdir(exist_ok=True)

def put(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,path)
while not (E/'TRAIN_LAUNCH.json').exists():
 if (E/'LAUNCH_ERROR.json').exists():raise RuntimeError('New launch failed; see LAUNCH_ERROR.json')
 time.sleep(3)
seen={};models={};queue=[];active=None;history=[];last_boundary=-1;failures=0;closed=False
while True:
 try:
  c=connect()
  try:
   sf=c.open_sftp();files=sf.listdir_attr(JOB)
   for item in files:
    name=item.filename
    if not name.endswith('.json') or seen.get(name)==(item.st_mtime,item.st_size):continue
    target=E/'training'/name;tmp=target.with_name(target.name+'.partial');sf.get(JOB+'/'+name,str(tmp));json.loads(tmp.read_text());os.replace(tmp,target);seen[name]=(item.st_mtime,item.st_size)
   for item in files:
    name=item.filename
    if not(name.startswith('model_') and name.endswith('.pt')) or name in models:continue
    target=W/name;tmp=target.with_name(target.name+'.partial');sf.get(JOB+'/'+name,str(tmp));digest=hashlib.sha256(tmp.read_bytes()).hexdigest();remote_sha=execute(c,'sha256sum -- '+shlex.quote(JOB+'/'+name)).split()[0];assert digest==remote_sha,name;os.replace(tmp,target);models[name]=dict(file=name,path=str(target),bytes=target.stat().st_size,sha256=digest,remote=JOB+'/'+name,verified_epoch=time.time());print('FULL_PT_COLLECTED '+name+' '+digest,flush=True)
    if name!='model_first_complete.pt':queue.append(str(target))
   progress=E/'training/LATEST_PROGRESS.json'
   if progress.exists():
    current=json.loads(progress.read_text());phase_elapsed=current.get('training_elapsed_seconds',0.);elapsed=current.get('cumulative_training_elapsed_seconds',phase_elapsed);boundary=int(elapsed//300)
    if boundary>last_boundary:
     last_boundary=boundary;report=dict(epoch=time.time(),training_minutes=elapsed/60,phase_training_seconds=phase_elapsed,course_groups=current.get('terrain',{}).get('course_groups'),specialist=current.get('terrain',{}).get('specialist'),iteration=current['iteration'],done_totals=current['done_totals'],mean_reward=current['mean_reward'],continuous_stair=current.get('terrain',{}).get('continuous_stair'),numeric_peaks=current.get('numeric_peaks'),teacher_retention=current.get('teacher_retention'),flat_fixed_steady_tracking=current.get('flat_fixed_steady_tracking'),optimizer_entries=current.get('optimizer_entries'),collected_full_PT=len(models));put(E/'inspections'/f'INSPECTION_{boundary*5:03d}M.json',report)
     with (E/'INSPECTIONS.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(report,ensure_ascii=False)+'\n')
     print(json.dumps(report),flush=True)
    put(E/'MONITOR_STATUS.json',dict(epoch=time.time(),pid=os.getpid(),training_elapsed_seconds=elapsed,phase_training_seconds=phase_elapsed,course_groups=current.get('terrain',{}).get('course_groups'),specialist=current.get('terrain',{}).get('specialist'),iteration=current['iteration'],collected_full_PT=len(models),queued_evaluations=len(queue),active_evaluation=active['model'] if active else None,consecutive_transport_failures=0,remote_closed=(E/'training/SAFE_CLOSED.json').exists(),training_has_error=(E/'training/ERROR.json').exists()))
   closed=(E/'training/SAFE_CLOSED.json').exists()
   if closed:
    try:sf.get(REMOTE+'/train120m_height_continue_r1.log',str(E/'train120m_height_continue_r1.log'))
    except FileNotFoundError:pass
  finally:c.close()
  failures=0
 except Exception:
  failures+=1;put(E/'MONITOR_LAST_ERROR.json',dict(epoch=time.time(),count=failures,traceback=traceback.format_exc()));print('COLLECTOR_RETRY '+str(failures),flush=True)
 if active is not None and active['process'].poll() is not None:
  result=dict(model=active['model'],exit_code=active['process'].returncode,finished_epoch=time.time(),evaluation=str(E/'checkpoint_evals'/Path(active['model']).stem/'EVALUATION.json'));history.append(result);put(E/'EVALUATION_QUEUE.json',dict(completed=history,queued=queue));active=None
 if active is None and queue:
  model=queue.pop(0);log=(E/(Path(model).stem+'_evaluation_worker.log')).open('wb');process=subprocess.Popen([sys.executable,'-X','utf8','-u',str(T/'evaluate_checkpoint.py'),model],cwd=R,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);log.close();active=dict(model=model,process=process);print('EVALUATING '+Path(model).name,flush=True)
 put(E/'MODEL_COLLECTION.json',dict(models=list(models.values()),remote_job=JOB,full_PT_bytes=True))
 if closed and not queue and active is None:
  put(E/'MONITOR_COMPLETE.json',dict(epoch=time.time(),training_closed=True,training_has_error=(E/'training/ERROR.json').exists(),models=list(models.values()),evaluations=history));print('MONITOR_COMPLETE',flush=True)
  if False and (T/'finalize_run.py').exists():
   with (E/'finalize.log').open('wb') as log:result=subprocess.run([sys.executable,'-X','utf8',str(T/'finalize_run.py')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
   print('FINALIZE_EXIT '+str(result.returncode),flush=True)
  break
 time.sleep(20)
