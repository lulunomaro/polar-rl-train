"""Frozen two-expert adapter for the actual original35 terrain route loop."""
from pathlib import Path
import json,time
import numpy as np,torch
from tensordict import TensorDict
from s4_shared_feedback_hardtop1_v1 import PairRouter,sha
from s4_eval_trained_gate_source_v1 import load_trained_gate
def build_route_pair(vec,path,device,output,save):
 from frozen_history_policy import DecisionHistoryVec
 Q=Path(__file__).resolve().parent;refs=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes())['sources']
 assert Path(path).resolve()==Path(refs[1]['local_path']).resolve()
 before=torch.get_rng_state().clone();cuda=torch.cuda.get_rng_state(device).clone()
 router=PairRouter(refs,vec.num_envs,device)
 gate_manifest=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
 gate_proof=load_trained_gate(router,gate_manifest)
 assert torch.equal(before,torch.get_rng_state()) and torch.equal(cuda,torch.cuda.get_rng_state(device))
 for row,expert in zip(refs,router.experts):
  source=torch.load(row['local_path'],map_location='cpu',weights_only=False)
  assert sha(row['local_path'])==row['sha256'] and all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in expert.snapshot().items())
 save('S4_FROZEN_PAIR_SOURCE_ACTUAL.json',dict(sources=refs,all18_actor_std_GPU_source_exact=True,source_std_retained=router.std.cpu().tolist(),no_construction_CPUCUDA_RNG_draw=True,trained_gate6_loaded_critic_fixture_unused_for_frozen_eval=True,gate_source=gate_manifest,gate_proof=gate_proof,optimizer_updates=0,no_PPO=True,not_training_environment_DR_resume=True))
 wrapped=DecisionHistoryVec(vec,'A0');original_get=wrapped.get_observations;original_step=wrapped.step
 rows=[];timing=[];start=[None]
 def observed():
  if router.pending is None:torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=router.decide(int(wrapped.env.common_step_counter),lambda:original_get()['policy'],'gate_eval')
  assert torch.max(abs(p['shared_obs'][:,:3]-wrapped.env.command_manager.get_term('twist').command))<=1e-6
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(obs):
  p=router.pending;assert p is not None and torch.equal(obs['policy'],p['shared_obs'])
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000)
  rows.append({k:p[k].detach().cpu().numpy().copy() for k in ('shared_obs','expert_means','logits','probabilities','z','raw_action','clipped_action')})
  return p['raw_action']
 def step(action):
  assert router.pending is not None and torch.equal(action,router.pending['raw_action'])
  tick=router.last_tick;result=original_step(action);phase=wrapped.env._s4_before_reset_route_phase
  router.finish(tick,torch.as_tensor(phase['processed_action'],device=device),torch.as_tensor(phase['terminated']|phase['truncated'],device=device))
  return result
 class Observer:
  checkpoint_sha256=gate_manifest['sha256']
  def audit(self):
   assert router.pending is None and router.completed_controls==router.observation_calls==len(rows)==len(timing)
   arrays={k:np.stack([r[k] for r in rows]) for k in rows[0]};arrays['inference_chain_wall_ms']=np.asarray(timing)
   p=Path(output)/'S4_ROUTING_FULL_CONTROL_ACTUAL.npz';assert not p.exists();np.savez_compressed(p,**arrays)
   for row,expert in zip(refs,router.experts):
    c=torch.load(row['local_path'],map_location='cpu',weights_only=False);assert all(torch.equal(v.cpu(),c['actor_state_dict'][k]) for k,v in expert.snapshot().items())
   r=dict(sources=refs,controls=router.completed_controls,feedback_provider_calls=router.observation_calls,switches=router.switch_count,whole6_exact=True,previous_actual_control_reset_exact=True,all18_weights_std_unchanged=True,normal_mode_required_constant=True,rule_only_command_from_shared35=False,deterministic_trained_gate=True,gate_source=gate_manifest,gate_proof=gate_proof,stateless_rule_hysteresis_disabled=True,gate_updates=0,critic_updates=0,new_fixture_not_trained_gate=False,raw=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)),latency_ms={k:float(np.percentile(timing,v)) for k,v in (('p50',50),('p95',95),('p99',99))},latency_includes_shared_feedback_both_experts_fixture_and_GPUhostsync_not_board_deadline=True,no_PPO=True,full_training_DR_restore_not_claimed_by_frozen_actor_eval=True,qualification_claimed=False)
   save('S4_ROUTER_ROUTE_CONTROL_ACTUAL.json',r);return r
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,Observer()
