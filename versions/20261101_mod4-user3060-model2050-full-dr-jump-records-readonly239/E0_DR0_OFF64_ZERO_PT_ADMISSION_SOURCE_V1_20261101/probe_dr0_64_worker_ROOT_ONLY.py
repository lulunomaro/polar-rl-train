"""ROOT-only64env/8control actual physical off probe;no NN/model/PPO."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
N=Path(__file__).resolve().parent
from dr0_contract import apply_env
from dr0_actual_readback import collect
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();task=read(a.task)
 assert task['kind']=='DR0_OFF64_ZERO_PT_ORIGINAL_PHYSICAL_ADMISSION_V1' and task['num_envs']==64 and task['controls']==8
 assert task['actual_parent_private_validation_EX_held'] and task['NN_model_reads']==0 and task['PPO_updates']==0
 R=Path(task['new_runtime_root']);M=R/'isaac/mod4';assert R.resolve().is_relative_to(N.resolve())
 for r in task['off_modules']:
  b=(M/Path(r['relative']).name).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in task['original_env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')});apply_env(os.environ)
 os.environ.update(RM_MOD4_USD=str(R/'assets/robot.usd'),MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4_EXPERT213_JOB_ROOT=str(N),MOD4_EXPERT213_KIT_STORAGE_ROOT=str(N/'kit_isolation'))
 store=N/'kit_isolation';store.mkdir(exist_ok=False);(store/'data').mkdir();(store/'DerivedDataCache').mkdir();(store/'data/user.config.json').write_text('{}')
 sys.path[:0]=[str(N),str(M),str(R)]
 from launcher213 import IsolatedAppLauncher213
 q=argparse.ArgumentParser();IsolatedAppLauncher213.add_app_launcher_args(q);launch_args=q.parse_args(['--headless','--device','cuda:0']);app=IsolatedAppLauncher213(launch_args).app
 real=None
 try:
  import torch
  import mod4_task
  from chassis_pd_training_env import ChassisPDMod4Env
  cfg=mod4_task.Mod4EnvCfg();cfg.scene.num_envs=64;cfg.seed=task['seed']
  assert cfg.terminations.closure.params['threshold']==.002 and cfg.terminations.mimic.params['threshold'] in (.05,.01)
  before=cfg.terminations.mimic.params['threshold'];cfg.terminations.mimic.params['threshold']=.01
  put(N/'BEFORE_CONSTRUCTOR_DR0_GUARDS.json',dict(epoch=time.time(),original_mimic=before,effective_mimic=.01,closure=.002,other_cfg_unmodified=True))
  real=ChassisPDMod4Env(cfg=cfg);real.reset()
  before_snapshot=collect(real,True);put(N/'DR064_ACTUAL_NOMINAL_BEFORE_CONTROLS.json',before_snapshot)
  tick=int(real._integrated_contact.tick);fb=int(real._feedback_100hz_tick);queues=dict(real._physics_action_delay.calls);dts=[];terms={}
  original=real.reward_manager.compute
  def reward(*aa,**kw):
   dt=kw.get('dt',aa[0] if aa else None);assert dt==.02;dts.append(dt);return original(*aa,**kw)
  real.reward_manager.compute=reward
  try:
   zero=torch.zeros((64,6),device=real.device)
   for i in range(8):
    value=real.step(zero);assert bool(torch.isfinite(value[1]).all())
    for name in real.termination_manager.active_terms:terms[name]=terms.get(name,0)+int(real.termination_manager.get_term(name).sum())
  finally:real.reward_manager.compute=original
  assert int(real._integrated_contact.tick)-tick==64 and int(real._feedback_100hz_tick)-fb==16 and dts==[.02]*8
  assert {k:real._physics_action_delay.calls[k]-queues[k] for k in ('legs','wheels')}=={'legs':64,'wheels':64}
  after=collect(real,True);put(N/'DR064_ACTUAL_NOMINAL_AFTER_CONTROLS.json',after)
  put(N/'ACTUAL_DR064_RESULT.json',dict(epoch=time.time(),passed=True,num_envs=64,controls=8,physics=64,feedback=16,
   original_termination_counts=terms,alloff_before_after=True,effective_mimic=.01,closure=.002,
   source_model_byte_reads=0,source_model_decodes=0,NN_constructors=0,PPO_updates=0,account_writes=0,
   Fudan_reward_not_executed_or_qualified_by_this_physical_probe=True,skill='UNKNOWN'))
 except BaseException:
  put(N/'ACTUAL_DR064_WORKER_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
 finally:
  if real is not None:real.close()
  put(N/'DR064_APPCLOSING_BEFORE_CLOSE.json',dict(epoch=time.time(),model_read_counts=[0,0],result_written_before_Appclose=True))
  app.close()
if __name__=='__main__':main()

