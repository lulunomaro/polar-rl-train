from pathlib import Path
import torch,json,hashlib,inspect,ast,copy
import wave50_route_runtime as previous
from wave50_lifetime_state import PROFILE,KEY,FIELDS,IDENTITY,validate,identity,evaluate
PARENT=None;PARENT_SHA=None
def source_sha(function):return hashlib.sha256(ast.unparse(ast.parse(inspect.getsource(function))).encode()).hexdigest()
def configure_retention(cfg):
 global PARENT,PARENT_SHA
 previous.configure_retention(cfg);assert cfg.episode_length_s==20.
 PARENT=cfg.terminations.time_out.func;PARENT_SHA=source_sha(PARENT)
 assert PARENT.__name__=='time_out' and cfg.terminations.time_out.time_out
 cfg.terminations.time_out.func=time_out
def bind(env):
 route=previous.bind(env);n=env.num_envs;device=env.device
 assert PARENT_SHA and abs(float(env.step_dt)-.01)<1e-12 and int(env.max_episode_length)==2000
 s=getattr(env,'_wave50_lifetime_state',None)
 metadata=dict(version=1,profile=PROFILE,num_envs=n,no_new_rng=True,step_dt_s=.01,Wave_seconds=40.,other_seconds=20.,route_profile=route['profile'],assignment_sha256=route['assignment_sha256'],entry_map_sha256=route['entry_map_sha256'],entry_origin_sha256=route['entry_origin_sha256'],parent_timeout_source_sha256=PARENT_SHA)
 if s is None:
  s=dict(metadata,wave_mask=torch.zeros(n,dtype=torch.bool,device=device),bound_episode=torch.full((n,),-1,dtype=torch.long,device=device),limit_steps=torch.full((n,),2000,dtype=torch.long,device=device));env._wave50_lifetime_state=s
 assert identity(s)==identity(metadata)
 changed=s['bound_episode']!=route['bound_episode'];s['wave_mask'][changed]=route['wave_mask'][changed];s['bound_episode'][changed]=route['bound_episode'][changed];s['limit_steps'][changed]=torch.where(s['wave_mask'][changed],4000,2000)
 validate(s,n);assert torch.equal(s['wave_mask'],route['wave_mask']) and torch.equal(s['bound_episode'],env._e1_episode);return s
def time_out(env):
 assert PARENT is not None
 old=PARENT(env);assert torch.equal(old,env.episode_length_buf>=env.max_episode_length)
 return evaluate(env.episode_length_buf,bind(env),old)
def state_dict(env,refresh=False):
 s=bind(env) if refresh else env._wave50_lifetime_state
 return {k:v.detach().clone().cpu() if isinstance(v,torch.Tensor) else copy.deepcopy(v) for k,v in s.items()}
def load_state(env,state):
 validate(state,env.num_envs);current=bind(env);assert identity(current)==identity(state)
 env._wave50_lifetime_state={k:v.detach().clone().to(env.device) if isinstance(v,torch.Tensor) else copy.deepcopy(v) for k,v in state.items()}
def audit(env):
 s=bind(env);return dict(profile=PROFILE,Wave_birth_environments=int(s['wave_mask'].sum()),other_birth_environments=int((~s['wave_mask']).sum()),Wave_seconds=40.,other_seconds=20.,parent_timeout_source_sha256=PARENT_SHA,episode_bound_exact=True,no_new_rng=True,only_time_out_function_changed=True,unchanged_initial_random_episode_age_draw=True,unchanged_clock_and_route_and_commands=True)
def verify_GPU_lifetime_fixture(env):
 before=env.episode_length_buf.clone();rng=torch.get_rng_state().clone();cuda_rng=torch.cuda.get_rng_state(env.device).clone() if str(env.device).startswith('cuda') else None;s=bind(env);rows=[]
 try:
  for age in (0,1999,2000,3999,4000):
   env.episode_length_buf.fill_(age);old=PARENT(env);new=time_out(env)
   assert torch.equal(new[~s['wave_mask']],old[~s['wave_mask']]);assert torch.equal(new[s['wave_mask']],torch.full_like(new[s['wave_mask']],age>=4000));rows.append(dict(age=age,Wave_timeouts=int(new[s['wave_mask']].sum()),other_timeouts=int(new[~s['wave_mask']].sum())))
 finally:env.episode_length_buf.copy_(before)
 assert torch.equal(before,env.episode_length_buf) and torch.equal(rng,torch.get_rng_state())
 if cuda_rng is not None:assert torch.equal(cuda_rng,torch.cuda.get_rng_state(env.device))
 return dict(passed=True,actual_bound_CUDA_state=cuda_rng is not None,fixtures=rows,actual_episode_length_buf_restored_exact=True,no_physical_step_or_reset_teleport_or_progress_credit=True,no_new_rng=True)
