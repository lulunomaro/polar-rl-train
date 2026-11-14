"""Exactly one authorized additional2h window after the current physical work closes."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,shlex,subprocess,sys,time,traceback
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
PREVIOUS=T.parent/'MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113'
JOB_NAME='train120m_height_continue_r1'
TZ=__import__('datetime').timezone(__import__('datetime').timedelta(hours=8))
def put(path,data):
 path=Path(path);temporary=path.with_name(path.name+'.partial');temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');os.replace(temporary,path)
def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def spawn(script,logname):
 with (T/(logname+'.log')).open('xb') as out,(T/(logname+'_error.log')).open('xb') as err:
  child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/script)],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 return child.pid

def make_plan(selected,checkpoint):
 plan=copy.deepcopy(read(T/'PLAN_TEMPLATE.json'));weight=PREVIOUS/'weights'/selected['source_file'];sha=hashlib.sha256(weight.read_bytes()).hexdigest();assert sha==selected['sha256']
 plan['parent_sha256']=sha;plan['parent_iteration']=int(checkpoint['iter']);plan['teacher_retention']['student_initial_sha256']=sha;plan['teacher_retention']['student_initial_iteration']=int(checkpoint['iter'])
 plan['specialist_transfer']['frozen_student_parent_sha256']=sha;plan['continuation']['state']='pinned_complete_prior_round_PPO';plan['current_repair']['starting_checkpoint']=dict(source=str(weight),sha256=sha,selection=selected)
 assert plan['training_round']['seconds']==7200 and plan['cumulative_training_seconds_before']==0
 assert not plan['online_success_replay']['fresh_pool_for_repaired_round']
 return plan

def publish_active(started):
 registry=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(registry);sid='high_stance_continue_2h_20261114';plan=read(T/'PLAN.json')
 reg['queued_training']=[item for item in reg.get('queued_training',[]) if item.get('id')!=sid]
 reg['active_training']=dict(id=sid,title='高站姿追加两小时接训',source_directory=T.relative_to(R).as_posix(),plan=(T/'PLAN.json').relative_to(R).as_posix(),remote_job=plan['root']+'/'+JOB_NAME,actual_start=started['actual_PPO_start_local'],planned_end=started['planned_PPO_end_local'],parent_sha256=plan['parent_sha256'],keep_teacher_sha256=plan['teacher_retention']['keep_teacher_sha256'],budget_seconds=7200,checkpoint_every_seconds=300,automatic_extension=False)
 reg['current_training_status']='active: additional7200s high-stance continuation; prior round closed; exact recipe and20stratum replay restored';reg['updated_at_epoch']=time.time();registry.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\r\n')
 entry='\n## 2026-11-14 高站姿追加两小时：实际接续\n\n实际PPO '+started['actual_PPO_start_local']+'至预算约'+started['planned_PPO_end_local']+'；完整PPO/Adam/STD与20组成功池恢复。原高站姿指导、fullDR、平地/rough配比及速度奖励沿用；每5分钟完整PT和检查。记录：'+T.relative_to(R).as_posix()+'/README.md。\n'
 for file in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',registry.parent/'README.md']:
  with file.open('a',encoding='utf8',newline='\r\n') as out:out.write(entry)

if __name__=='__main__':
 training_launched=False
 try:
  assert not (E/'TRAIN_LAUNCH.json').exists(),'This additional window already launched'
  put(E/'WAITING_FOR_CURRENT_ROUND.json',dict(epoch=time.time(),state='queued_not_training',previous=str(PREVIOUS),additional_PPO_seconds=7200,one_additional_round_only=True))
  print('QUEUED_ONE_ADDITIONAL7200S_WAITING_CURRENT_PHYSICAL_EVALUATIONS',flush=True)
  required=[PREVIOUS/'evidence/training/SAFE_CLOSED.json',PREVIOUS/'evidence/post_native_recovery_r2/COMPLETE.json',PREVIOUS/'DECISION.json']
  while not all(file.exists() for file in required):
   if (PREVIOUS/'evidence/training/ERROR.json').exists() or (PREVIOUS/'evidence/PIPELINE_RECOVERY_R2_ERROR.json').exists():raise RuntimeError('Current round has not completed its physical work; see original error')
   time.sleep(10)
  assert read(PREVIOUS/'evidence/post_native_recovery_r2/COMPLETE.json')['all_closed']
  selected=read(PREVIOUS/'weights/SELECTED_STUDENT.json');weight=PREVIOUS/'weights'/selected['source_file'];checkpoint=torch.load(weight,map_location='cpu',weights_only=False)
  replay=checkpoint['success_replay_state'];assert replay['version']==2 and len(replay['counts'])==20
  plan=make_plan(selected,checkpoint);put(T/'PLAN.json',plan)
  previous_plan=read(PREVIOUS/'PLAN.json');source_remote=previous_plan['root']+'/train120m_repair_r1/'+selected['source_file']
  put(T/'PROVENANCE.json',dict(source_recipe=str(PREVIOUS/'PLAN.json'),source_parent_remote=source_remote,parent_sha256=plan['parent_sha256'],requested_additional_seconds=7200,comprehensive_teacher_sha256=plan['teacher_retention']['keep_teacher_sha256'],selected_previous=selected))
  put(E/'INHERITED_REPLAY_BASELINE.json',dict(source_sha256=plan['parent_sha256'],version=2,accepted_whole_successes=replay['accepted'],counts=list(replay['counts']),note='Inherited old successes; never report these as new successes in this additional round'))
  put(E/'ADMISSION_REUSED.json',dict(epoch=time.time(),source_reuse=read(E/'SOURCE_REUSE.json'),no_new_physics_probe=True,parent_sha256=plan['parent_sha256'],prior_paired_native_complete=True,new_budget_seconds=7200))
  spec=importlib.util.spec_from_file_location('additional_height_remote',T/'remote_run.py');remote=importlib.util.module_from_spec(spec);spec.loader.exec_module(remote);root=plan['root'];c=remote.connect()
  try:
   # The inherited single-GPU launcher independently checks ownership again.
   while remote.execute(c,'nvidia-smi --query-compute-apps=pid --format=csv,noheader').strip():time.sleep(5)
   create="from pathlib import Path;import json;root=Path("+repr(root)+");assert not root.exists();root.mkdir();assert str(root.resolve()).startswith('/mnt/mod4_windows_data/MOD4_training_data/rl_candidates/');print(json.dumps(dict(root=str(root.resolve()),created=True)))"
   put(E/'REMOTE_DIRECTORY.json',json.loads(remote.execute(c,plan['python']+' -B -c '+shlex.quote(create))))
   sf=c.open_sftp();made={root};index={}
   def mkdir(path):
    if path in made:return
    parent=path.rsplit('/',1)[0]
    if parent not in made:mkdir(parent)
    try:sf.mkdir(path)
    except OSError:sf.stat(path)
    made.add(path)
   files=[T/'PLAN.json',T/'launch.py',T/'teacher_movement_balanced_demos.pt',T/'high_stance_comprehensive_anchors.pt',T/'comprehensive_keep_teacher.pt']+[f for f in (T/'support').rglob('*') if f.is_file() and '__pycache__' not in f.parts]
   for file in files:
    rel=file.relative_to(T).as_posix();dest=root+'/'+rel;mkdir(dest.rsplit('/',1)[0]);sf.put(str(file),dest);index[rel]=hashlib.sha256(file.read_bytes()).hexdigest()
   with sf.open(root+'/UPLOADED_INPUT_SHA256.json','w') as out:out.write(json.dumps(index))
   code="from pathlib import Path;import json,hashlib,shutil;root=Path("+repr(root)+");source=Path("+repr(source_remote)+");expected="+repr(plan['parent_sha256'])+";assert hashlib.sha256(source.read_bytes()).hexdigest()==expected;shutil.copyfile(source,root/'frozen_best_parent.pt');files=json.loads((root/'UPLOADED_INPUT_SHA256.json').read_text());assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in files.items());print(json.dumps(dict(parent_sha256=expected,verified_inputs=len(files))))"
   put(E/'UPLOADED_INPUTS.json',dict(files=index,verified=json.loads(remote.execute(c,plan['python']+' -B -c '+shlex.quote(code)))))
   launch=json.loads(remote.execute(c,plan['python']+' -B '+shlex.quote(root+'/launch.py')+' '+JOB_NAME+' --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',launch);training_launched=True
  finally:c.close()
  put(E/'MONITOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run.py','monitor'),interval_seconds=300,full_PT=True))
  while not (E/'training/FIRST_UPDATE.json').exists():
   if (E/'training/ERROR.json').exists():raise RuntimeError('New round failed before first update; original error retained')
   time.sleep(5)
  first=read(E/'training/FIRST_UPDATE.json');restore=read(E/'training/RESTORE.json');startup=read(E/'training/TEACHER_RETENTION_STARTUP.json');assert first['actor_changed'] and restore['actor_critic_STD_Adam_restored']
  assert startup['online_success_replay']['frames_by_stratum']==list(replay['counts'])
  start=first['epoch']-first['training_elapsed_seconds'];clock=__import__('datetime').datetime;started=dict(actual_PPO_start_epoch=start,actual_PPO_start_local=clock.fromtimestamp(start,TZ).isoformat(),planned_PPO_end_local=clock.fromtimestamp(start+7200,TZ).isoformat(),actor_changed=True,optimizer_entries=first['optimizer_entries'],restored_replay_version=2,inherited_successes=replay['accepted'],budget_seconds=7200,parent_sha256=plan['parent_sha256'])
  put(E/'TRAINING_STARTED_CONFIRMED.json',started)
  with (T/'README.md').open('a',encoding='utf8') as out:out.write('\n## 追加轮实际开训\n\n实际PPO '+started['actual_PPO_start_local']+'，预算约到'+started['planned_PPO_end_local']+'。完整actor/critic/STD/Adam和20组成功池恢复；首个完整PT已保存。父SHA '+plan['parent_sha256']+'。\n')
  print('ADDITIONAL2H_ACTUALLY_UPDATED '+json.dumps(started),flush=True)
  # Git handoff is after training starts; archiving never holds the GPU idle.
  while not (PREVIOUS/'evidence/PIPELINE_RECOVERY_R2_COMPLETE.json').exists():
   if (PREVIOUS/'evidence/PIPELINE_RECOVERY_R2_ERROR.json').exists():
    put(E/'GIT_ARCHIVE_PENDING.json',dict(epoch=time.time(),reason='Previous archive needs attention; new training and its monitoring continue',previous_error=str(PREVIOUS/'evidence/PIPELINE_RECOVERY_R2_ERROR.json')));break
   time.sleep(10)
  if (PREVIOUS/'evidence/PIPELINE_RECOVERY_R2_COMPLETE.json').exists():
   publish_active(started)
   with (E/'ARCHIVE_LAUNCH.log').open('xb') as out,(E/'ARCHIVE_LAUNCH_ERROR.log').open('xb') as err:result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
   if result.returncode:put(E/'GIT_ARCHIVE_PENDING.json',dict(epoch=time.time(),phase='launch',exit_code=result.returncode,training_continues=True))
   else:print('ADDITIONAL2H_LAUNCH_ARCHIVED',flush=True)
 except BaseException:
  put(E/('CONTINUATION_RECOVERY_R2_ERROR.json' if training_launched else 'LAUNCH_RECOVERY_R2_ERROR.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=training_launched,no_automatic_repeat=True));raise
