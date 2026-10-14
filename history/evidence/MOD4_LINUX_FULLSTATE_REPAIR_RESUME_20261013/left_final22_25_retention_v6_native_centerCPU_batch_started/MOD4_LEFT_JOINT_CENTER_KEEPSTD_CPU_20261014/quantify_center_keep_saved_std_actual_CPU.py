"""CPU mathematical plan only: actual20k source, no candidate/checkpoint write.

Copying the existing final hip row to the left row and subtracting .2343 from
the hip bias gives a same-hidden-input mathematical difference of -.2343 raw,
or -.11715rad after scale. CPU mapped saved hip means are counterfactual mean
math at the old observed states; they are not GPU actor or physical rollouts.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,json,time,traceback,math
import numpy as np
import torch
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf')
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
SOURCE=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'
SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
OUT=R/'JOINT_CENTER_KEEP_ACTUAL_STD_CPU_MATH_ACTUAL_REVIEW.json';assert not OUT.exists()
NEW=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014'
PROFILE='left_initial_joint_interval_center_keep_saved_std_v1'
NEWKEY='LINUX20K_LEFT_JOINT_CENTER_KEEP_SAVED_STD_INITIALIZATION_V1'
OLDKEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def tensor_sha(t):return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
def walk(v,k=''):
 if torch.is_tensor(v):yield k,v
 elif isinstance(v,dict):
  for n,x in v.items():yield from walk(x,k+'/'+str(n))
 elif isinstance(v,(list,tuple)):
  for n,x in enumerate(v):yield from walk(x,k+'/'+str(n))
def digest(v):
 h=hashlib.sha256()
 def visit(x):
  h.update(type(x).__name__.encode());h.update(b'\0')
  if torch.is_tensor(x):
   h.update(str(x.dtype).encode());h.update(str(tuple(x.shape)).encode());h.update(x.detach().cpu().contiguous().numpy().tobytes())
  elif isinstance(x,np.ndarray):h.update(str(x.dtype).encode());h.update(str(x.shape).encode());h.update(x.tobytes())
  elif isinstance(x,dict):
   for k in sorted(x,key=lambda n:str(n)):visit(k);visit(x[k])
  elif isinstance(x,(tuple,list)):
   for y in x:visit(y)
  else:h.update(repr(x).encode())
 visit(v);return h.hexdigest()
def stats(x):return dict(min=float(x.min()),mean=float(x.mean()),median=float(x.median()),max=float(x.max()))
def legal_probability(mu,hip,sigma):
 lo=(hip-1.0843/.5).clamp(min=-6);hi=(hip+.85/.5).clamp(max=6)
 # All actual hipmean here is far from outer clip; mathematical exact interval.
 assert bool((lo>-6).all()) and bool((hi<6).all())
 p=.5*(torch.special.erfc((lo-mu)/(sigma*2**.5))-torch.special.erfc((hi-mu)/(sigma*2**.5)))
 assert bool((p>=0).all()) and bool((p<=1).all())
 return p,lo,hi
try:
 rngbefore=torch.get_rng_state().clone();npbefore=digest(np.random.get_state())
 assert SOURCE.stat().st_size==19044152 and sha(SOURCE)==SHA
 ck=torch.load(SOURCE,map_location='cpu',weights_only=False)
 source_digest=digest(ck);allT=list(walk(ck));floating=[(k,t) for k,t in allT if t.is_floating_point()];perenv=[(k,t) for k,t in allT if t.ndim and t.shape[0]==20000]
 assert len(floating)==107 and len(perenv)==99 and all(bool(torch.isfinite(t).all()) for k,t in floating)
 assert ck['sensor_DR_state']['n']==20000 and ck['independent_terrain_expert']=='E1_WAVE50'
 assert ck[OLDKEY]['profile']=='left_initial_joint_margin014_std1_v1' and NEWKEY not in ck
 A=ck['actor_state_dict'];O=ck['optimizer_state_dict'];std=A['distribution.std_param']
 assert std.shape==(6,) and float(std[0])==0.6773233413696289
 assert A['mlp.6.weight'].shape==(6,64) and A['mlp.6.bias'].shape==(6,)
 assert O['state'][7]['exp_avg'].shape==(6,64) and O['state'][8]['exp_avg'].shape==(6,)
 assert O['state'][0]['exp_avg'].shape==(6,)
 # Scalar arithmetic only. No actor state cloned/mutated/materialized.
 hipbias=A['mlp.6.bias'][1]
 plannedbias=hipbias-torch.tensor(.2343,dtype=hipbias.dtype)
 delta=float(plannedbias.double()-hipbias.double())
 reviewpath=NEW/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'
 review=json.loads(reviewpath.read_bytes());assert review['source_SHA']==SHA and review['passed']
 raw=Path(review['raw']['local_path']);assert sha(raw)==review['raw']['sha256']
 with np.load(raw) as z:a=torch.from_numpy(z['action']).double();group=z['group_ids'].copy();term=z['terminated'];trunc=z['truncated']
 assert a.shape==(1500,80,6) and not term.any() and not trunc.any()
 hipraw=a[:,:,1];hip=hipraw.clip(-6,6)
 # Derived hypothetical same-hidden mean. Actual saved policy_obs is excluded.
 mean_math=hipraw+delta;mean_cpu_float32=mean_math.float().double()
 afterdiff=.5*(mean_cpu_float32.clip(-6,6)-hip)
 lowermargin=afterdiff+1.0843;uppermargin=.85-afterdiff
 assert bool((lowermargin>0).all()) and bool((uppermargin>0).all())
 oldprob,lo,hi=legal_probability(a[:,:,0],hip,std[0].double())
 plannedprob,_,_=legal_probability(mean_cpu_float32,hip,std[0].double())
 actual_rows=[]
 completed={r['env']:r['contact_complete'] for r in review['rows']}
 for i in range(80):
  actual_rows.append(dict(env=i,group=int(group[i]),standing=int(group[i])==2,baseline_complete_original_protocol=completed[i],actual_hip_raw_domain=stats(hipraw[:,i]),current_raw_left_mean_domain=stats(a[:,i,0]),planned_same_hidden_left_mean_math_domain=stats(mean_cpu_float32[:,i]),planned_clipped_scaled_mean_joint_difference_rad=stats(afterdiff[:,i]),planned_lower_margin_rad=stats(lowermargin[:,i]),planned_upper_margin_rad=stats(uppermargin[:,i]),current_conditional_legal_probability=stats(oldprob[:,i]),planned_conditional_legal_probability=stats(plannedprob[:,i]),current_last3s_conditional_probability=stats(oldprob[-300:,i]),planned_last3s_conditional_probability=stats(plannedprob[-300:,i])))
 # Analytic full real rawhip domain: clip is monotonic and1-Lipschitz, so
 # clip(h+delta)-clip(h) is in[delta,0]. No random fixture is used.
 globaldiffrange=[.5*delta,0.]
 globalmargin=[1.0843+.5*delta,.85]
 assert globaldiffrange[0]>-1.0843 and globaldiffrange[1]<.85
 deterministic_edge_hips=torch.tensor([-1e9,-6.2343,-6.,-5.7657,-1.,0.,1.,5.7657,6.,6.2343,1e9],dtype=torch.float64)
 edge_diff=.5*((deterministic_edge_hips+delta).clip(-6,6)-deterministic_edge_hips.clip(-6,6))
 assert bool((edge_diff>=.5*delta-1e-7).all()) and bool((edge_diff<=1e-7).all())
 sourcefiniteproof=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/reports/LEFT_FORMAL_FINAL_LOCAL_CPU_AND_FROZEN80_CANDIDATE_PREPARED.json'
 assert json.loads(sourcefiniteproof.read_bytes())['whole107finite']
 requires=dict(CPU_prepared_only=True,new_profile=PROFILE,new_private_DICT_KEY=NEWKEY,initial_source_SHA=SHA,old_left_marker_must_remain_historical_and_exact=OLDKEY,old_fullstate_13_sameidentity_markers_first=True,new_mean_initializer_marker_fourteenth_prepared_not_run=True,
  actor_critic_std_optimizer_allDR_globalnamed_dictprivate_CPU_CUDA_before_axis_strict=True,
  one_time_new_left_final_meanrow0_copy_existing_hiprow1=True,bias_shift_raw=-.2343,expected_ideal_joint_mean_rad=-.11715,
  all_other5_heads_std_sharedtrunk_critic_full20k99perenv_DR_RNG_terrain_entry_direction_route_lifetime_initial_exact_required=True,
  Adam_only_param7_and8_meanrow0_exp_avg_exp_avg_sq_zeroed=True,Adam_param0_std_moments_and_all17_step_counters_exact=True,
  actual_all20k_offset_defaultq_scale_required_before_new_GPU_use=True,new_mark_saved_and_CUDA_disk_roundtrip_episode_plus_one_required=True,
  same_new_identity_no_repeat_initializer_required=True,wrong_source_expert_numenv_profile_legacy_ancestry_existing_new_key_negative_admission_required=True,
  hardware_solver_geometry_original6action_clip_scale_CADprocessor_DR_reward_LR_clock_commands_unchanged_required=True,no_live_coupling_teacher_heading_truth_gate=True,
  native_fullstate_PPO_fresh_and_complete_fourcase_actual_behavior_not_run=True,prepared_is_not_GPU_PPO_or_passability_admission=True,qualified50=False)
 assert digest(ck)==source_digest and sha(SOURCE)==SHA
 assert torch.equal(torch.get_rng_state(),rngbefore) and digest(np.random.get_state())==npbefore and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed=True,scope='Independent CPU mathematics only, no candidate weights written or actor state changed',source=dict(path=str(SOURCE),bytes=SOURCE.stat().st_size,sha256=SHA,full107floating_finite=True,perenv99_count_actual=True,whole_saved_envs=20000),actual_source_CPU_state_fingerprint_before_after=source_digest,
  actual_std_all6=std.tolist(),planned_std_all6_exact_unchanged=True,actual_hip_final_bias=float(hipbias),planned_left_final_bias_scalar=float(plannedbias),actual_float32_bias_delta_raw=delta,ideal_bias_delta_raw=-.2343,ideal_joint_interval_center_rad=(-1.0843+.85)*.5,
  planned_weightrow_source_actual_hiprow1_sha256=tensor_sha(A['mlp.6.weight'][1]),actual_leftrow0_current_sha256=tensor_sha(A['mlp.6.weight'][0]),actual_std_sha256=tensor_sha(std),Adam_all_actual_step_values={str(k):float(v['step']) for k,v in O['state'].items()},
  original_mean_processor_math='clip each rawhead[-6,6]*.5, original CAD crank lowerhip-1.0843 upperhip+.85. No q mechanical limits substituted.',
  global_real_rawhip_domain_analytic_proof='For delta<0, monotone1-Lipschitz clip(h+delta)-clip(h) lies in[delta,0] for every real h. Therefore scaled planned mean difference lies in[.5delta,0], strictly inside[-1.0843,.85].',
  all_real_rawhip_planned_mean_diff_bound_rad=globaldiffrange,all_real_rawhip_min_lower_margin_rad=globalmargin[0],all_real_rawhip_min_upper_margin_rad=globalmargin[1],deterministic_edge_math_not_RNG_fixture=[dict(rawhip=float(h),scaled_mean_diff=float(v)) for h,v in zip(deterministic_edge_hips,edge_diff)],
  actual_saved80_all120000_hip_raw_domain=stats(hipraw),actual_saved80_all120000_planned_mean_within_domain=True,actual_saved80_all120000_planned_lower_margin_rad=stats(lowermargin),actual_saved80_all120000_planned_upper_margin_rad=stats(uppermargin),
  conditional_probability_definition='Saved independent leftNormal std.677323 held unchanged, hip fixed at saved observed frozen mean; compares old/current rawleft mean with planned center samehidden mathematical mean. Not full joint sampled hip/crank, actual physical control or passability probability.',
  candidate_samehidden_raw_mean_math_has_not_been_GPU_executed=True,CPUfloat32_relation_is_not_CUDA_linear_kernel_byteexact_claim=True,saved_policy_obs_poststep_not_replayed_or_claimed_samecontrol=True,actual_all80=actual_rows,residual7=[r for r in actual_rows if r['env'] in [6,15,21,67,69,70,72]],
  whole_source_proof_reference=dict(path=str(sourcefiniteproof),sha256=sha(sourcefiniteproof)),actual_raw_index=review['raw'],fullstate_prepared_requirements=requires,
  comparison_retained=dict(old512_same_center_meanonly_factor='Different17b512 source/std~23.67,1/7 ordinary20 rejected. This is not same20kstd/source causal evidence.',old512_margin014_meanonly='0/7 ordinary3 rejected, source512 remains inadmissible for new20k training.',current20k_margin014std1_initialization='Own189PPO then2b currently std.677323 and joint lower projection99.998765%; forward22vs7 reverse25vs27, full original physical threshold preserved. Changes normalcoadaptation otherheads, not solecause.',other3skills='Still pending actual complete behavior at task handoff; cannot choose/adopt center plan as production source.'),
  risks=['One-time interior mean may alter leg posture enough to damage flat/spin/world/terrain skills; CPU legal-domain math does not prove stable mechanics.', 'Keeping std.677323 improves conditional legal probability only at initialization; normalPPO can move mean back outside jointdomain.', 'Future actions alter lastaction/observations/physical trajectory; frozen oldstate mean transformation is not candidate trajectory replay.'],
  no_new_checkpoint_or_weight_file=True,no_source_mutation=True,no_CPU_RNG_draw=True,no_CUDA_initialized=True,no_SSH_GPU_PPO_budget_or_Gitcommit=True,only_second_learning_block_can_be_selected_after_actual_scope_decision_no_blind_third=True,Git_archive_pending_root_owner=True)
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(OUT),actualstd0=float(std[0]),plannedbias=float(plannedbias),jointmean_domain=stats(afterdiff),min_conditional_probability=float(plannedprob.min()),max_conditional_probability=float(plannedprob.max()),residual=[dict(env=r['env'],current_prob=r['current_conditional_legal_probability']['mean'],planned_prob=r['planned_conditional_legal_probability']['mean']) for r in out['residual7']],no_weight_written=True)))
except Exception:
 p=R/f'CPU_CENTER_PLAN_ORIGINAL_ERROR_{time.time_ns()}.json'
 p.write_text(json.dumps(dict(error=traceback.format_exc(),source_script=str(__file__),source_script_sha256=sha(__file__),no_GPU=True,no_new_weight_file=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 raise
