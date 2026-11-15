"""Launch the independently authorized7200s window once and verify native PPO."""
from pathlib import Path
import sys,json,hashlib,shlex,time,subprocess,datetime,os,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
launched=False

def put(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def spawn(name):
 with(T/(name+'.log')).open('xb')as out,(T/(name+'_error.log')).open('xb')as err:
  p=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/(name+'.py'))],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 return p.pid
try:
 probe=json.loads((E/'native_probe_ROUGH_PROBE.json').read_text());assert probe['passed']and probe['no_optimizer_updates']and probe['actor_identical']
 assert json.loads((E/'LOCAL_REGRESSION.json').read_text())['passed']==10
 assert P['training_round']['seconds']==7200 and P['cumulative_training_seconds_before']==0 and P['parent_sha256'].startswith('db6e9ccf')
 assert P['brake_distillation']['lambda_brake']==.25
 P['pitch_stability']['proposed_only_until_probe']=False;P['teacher_retention']['coefficient_schedule']+=';0.25 train-only first100ms high-stance/high-speed wheel coordination'
 put(T/'PLAN.json',P)
 c=connect()
 try:
  sf=c.open_sftp();sf.put(str(T/'PLAN.json'),REMOTE+'/PLAN.json')
  index=json.loads((E/'UPLOADED_INPUTS.json').read_text())['files'];index['PLAN.json']=hashlib.sha256((T/'PLAN.json').read_bytes()).hexdigest()
  for q in (T/'support').rglob('*'):
   if q.is_file()and q.suffix!='.pyc'and'__pycache__'not in q.parts:index[q.relative_to(T).as_posix()]=hashlib.sha256(q.read_bytes()).hexdigest()
  code="from pathlib import Path;import hashlib,json;root=Path("+repr(REMOTE)+");d="+repr(index)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256=d['parent_comprehensive.pt'])))"
  verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'TRAINING_INPUT_SHA256.json',dict(verification=verified,files=index))
  receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+P['training_job']+' --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt);launched=True
 finally:c.close()
 put(E/'COLLECTOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run')));put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline'),additional_training=False))
 print('PPO_PROCESS_LAUNCHED',receipt['pid'],flush=True)
 deadline=time.time()+600
 while not(E/'training/FIRST_UPDATE.json').exists():
  if(E/'training/ERROR.json').exists():raise RuntimeError('Native PPO failed; retain evidence; no automatic relaunch')
  if time.time()>deadline:raise RuntimeError('First update not observed in600s; preserve actual remote process for inspection')
  time.sleep(5)
 first=json.loads((E/'training/FIRST_UPDATE.json').read_text());restore=json.loads((E/'training/RESTORE.json').read_text());assert first['actor_changed']and restore['actor_critic_STD_Adam_restored']and first['optimizer_entries']==17
 pitch=first['terrain']['pitch_stability'];assert pitch['rate_square_coefficient']==.05 and pitch['prediction_coefficient']==0. and pitch['target_envs']==615 and pitch['velocity_fix_samples']>0
 start_epoch=first['epoch']-first['training_elapsed_seconds'];tz=datetime.timezone(datetime.timedelta(hours=8));confirmed=dict(actual_PPO_start_local=datetime.datetime.fromtimestamp(start_epoch,tz).isoformat(),planned_end_local=datetime.datetime.fromtimestamp(start_epoch+7200,tz).isoformat(),parent_sha256=P['parent_sha256'],parent_iteration=25331,actor_changed=True,optimizer_entries=17,requested_training_seconds=7200,checkpoint_seconds=300,automatic_extension=False,pitch=pitch)
 put(E/'TRAINING_STARTED_CONFIRMED.json',confirmed);print('FIRST_UPDATE_CONFIRMED',json.dumps(confirmed),flush=True)
 # Verify that real native PPO minibatches consumed causal wheel labels.
 while time.time()<deadline:
  p=E/'training/LATEST_PROGRESS.json'
  if p.exists():
   progress=json.loads(p.read_text());teacher=progress.get('teacher_retention',{})
   if teacher.get('pitch_brake_samples_cumulative',0)>0:
    put(E/'BRAKE_LOSS_NATIVE_CONFIRMED.json',dict(epoch=time.time(),iteration=progress['iteration'],teacher=teacher,training_elapsed_seconds=progress['training_elapsed_seconds']));print('NATIVE_BRAKE_LOSS_CONFIRMED',teacher.get('pitch_brake_samples_cumulative'),flush=True);break
  if(E/'training/ERROR.json').exists():raise RuntimeError('Native PPO failed while verifying brake labels')
  time.sleep(10)
 else:raise RuntimeError('Native brake labels not observed by600s; inspect existing process without extra training')
 note='2026-11-16新独立两小时俯仰修复已实际开训：'+confirmed['actual_PPO_start_local']+'，预计完整迭代结束约'+confirmed['planned_end_local']+'；从冻结db6/iter25331完整恢复，新增SCUT稠密姿态、水平速度奖励修复和训练期急停轮协调示范。每5分钟完整PT与固定回放，默认不自动晋升。见sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116/README.md。'
 with(T/'README.md').open('a',encoding='utf8')as f:f.write('\n实际开始：'+confirmed['actual_PPO_start_local']+'；预计结束：'+confirmed['planned_end_local']+'。首迭代actor已改变，17项Adam完整恢复，原生PPO已实际使用轮协调标签。\n')
 for path in [R/'AGENTS.md',R.parent/'AGENTS.md']:
  text=path.read_text(encoding='utf8');head,sep,rest=text.partition('\n');path.write_text(head+sep+'\n'+note+'\n'+rest,encoding='utf8')
 (E/'WORKSPACE_AGENTS_SNAPSHOT.md').write_text((R.parent/'AGENTS.md').read_text(encoding='utf8'),encoding='utf8')
 path=R/'docs/DR_TRAINING_INDEX_20261111.md';text=path.read_text(encoding='utf8');head,sep,rest=text.partition('\n');path.write_text(head+sep+'\n## 2026-11-16：SCUT奖励与急停轮协调两小时训练\n\n'+note+'\n'+rest,encoding='utf8')
 subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','launch'],cwd=R,check=True)
 print('START_AND_REPAIR_ARCHIVED',flush=True)
except Exception:
 put(E/'START_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=launched,automatic_relaunch=False));raise

# Existing job acknowledgement uses confirm_running_start.py; never rerun this launcher.
