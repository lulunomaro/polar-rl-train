"""Actual saved35 inputs + independent sampled fixture; zero optimization."""
from pathlib import Path
import os,sys,json,hashlib,time,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;sys.path.insert(0,str(D))
from s4_shared_feedback_hardtop1_v1 import PairRouter,sha
from s4_saved_rollout_gate_objective_v1 import SavedGateObjective
N=W/'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015';case='s4_rule_original35_query35_native120_v2'
receipt=json.loads(sorted((N/'reports').glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
raw=next(Path(r['local_path']) for r in receipt['collected_files'] if r['relative'].endswith('/S4_ROUTING_FULL_CONTROL_ACTUAL.npz'))
with np.load(raw,allow_pickle=False) as z:saved=z['shared_obs'].copy()
refs=json.loads((N/'payload/S4_PAIR_SOURCE_MANIFEST.json').read_bytes())['sources']
for r in refs:r['local_path']=str(N/'payload/source'/Path(r['local_path']).name)
before=torch.get_rng_state().clone();router=PairRouter(refs,80);objective=SavedGateObjective(router)
source=[e.snapshot() for e in router.experts];gate={k:v.clone() for k,v in router.gate.state_dict().items()};critic={k:v.clone() for k,v in router.critic.state_dict().items()};opt=copy.deepcopy(router.optimizer.state_dict())
assert torch.equal(before,torch.get_rng_state())
g=torch.Generator(device='cpu');g.manual_seed(20261015);errors=[];bad=0
for count in (1,13,80,127,321):
 obs=torch.from_numpy(saved.reshape(-1,35)[:count].copy())
 # This objective must accept historical rows and arbitrary minibatch size.
 assert count!=router.n or not torch.equal(obs[:,22:28],router.last_action)
 with torch.no_grad():
  means=torch.stack([e(obs) for e in router.experts],1);logits=router.gate(obs);z=torch.multinomial(logits.softmax(-1),1,generator=g).squeeze(-1)
  rows=torch.arange(count);raw_a=means[rows,z]+router.std[z]*torch.randn(count,6,generator=g)
  distribution=torch.distributions.Categorical(logits=logits);conditional=torch.distributions.Independent(torch.distributions.Normal(means[rows,z],router.std[z]),1)
  independent=distribution.log_prob(z)+conditional.log_prob(raw_a)
 stat=objective.statistics(obs,z,raw_a);errors.append(float(abs(stat['joint_log_probability']-independent).max()))
 assert errors[-1]<=2e-5
 # Constant private CPU fixtures are declared; they are not physical critic observations.
 critic_obs=torch.cos(torch.arange(count*38).reshape(count,38).float()*.017)
 advantages=torch.sin(torch.arange(count).float()+.1);returns=torch.sin(torch.arange(count).float()*.05)
 with torch.no_grad():old_values=router.critic(critic_obs).squeeze(-1)
 terms=objective.losses(obs,critic_obs,z,raw_a,independent.detach(),logits.detach(),advantages,returns,old_values)
 assert torch.allclose(terms['ratio'],torch.ones(count),atol=2e-5,rtol=0) and terms['KL'].abs()<1e-6
 loss=terms['policy_loss']+terms['value_loss']-.01*terms['entropy'];grads=objective.gradients_only(loss)
 assert len(grads)==len(list(router.gate.parameters()))+len(list(router.critic.parameters()))
 # Probability must be for saved raw a, even when actual env execution clipped it.
 clipped=objective.statistics(obs,z,raw_a.clamp(-6,6))['joint_log_probability']
 if bool((abs(raw_a)>6).any()):assert not torch.allclose(clipped,independent,atol=1e-4,rtol=0)
 for mutate in ('missing_z','raw_width','oracle_mode','nonfinite','illegal_choice'):
  x=obs.clone();choice=z.clone();action=raw_a.clone()
  if mutate=='missing_z':choice=choice.float()
  elif mutate=='raw_width':action=action[:,:5]
  elif mutate=='oracle_mode':x[:,28:35]=0;x[:,29]=1
  elif mutate=='nonfinite':x[0,0]=float('nan')
  elif mutate=='illegal_choice':choice[0]=2
  try:objective.statistics(x,choice,action)
  except AssertionError:bad+=1
  else:raise AssertionError(mutate+' accepted')
assert bad==25 and torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
for e,s in zip(router.experts,source):assert all(torch.equal(v,s[k]) for k,v in e.snapshot().items())
assert all(torch.equal(v,gate[k]) for k,v in router.gate.state_dict().items()) and all(torch.equal(v,critic[k]) for k,v in router.critic.state_dict().items()) and router.optimizer.state_dict()==opt
result=dict(epoch=time.time(),passed_CPU_saved_rollout_objective=True,actual_saved35_input_source=dict(path=str(raw),sha256=sha(raw)),batch_sizes=[1,13,80,127,321],arbitrary_historical_minibatch_not_current_tick_lastaction_check=True,independent_categorical_plus_conditional_raw_logp_max_errors=errors,ratios_initially_one_and_exact_fixed_expert_KL=True,raw_not_clipped_probability_negative_passed=True,gate_plus_newcritic_gradient_ownership=True,frozen_expert_weights_and_std_unchanged=True,all_gate_critic_optimizer_states_unchanged=True,optimizer_updates=0,negative_cases=25,synthetic_sampled_z_raw_and_critic_values_explicit_not_GPU_rollout=True,global_CPU_RNG_unchanged=True,no_CUDA_no_PPO_no_budgetwrite=True,production_environment_DR_globalnamed_privateCPUCUDA_fullsave_pending=True,actual_gate_learning_admission=False)
p=D/'reports/S4_SAVED_HISTORICAL_VARIABLE_BATCH_OBJECTIVE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),passed=True,bad=bad,updates=0,max_logp_error=max(errors))))
