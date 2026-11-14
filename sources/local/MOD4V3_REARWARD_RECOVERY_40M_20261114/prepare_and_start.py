"""Upload, functional probe, and one user-authorized2400s round. No automatic extension."""
from pathlib import Path
import datetime,hashlib,json,os,shlex,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
PREVIOUS=T.parent/'MOD4V3_REARWARD_SUPPORTED_STAIRS_40M_20261114';JOB='train40m_rearward_recovery_r1';PROBE='probe64_rearward_recovery_r1';TZ=datetime.timezone(datetime.timedelta(hours=8))
def put(path,data):
 path=Path(path);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,path)
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def spawn(script,name):
 with (T/(name+'.log')).open('xb')as out,(T/(name+'_error.log')).open('xb')as err:
  child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/script)],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 return child.pid

def publish_active(started):
 path=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(path);sid='rearward_recovery_40m_20261114'
 reg['active_training']=dict(id=sid,title='后摆收腿恢复参考引导40分钟',source_directory=T.relative_to(R).as_posix(),plan=(T/'PLAN.json').relative_to(R).as_posix(),remote_job=REMOTE+'/'+JOB,actual_start=started['actual_PPO_start_local'],planned_end=started['planned_PPO_end_local'],parent_sha256=P['parent_sha256'],budget_seconds=2400,checkpoint_every_seconds=300,automatic_extension=False)
 reg['current_training_status']='active: frozen db6 parent, independent rearward/rise progress and physically successful nominal reference; fullDR40/35/25 retained';reg['updated_at_epoch']=time.time();path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\r\n')
 for p in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',path.parent/'README.md']:
  with p.open('a',encoding='utf8',newline='\r\n')as f:f.write('\n## 2026-11-14 后摆收腿修复独立40分钟已开训\n\n原生64环境功能探针完成；从综合父db6e9ccf/iter25331恢复。原乘积改为独立后摆/抬升进展，加入3个后摆中段辅助姿态及4条真实单阶恢复的194帧腿参考，保留完整DR、40/35/25、原教师和高站姿锚。每5分钟完整PT与纯策略固定回放。PPO '+started['actual_PPO_start_local']+'，计划到'+started['planned_PPO_end_local']+'；不自动晋升。见'+T.relative_to(R).as_posix()+'/README.md。\n')

if __name__=='__main__':
 launched=False
 try:
  assert not(E/'TRAIN_LAUNCH.json').exists(),'This authorized round already launched'
  assert P['training_round']['seconds']==2400 and P['parent_iteration']==25331
  assert read(PREVIOUS/'evidence/post_native/COMPLETE.json')['all_closed']
  assert read(PREVIOUS/'evidence/PIPELINE_COMPLETE_RECOVERED_R1.json')['remote_verified']
  c=connect()
  try:
   sf=c.open_sftp()
   try:sf.stat(REMOTE);raise RuntimeError('New remote root already exists; inspect before repeat')
   except FileNotFoundError:sf.mkdir(REMOTE)
   def mkdir(path):
    try:sf.stat(path);return
    except FileNotFoundError:mkdir(path.rsplit('/',1)[0]);sf.mkdir(path)
   files=[T/n for n in ['PLAN.json','launch.py','comprehensive_keep_teacher.pt','high_stance_comprehensive_anchors.pt','teacher_movement_balanced_demos.pt','rearward_reference_dataset.pt']]
   files +=[p for p in (T/'support').rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc']
   index={}
   for file in files:
    rel=file.relative_to(T).as_posix();target=REMOTE+'/'+rel;mkdir(target.rsplit('/',1)[0]);sf.put(str(file),target);index[rel]=hashlib.sha256(file.read_bytes()).hexdigest()
   file=T/'weights/frozen_comprehensive_parent.pt';assert hashlib.sha256(file.read_bytes()).hexdigest()==P['parent_sha256'];sf.put(str(file),P['parent']);index['frozen_best_parent.pt']=P['parent_sha256']
   with sf.open(REMOTE+'/UPLOADED_INPUT_SHA256.json','w')as out:out.write(json.dumps(index))
   code="from pathlib import Path;import hashlib,json;root=Path("+repr(REMOTE)+");files=json.loads((root/'UPLOADED_INPUT_SHA256.json').read_text());assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in files.items());print(json.dumps(dict(verified_inputs=len(files),parent_sha256=files['frozen_best_parent.pt'])))"
   put(E/'UPLOADED_INPUTS.json',dict(epoch=time.time(),files=index,verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)))))
   receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+PROBE+' --kind probe --num-envs 64'));put(E/'PROBE_LAUNCH.json',receipt)
  finally:c.close()
  print('FUNCTIONAL_PROBE64_STARTED',flush=True);target=E/'probe64_r1';target.mkdir()
  while True:
   c=connect()
   try:
    sf=c.open_sftp()
    try:names=sf.listdir(REMOTE+'/'+PROBE)
    except FileNotFoundError:names=[]
    if 'SAFE_CLOSED.json'in names:
     for name in names:
      if name.endswith(('.json','.py')):sf.get(REMOTE+'/'+PROBE+'/'+name,str(target/name))
     sf.get(REMOTE+'/'+PROBE+'.log',str(target/'stdout.log'))
     if(target/'ERROR.json').exists():raise RuntimeError('Functional probe failed; originalERROR retained')
     assert(target/'ROUGH_PROBE.json').exists()
     assert read(target/'ROUGH_PROBE.json')['done_totals'].get('numerical',0)==0,'Nonfinite probe requires repair'
     if not execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip():break
   finally:c.close()
   time.sleep(5)
  print('FUNCTIONAL_PROBE64_COMPLETE',flush=True)
  c=connect()
  try:receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+JOB+' --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt);launched=True
  finally:c.close()
  put(E/'MONITOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run.py','monitor'),checkpoint_interval_seconds=300,full_PT=True))
  put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline.py','pipeline'),no_further_training=True))
  while not(E/'training/FIRST_UPDATE.json').exists():
   if(E/'training/ERROR.json').exists():raise RuntimeError('Training failed before first update; originalERROR retained')
   time.sleep(5)
  first=read(E/'training/FIRST_UPDATE.json');restore=read(E/'training/RESTORE.json');assert first['actor_changed']and restore['actor_critic_STD_Adam_restored']
  start=first['epoch']-first['training_elapsed_seconds'];started=dict(actual_PPO_start_epoch=start,actual_PPO_start_local=datetime.datetime.fromtimestamp(start,TZ).isoformat(),planned_PPO_end_local=datetime.datetime.fromtimestamp(start+2400,TZ).isoformat(),parent_sha256=P['parent_sha256'],parent_iteration=P['parent_iteration'],actor_changed=True,optimizer_entries=first['optimizer_entries'],budget_seconds=2400,automatic_extension=False)
  put(E/'TRAINING_STARTED_CONFIRMED.json',started);publish_active(started)
  with(T/'README.md').open('a',encoding='utf8',newline='\r\n')as out:out.write('\n## 实际开训\n\nPPO开始'+started['actual_PPO_start_local']+'，计划到'+started['planned_PPO_end_local']+'。完整父状态恢复及首轮actor更新已确认。\n')
  print('ACTUALLY_TRAINING '+json.dumps(started),flush=True)
  with(E/'ARCHIVE_LAUNCH.log').open('xb')as out,(E/'ARCHIVE_LAUNCH_ERROR.log').open('xb')as err:result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=out,stderr=err)
  if result.returncode:put(E/'GIT_ARCHIVE_PENDING.json',dict(epoch=time.time(),phase='launch',exit_code=result.returncode));raise RuntimeError('Launch Git archive failed; training and monitor continue')
  print('LAUNCH_ARCHIVED_VIA7897',flush=True)
 except BaseException:
  put(E/('STARTUP_ERROR.json'if launched else'PREPARATION_ERROR.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=launched,automatic_repeat=False));raise
