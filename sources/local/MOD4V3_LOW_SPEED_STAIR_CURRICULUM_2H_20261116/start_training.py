"""Launch this authorized7200s run exactly once after native admission; confirm real PPO."""
from pathlib import Path
import sys,json,time,hashlib,shlex,subprocess,os,traceback,datetime
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE

def put(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,path)

def spawn(name):
 out=(T/(name+'.log')).open('xb');err=(T/(name+'_error.log')).open('xb')
 process=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/(name+'.py'))],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt'else 0)
 out.close();err.close();return process.pid

launched=False
try:
 assert not(E/'TRAIN_LAUNCH.json').exists(),'Existing training receipt; inspect its PID instead of relaunching'
 probe=json.loads((E/'native_probe_r6_ROUGH_PROBE.json').read_text());closed=json.loads((E/'native_probe_r6_SAFE_CLOSED.json').read_text())
 assert probe['passed']and probe['no_optimizer_updates']and closed['scene_closed']
 assert probe['closure_2mm_diagnostic_only']and not probe['closure_2mm_reset_enabled']
 assert json.loads((E/'LOCAL_CURRICULUM_CHECKS.json').read_text())['passed']
 assert P['parent_iteration']==25362 and P['training_round']['seconds']==7200
 assert hashlib.sha256((T/'weights/parent_comprehensive.pt').read_bytes()).hexdigest()==P['parent_sha256']==P['teacher_retention']['keep_teacher_sha256']
 c=connect()
 try:
  probe_pid=json.loads((E/'NATIVE_PROBE_R6_LAUNCH.json').read_text())['pid']
  wait_code="from pathlib import Path;import time,json;pid="+str(probe_pid)+";name="+repr(P['probe_job'])+"\nfor _ in range(30):\n p=Path('/proc')/str(pid)/'cmdline'\n if not p.exists() or name not in p.read_bytes().decode(errors='ignore'):break\n time.sleep(1)\nelse:raise RuntimeError('Probe process still closing; preserve its PID')\nprint(json.dumps(dict(probe_process_closed=True)))"
  execute(c,P['python']+' -B -c '+shlex.quote(wait_code))
  uploaded=json.loads((E/'UPLOADED_INPUTS_R6.json').read_text())['files']
  for name,sha in uploaded.items():
   local=T/('weights/parent_comprehensive.pt'if name=='parent_comprehensive.pt'else name)
   assert hashlib.sha256(local.read_bytes()).hexdigest()==sha,'Source changed after admission: '+name
  code="from pathlib import Path;import hashlib,json;root=Path("+repr(REMOTE)+");inputs="+repr(uploaded)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in inputs.items());print(json.dumps(dict(input_files_verified=len(inputs),parent_sha256="+repr(P['parent_sha256'])+")))"
  put(E/'TRAINING_INPUT_SHA256.json',json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code))))
  receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+P['training_job']+' --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt);launched=True
 finally:c.close()
 put(E/'COLLECTOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run')))
 put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline'),additional_training=False))
 print('PPO_PROCESS_LAUNCHED',receipt['pid'],flush=True)
 deadline=time.time()+900
 while not(E/'training/FIRST_UPDATE.json').exists():
  if(E/'training/ERROR.json').exists():raise RuntimeError('PPO error; inspect original evidence without automatic restart')
  if time.time()>deadline:raise RuntimeError('First update not observed within900s; inspect existing process without relaunch')
  time.sleep(5)
 first=json.loads((E/'training/FIRST_UPDATE.json').read_text());restore=json.loads((E/'training/RESTORE.json').read_text())
 assert first['actor_changed']and first['optimizer_entries']==17 and restore['actor_critic_STD_Adam_restored']and restore['iteration']==25362
 groups=first['terrain']['course_groups'];assert groups==P['expected_env_groups']
 course=first['terrain']['single_step_curriculum'];assert sum(course['mastered_population'])==819
 teacher=first['teacher_retention'];assert teacher['keep_teacher_sha256']==P['parent_sha256']and teacher['keep_teacher_max_parameter_change']==0. and teacher['last']['curriculum_teacher_samples']==0
 assert teacher['last']['teacher_keep_samples']>0
 clock=json.loads((E/'training/TRAINING_CLOCK.json').read_text());start=clock['epoch'];tz=datetime.timezone(datetime.timedelta(hours=8))
 assert first['terrain']['closure_contract']['closure_2mm_reset_enabled']is False
 confirmed=dict(epoch=time.time(),remote_pid=receipt['pid'],actual_PPO_start_local=datetime.datetime.fromtimestamp(start,tz).isoformat(),planned_end_local=datetime.datetime.fromtimestamp(start+7200,tz).isoformat(),requested_training_seconds=7200,parent_sha256=P['parent_sha256'],parent_iteration=25362,first_updated_iteration=first['iteration'],actor_changed=True,optimizer_entries=17,course_groups=groups,heights_m=course['heights_m'],initial_mastered_population=course['mastered_population'],teacher_sha256=teacher['keep_teacher_sha256'],teacher_curriculum_samples=0,checkpoint_seconds=300,automatic_extension=False,automatic_promotion=False,native_probe_no_optimizer=True,closure_2mm_diagnostic_only=True,solver="TGS32/4")
 put(E/'TRAINING_STARTED_CONFIRMED.json',confirmed);print('FIRST_UPDATE_CONFIRMED',json.dumps(confirmed),flush=True)
 note='2026-11-16逐环境低速单台阶课程两小时已实际开训：'+confirmed['actual_PPO_start_local']+'，预计最后完整迭代结束约'+confirmed['planned_end_local']+'。从当前采用c874/iter25362完整PPO和17项Adam续训；819环境从5cm独立升到7/9/11/13/15/17/19/20cm，实际入阶速度与双轮接触/车身越边/0.4s稳定合格才升级。3次失败降级、15%低级复习；1229保留平地/崎岖环境由当前c874教师约束，课程环境无旧高速台阶/高站姿BC。每5分钟完整PT与固定回放；2mm仅诊断、不reset、不整轮停训，沿用TGS32/4与原有数值保护；7200s上限，无自动延长/晋升。见sources/local/MOD4V3_LOW_SPEED_STAIR_CURRICULUM_2H_20261116/README.md。'
 for file in [R/'AGENTS.md',R.parent/'AGENTS.md']:
  text=file.read_text(encoding='utf-8-sig');file.write_text('## 2026-11-16 最新训练：逐环境低速单台阶课程\n\n'+note+'\n\n'+text,encoding='utf8')
 put(E/'PROJECT_MEMORY_UPDATE.json',dict(epoch=time.time(),note=note,current_adopted_model_unchanged=True))
 (E/'WORKSPACE_AGENTS_SNAPSHOT.md').write_text((R.parent/'AGENTS.md').read_text(encoding='utf8'),encoding='utf8')
 index=R/'docs/DR_TRAINING_INDEX_20261111.md'
 if index.exists():index.write_text('## 2026-11-16 逐环境低速台阶课程\n\n'+note+'\n\n'+index.read_text(encoding='utf8'),encoding='utf8')
 with(T/'README.md').open('a',encoding='utf8')as f:f.write('\n实际开训：'+confirmed['actual_PPO_start_local']+'；预计结束：'+confirmed['planned_end_local']+'；PID '+str(receipt['pid'])+'。首个actor已实际更新，17项Adam完整恢复。\n')
 with(E/'ARCHIVE_LAUNCH.log').open('wb')as log:
  result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('PPO is running; launch archive pending; inspect ARCHIVE_LAUNCH.log without relaunch')
 print('START_AND_SOURCE_ARCHIVED',flush=True)
except Exception:
 put(E/'START_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=launched,automatic_relaunch=False));raise
