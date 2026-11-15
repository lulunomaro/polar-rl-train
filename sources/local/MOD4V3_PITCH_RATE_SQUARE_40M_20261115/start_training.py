"""Start one new2400s trial after the zero-update diagnosis, never replay old rounds."""
from pathlib import Path
import sys,json,hashlib,shlex,time,subprocess,datetime,os,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
launched=False
def put(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def spawn(name):
 with (T/(name+'.log')).open('xb')as out,(T/(name+'_error.log')).open('xb')as err:
  proc=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/(name+'.py'))],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)|getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0))
 return proc.pid
try:
 assert json.loads((E/'diagnostic_original/ROUGH_PROBE.json').read_text())['no_optimizer_updates']
 assert (E/'diagnostic_original/SAFE_CLOSED.json').exists() and (E/'ROOT_CAUSE.json').exists()
 assert json.loads((E/'PITCH_REWARD_REGRESSION.json').read_text())['passed']>=9
 assert P['training_round']['seconds']==2400 and P['pitch_stability']['pitch_rate_square_coefficient']==3.5 and not P['pitch_stability'].get('proposed_only_until_probe',True)
 c=connect()
 try:
  sf=c.open_sftp();index={}
  for path in [T/'PLAN.json',T/'launch.py']+[x for x in (T/'support').rglob('*')if x.is_file() and '__pycache__'not in x.parts and x.suffix!='.pyc']:
   rel=path.relative_to(T).as_posix();sf.put(str(path),REMOTE+'/'+rel);index[rel]=hashlib.sha256(path.read_bytes()).hexdigest()
  code="from pathlib import Path;import json,hashlib;root=Path("+repr(REMOTE)+");d="+repr(index)+";assert all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in d.items());assert hashlib.sha256((root/'parent_comprehensive.pt').read_bytes()).hexdigest()=="+repr(P['parent_sha256'])+";package=Path("+repr(P['package'])+");assets="+repr(P['asset_identity']['actual_training_assets'])+";assert all(hashlib.sha256((package/'assets'/k).read_bytes()).hexdigest()==v['sha256'] for k,v in assets.items());print(json.dumps(dict(verified_inputs=len(d),parent_sha256="+repr(P['parent_sha256'])+",frozen_assets_verified=True)))"
  verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));put(E/'TRAINING_INPUT_SHA256.json',dict(verification=verified,files=index))
  receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(REMOTE+'/launch.py')+' '+P['training_job']+' --kind train --num-envs 2048'));put(E/'TRAIN_LAUNCH.json',receipt);launched=True
 finally:c.close()
 put(E/'COLLECTOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run')));put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline'),no_additional_training=True))
 print('PPO_LAUNCHED '+json.dumps(receipt),flush=True)
 while not(E/'training/FIRST_UPDATE.json').exists():
  if(E/'training/ERROR.json').exists():raise RuntimeError('Actual PPO failed; see original ERROR.json; no relaunch')
  time.sleep(5)
 first=json.loads((E/'training/FIRST_UPDATE.json').read_text());restore=json.loads((E/'training/RESTORE.json').read_text());assert first['actor_changed']and restore['actor_critic_STD_Adam_restored'];pitch=first['terrain']['pitch_stability'];assert pitch['rate_square_coefficient']==3.5
 assert pitch['target_envs']==615 and first['optimizer_entries']==17
 start=first['epoch']-first['training_elapsed_seconds'];tz=datetime.timezone(datetime.timedelta(hours=8));result=dict(actual_PPO_start_local=datetime.datetime.fromtimestamp(start,tz).isoformat(),planned_end_local=datetime.datetime.fromtimestamp(start+2400,tz).isoformat(),parent_sha256=P['parent_sha256'],parent_iteration=25331,actor_changed=True,optimizer_entries=first['optimizer_entries'],new_round_seconds=2400,checkpoint_seconds=300,rate_square_coefficient=3.5,angle_square_coefficient=30.,automatic_extension=False,pitch= pitch)
 put(E/'TRAINING_STARTED_CONFIRMED.json',result)
 with(T/'README.md').open('a',encoding='utf8')as f:f.write('\n实际PPO开始：'+result['actual_PPO_start_local']+'；计划结束：'+result['planned_end_local']+'。首迭代actor已改变，完整17项Adam恢复，新角速度平方系数3.5已在原生奖励实际生效。\n')
 print('FIRST_UPDATE_CONFIRMED '+json.dumps(result),flush=True)
 with(E/'ARCHIVE_LAUNCH.log').open('wb')as out:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
 r.check_returncode();print('LAUNCH_ARCHIVED_VIA7897',flush=True)
except BaseException:
 put(E/'STARTUP_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),training_launched=launched,automatic_relaunch=False));raise
