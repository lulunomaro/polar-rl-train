"""Actual per-environment public0/4 source actor; no hidden phase supplied to actor."""
from pathlib import Path
import numpy as np,torch,time
from tensordict import TensorDict
from h1_closed24_single35_public04_v1 import Single35,EXPECTED
def build_retention_single(vec,path,device):
 from frozen_history_policy import DecisionHistoryVec
 from h1_frozen_witness_v1 import CONTEXT,cpu
 before=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state(device).clone();c=Single35(path,vec.num_envs,device)
 assert c.exact() and torch.equal(before,torch.get_rng_state()) and torch.equal(cuda,torch.cuda.get_rng_state(device))
 CONTEXT['save']('H1_FROZEN_SOURCE_ACTUAL.json',dict(source_SHA=EXPECTED,source_path=str(path),actor9_including_STD_initial_exact=True,construction_RNG_unchanged=True,critic_optimizer_gate_not_loaded_to_GPU=True,no_PPO=True,fresh80_not_source20000_fullstate_restore=True))
 wrapped=DecisionHistoryVec(vec,'A0');get=wrapped.get_observations;step0=wrapped.step;rows=[];timing=[];start=[None]
 def observed():
  wrapped.env._h1_publish_external_request()
  if c.pending is None:torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=c.begin(int(wrapped.env.common_step_counter),lambda:get()['policy'],wrapped.env._mod4_mode_bit)
  assert not p['shared_obs'][:,:3].any()
  wrapped.env._retention_native_witness.obs=cpu(p['shared_obs'])
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(obs):
  assert c.pending is not None and torch.equal(obs['policy'],c.pending['shared_obs'])
  result=c.pending['raw_action'];wrapped.env._retention_native_witness.raw_action=cpu(result)
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000);rows.append({k:cpu(v) for k,v in c.pending.items()});return result
 def step(action):
  assert c.pending is not None and torch.equal(action,c.pending['raw_action'])
  result=step0(action);actual=wrapped.env._retention_native_witness.rows[-1]
  c.finish(torch.as_tensor(actual['processed_action'],device=device),torch.as_tensor(actual['terminated']|actual['truncated'],device=device));return result
 class Observer:
  def audit(self):
   import hashlib
   assert c.controls==c.calls==len(rows)==len(timing) and c.pending is None and c.exact()
   p=Path(CONTEXT['output_dir'])/'H1_SINGLE_FULL_CONTROL_ACTUAL.npz';assert not p.exists();np.savez_compressed(p,**{k:np.stack([r[k] for r in rows]) for k in rows[0]},inference_chain_wall_ms=np.asarray(timing))
   out=dict(source_SHA=EXPECTED,actor9_STD_initial_final_literalexact=True,controls=c.controls,provider_calls=c.calls,public_modes_0_or4_actual_perenv=True,whole6_clip6_previous_actual6_selectedreset=True,no_PPO=True,optimizer_updates=0,raw=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()),host_latency_not_board_deadline=True)
   CONTEXT['save']('H1_SINGLE_POLICY_CONTROL_ACTUAL.json',out);return out
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,Observer()
