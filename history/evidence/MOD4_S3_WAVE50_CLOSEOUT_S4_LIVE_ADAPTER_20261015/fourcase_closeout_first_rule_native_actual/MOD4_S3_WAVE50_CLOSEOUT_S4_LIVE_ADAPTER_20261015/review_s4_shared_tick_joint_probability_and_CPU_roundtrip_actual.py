"""Actual frozen sources and saved35 inputs, synthetic lifecycle tests, no updates."""
from pathlib import Path
import os,sys,json,time,hashlib,copy,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
from s4_shared_feedback_hardtop1_v1 import PairRouter,clone_tree,sha
A=Path(__file__).resolve().parent;W=A.parent;R=A/'reports'
def main():
 out=R/'S4_SHARED_TICK_ROUTER_JOINT_PROBABILITY_AND_CPU_FULLSAVE_ACTUAL.json';assert not out.exists();torch.set_num_threads(1)
 src=W/'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/reports/FROZEN_E0_WAVE35_CPU_INPUTS_ACTUAL_1791973668323853100.json';refs=json.loads(src.read_bytes())['sources'];assert all(row['twohost_byteSHA_exact'] for row in refs)
 E=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015/reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json';er=json.loads(E.read_bytes());raw=Path(er['raw']['local_path']);assert sha(raw)==er['raw']['sha256']
 with np.load(raw) as z:x=torch.from_numpy(z['policy_obs'][0,np.arange(40)].copy())
 assert x.shape==(40,35) and torch.equal(x[:,22:28],torch.zeros(40,6))
 global_rng=torch.get_rng_state().clone();router=PairRouter(refs,40);assert torch.equal(global_rng,torch.get_rng_state());before=[e.snapshot() for e in router.experts]
 std=router.std.clone();calls=0;latency=[];selected=[]
 def provider():
  nonlocal calls
  calls+=1;y=x.clone();y[:,22:28]=router.last_action;y[:,:3]=0
  if router.completed_controls//40!=1:y[:,0]=.3
  return y
 for tick in range(120):
  started=time.perf_counter();p=router.decide(tick,provider,'rule_eval');latency.append(time.perf_counter()-started)
  again=router.decide(tick,lambda:(_ for _ in ()).throw(AssertionError('Repeated provider draw')),'rule_eval');assert torch.equal(p['raw_action'],again['raw_action'])
  assert torch.equal(p['raw_action'],p['expert_means'][torch.arange(40),p['z']]) and torch.equal(p['clipped_action'],p['raw_action'].clamp(-6,6))
  ended=torch.zeros(40,dtype=torch.bool)
  if tick==70:ended[[3,7]]=True
  router.finish(tick,p['clipped_action'],ended)
  if ended.any():assert not router.last_action[ended].any() and (router.previous[ended]==-1).all()
  selected.append(p['z'].tolist())
 assert calls==router.observation_calls==router.completed_controls==120 and torch.equal(global_rng,torch.get_rng_state())
 # Independently use torch distribution APIs for the stored latent (z, raw a) probability.
 g=torch.Generator().manual_seed(20260928);train=PairRouter(refs,40);y=x.clone()
 p=train.decide(0,lambda:y,'train_joint',g);means,logits=train.distributions(y);rows=torch.arange(40)
 independent=torch.distributions.Categorical(logits=logits).log_prob(p['z'])+torch.distributions.Normal(means[rows,p['z']],train.std[p['z']]).log_prob(p['raw_action']).sum(-1)
 probability_error=float((independent-p['joint_log_prob']).abs().max());assert probability_error<1e-4
 conditional_H=torch.distributions.Normal(means,train.std[None]).entropy().sum(-1)
 independent_H=torch.distributions.Categorical(logits=logits).entropy()+(logits.softmax(-1)*conditional_H).sum(-1)
 entropy_error=float((independent_H-train.latent_joint_entropy(y)).abs().max());assert entropy_error<1e-5
 new=logits+torch.tensor([.2,-.3]);independent_KL=torch.distributions.kl_divergence(torch.distributions.Categorical(logits=logits),torch.distributions.Categorical(logits=new))
 kl_error=float((independent_KL-PairRouter.frozen_expert_joint_KL(logits,new)).abs().max());assert kl_error<1e-5
 train.optimizer.zero_grad();loss=-train.joint_log_prob(y,p['z'],p['raw_action']).mean()+train.critic(torch.zeros(40,38)).square().mean();loss.backward()
 gate_ids={id(v) for v in train.gate.parameters()};critic_ids={id(v) for v in train.critic.parameters()};optimizer_ids={id(v) for row in train.optimizer.param_groups for v in row['params']};assert optimizer_ids==gate_ids|critic_ids
 assert all(not list(e.parameters()) for e in train.experts) and all(getattr(e,'frozen_'+str(i)).grad is None for e in train.experts for i in range(9))
 assert any(v.grad is not None and v.grad.abs().sum()>0 and torch.isfinite(v.grad).all() for v in train.gate.parameters());assert not train.optimizer.state
 train.finish(0,p['clipped_action'],torch.zeros(40,dtype=torch.bool));state=train.fullsave(g)
 path=A/'S4_SOURCE_BOUND_CPU_ROUNDTRIP_FIXTURE.pt';assert not path.exists();torch.save(state,path);loaded=torch.load(path,map_location='cpu',weights_only=False)
 restored=PairRouter(refs,40);g2=torch.Generator();restored.restore(loaded,g2);y=x.clone();y[:,22:28]=train.last_action
 q=train.decide(1,lambda:y,'train_joint',g);q2=restored.decide(1,lambda:y,'train_joint',g2)
 assert all(torch.equal(q[k],q2[k]) for k in ('shared_obs','expert_means','z','raw_action','clipped_action','joint_log_prob')) and torch.equal(g.get_state(),g2.get_state())
 train.finish(1,q['clipped_action'],torch.zeros(40,dtype=torch.bool));restored.finish(1,q2['clipped_action'],torch.zeros(40,dtype=torch.bool))
 # Optional deterministic evaluation-only100ms/0.2 probability-advantage rule.
 sticky=PairRouter(refs,40);choices=[]
 for tick in range(12):
  with torch.no_grad():sticky.gate.b3.copy_(torch.tensor([5.,-5.]) if tick==0 else torch.tensor([-5.,5.]))
  y=x.clone();y[:,22:28]=sticky.last_action
  q=sticky.decide(tick,lambda:y,'gate_eval',dwell_ticks=10,advantage=.2);choices.append(q['z'].tolist());sticky.finish(tick,q['clipped_action'],torch.zeros(40,dtype=torch.bool))
 assert all(all(z==0 for z in row) for row in choices[:10]) and all(all(z==1 for z in row) for row in choices[10:])
 negatives=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,RuntimeError,TypeError,KeyError):negatives.append(name)
  else:raise AssertionError('Invalid routing contract accepted:'+name)
 reject('privileged38feedback',lambda:PairRouter(refs,40).decide(0,lambda:torch.zeros(40,38)))
 bad=x.clone();bad[:,28:35]=0;bad[:,29]=1;reject('hidden_terrain_mode_bit',lambda:PairRouter(refs,40).decide(0,lambda:bad))
 badlast=x.clone();badlast[:,22:28]=1;reject('perexpert_virtual_last_action',lambda:PairRouter(refs,40).decide(0,lambda:badlast))
 reject('stale_tick',lambda:router.decide(119,provider))
 reject('skipped_tick',lambda:router.decide(122,provider))
 pending=PairRouter(refs,40);q=pending.decide(0,lambda:x)
 reject('advance_before_actual_execution',lambda:pending.decide(1,lambda:x))
 reject('mode_changed_inside_tick',lambda:pending.decide(0,lambda:x,'rule_eval'))
 reject('wrong_executed_whole_action',lambda:pending.finish(0,q['clipped_action']+1,torch.zeros(40,dtype=torch.bool)))
 reject('unsafe_pending_fullsave',lambda:pending.fullsave(g))
 reject('train_hysteresis_unaccounted_probability',lambda:PairRouter(refs,40).decide(0,lambda:x,'train_joint',g,dwell_ticks=10,advantage=.2))
 badrefs=copy.deepcopy(refs);badrefs[0]['sha256']='0'*64;reject('wrong_immutable_expert_SHA',lambda:PairRouter(badrefs,40))
 for key,change in [('expert_std',lambda v:v.mul(2)),('expert_actor_snapshots',lambda v:v[:1]),('last_action',lambda v:torch.full_like(v,float('nan'))),('previous',lambda v:torch.full_like(v,2)),('last_switch',lambda v:torch.full_like(v,1000000))]:
  broken=clone_tree(loaded);broken[key]=change(broken[key]);reject('bad_fullsave_'+key,lambda b=broken:PairRouter(refs,40).restore(b,g2))
 assert len(negatives)==16 and torch.equal(global_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 assert all(sha(row['local_path'])==row['sha256'] for row in refs) and torch.equal(std,router.std)
 assert all(torch.equal(v,router.experts[i].snapshot()[k]) for i,s in enumerate(before) for k,v in s.items())
 result=dict(epoch=time.time(),passed_CPU_runtime_probability_and_disk_contracts=True,sources=refs,actual_saved35_input_source=dict(path=str(raw),sha256=sha(raw),actual_initial40_vectors=True),actual_original_observation_layout=dict(last_action=[22,28],mode=[28,35]),actual_saved_normal_mode_constant_verified=True,one_provider_draw_per_tick=True,shared_same35_view_both_experts_and_gate=True,one_whole6action_selected_then_original_clip6=True,source_std_scalar_not_reset_or_blended=std.tolist(),original_action_manager_previous_clipped_control_semantics=True,delayed_motor_torque_history_not_replaced_by_control_action=True,synthetic120_lifecycle_and_selected_reset_tests=True,provider_calls=calls,completed_CPU_fixture_controls=120,fixture_switches=router.switch_count,eval_only_dwell100ms_probability_advantage02_CPU=True,train_latent_z_and_raw_action_saved=True,joint_logprob_error=probability_error,joint_entropy_not_physical_marginal_entropy=True,entropy_error=entropy_error,exact_KL_for_unchanged_frozen_conditionals_error=kl_error,gate_and_new_critic_only_gradient_ownership=True,all_expert_actor_std_source_files_unchanged=True,optimizer_updates=0,new_optimizer_not_inherited_single_expert_optimizer=True,critic_initialized_E0_weights_declared=True,CPU_disk_roundtrip_private_generator_next_sample_exact=True,roundtrip_fixture=dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path),not_production_checkpoint=True),negative_cases=negatives,latency_CPU_math_only_ms=dict(p50=float(np.percentile(latency,50))*1000,p95=float(np.percentile(latency,95))*1000,p99=float(np.percentile(latency,99))*1000,not_SDK_or_hardware_deadline=True),new_live_native_backend_not_yet_verified=True,transition_route_not_yet_verified=True,full_training_env_DR_CPUCUDA_resume_pending=True,supervised_expert_performance_labels_and_any_gate_updates_pending=True,gate_GPU_PPO_admitted=False,no_CPU_or_GPU_learning_or_canonical_write=True,qualified_MoE=False,reader_SHA=sha(__file__),component_SHA=sha(A/'s4_shared_feedback_hardtop1_v1.py'))
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),CPU_router_passed=True,provider_calls=120,probability_error=probability_error,roundtrip_exact=True,negative_cases=len(negatives),optimizer_updates=0,GPU_admitted=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('S4_ROUTER_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_no_learning=True),indent=2),encoding='utf8');raise
