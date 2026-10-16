"""Single frozen CURB878 actor; same deployable35 and actual-action reset semantics."""
from pathlib import Path
import hashlib,json,time
import numpy as np,torch
from tensordict import TensorDict
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
EXPECTED='81247281129fa98820b6cf78799e0c72eda9e811fa480cdb019130eaea15f7ff'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Single35:
 def __init__(self,path,n,device):
  assert sha(path)==EXPECTED and isinstance(n,int) and n>0
  source=torch.load(path,map_location='cpu',weights_only=False)
  assert source.get('history_architecture',{}).get('variant','A0')=='A0' and source['E1_terrain_state']['num_envs']==20000
  self.model=FrozenMean35(source['actor_state_dict']).to(device).eval();self.model.requires_grad_(False)
  self.source={k:v.detach().cpu().clone() for k,v in source['actor_state_dict'].items()};assert len(self.source)==9
  self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider):
  if self.pending is not None:assert self.tick==tick;return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all()
  assert torch.equal(x[:,22:28],self.last)
  normal=torch.zeros_like(x[:,28:35]);normal[:,0]=1;assert torch.equal(x[:,28:35],normal)
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all()
  self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6));self.tick=tick;self.calls+=1
  return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and actual.shape==(self.n,6) and ended.shape==(self.n,) and ended.dtype==torch.bool
  assert torch.equal(actual,self.pending['clipped_action'])
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(v.detach().cpu(),self.source[k]) for k,v in self.model.snapshot().items())
  return True
def build_route_pair(vec,path,device,output,save):
 from frozen_history_policy import DecisionHistoryVec
 before=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state(device).clone();c=Single35(path,vec.num_envs,device)
 assert torch.equal(before,torch.get_rng_state()) and torch.equal(cuda,torch.cuda.get_rng_state(device)) and c.exact()
 source=dict(source_SHA=EXPECTED,source_path=str(path),all9_actor_std_GPU_source_exact=True,no_construction_CPUCUDA_RNG_draw=True,only_single_CURB_actor_executed=True,no_gate_or_second_expert_forward=True,optimizer_updates=0,no_PPO=True,training_environment_fullrestore_claimed=False)
 save('S5_SINGLE_POLICY_SOURCE_ACTUAL.json',source)
 wrapped=DecisionHistoryVec(vec,'A0');get=wrapped.get_observations;step0=wrapped.step;rows=[];timing=[];start=[None]
 def observed():
  if c.pending is None:torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=c.begin(int(wrapped.env.common_step_counter),lambda:get()['policy'])
  assert torch.max(abs(p['shared_obs'][:,:3]-wrapped.env.command_manager.get_term('twist').command))<=1e-6
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(obs):
  assert c.pending is not None and torch.equal(obs['policy'],c.pending['shared_obs'])
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000)
  rows.append({k:v.detach().cpu().numpy().copy() for k,v in c.pending.items()});return c.pending['raw_action']
 def step(action):
  assert c.pending is not None and torch.equal(action,c.pending['raw_action'])
  result=step0(action);phase=wrapped.env._s4_before_reset_route_phase
  c.finish(torch.as_tensor(phase['processed_action'],device=device),torch.as_tensor(phase['terminated']|phase['truncated'],device=device));return result
 class Observer:
  checkpoint_sha256=EXPECTED
  def audit(self):
   assert c.controls==c.calls==len(rows)==len(timing) and c.pending is None and c.exact()
   arrays={k:np.stack([r[k] for r in rows]) for k in rows[0]};arrays['inference_chain_wall_ms']=np.asarray(timing)
   p=Path(output)/'S5_SINGLE_FULL_CONTROL_ACTUAL.npz';assert not p.exists();np.savez_compressed(p,**arrays)
   result=dict(source_SHA=EXPECTED,all9_initial_final_actor_STD_exact=True,controls=c.controls,feedback_provider_calls=c.calls,whole6_original_clip6=True,previous_actual_action_and_selectedreset_exact=True,normal_mode_only=True,switches=0,only_single_actor_forward=True,no_gate_or_other_expert_forward=True,optimizer_updates=0,no_PPO=True,raw=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)),latency_ms={k:float(np.percentile(timing,v)) for k,v in (('p50',50),('p95',95),('p99',99))},latency_includes_shared_feedback_single_actor_GPU_host_sync_not_board_deadline=True)
   save('S5_SINGLE_POLICY_CONTROL_ACTUAL.json',result);return result
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,Observer()
