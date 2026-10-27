"""Only V2 reward aggregation/gradients; reuse V1 FK error qualification.

Reads only expressly allowed NEW derived NPZ; no old raw/fixture replay/model.
"""
from pathlib import Path
import hashlib,json,sys,traceback
import numpy as np,torch
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];B=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1';R2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
sys.path[:0]=[str(HERE),str(B/'source'),str(B/'source/sm_deps')];torch.set_num_threads(2)
from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
from own_step_differentiable_objective_v2 import OwnStepDifferentiableMdpV2
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
from supermimic_wheel_leg_v3.geometry import unflatten_state
def put(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
checks=[]
def ok(name,v=True):assert bool(v),name;checks.append(name)
put('V1_REVIEW_REJECTION_NEGATIVE_SURVIVAL_SCALE_ACTUAL.json',dict(V1_CPU_checks_passed=20,V1_selected_for_deployment=False,
 reason='V1 unbounded1-HuberCost produced negative failure returns; original native survival weighting could then reduce future penalties by ending imagination. This is a source structural concern, not an observed training failure.',
 correction='V2 uses .06/(1+nonnegative weighted Huber+style deficit+actioncost/6). Positive rewards remove this negative-future-avoidance mechanism; actual optimization gain is not proven.',
 original_V1_source_and_reports_retained=True,no_old_model_or_rollout_repeated=True))
try:
 c=json.loads((B/'job0/assets/import_contract.json').read_bytes());g=json.loads((R2/'DERIVED_GEOMETRY_20260928.json').read_bytes());doc=json.loads((B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json').read_bytes());names=json.loads((B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').read_bytes())['expected_runtime_joint_names']
 provider=ConvertedMOD4Reference(doc).bind_named_order(names,scope='source_CPU_fixture');kin=OwnStepWheelGeometry(c,g,names);mdp=OwnStepDifferentiableMdpV2(provider,kin,('left_crank','left_hip','right_crank','right_hip'));old=ConvertedMOD4JumpMdp(provider,mdp.leg_encoder_joint_names)
 comparisons=[];base=None
 with np.load(R2/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz',allow_pickle=False) as data:
  for seed in (20260928,20260929,20260930):
   packed=torch.from_numpy(data[str(seed)+'_packed127'].copy());frames=torch.from_numpy(data[str(seed)+'_control_age'].astype(np.int64));a=torch.from_numpy(data[str(seed)+'_raw'].copy());previous=torch.cat((torch.zeros_like(a[:1]),a[:-1].clamp(-6,6)),0)
   terms=mdp.objective_terms(unflatten_state(packed),frames,a,previous);ok(str(seed)+'_real_failed_states_rewards_positive_bounded',((terms['total']>0)&(terms['total']<=.06)).all())
   group={}
   for label,mask in [('request100_179',(frames>=100)&(frames<180)),('post200_499',frames>=200)]:group[label]=dict(rows=int(mask.sum()),old_tracking_fraction_mean=float(terms['old_tracking_fraction'][mask].mean()),new_task_score_mean=float(terms['task_score_surrogate'][mask].mean()),new_reward_mean=float(terms['total'][mask].mean()),combined_cost_mean=float(terms['combined_nonnegative_cost'][mask].mean()))
   comparisons.append(dict(seed=seed,groups=group));
   if seed==20260928:base=packed[250:251].clone()
 age=torch.tensor([200]);zero=torch.zeros(1,6);target,_=provider.query(age);aux=torch.zeros(1,54);aux[:,2]=aux[:,5]=1;goal=torch.cat((target,aux),-1)
 gs=float(mdp.objective_terms(unflatten_state(goal),age,zero,zero)['task_score_surrogate'][0]);ok('real_failed_state_under6percent_vs_geometric_goal_near1',gs>.99 and all(r['groups']['post200_499']['new_task_score_mean']<.06 for r in comparisons))
 bs=float(mdp.objective_terms(unflatten_state(base),age,zero,zero)['task_score_surrogate'][0]);raised=base.clone();raised[:,2]+=.27;rs=float(mdp.objective_terms(unflatten_state(raised),age,zero,zero)['task_score_surrogate'][0]);ok('COM_rise_only_still_short_of_platform_scores_low',rs<.2 and rs<gs)
 feature_before=mdp.geometry_costs(unflatten_state(base),age,kin(unflatten_state(base)),kin(unflatten_state(goal)));feature_after=mdp.geometry_costs(unflatten_state(raised),age,kin(unflatten_state(base)),kin(unflatten_state(goal)));ok('COM_rise_same_ground_wheel_geometry_still_no_credit',all(torch.equal(feature_before[k],feature_after[k]) for k in feature_before))
 x=base.clone().requires_grad_(True);reward=mdp.reward(unflatten_state(x),age,zero,zero);grad=torch.autograd.grad(reward.sum(),x)[0];ok('bounded_reward_ground_gradient_forward_and_up',grad[0,0]>0 and grad[0,2]>0)
 early=base.clone();early[:,0]=.45;early.requires_grad_(True);er=mdp.objective_terms(unflatten_state(early),age,zero,zero);eg=torch.autograd.grad(er['total'].sum(),early)[0];ok('early_low_wall_cross_worse_than_ground_and_gradient_back_up',float(er['task_score_surrogate'][0])<bs and eg[0,0]<0 and eg[0,2]>0)
 fd=[]
 for column in (0,2,13+names.index('left_hip')):
  epsilon=.001;plus=base.clone();minus=base.clone();plus[0,column]+=epsilon;minus[0,column]-=epsilon
  numeric=float((mdp.reward(unflatten_state(plus),age,zero,zero)-mdp.reward(unflatten_state(minus),age,zero,zero))/(2*epsilon));analytic=float(grad[0,column]);error=abs(numeric-analytic)/max(.001,abs(numeric),abs(analytic));fd.append(dict(column=column,epsilon=epsilon,analytic=analytic,finite_difference=numeric,relative_error=error))
 ok('bounded_reward_gradient_finite_difference_float32',all(r['relative_error']<.02 for r in fd))
 noforce=goal.clone();noforce[:,73:79]=0;noforce.requires_grad_(True);nr=mdp.reward(unflatten_state(noforce),age,zero,zero);ng=torch.autograd.grad(nr.sum(),noforce)[0];ok('soft_contact_force_deficit_retains_gradient',ng[0,75]>0 and ng[0,78]>0)
 moving=goal.clone();moving[:,7]=.2;moving.requires_grad_(True);mr=mdp.reward(unflatten_state(moving),age,zero,zero);mg=torch.autograd.grad(mr.sum(),moving)[0];ok('soft_stability_opposes_motion',mg[0,7]<0)
 goals=torch.tensor([0,100,145,200,499]);ok('V2_to_preserves_new_class_and_goal1460_exact',isinstance(mdp.to('cpu'),OwnStepDifferentiableMdpV2) and torch.equal(mdp.goal(goals,10),old.goal(goals,10)))
 huge=torch.full((1,6),20.);large=mdp.reward(unflatten_state(base),age,huge,-huge);ok('large_action_rate_cost_still_nonnegative_return',0<float(large[0])<=.06)
 ok('no_CUDA_actor_WM_optimizer_or_new_physics',not torch.cuda.is_initialized() and sum(p.numel() for p in kin.parameters())==0)
 result=dict(passed=True,source_CPU_qualified_only=True,selected_candidate='OwnStepDifferentiableMdpV2',checks=len(checks),check_names=checks,old_vs_new_same_real_derived_states=comparisons,
  counterfactuals=dict(geometric_goal_score=gs,contact1N_is_synthetic_soft_target_not_real=True,actual_failed_ground_score=bs,COM_only_rise27cm_score=rs,COM_rise_same_ground_wheels_geometry_loss_unchanged=True,early_low_wall_cross_score=float(er['task_score_surrogate'][0]),failed_reward_gradient_xz=[float(grad[0,0]),float(grad[0,2])],early_wall_gradient_xz=[float(eg[0,0]),float(eg[0,2])],finite_difference=fd,soft_contact_gradient=[float(ng[0,75]),float(ng[0,78])],soft_stability_gradient_vx=float(mg[0,7])),
  objective_contract=mdp.contract_manifest(),geometry_fidelity_source_report='ACTUAL_NEW_R2_DERIVED_FK_MAPPING_ERRORS_ACTUAL.json',V1_negative_return_rejected=True,
  physical_success_V8_reference_inputs_architecture_normalizers_optimizers_RNG_unchanged=True,actual_new400_SDK_or_training_gain_qualified=False,platform_contact_identity_and_WM_aux_prediction_fidelity_pending=True)
 put('OWN_STEP_OBJECTIVE_V2_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json',result);print(json.dumps(result,indent=2))
except BaseException:
 put('V2_ORIGINAL_OBJECTIVE_INCREMENT_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),checks=checks,old_files_retained=True));raise
