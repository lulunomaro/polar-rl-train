"""Explicit CPU mock config fixture, separate from actual target SDK RewardManager probe."""
from pathlib import Path
import sys,types,copy,json,time,torch
from h1_public_request_phase_v1 import H1PublicRequestPhase
import h1_reward_scope_v1 as rewards
D=Path(__file__).resolve().parent;R=D/'reports'
class FixtureTerm:
 def __init__(self,func,weight,params=None):self.func=func;self.weight=weight;self.params={} if params is None else params
def original(env,factor=2.):return torch.tensor([1.,2.,3.,4.])*factor
def main():
 state=torch.get_rng_state().clone();mock=types.ModuleType('isaaclab.managers');mock.RewardTermCfg=FixtureTerm;sys.modules['isaaclab.managers']=mock;cfg=types.SimpleNamespace(rewards=types.SimpleNamespace(),terminations=object());keep={}
 for name in rewards.MASKED+('torques','joint_power','action_rate','action_acc','base_contact','termination','alive'):
  t=FixtureTerm(original,-.5,dict(factor=3.));setattr(cfg.rewards,name,t);keep[name]=(t,t.func,t.weight,dict(t.params))
 terms=cfg.terminations;rewards.configure(cfg);assert cfg.terminations is terms
 phase=H1PublicRequestPhase(4,'cpu');phase.request_for_action[:]=torch.tensor([False,True,False,True]);env=types.SimpleNamespace(h1_phase=phase,num_envs=4,device='cpu',step_dt=.01)
 for name,(term,func,weight,params) in keep.items():
  actual=getattr(cfg.rewards,name);assert actual is term and actual.weight==weight
  if name in rewards.MASKED:
   result=actual.func(env,**actual.params);expected=func(env,**params).clone();expected[phase.request_for_action]=0;assert torch.equal(result,expected)
  else:assert actual.func is func and actual.params==params
 phase.event_control[:]=torch.tensor([0.,1.,2.,3.]);assert torch.equal(cfg.rewards.h1_control_events.func(env),torch.tensor([0.,100.,200.,300.]))
 p=H1PublicRequestPhase(20000,'cpu');valid=p.state_dict();variants=[]
 bad=copy.deepcopy(valid);bad['profile']['version']=2;variants.append(bad)
 bad=copy.deepcopy(valid);bad['num_envs']=80;variants.append(bad)
 bad=copy.deepcopy(valid);bad['tensors'].pop('age_control');variants.append(bad)
 bad=copy.deepcopy(valid);bad['tensors']['age_control']=torch.zeros(20000,dtype=torch.float32);variants.append(bad)
 bad=copy.deepcopy(valid);bad['tensors']['age_control']=torch.zeros(19999,dtype=torch.long);variants.append(bad)
 bad=copy.deepcopy(valid);bad['tensors']['yaw_reference'][3]=float('nan');variants.append(bad)
 for bad in variants:
  q=H1PublicRequestPhase(20000,'cpu')
  try:q.load_state_dict(bad)
  except (AssertionError,KeyError):pass
  else:raise AssertionError('Bad phase state accepted')
 assert torch.equal(state,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_mock_only=True,masked_terms=list(rewards.MASKED),normal_rows_old_rewards_exact=True,jump_request_rows_only_explicit_conflicts_zeroed=True,unmasked_energy_action_rate_torque_bodycosts_identity_weight_params_exact=True,termination_config_identity_unchanged=True,candidate_event_rate_divides_by_point01=True,actual_SDK_dt_probe_still_requires_native=True,phase6_typed_bad_schema_cases_rejected=True,global_CPU_RNG_unchanged=True,no_CUDA_or_optimizer=True,no_live_runtime_or_native_payload_changed=True,no_inference_terraintruth_or_extra_action=True)
 (R/'H1_REWARD_MASK_PRESERVED_COSTS_PHASE6_SCHEMA_NEGATIVES_CPU_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
