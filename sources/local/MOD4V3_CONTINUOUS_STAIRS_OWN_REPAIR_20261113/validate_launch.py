"""Read back the first complete own-recipe update, then archive the launch evidence."""
from pathlib import Path
import sys,time,json,hashlib,subprocess,traceback,datetime,os
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';P=json.loads((T/'PLAN.json').read_text(encoding='utf8'))
def put(name,data):(E/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 while not (E/'TRAIN_LAUNCH.json').exists():
  if (E/'LAUNCH_ERROR.json').exists():raise RuntimeError('Native probe/launch failed; inspect original preserved evidence')
  time.sleep(3)
 for name in ('monitor.log','monitor_error.log'):
  path=T/name
  if path.exists():path.rename(E/('PRELAUNCH_R2_'+name.replace('.log','.txt')))
 with (T/'monitor.log').open('wb') as out,(T/'monitor_error.log').open('wb') as err:
  monitor=subprocess.Popen([sys.executable,'-X','utf8','-u',str(T/'monitor_run.py')],cwd=R,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 put('MONITOR_LAUNCH.json',{'epoch':time.time(),'pid':monitor.pid})
 while not ((E/'training/FIRST_UPDATE.json').exists() and (T/'weights/model_first_complete.pt').exists()):
  if (E/'training/ERROR.json').exists():raise RuntimeError('Native main run failed; original error retained')
  if monitor.poll() is not None:raise RuntimeError('Collector exited before first complete checkpoint')
  time.sleep(3)
 first=json.loads((E/'training/FIRST_UPDATE.json').read_text(encoding='utf8'));restore=json.loads((E/'training/RESTORE.json').read_text(encoding='utf8'));file=T/'weights/model_first_complete.pt';d=torch.load(file,map_location='cpu',weights_only=False);parent=torch.load(T/'weights/parent_iter24692.pt',map_location='cpu',weights_only=False)
 assert restore['source_sha256']==P['parent_sha256'] and restore['iteration']==24692 and restore['optimizer_entries']==17
 assert d['iter']==24693 and len(d['optimizer_state_dict']['state'])==17
 assert d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78 and d['actor_state_dict']['mlp.6.weight'].shape[0]==6
 assert d['reward_recipe']['weights']['track_lin_vel_xy_square']==-1.5 and d['reward_recipe']['lin_vel_xy_square_sigma']==1. and d['reward_recipe']['weights']['track_lin_vel_xy']==1.2
 assert d['continuous_stair']['extra_reward']==P['continuous_stair']['extra_reward']
 assert abs(d['learning_rate']-3e-5)<1e-12
 actor_change=max(float((value-parent['actor_state_dict'][key]).abs().max()) for key,value in d['actor_state_dict'].items());assert actor_change>0
 steps=[float(x['step']) for x in d['optimizer_state_dict']['state'].values()]
 deltas=[float(v['step'])-float(parent['optimizer_state_dict']['state'][k]['step']) for k,v in d['optimizer_state_dict']['state'].items()]
 start=first['epoch']-first['training_elapsed_seconds'];tz=datetime.timezone(datetime.timedelta(hours=8))
 result={'epoch':time.time(),'parent_iteration':24692,'parent_sha256':P['parent_sha256'],'first_new_iteration':d['iter'],'first_complete_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'complete_PPO':True,'optimizer_entries':17,'optimizer_restored':True,'optimizer_step_increment_min':min(deltas),'optimizer_step_increment_max':max(deltas),'actor35_critic78_action6':True,'max_actor_parameter_change':actor_change,'own_speed_reward':{'square':-1.5,'sigma':1.,'exponential':1.2},'own_stair_shaping_restored':True,'actual_flat_preservation':first['terrain']['flat_preservation'],'actual_course_groups':first['terrain']['course_groups'],'training_start_local':datetime.datetime.fromtimestamp(start,tz).isoformat(),'planned_training_end_local':datetime.datetime.fromtimestamp(start+2400,tz).isoformat(),'seconds':2400,'claim':'Launch and update verified; no skill improvement claimed before fixed replay'}
 put('LAUNCH_VALIDATION.json',result)
 with (T/'README.md').open('a',encoding='utf8') as f:f.write('\n## 实际启动\n\n本轮PPO于'+result['training_start_local']+'开始，预计'+result['planned_training_end_local']+'结束2400秒及最后正常保存。首个完整更新iter24693，父完整Adam/RNG和35/78/6已读回核验；原速度奖励和自有登阶分数实际生效，平地保留205环境/6项目标。每5分钟完整保存与回放继续。\n')
 print(json.dumps(result,ensure_ascii=False),flush=True)
 with (E/'ARCHIVE_LAUNCH.log').open('wb') as log:rc=subprocess.run([sys.executable,'-X','utf8',str(T/'archive_run.py'),'--phase','launch'],cwd=R,stdout=log,stderr=subprocess.STDOUT).returncode
 if rc:raise RuntimeError('Launch archive failed; inspect log and retry existing objects only')
 put('LAUNCH_HANDLED.json',{'epoch':time.time(),'monitor_pid':monitor.pid,'launch_verified':True,'archive_complete':True})
 print('OWN_RECIPE_LAUNCH_VALIDATED_AND_ARCHIVED',flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('LAUNCH_HANDLING_ERROR.json',{'epoch':time.time(),'traceback':traceback.format_exc()});raise
