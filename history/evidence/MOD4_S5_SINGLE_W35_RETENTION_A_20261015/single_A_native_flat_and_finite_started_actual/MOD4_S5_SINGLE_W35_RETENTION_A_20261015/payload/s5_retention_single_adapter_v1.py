"""Same singleW35 controller as the admitted35 cell, with native readback only."""
from pathlib import Path
import json,time
import numpy as np,torch
from tensordict import TensorDict
from s5_single_frozen35_v1 import Single35,EXPECTED,sha

def build_retention_single(vec,path,device):
 from frozen_history_policy import DecisionHistoryVec
 from retention_native_witness_v8 import CONTEXT,cpu
 before=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state(device).clone();c=Single35(path,vec.num_envs,device)
 assert c.exact() and torch.equal(before,torch.get_rng_state()) and torch.equal(cuda,torch.cuda.get_rng_state(device))
 CONTEXT['save']('S5_SINGLE_POLICY_SOURCE_ACTUAL.json',dict(source_SHA=EXPECTED,source_path=str(path),all9_actor_std_GPU_source_exact=True,no_construction_CPUCUDA_RNG_draw=True,only_single_W35_actor_executed=True,no_gate_or_second_expert_forward=True,optimizer_updates=0,no_PPO=True,training_environment_fullrestore_claimed=False))
 wrapped=DecisionHistoryVec(vec,'A0');get=wrapped.get_observations;step0=wrapped.step;rows=[];timing=[];start=[None]
 def observed():
  if c.pending is None:torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=c.begin(int(wrapped.env.common_step_counter),lambda:get()['policy'])
  assert torch.max(abs(p['shared_obs'][:,:3]-wrapped.env.command_manager.get_term('twist').command))<=1e-6
  wrapped.env._retention_native_witness.obs=cpu(p['shared_obs'])
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(obs):
  assert c.pending is not None and torch.equal(obs['policy'],c.pending['shared_obs'])
  output=c.pending['raw_action'];wrapped.env._retention_native_witness.raw_action=cpu(output)
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000)
  rows.append({k:cpu(v) for k,v in c.pending.items()});return output
 def step(action):
  assert c.pending is not None and torch.equal(action,c.pending['raw_action'])
  result=step0(action);actual=wrapped.env._retention_native_witness.rows[-1]
  c.finish(torch.as_tensor(actual['processed_action'],device=device),torch.as_tensor(actual['terminated']|actual['truncated'],device=device));return result
 class Observer:
  def audit(self):
   assert c.controls==c.calls==len(rows)==len(timing) and c.pending is None and c.exact()
   arrays={k:np.stack([r[k] for r in rows]) for k in rows[0]};arrays['inference_chain_wall_ms']=np.asarray(timing)
   p=Path(CONTEXT['output_dir'])/'S5_SINGLE_FULL_CONTROL_ACTUAL.npz';assert not p.exists();np.savez_compressed(p,**arrays)
   out=dict(source_SHA=EXPECTED,all9_initial_final_actor_STD_exact=True,controls=c.controls,feedback_provider_calls=c.calls,whole6_original_clip6=True,previous_actual_action_and_selectedreset_exact=True,normal_mode_only=True,switches=0,only_single_actor_forward=True,no_gate_or_other_expert_forward=True,optimizer_updates=0,no_PPO=True,raw=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)),latency_ms={k:float(np.percentile(timing,v)) for k,v in (('p50',50),('p95',95),('p99',99))},latency_includes_shared_feedback_single_actor_GPU_host_sync_not_board_deadline=True)
   CONTEXT['save']('S5_SINGLE_POLICY_CONTROL_ACTUAL.json',out);return out
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,Observer()
