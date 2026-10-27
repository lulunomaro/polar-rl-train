"""NEW purpose: derived-only R2 geometry+objective CPU. No old raw or models."""
from pathlib import Path
import csv,hashlib,json,sys,traceback
import numpy as np,torch
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1';R2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
sys.path[:0]=[str(HERE),str(B/'source'),str(B/'source/sm_deps')];torch.set_num_threads(2)
from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry,qmat
from own_step_differentiable_objective_v1 import OwnStepDifferentiableMdp
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
from supermimic_wheel_leg_v3.geometry import unflatten_state
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ok(name,value=True):assert bool(value),name;checks.append(name)
def refuse(name,f):
 try:f()
 except (ValueError,AssertionError,KeyError):ok(name);return
 raise AssertionError('negative accepted '+name)
put('NEW_DERIVED_ONLY_SOURCE_CPU_ENTRY_CONSUMED_ACTUAL.json',dict(purpose='own-step dense objective source+CPU and newR2 derived geometry only',allowed_NPZ=str(R2/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz'),no_old_raw_models_SDK_or_physics=True))
try:
 C=B/'job0/assets/import_contract.json';P=B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json';S=B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'
 contract=json.loads(C.read_bytes());doc=json.loads(P.read_bytes());names=json.loads(S.read_bytes())['expected_runtime_joint_names'];ok('exact9223_source_reference',H(P)=='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3')
 G=R2/'DERIVED_GEOMETRY_20260928.json';geometry=json.loads(G.read_bytes());kin=OwnStepWheelGeometry(contract,geometry,names)
 provider=ConvertedMOD4Reference(doc).bind_named_order(names,scope='source_CPU_fixture');mdp=OwnStepDifferentiableMdp(provider,kin,('left_crank','left_hip','right_crank','right_hip'));old=ConvertedMOD4JumpMdp(provider,mdp.leg_encoder_joint_names)
 motion=R2/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz';mapping=[];comparisons=[];states={};sample_rows=[]
 # The only NPZ opened is the expressly permitted new derived-only artifact.
 with np.load(motion,allow_pickle=False) as data:
  for seed in (20260928,20260929,20260930):
   prefix=str(seed)+'_';packed=torch.from_numpy(data[prefix+'packed127'].copy());frames=torch.from_numpy(data[prefix+'control_age'].astype(np.int64));state=unflatten_state(packed)
   ok(str(seed)+'_500native127_controls',packed.shape==(500,127) and frames.shape==(500,))
   indices=np.arange(500)*4;worldbody=torch.from_numpy(data[prefix+'body_position'][indices].copy());worldquat=torch.from_numpy(data[prefix+'body_quaternion'][indices].copy());worldroot=torch.from_numpy(data[prefix+'root'][indices].copy())
   offsets=worldroot[:,:3]-packed[:,:3];origin=offsets[:1];fk=kin(state);pred=fk['body_position']+origin[:,None,:]
   body_error=(pred-worldbody).norm(dim=-1);Ractual=qmat(worldquat[..., [3,0,1,2]]);rotation_error=(fk['body_rotation']-Ractual).square().sum((-1,-2)).sqrt()
   direct_low=[];direct_high=[]
   for i,name in enumerate(kin.wheel_names):
    bodyid=kin.body_names.index(name);points=getattr(kin,'points'+str(i));points=(Ractual[:,bodyid]@points.T).transpose(-1,-2)+worldbody[:,bodyid,None,:]
    direct_low.append(points.amin(-2));direct_high.append(points.amax(-2))
   direct_low=torch.stack(direct_low,-2);direct_high=torch.stack(direct_high,-2)
   bound_error=torch.cat(((fk['low']+origin[:,None,:]-direct_low).abs().flatten(1),(fk['high']+origin[:,None,:]-direct_high).abs().flatten(1)),1)
   cached_low=torch.from_numpy(data[prefix+'wheel_min'][indices].copy());cached_high=torch.from_numpy(data[prefix+'wheel_max'][indices].copy());valid=torch.isfinite(cached_low).all((-1,-2))&torch.isfinite(cached_high).all((-1,-2))
   cache_error=torch.cat(((direct_low[valid]-cached_low[valid]).abs().flatten(1),(direct_high[valid]-cached_high[valid]).abs().flatten(1)),1)
   mapping.append(dict(seed=seed,aligned_control_state_and_pose_frame_index='4*(control-1); first control index0 uses initial frame0',controls=500,origin_offset_m=origin[0].tolist(),maximum_origin_drift_m=float((offsets-origin).abs().max()),body_position_error_max_m=float(body_error.max()),body_position_error_RMS_m=float(body_error.square().mean().sqrt()),body_error_per_name_max_m={name:float(body_error[:,i].max()) for i,name in enumerate(kin.body_names)},body_rotation_matrix_error_max=float(rotation_error.max()),wheel_support_FK_vs_bodyposes_max_abs_m=float(bound_error.max()),wheel_support_FK_vs_bodyposes_RMS_m=float(bound_error.square().mean().sqrt()),bodypose_support_vs_original_callback_cache_max_abs_m=float(cache_error.max()),valid_original_cache_rows=int(valid.sum()),no_new_physical_tolerance_or_skill_gate=True))
   ok(str(seed)+'_finite_derived_FK_mapping_not_assumed_exact',torch.isfinite(body_error).all() and torch.isfinite(bound_error).all())
   raw=torch.from_numpy(data[prefix+'raw'].copy());previous=torch.cat((torch.zeros_like(raw[:1]),raw[:-1].clamp(-6,6)),0)
   terms=mdp.objective_terms(state,frames,raw,previous)
   groups={}
   for label,mask in [('request100_179',(frames>=100)&(frames<180)),('post200_499',frames>=200)]:
    groups[label]=dict(rows=int(mask.sum()),old_tracking_fraction_mean=float(terms['old_tracking_fraction'][mask].mean()),new_task_score_mean=float(terms['task_score_surrogate'][mask].mean()),new_reward_mean=float(terms['total'][mask].mean()),new_geometry_task_loss_mean=float(terms['geometry_task_loss'][mask].mean()),cost_means={name:float(value[mask].mean()) for name,value in terms.items() if name.endswith('_cost')})
   comparisons.append(dict(seed=seed,groups=groups,not_a_success_probability_or_actual_training_gain=True))
   states[seed]=dict(packed=packed,frames=frames)
   for index in range(500):sample_rows.append(dict(seed=seed,control=index+1,age=int(frames[index]),old_tracking_fraction=float(terms['old_tracking_fraction'][index]),new_task_score=float(terms['task_score_surrogate'][index]),new_reward=float(terms['total'][index]),bottom_cost=float(terms['bottom_cost'][index]),forward_cost=float(terms['forward_cost'][index]),wall_cost=float(terms['wall_cost'][index])))
 put('ACTUAL_NEW_R2_DERIVED_FK_MAPPING_ERRORS_ACTUAL.json',dict(source_only=True,rows=mapping,treeFK_does_not_enforce_closed_loop_contacts=True,no_runtime_physical_qualification=True))
 put('OLD_VS_NEW_OBJECTIVE_ON_SAME_NEW_R2_DERIVED_STATES_ACTUAL.json',dict(rows=comparisons,no_model_or_optimization_or_new_rollout=True))
 # Ideal geometric reference counterfactual with DECLARED soft1N top support,
 # not real contact. Same reference/binary masks/goal/observation dimensions.
 age=torch.tensor([200]);goal,_=provider.query(age);aux=torch.zeros(1,54);aux[:,2]=aux[:,5]=1.;goal127=torch.cat((goal,aux),-1);zero=torch.zeros(1,6)
 gt=mdp.objective_terms(unflatten_state(goal127),age,zero,zero)
 goal_score=float(gt['task_score_surrogate'][0]);ok('geometric_goal_scores_above_all_actual_failed_group_means',all(v['new_task_score_mean']<goal_score for row in comparisons for v in row['groups'].values()))
 # Root-only rise moves the whole robot, but still leaves tires short of edge.
 base=states[20260928]['packed'][250:251].clone();raised=base.clone();raised[:,2]+=.27
 base_terms=mdp.objective_terms(unflatten_state(base),age,zero,zero);raised_terms=mdp.objective_terms(unflatten_state(raised),age,zero,zero)
 ok('root_height_only_short_of_edge_not_geometric_goal',float(raised_terms['task_score_surrogate'][0])<goal_score-.5)
 # Feature-level COM rise while wheels stay fixed on ground: isolate the
 # claimed loophole without pretending that this is a closed-chain rollout.
 bs=unflatten_state(base);rs=unflatten_state(raised);actual=kin(bs);target=kin(unflatten_state(goal127));before=mdp.geometry_costs(bs,age,actual,target);after=mdp.geometry_costs(rs,age,actual,target)
 ok('COM_only_with_same_ground_wheels_gets_no_task_geometry_credit',all(torch.equal(before[k],after[k]) for k in before))
 # Differentiable height/progress direction at the real failed state.
 x=base.clone().requires_grad_(True);reward=mdp.reward(unflatten_state(x),age,zero,zero).sum();gradient=torch.autograd.grad(reward,x)[0]
 ok('failed_ground_state_positive_height_and_forward_gradients',gradient[0,2]>0 and gradient[0,0]>0)
 # Crossing the vertical edge with low tires must be worse, with gradient back
 # from the wall/UP, rather than free forward progress through it.
 early=base.clone();early[:,0]=.45;early.requires_grad_(True);early_terms=mdp.objective_terms(unflatten_state(early),age,zero,zero);eg=torch.autograd.grad(early_terms['total'].sum(),early)[0]
 ok('early_low_cross_wall_has_backward_and_upward_gradients',eg[0,0]<0 and eg[0,2]>0 and float(early_terms['wall_cost'][0])>0)
 # Source finite differences at representative nonzero state coordinates.
 fd=[]
 for column in (0,2,13+names.index('left_hip')):
  epsilon=.0002;plus=base.clone();minus=base.clone();plus[0,column]+=epsilon;minus[0,column]-=epsilon
  value=float((mdp.reward(unflatten_state(plus),age,zero,zero)-mdp.reward(unflatten_state(minus),age,zero,zero))/(2*epsilon));analytic=float(gradient[0,column]);rel=abs(value-analytic)/max(1.,abs(value),abs(analytic));fd.append(dict(column=column,epsilon=epsilon,autograd=analytic,central_finite_difference=value,relative_error=rel))
 ok('FK_task_gradient_finite_difference_agrees_source_float32',all(r['relative_error']<.02 for r in fd))
 # Soft contact/stability remain dense only, never a claim of platform truth.
 noforce=goal127.clone();noforce[:,73:79]=0;noforce.requires_grad_(True);nf=mdp.objective_terms(unflatten_state(noforce),age,zero,zero);ng=torch.autograd.grad(nf['total'].sum(),noforce)[0]
 ok('soft_missing_top_support_force_has_positive_force_gradient',ng[0,75]>0 and ng[0,78]>0)
 moving=goal127.clone();moving[:,7]=.2;moving.requires_grad_(True);mr=mdp.reward(unflatten_state(moving),age,zero,zero);mg=torch.autograd.grad(mr.sum(),moving)[0]
 ok('soft_stability_velocity_gradient_opposes_motion',mg[0,7]<0)
 frames=torch.tensor([0,100,145,200,499]);ok('future10_goal1460_literal_unchanged',mdp.goal(frames,10).shape==(5,1460) and torch.equal(mdp.goal(frames,10),old.goal(frames,10)))
 ps,_=provider.query(frames);fake=unflatten_state(torch.cat((ps,torch.zeros(5,54)),-1));context=torch.zeros(5,31);previous=torch.zeros(5,6)
 ok('actor86_critic_features_and_context31_interfaces_unchanged',mdp.obs(fake,previous,context,frames).shape==(5,86) and torch.equal(mdp.obs(fake,previous,context,frames),old.obs(fake,previous,context,frames)) and torch.equal(mdp.critic_features(fake,frames,context),old.critic_features(fake,frames,context)))
 refuse('wrong_named_joint_set_rejected',lambda:OwnStepWheelGeometry(contract,geometry,['missing']+names[1:]))
 refuse('old73_without_aux54_rejected',lambda:kin(tuple(fake[:6])))
 counterfactuals=dict(geometric_reference_age200_score=goal_score,geometric_reference_contacts_are_synthetic1N_not_real=True,real_failed_ground_score=float(base_terms['task_score_surrogate'][0]),root_only_rise27cm_score=float(raised_terms['task_score_surrogate'][0]),COM_rise_same_ground_wheels_geometry_costs_literal_equal=True,early_low_cross_wall_score=float(early_terms['task_score_surrogate'][0]),early_wall_gradient_xz=[float(eg[0,0]),float(eg[0,2])],failed_state_reward_gradient_xz=[float(gradient[0,0]),float(gradient[0,2])],finite_difference=fd,contact_gradient_left_right=[float(ng[0,75]),float(ng[0,78])],moving_base_vx_gradient=float(mg[0,7]),all_counterfactuals_are_source_or_feature_analytic_not_rollouts=True)
 put('COUNTERFACTUAL_AND_GRADIENT_DIRECTION_CPU_ACTUAL.json',counterfactuals)
 with (HERE/'NEW_DERIVED_OLD_NEW_OBJECTIVE_PER_CONTROL.csv').open('x',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(sample_rows[0]));writer.writeheader();writer.writerows(sample_rows)
 inputs=[C,P,S,G,motion,B/'source/converted_MOD4_jump_mdp_v4.py'];put('SOURCE_INPUT_SHA_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in inputs],only_explicitly_allowed_new_derived_NPZ_read=True,no_old_raw_PT_USD_or_physics=True))
 ok('no_new_trainable_parameters_or_CUDA',sum(p.numel() for p in kin.parameters())==0 and not torch.cuda.is_initialized())
 put('OWN_STEP_OBJECTIVE_SOURCE_CPU_QUALIFIED_NOT_ADMITTED_ACTUAL.json',dict(passed=True,source_CPU_qualified_only=True,checks=len(checks),check_names=checks,objective_contract=mdp.contract_manifest(),counterfactuals=counterfactuals,recorded_FK_errors=mapping,
  physical_success_changed=False,reference9223_and_interfaces_literal_unchanged=True,actual_SDK_new400N_and_model_or_training_gain_admitted=False,soft_force_proxy_is_not_platform_contact_truth=True,contact_model_fidelity_and_nonwheel_collision_terms_pending=True))
 print(json.dumps(dict(source_CPU_passed=True,checks=len(checks),mapping=mapping,comparisons=comparisons,counterfactuals=counterfactuals),indent=2))
except BaseException:
 put('ORIGINAL_OWN_STEP_OBJECTIVE_SOURCE_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),checks=checks,derived_only_partial_results_preserved=True,no_old_raw_or_model_or_runtime=True));raise
