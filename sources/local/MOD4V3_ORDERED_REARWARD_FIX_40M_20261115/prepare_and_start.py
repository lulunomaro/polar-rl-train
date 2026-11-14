"""One new authorized2400s PPO round after an isolated zero-update functional probe."""
from pathlib import Path
import datetime,hashlib,json,os,shlex,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
JOB='train40m_ordered_rearward_fix_r2';PROBE='probe64_ordered_rearward_fix_r2';TZ=datetime.timezone(datetime.timedelta(hours=8))
def put(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,path)
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def spawn(script,name):
 with(T/(name+'.log')).open('xb')as out,(T/(name+'_error.log')).open('xb')as err:
  child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/script)],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 return child.pid
if __name__=='__main__':
 launched=False
 try:
  c=connect()
  try:
   sf=c.open_sftp()
   try:sf.stat(REMOTE);raise RuntimeError('Remote round already exists; do not replay it')
   except FileNotFoundError:pass
   code="from pathlib import Path;import hashlib,json;root=Path("+repr(P['package'])+");want="+repr(P['asset_identity']['actual_training_assets'])+";assert all(hashlib.sha256((root/'assets'/k).read_bytes()).hexdigest()==v['sha256']for k,v in want.items());print(json.dumps(dict(verified_assets=want,actual_root=str(Path('/home/egde/rl_candidates').resolve()))))"
   put(E/'FROZEN_ASSET_REUSE.json',json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code))))
   def mkdir(path):
    try:sf.stat(path)
    except FileNotFoundError:
     mkdir(path.rsplit('/',1)[0]);sf.mkdir(path)
   mkdir(REMOTE);index={}
   files=[T/name for name in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt','teacher_movement_balanced_demos.pt','high_stance_comprehensive_anchors.pt','rearward_reference_dataset.pt']]
   files +=[p for p in(T/'support').rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc']
   for path in files:
    rel=path.relative_to(T).as_posix();target=REMOTE+'/'+rel;mkdir(target.rsplit('/',1)[0]);sf.put(str(path),target);index[rel]=hashlib.sha256(path.read_bytes()).hexdigest()
   source=T/'weights/frozen_comprehensive_parent.pt';assert hashlib.sha256(source.read_bytes()).hexdigest()==P['parent_sha256'];sf.put(str(source),P['parent']);index['frozen_best_parent.pt']=P['parent_sha256']
   with sf.open(REMOTE+'/UPLOADED_INPUT_SHA256.json','w')as out:out.write(json.dumps(index))
   code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d=json.loads((root/'UPLOADED_INPUT_SHA256.json').read_text());assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256=d['frozen_best_parent.pt'])))"
   put(E/'UPLOADED_INPUTS.json',dict(epoch=time.time(),files=index,verification=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))))
   put(E/'PROBE_LAUNCH.json',json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+PROBE+' --kind probe --num-envs 64')))
  finally:c.close()
  print('ZERO_UPDATE_FUNCTIONAL_PROBE_STARTED',flush=True);target=E/'probe64_r1';target.mkdir()
  while True:
   c=connect()
   try:
    sf=c.open_sftp()
    try:names=sf.listdir(REMOTE+'/'+PROBE)
    except FileNotFoundError:names=[]
    if 'SAFE_CLOSED.json'in names:
     for name in names:
      if name.endswith('.json'):sf.get(REMOTE+'/'+PROBE+'/'+name,str(target/name))
     sf.get(REMOTE+'/'+PROBE+'.log',str(target/'stdout.log'))
     if(target/'ERROR.json').exists():raise RuntimeError('Functional probe error; preserve it and repair a new attempt')
     assert read(target/'ROUGH_PROBE.json')['done_totals'].get('numerical',0)==0
     code="from pathlib import Path;import subprocess,json;pid="+str(read(E/'PROBE_LAUNCH.json')['pid'])+";owners=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True);print(json.dumps(dict(probe_gpu_context_released=str(pid)not in owners.split())))"
     if json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))['probe_gpu_context_released']:break
   finally:c.close()
   time.sleep(5)
  print('ZERO_UPDATE_FUNCTIONAL_PROBE_COMPLETE',flush=True)
  c=connect()
  try:put(E/'TRAIN_LAUNCH.json',json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+JOB+' --kind train --num-envs 2048')));launched=True
  finally:c.close()
  put(E/'MONITOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run.py','monitor'),checkpoint_seconds=300))
  put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline.py','pipeline'),no_additional_training=True))
  while not(E/'training/FIRST_UPDATE.json').exists():
   if(E/'training/ERROR.json').exists():raise RuntimeError('Owner failed before first actor update')
   time.sleep(5)
  first=read(E/'training/FIRST_UPDATE.json');restore=read(E/'training/RESTORE.json');assert first['actor_changed']and restore['actor_critic_STD_Adam_restored']
  start=first['epoch']-first['training_elapsed_seconds'];result=dict(actual_PPO_start_epoch=start,actual_PPO_start_local=datetime.datetime.fromtimestamp(start,TZ).isoformat(),planned_PPO_end_local=datetime.datetime.fromtimestamp(start+P['training_round']['seconds'],TZ).isoformat(),parent_sha256=P['parent_sha256'],parent_iteration=25331,actor_changed=True,optimizer_entries=first['optimizer_entries'],budget_seconds=P['training_round']['seconds'],previous_phase_PPO_seconds=P['cumulative_training_seconds_before'],original_round_budget_seconds=2400,checkpoint_seconds=300,automatic_extension=False)
  put(E/'TRAINING_STARTED_CONFIRMED.json',result)
  with(T/'README.md').open('a',encoding='utf8')as out:out.write('\n## 实际开训\n\n'+result['actual_PPO_start_local']+'开始，预计到'+result['planned_PPO_end_local']+'。已确认完整父状态恢复、17项Adam状态与首轮actor更新。\n')
  regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);reg['active_ordered_rearward_fix_training_20261115']=dict(result,source_directory=T.relative_to(R).as_posix(),plan=(T/'PLAN.json').relative_to(R).as_posix(),remote_job=REMOTE+'/'+JOB);put(regpath,reg)
  print('ACTUALLY_TRAINING '+json.dumps(result),flush=True)
  with(E/'ARCHIVE_LAUNCH.log').open('xb')as out,(E/'ARCHIVE_LAUNCH_ERROR.log').open('xb')as err:done=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=out,stderr=err)
  if done.returncode:put(E/'GIT_LAUNCH_PENDING.json',dict(exit_code=done.returncode,training_continues=True));raise RuntimeError('Launch archive pending; do not relaunch PPO')
  print('LAUNCH_ARCHIVED_VIA7897',flush=True)
 except BaseException:
  put(E/('STARTUP_ERROR.json'if launched else'PREPARATION_ERROR.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=launched,automatic_repeat=False));raise
