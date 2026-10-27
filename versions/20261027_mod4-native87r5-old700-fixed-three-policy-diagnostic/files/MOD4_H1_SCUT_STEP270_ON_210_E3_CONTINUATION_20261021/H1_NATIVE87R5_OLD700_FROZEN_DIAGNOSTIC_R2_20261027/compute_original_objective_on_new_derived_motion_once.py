"""Evaluate original analytic tracking head on new recorded states; no model/WM/actor."""
from pathlib import Path
import hashlib,json,sys,time,traceback
import numpy as np,torch
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
B=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1'
def main():
 q=json.loads((S/'BINDING.json').read_bytes());sys.path.insert(0,str(B/'source'))
 from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 # New reference-source arithmetic, no historical fixture rerun or native model load.
 doc=json.loads((B/q['reference_relative']).read_bytes())
 provider=ConvertedMOD4Reference(doc).bind_named_order(q['runtime_source_contract']['expected_runtime_joint_names'],scope='source_CPU_fixture')
 mdp=ConvertedMOD4JumpMdp(provider)
 derived=np.load(S/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz');rows=[]
 for seed in q['seeds']:
  prefix=str(seed)+'_';packed=torch.from_numpy(derived[prefix+'packed127']);frames=torch.from_numpy(derived[prefix+'control_age'].astype(np.int64));action=torch.from_numpy(derived[prefix+'raw'])
  previous=torch.cat((torch.zeros_like(action[:1]),action[:-1].clamp(-6,6)),0)
  terms=mdp.objective_terms(unflatten_state(packed),frames,action,previous)
  masks=dict(request100_179=(frames>=100)&(frames<180),post200_499=frames>=200)
  groups={}
  for name,mask in masks.items():
   groups[name]=dict(rows=int(mask.sum()),mean_original_terms={k:float(v[mask].mean()) for k,v in terms.items()},mean_tracking_fraction_of_6=float(terms['tracking_sum'][mask].mean()/6))
  target,_=provider.query(frames)
  poserr=((packed[:,:3]-target[:,:3])**2).sum(-1).sqrt()
  rows.append(dict(seed=seed,source_only_analytic_reward_on_real_recorded_state=groups,request_mean_base_target_position_error_m=float(poserr[masks['request100_179']].mean()),not_dynamic_model_accuracy_or_actual_training_causal_attribution=True))
 report=dict(epoch=time.time(),purpose='bounded new recorded-motion objective contribution check',rows=rows,original_objective_file=str(B/'source/converted_MOD4_jump_mdp_v4.py'),original_objective_SHA=hashlib.sha256((B/'source/converted_MOD4_jump_mdp_v4.py').read_bytes()).hexdigest(),source_uses_six_additive_tracking_terms=True,no_direct_original_landing_event_or_wheel_clearance_in_native_objective_terms=True,original_physical_V8_reward_separately_logged_not_this_native_return=True,source_counterexample_not_proven_unique_actual_failure_cause=True,no_reward_change_or_deployment=True,no_model_load_or_WM_actor_forward_or_gradient_or_physics=True)
 with (R/'ORIGINAL_NATIVE_OBJECTIVE_ON_NEW_RECORDED_MOTION_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,allow_nan=False)
 print(json.dumps(report))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('NEW_ANALYTIC_OBJECTIVE_READER_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
  raise
