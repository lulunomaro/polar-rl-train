"""Approved S2 D1+D2 only, on the frozen A0/1ms E0 task."""
from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope
import os,torch
from isaaclab.managers import EventTermCfg,SceneEntityCfg
from mod4_env import Mod4Env
import mod4_task as task
from sensor_mild_math import SensorCorruption,CHANNELS,PROFILES

def state(env):
 if not hasattr(env,'_sensor_mild'):
  env._sensor_mild=SensorCorruption(env.num_envs,env.device,env.cfg.seed,env.cfg.sensor_mild_profile)
 return env._sensor_mild
def reset_sensor(env,env_ids):
 state(env).reset(torch.arange(env.num_envs,device=env.device) if env_ids is None else env_ids)
def base_ang_vel(env,asset_cfg=SceneEntityCfg('robot')):
 return state(env).apply('base_ang_vel',task.mdp_obs.base_ang_vel(env,asset_cfg=asset_cfg),env.common_step_counter)
def projected_gravity(env,asset_cfg=SceneEntityCfg('robot')):
 return state(env).apply('projected_gravity',task.mdp_obs.projected_gravity(env,asset_cfg=asset_cfg),env.common_step_counter)
def leg_pos(env,asset_cfg,bias_key):
 assert bias_key=='_mod4_leg_bias' and task.OBS_DELAY_MAX==0 and getattr(env,bias_key,None) is None
 return state(env).apply('leg_pos',task.mdp_obs.joint_pos_rel(env,asset_cfg=asset_cfg),env.common_step_counter)
def joint_vel(env,asset_cfg,key):
 return state(env).apply(key,task.mdp_obs.joint_vel_rel(env,asset_cfg=asset_cfg),env.common_step_counter)

def configure_sensor(cfg,profile):
 assert profile in PROFILES and task.DR_OFF and task.OBS_DELAY_MAX==task.ACTION_DELAY_MAX==0
 cfg.sensor_mild_profile=profile;p=cfg.observations.policy
 p.base_ang_vel.func=base_ang_vel;p.projected_gravity.func=projected_gravity;p.leg_pos.func=leg_pos;p.leg_vel.func=joint_vel;p.wheel_vel.func=joint_vel
 assert all(getattr(p,k).noise is None for k in CHANNELS)
 cfg.events.sensor_mild_episode_bias=EventTermCfg(func=reset_sensor,mode='reset')

class SensorMod4Env(Mod4Env):
 def __init__(self,*a,**kw):
  assert not a and 'cfg' in kw
  configure_sensor(kw['cfg'],os.environ.get('RM_SENSOR_PROFILE','noise_bias_mild_v1'))
  super().__init__(**kw)
  assert sum(self.observation_manager.group_obs_dim['policy'])==35 and sum(self.observation_manager.group_obs_dim['critic'])==38

 def clean_policy(self):
  s=state(self);old=s.profile;s.profile='off'
  try:return self.observation_manager.compute_group('policy').clone()
  finally:s.profile=old

 def sensor_sdk_audit(self):
  s=state(self);tick=self.common_step_counter;counts=dict(s.draw_counts)
  actor=self.observation_manager.compute_group('policy').clone();critic=self.observation_manager.compute_group('critic').clone()
  actor2=self.observation_manager.compute_group('policy');assert torch.equal(actor,actor2) and counts==s.draw_counts
  clean=self.clean_policy();assert torch.equal(critic,self.observation_manager.compute_group('critic'))
  expected=clean.clone();offset=0
  for name,dims in zip(self.observation_manager.active_terms['policy'],self.observation_manager.group_obs_term_dim['policy']):
   width=int(dims[0])
   if name in CHANNELS and s.profile!='off':
    noise=s.cache[name][1];last=s.cache[name][0];assert bool((last==tick).all())
    scale=.5 if name=='base_ang_vel' else .1 if name in ('leg_vel','wheel_vel') else 1.
    expected[:,offset:offset+width]+=(noise+(s.bias if name=='leg_pos' else 0.))*scale
   offset+=width
  error=float((actor-expected).abs().max());assert error<=2e-6,error
  assert torch.equal(actor[:,:4],clean[:,:4]) and torch.equal(actor[:,14:16],clean[:,14:16]) and torch.equal(actor[:,22:],clean[:,22:])
  return dict(tick=int(tick),actor35=True,critic38_clean=True,command_lastaction_mode_wheel_slots_exact=True,formula_max_error=error,same_tick_draws_unchanged=True)

def install_sensor_save_contract(runner,env):
 """Called before the existing atomic bounded-save wrapper publishes its receipt."""
 original=runner.save
 def save(path,*a,**kw):
  original(path,*a,**kw);ck=cached_load(path,map_location='cpu',weights_only=False,purpose='runtime/isaac/mod4/sensor_a0_runtime.py:64')
  s=state(env);ck['sensor_DR_state']=s.state_dict();ck['sensor_recipe']=s.receipt()
  ck['sensor_resume_contract']='Full feedback RNG/cache preserved; new physical episode clears caches and samples its own episode bias. No PhysX exact resume claim.'
  ck['sensor_global_rng_state']=dict(cpu=torch.random.get_rng_state(),cuda=torch.cuda.get_rng_state_all())
  ck['sensor_command_DR_rng_state']={name:obj.get_state() for name,obj in vars(env.command_manager.get_term('twist')).items() if isinstance(obj,torch.Generator)}
  ck['sensor_physical_DR_rng_state']={name:obj.get_state() for name,obj in vars(env._mild_dr).items() if isinstance(obj,torch.Generator)}
  torch.save(ck,path)
 runner.save=save
