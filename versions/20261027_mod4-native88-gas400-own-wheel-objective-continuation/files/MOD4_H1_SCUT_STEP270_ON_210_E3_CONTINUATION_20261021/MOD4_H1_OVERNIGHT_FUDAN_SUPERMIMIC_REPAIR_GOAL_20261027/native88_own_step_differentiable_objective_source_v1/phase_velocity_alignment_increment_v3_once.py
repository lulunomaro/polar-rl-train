"""New phase-coherence increment; only allowed derived NPZ, no old raw/model."""
from pathlib import Path
import ast,copy,hashlib,json,sys,traceback
import numpy as np,torch
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];B=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1';R2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
sys.path[:0]=[str(HERE),str(B/'source'),str(B/'source/sm_deps')];torch.set_num_threads(2)
from own_step_differentiable_objective_v2 import build_own_step_mdp
from supermimic_wheel_leg_v3.geometry import unflatten_state
def read(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (HERE/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
checks=[]
def ok(n,v=True):assert bool(v),n;checks.append(n)
put('PREVIOUS_CONTACT_PHASE_STOP_TARGET_ERRATUM_ACTUAL.json',dict(original_source_preserved='OBJECTIVE_BEFORE_PHASE_VELOCITY_ALIGNMENT.txt',original_report_preserved=True,
 reason='Support_age165 is vertical settling; horizontal reference brakes145..185. A zero-speed soft stable target starting during contact conflicted with that reference. This is a source semantic issue, not a runtime failure.',
 correction='Track same reference wheel-center/root/omega velocities through brake; after reference stop they naturally become0. No clock/reference/command/physical success changed.',
 prior_failure_state_post200_and_gradient_results_still_apply_because_reference_velocities_are0=True,no_old_raw_model_or_actual_run_repeated=True))
try:
 c=read(B/'job0/assets/import_contract.json');g=read(R2/'DERIVED_GEOMETRY_20260928.json');ref=read(B/'source/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json');names=read(B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json')['expected_runtime_joint_names']
 mdp=build_own_step_mdp(c,g,ref,names,('left_crank','left_hip','right_crank','right_hip'),order_scope='source_CPU_fixture');zero=torch.zeros(1,6)
 age=torch.tensor([170]);p,_=mdp.provider.query(age);aux=torch.zeros(1,54);aux[:,2]=aux[:,5]=1;goal=torch.cat((p,aux),-1)
 ideal=mdp.objective_terms(unflatten_state(goal),age,zero,zero)
 stopped=goal.clone();stopped[:,7:13]=0;stopped[:,43:73]=0;stopped_terms=mdp.objective_terms(unflatten_state(stopped),age,zero,zero)
 ok('reference170_brake_not_forced_to_earlier_zero_speed',abs(float(p[0,7]))>.1 and float(ideal['stable_cost'][0])==0 and float(stopped_terms['stable_cost'][0])>0)
 ok('reference_brake_target_beats_premature_stop',ideal['total'][0]>stopped_terms['total'][0])
 comparisons=[];base=None
 with np.load(R2/'NEW_FIXED_R2_MOTION_DERIVED_ONLY.npz',allow_pickle=False) as data:
  for seed in (20260928,20260929,20260930):
   packed=torch.from_numpy(data[str(seed)+'_packed127'].copy());frames=torch.from_numpy(data[str(seed)+'_control_age'].astype(np.int64));a=torch.from_numpy(data[str(seed)+'_raw'].copy());previous=torch.cat((torch.zeros_like(a[:1]),a[:-1].clamp(-6,6)),0)
   terms=mdp.objective_terms(unflatten_state(packed),frames,a,previous);groups={}
   for label,mask in [('request100_179',(frames>=100)&(frames<180)),('post200_499',frames>=200)]:groups[label]=dict(old_tracking_fraction_mean=float(terms['old_tracking_fraction'][mask].mean()),new_task_score_mean=float(terms['task_score_surrogate'][mask].mean()),new_reward_mean=float(terms['total'][mask].mean()),stable_cost_mean=float(terms['stable_cost'][mask].mean()))
   comparisons.append(dict(seed=seed,groups=groups));ok(str(seed)+'_all_new_rewards_positive_and_failed_post200_under6percent',((terms['total']>0)&(terms['total']<=.06)).all() and groups['post200_499']['new_task_score_mean']<.06)
   if seed==20260928:base=packed[250:251].clone()
 age=torch.tensor([200]);p,_=mdp.provider.query(age);goal=torch.cat((p,aux),-1);gt=mdp.objective_terms(unflatten_state(goal),age,zero,zero);ok('poststop_geometric_goal_unchanged',gt['stable_cost'][0]==0 and gt['task_score_surrogate'][0]>.99)
 x=base.clone().requires_grad_(True);reward=mdp.reward(unflatten_state(x),age,zero,zero);gradient=torch.autograd.grad(reward.sum(),x)[0];ok('post200_forward_up_gradient_preserved',gradient[0,0]>0 and gradient[0,2]>0)
 # Verify final inherited interface methods are still literally base methods.
 from converted_MOD4_jump_mdp_v4 import ConvertedMOD4JumpMdp
 ok('all_nonreward_MDP_methods_inherit_exact_original_functions',all(getattr(type(mdp),name) is getattr(ConvertedMOD4JumpMdp,name) for name in ('obs','critic_features','goal','relative_features','normalize_context','add_noise','soft_termination','valid_imagination_start')))
 # Geometry fields+points must be identical for all three independent SDK runs.
 ok('three_derived_geometry_body_shapes_equal',all(all(read(R2/('DERIVED_GEOMETRY_'+str(seed)+'.json'))[field]==g[field] for field in ('body_names','shapes','geometry')) for seed in (20260929,20260930)))
 for f in HERE.glob('*.py'):ast.parse(f.read_bytes())
 put('PHASE_COHERENT_V2_FINAL_SOURCE_CPU_INCREMENT_ACTUAL.json',dict(passed=True,checks=len(checks),check_names=checks,old_vs_new_same_real_derived_states=comparisons,
  brake_counterfactual=dict(age170_reference_vx=float(p[0,7]) if False else float(mdp.provider.query(torch.tensor([170]))[0][0,7]),reference_stable_cost=float(ideal['stable_cost'][0]),premature_stop_stable_cost=float(stopped_terms['stable_cost'][0]),reference_reward=float(ideal['total'][0]),premature_stop_reward=float(stopped_terms['total'][0])),
  contact_stop_clock_or_goals_not_changed=True,source_interface_and_all3_geometry_equality_verified=True,no_actual_models_SDK_or_training=True))
 print(json.dumps(dict(passed=True,checks=len(checks),comparisons=comparisons,brake_reference_stable=float(ideal['stable_cost'][0]),brake_premature_stop_stable=float(stopped_terms['stable_cost'][0])),indent=2))
except BaseException:
 put('V3_ORIGINAL_PHASE_ALIGNMENT_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),checks=checks,originals_retained=True));raise
