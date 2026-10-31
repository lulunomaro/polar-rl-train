"""New routing/commands/typed-GO test only; no old full fixture or model read."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast, copy, hashlib, importlib.util, json, sys, time, traceback, types
import torch
N=Path(__file__).resolve().parent;P=N/'package';R=N/'reports'

def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(name):
 m=types.ModuleType(name);sys.modules[name]=m;return m

def main():
 put('SOURCE209_MIXED_CPU_ONCE_CONSUMED.json',dict(epoch=time.time(),model_raw_NPZ_SDK_GPU_remote_reads=0,scope='new disjoint reward routing, exact source lineage, commands and TaskGO'))
 rng=torch.random.get_rng_state().clone();groups=[]
 task=json.loads((P/'TASK209.json').read_bytes())
 assert H(P/'literal_original_methods.py')=='514822b6d86c02bb7501d04a2c63c04b46e3b0aac07e1de204111b70b42ac244'
 assert H(P/'literal_original_config.py')=='8d3403cfeff086966e736332e42db54c13124761a96b6d23fbdca8caf7b8ccd7'
 for p in P.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 groups.append('whole package Python parse and unchanged literal JUMP source hashes')
 sys.path[:0]=[str(P),str(P/'payload/job0/runtime/isaac/mod4')]
 for name in ('isaaclab','isaaclab.envs','isaaclab.envs.mdp','isaaclab.envs.mdp.commands'):mod(name)
 managers=mod('isaaclab.managers')
 class Base:
  def __init__(self,cfg,env):self.cfg=cfg;self._env=env
 class Term:
  def __init__(self,func,weight,params=None):self.func=func;self.weight=weight;self.params=params or {}
 managers.ManagerTermBase=Base;managers.RewardTermCfg=Term
 class Uniform(Base):
  def __init__(self,cfg,env):
   super().__init__(cfg,env);self.device='cpu';self.num_envs=env.num_envs;self.robot=env.scene['robot']
   self.vel_command_b=torch.zeros(self.num_envs,3);self.is_standing_env=torch.zeros(self.num_envs,dtype=torch.bool);self.is_heading_env=self.is_standing_env.clone()
   self.time_left=torch.full((self.num_envs,),12.);self.command_counter=torch.zeros(self.num_envs,dtype=torch.long)
  def _resample_command(self,ids):
   for k,name in enumerate(('lin_vel_x','lin_vel_y','ang_vel_z')):
    self.vel_command_b[ids,k]=torch.empty(len(ids)).uniform_(*getattr(self.cfg.ranges,name))
   self.is_standing_env[ids]=torch.rand(len(ids))<self.cfg.rel_standing_envs
   self.is_heading_env[ids]=False
  def _update_command(self):self.vel_command_b[self.is_standing_env]=0
 mod('isaaclab.envs.mdp.commands.velocity_command').UniformVelocityCommand=Uniform
 taskmod=mod('mod4_task')
 taskmod.height_cmd=lambda e:e._height
 mod('spring_nominal_sdk_readback').tensor=lambda v:v
 jumpmod=mod('jump194_sdk');jumpmod.JumpMod4Env=object
 jumpmod.configure=lambda cfg:cfg
 s=importlib.util.spec_from_file_location('mixed209_sdk',P/'mixed209_sdk.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 def env(n=80):
  return types.SimpleNamespace(num_envs=n,device='cpu',step_dt=.02,cfg=types.SimpleNamespace(seed=27),
   _height=torch.full((n,1),.25),scene={'robot':types.SimpleNamespace(data=types.SimpleNamespace(heading_w=types.SimpleNamespace(torch=torch.linspace(-1,1,n))))})
 e=env();flat=m.assignment(e);assert int(flat.sum())==8 and int((~flat).sum())==72 and torch.equal(e._mixed209_mode,(~flat).long())
 e20=env(20000);assert int(m.assignment(e20).sum())==2000
 for count in (1,64,81):
  try:m.assignment(env(count))
  except AssertionError:pass
  else:raise AssertionError('Non-exact10% batch was silently admitted')
 groups.append('persistent exact10/90 environment assignment and explicit mode0/mode1')
 calls=[]
 class Stateful:
  def __init__(self,cfg,env):self.resets=[]
  def __call__(self,env,amount):calls.append(amount);return torch.arange(env.num_envs,dtype=torch.float32)+amount
  def reset(self,ids):self.resets.append(ids.clone())
 cfg=Term(m.OriginalFlat209Term,2.,dict(original_func=Stateful,original_params={'amount':3.}))
 f=m.OriginalFlat209Term(cfg,e);got=f(e,Stateful,{'amount':3.});assert torch.equal(got[flat],(torch.arange(80)+3.)[flat]) and (got[~flat]==0).all()
 f.reset(torch.tensor([0,1,10]));assert len(f.original.resets)==1 and calls==[3.]
 e.original_jump_once=lambda:torch.linspace(-2,3,80)
 jr=m.original_jump209_rate(e)*.02
 assert (jr[flat]==0).all() and torch.allclose(jr[~flat],e.original_jump_once()[~flat])
 assert torch.allclose(got*.02*2.+jr,torch.where(flat,(torch.arange(80)+3.)*.04,e.original_jump_once()))
 groups.append('stateful ground reset and exact disjoint dt-once reward selection, including negative JUMP values')
 ranges=types.SimpleNamespace(lin_vel_x=(-1.5,1.5),lin_vel_y=(0.,0.),ang_vel_z=(-12.566370614359172,12.566370614359172),heading=None)
 config=types.SimpleNamespace(heading_command=False,rel_heading_envs=0.,rel_standing_envs=.1,resampling_time_range=(12.,16.),ranges=ranges)
 old={k:os.environ.get(k) for k in ('RM_SPIN_MAX_RAD_S','RM_SPIN_WORLD_PROGRESS_M_S')}
 os.environ['RM_SPIN_MAX_RAD_S']='12.566370614359172';os.environ['RM_SPIN_WORLD_PROGRESS_M_S']='.5'
 try:
  command=m.Mixed209Command(config,e);reference=m.DirectionalSpinCommand(copy.deepcopy(config),e)
  ids=torch.arange(80);fid=ids[flat];jid=ids[~flat]
  torch.manual_seed(473);reference._resample_command(fid)
  torch.manual_seed(473);command._resample_command(ids)
  assert torch.equal(command.vel_command_b[fid],reference.vel_command_b[fid])
  for name in ('is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed'):
   assert torch.equal(getattr(command,name)[fid],getattr(reference,name)[fid]),name
  assert (command.time_left[jid]==20).all() and command.cfg is config
  assert (e._height[fid]==.25).all() and ((e._height[jid]>=.12)&(e._height[jid]<=.15)).all()
  assert command.vel_command_b[jid,0].abs().max()<=2.1 and command.vel_command_b[jid,2].abs().max()<=2.
  before=command.vel_command_b[jid].clone()
  for i in range(1100):command._update_command()
  assert torch.equal(before,command.vel_command_b[jid]),'E0 dynamic update overwrote JUMP commands'
  assert not (command.is_pure_spin[jid]|command.is_moving_spin[jid]|command.is_standing_env[jid]).any()
  command._resample_command(torch.tensor([0,1,2,10,11]));assert torch.equal(e._mod4_mode_bit,e._mixed209_mode)
 finally:
  for k,v in old.items():
   if v is None:os.environ.pop(k,None)
   else:os.environ[k]=v
 groups.append('original E0 subset command values and dynamic flags unchanged; JUMP bounds/height/timer unaffected through22s of command updates')
 from mixed209_task_protocol import validate_go
 go=dict(run_id='new209',role_key='e0_72',source_model_SHA=task['source_SHA'],source_iteration=32066,input_Adam=642840,
  ground_envs=2000,jump_envs=18000,num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,
  nominal_gas_k_N_m=2000,preserve_learned_STD=True,max_parent_seconds=3900,exit_headroom_seconds=300,learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,
  literal_original_fudan_JUMP=True,original_E0_ground_reward=True,one_original_writer=True,full_actor_critic_STD_17Adam_restore_required=True,explicit_fresh_physics_replay_history=True)
 assert validate_go(go,'new209',task,101.)
 rejects=0
 for key,value in [('source_model_SHA','a'*64),('source_iteration',31984),('input_Adam',641200),('ground_envs',0),('jump_envs',20000),('policy_hz',100),('TGS',[32,16]),('physics_dt',.001),('preserve_learned_STD',False),('max_parent_seconds',7500),('save_deadline',7300.),('original_E0_ground_reward',False),('one_original_writer',False),('nominal_gas_k_N_m',3500),('run_id','old'),('full_actor_critic_STD_17Adam_restore_required',False)]:
  bad=copy.deepcopy(go);bad[key]=value
  try:validate_go(bad,'new209',task,101.)
  except AssertionError:rejects+=1
  else:raise AssertionError(key)
 groups.append('typed fullstate mixed TaskGO and16 counterexamples rejected')
 torch.random.set_rng_state(rng)
 assert torch.equal(torch.random.get_rng_state(),rng) and not torch.cuda.is_initialized()
 put('ROOT209_MIXED_SOURCE_AND_TaskGO_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,groups=groups,groups_passed=len(groups),TaskGO_negatives=rejects,
  maximum_command_update_steps=1100,CUDA_initialized=False,model_raw_NPZ_reference_SDK_GPU_remote_reads=0,
  fixture_is_synthetic_SOURCE_routing_not_physics=True,original_full_fixtures_not_replayed=True,global_RNG_restored=True,source_SHA=task['source_SHA']))
 print(json.dumps(dict(passed=True,groups=len(groups),rejected=rejects,CUDA=False)))

if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT209_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
