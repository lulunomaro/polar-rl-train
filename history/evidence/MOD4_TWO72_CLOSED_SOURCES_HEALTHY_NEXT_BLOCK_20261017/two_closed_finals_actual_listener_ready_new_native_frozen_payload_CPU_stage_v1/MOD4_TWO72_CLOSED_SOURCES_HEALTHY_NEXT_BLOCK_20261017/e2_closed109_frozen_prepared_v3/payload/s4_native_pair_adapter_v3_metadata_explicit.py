"""Fresh native observer adapter for the registered E0+WAVE35 rule baseline.

No sampling, optimizer updates, extra physical steps, teacher or terrain ID.
The existing witness supplies the actual pre-reset action readback to commit.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np,torch
from tensordict import TensorDict
from s4_shared_feedback_hardtop1_v1 import PairRouter,sha

def build_native_rule_pair(vec,anchor_path,device):
 from frozen_history_policy import DecisionHistoryVec
 from retention_native_witness_v8 import CONTEXT,cpu
 Q=Path(__file__).resolve().parent;manifest=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());refs=manifest['sources']
 assert manifest['mode']=='rule_eval' and manifest['no_gate_learning'] and Path(refs[1]['local_path']).resolve()==Path(anchor_path).resolve()
 before=torch.get_rng_state().clone();cuda_before=torch.cuda.get_rng_state(device).clone()
 router=PairRouter(refs,vec.num_envs,device)
 assert torch.equal(before,torch.get_rng_state()) and torch.equal(cuda_before,torch.cuda.get_rng_state(device))
 for row,expert in zip(refs,router.experts):
  source=torch.load(row['local_path'],map_location='cpu',weights_only=False)
  assert sha(row['local_path'])==row['sha256'] and all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in expert.snapshot().items())
 CONTEXT['save']('S4_FROZEN_PAIR_SOURCE_ACTUAL.json',dict(experts=[dict(id=r['expert'],path=r['local_path'],bytes=Path(r['local_path']).stat().st_size,sha256=sha(r['local_path'])) for r in refs],all18_actor_weight_and_std_GPU_tensors_source_exact=True,source_std_scalar_retained=router.std.cpu().tolist(),gate_fixture_deterministic_untrained=True,rule_baseline_normal_command_only=True,no_CPU_or_CUDA_rng_draw_from_pair_construction=True,only_frozen_expert_actor_outputs_executed_no_training_DR_resume=True,new_gate_and_E0_initialized_critic_fixture_constructed_but_unused_for_rule_selection=True,new_optimizer_not_original_optimizer_resumed=True,checkpoint_field_is_WAVE35_scene_anchor_not_single_actor_policy=True,optimizer_updates=0,no_PPO=True))
 wrapped=DecisionHistoryVec(vec,'A0');original_get=wrapped.get_observations;original_step=wrapped.step;rows=[];timing=[];start=[None]
 def observed():
  tick=int(wrapped.env.common_step_counter)
  if router.pending is None:
   torch.cuda.synchronize(device);start[0]=time.perf_counter()
  p=router.decide(tick,lambda:original_get()['policy'],'rule_eval')
  requested=wrapped.env.command_manager.get_term('twist').command
  assert torch.max(abs(p['shared_obs'][:,:3]-requested))<=1e-6
  wrapped.env._retention_native_witness.obs=cpu(p['shared_obs'])
  return TensorDict(dict(policy=p['shared_obs']),batch_size=[vec.num_envs])
 def policy(values):
  p=router.pending;assert p is not None and torch.equal(values['policy'],p['shared_obs'])
  output=p['raw_action'];wrapped.env._retention_native_witness.raw_action=cpu(output)
  torch.cuda.synchronize(device);timing.append((time.perf_counter()-start[0])*1000)
  rows.append({k:cpu(p[k]) for k in ('shared_obs','expert_means','logits','probabilities','z','raw_action','clipped_action')})
  return output
 def step(action):
  assert router.pending is not None and torch.equal(action,router.pending['raw_action'])
  tick=router.last_tick;result=original_step(action);actual=wrapped.env._retention_native_witness.rows[-1]
  router.finish(tick,torch.as_tensor(actual['processed_action'],device=device),torch.as_tensor(actual['terminated']|actual['truncated'],device=device))
  return result
 class PairObserver:
  def audit(self):
   assert router.completed_controls==len(rows)==len(timing) and router.pending is None
   assert router.observation_calls==len(rows)
   arrays={k:np.stack([r[k] for r in rows]) for k in rows[0]};arrays['inference_chain_wall_ms']=np.asarray(timing)
   O=Path(CONTEXT['output_dir']);raw=O/'S4_ROUTING_FULL_CONTROL_ACTUAL.npz';assert not raw.exists();np.savez_compressed(raw,**arrays)
   for row,expert in zip(refs,router.experts):
    source=torch.load(row['local_path'],map_location='cpu',weights_only=False);assert all(torch.equal(v.cpu(),source['actor_state_dict'][k]) for k,v in expert.snapshot().items())
   report=dict(profile='S4_two_frozen_actor_shared35_rule_eval_v1',sources=refs,controls=router.completed_controls,feedback_provider_calls=router.observation_calls,whole6action_selection_exact=True,actual_original_action_manager_readback_and_selected_reset_exact=True,source_all18_weights_std_unchanged=True,rule_reads_only_normal_commands_from_shared35=True,existing_mode_bits_required_constant_normal_no_terrain_hint=True,rule_is_not_trained_gate=True,gate_optimizer_updates=0,critic_optimizer_updates=0,switches=router.switch_count,optional_hysteresis_disabled_for_first_stateless_native=True,router_raw=dict(path=str(raw),bytes=raw.stat().st_size,sha256=sha(raw)),source_pair_manifest_SHA=sha(Q/'S4_PAIR_SOURCE_MANIFEST.json'),inference_chain_latency_ms=dict(p50=float(np.percentile(timing,50)),p95=float(np.percentile(timing,95)),p99=float(np.percentile(timing,99)),includes_samefeedback_both_experts_gate_fixture_and_host_GPU_sync=True,not_hardware_board_deadline=True),transition_35mm_route_not_this_flat_scope=True,training_env_full_CPUCUDA_restore_and_gate_learning_not_admitted=True,architecture='A0 shared35/whole6 hardtop1/original clip6/no action averaging')
   CONTEXT['save']('S4_ROUTER_NATIVE_CONTROL_ACTUAL.json',report);return report
 wrapped.get_observations=observed;wrapped.step=step
 return wrapped,policy,PairObserver()
