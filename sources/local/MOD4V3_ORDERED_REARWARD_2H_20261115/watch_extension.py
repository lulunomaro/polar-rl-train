"""Collect the queued continuation receipt, then run original five-minute monitoring."""
from pathlib import Path
import json,sys,time,subprocess,os,traceback,datetime
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
TZ=datetime.timezone(datetime.timedelta(hours=8))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):
 p=Path(p);tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8');os.replace(tmp,p)
def spawn(name,label):
 with(T/(label+'.log')).open('xb')as out,(T/(label+'_error.log')).open('xb')as err:child=subprocess.Popen([sys.executable,'-X','utf8','-B','-u',str(T/name)],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return child.pid
try:
 while True:
  c=connect()
  try:
   sf=c.open_sftp();names=sf.listdir(REMOTE)
   for name in ['EXTENSION_STATUS.json','EXTENSION_ERROR.json','CONTINUATION_INPUT.json','CONTINUATION_LAUNCH.json']:
    if name in names:
     with sf.open(REMOTE+'/'+name)as f:d=json.loads(f.read());put(E/name,d)
   if 'EXTENSION_ERROR.json'in names:raise RuntimeError('Remote continuation preparation failed; see preserved EXTENSION_ERROR.json')
   if 'CONTINUATION_LAUNCH.json'in names:
    with sf.open(REMOTE+'/PLAN.json')as f:put(T/'PLAN.json',json.loads(f.read()))
    sf.get(REMOTE+'/continuation_parent.pt',str(T/'weights/continuation_parent.pt'));put(E/'TRAIN_LAUNCH.json',read(E/'CONTINUATION_LAUNCH.json'));break
  finally:c.close()
  time.sleep(10)
 put(E/'MONITOR_LAUNCH.json',dict(epoch=time.time(),pid=spawn('monitor_run.py','monitor'),checkpoint_seconds=300))
 put(E/'FINISHER_LAUNCH.json',dict(epoch=time.time(),pid=spawn('finish_pipeline.py','pipeline'),total_budget_seconds=7200))
 while not(E/'training/FIRST_UPDATE.json').exists():
  if(E/'training/ERROR.json').exists():raise RuntimeError('Continuation PPO failed before first update')
  time.sleep(10)
 plan=read(T/'PLAN.json');first=read(E/'training/FIRST_UPDATE.json');restore=read(E/'training/RESTORE.json');assert first['actor_changed']and restore['actor_critic_STD_Adam_restored']and restore['optimizer_entries']==17
 start=first['epoch']-first['training_elapsed_seconds'];info=dict(actual_PPO_start_epoch=start,actual_PPO_start_local=datetime.datetime.fromtimestamp(start,TZ).isoformat(),planned_PPO_end_local=datetime.datetime.fromtimestamp(start+plan['training_round']['seconds'],TZ).isoformat(),total_budget_seconds=7200,cumulative_seconds_before=plan['cumulative_training_seconds_before'],remaining_phase_budget_seconds=plan['training_round']['seconds'],continuation_parent_sha256=plan['parent_sha256'],root_frozen_parent_sha256=plan['frozen_comprehensive_parent_sha256'],actor_changed=True,optimizer_entries=17,checkpoint_seconds=300)
 put(E/'TRAINING_STARTED_CONFIRMED.json',info)
 regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);reg['active_ordered_rearward_2h_training_20261115'].update(info,status='running_continuation');put(regpath,reg)
 with(T/'README.md').open('a',encoding='utf8')as f:f.write(chr(10)+'实际接续开训：'+info['actual_PPO_start_local']+'；预计PPO结束：'+info['planned_PPO_end_local']+'。完整学生SHA '+plan['parent_sha256']+'；17项Adam状态已恢复，actor已更新。'+chr(10))
 print('CONTINUATION_ACTUALLY_TRAINING '+json.dumps(info),flush=True)
 with(E/'ARCHIVE_LAUNCH.log').open('xb')as out,(E/'ARCHIVE_LAUNCH_ERROR.log').open('xb')as err:result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=out,stderr=err)
 if result.returncode:put(E/'GIT_LAUNCH_PENDING.json',dict(exit_code=result.returncode,training_continues=True))
except BaseException:
 put(E/'CONTINUATION_WATCH_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
