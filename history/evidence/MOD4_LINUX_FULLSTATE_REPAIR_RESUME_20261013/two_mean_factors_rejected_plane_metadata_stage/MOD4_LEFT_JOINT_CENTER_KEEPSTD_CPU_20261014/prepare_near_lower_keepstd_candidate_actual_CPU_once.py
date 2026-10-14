"""New independent near-lower CPU factor from whole2b, never center parent."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import copy,json,hashlib,time,traceback
import numpy as np
import torch
D=Path(__file__).resolve().parent;W=D.parent
ROOT=D/'candidate_near_lower_cpu_v1';assert not ROOT.exists(),'New once candidate root required'
ROOT.mkdir();R=ROOT/'reports';R.mkdir()
SOURCE=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'
SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
KEY='LINUX20K_LEFT_JOINT_LOWER_MARGIN005_KEEP_SAVED_STD_INITIALIZATION_V1'
CENTERKEY='LINUX20K_LEFT_JOINT_CENTER_KEEP_SAVED_STD_INITIALIZATION_V1'
OLDKEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
PROFILE='left_initial_joint_lower_margin005_keep_saved_std_v1'
MODEL=ROOT/'own20k_left_joint_lower_margin005_keep_saved_std_CPU_prepared.pt'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def witness(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def walk(v,path=''):
 if torch.is_tensor(v):yield path,v
 elif isinstance(v,dict):
  for k,x in v.items():yield from walk(x,path+'/'+str(k))
 elif isinstance(v,(tuple,list)):
  for k,x in enumerate(v):yield from walk(x,path+'/'+str(k))
def same(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return type(a)is type(b) and a==b
def digest(v):
 h=hashlib.sha256()
 def visit(x):
  h.update(type(x).__name__.encode());h.update(b'\0')
  if torch.is_tensor(x):h.update(str(x.dtype).encode());h.update(str(tuple(x.shape)).encode());h.update(x.detach().cpu().contiguous().numpy().tobytes())
  elif isinstance(x,np.ndarray):h.update(str(x.dtype).encode());h.update(str(x.shape).encode());h.update(x.tobytes())
  elif isinstance(x,dict):
   for k in sorted(x,key=str):visit(k);visit(x[k])
  elif isinstance(x,(tuple,list)):
   for y in x:visit(y)
  else:h.update(repr(x).encode())
 visit(v);return h.hexdigest()
def counts(c):
 t=list(walk(c));floating=[x for k,x in t if x.is_floating_point()];per=[x for k,x in t if x.ndim and x.shape[0]==20000]
 assert len(t)==195 and len(floating)==107 and len(per)==99 and all(bool(torch.isfinite(x).all()) for x in floating)
 return dict(tensors=195,floating_finite=107,perenv=99,saved_envs=20000)
def accept_source(path):
 assert sha(path)==SOURCE_SHA,'Reject all non2b parents including failedcenter'
 c=torch.load(path,map_location='cpu',weights_only=False);counts(c)
 assert CENTERKEY not in c and KEY not in c and c['independent_terrain_expert']=='E1_WAVE50'
 assert c[OLDKEY]['profile']=='left_initial_joint_margin014_std1_v1'
 return c
def validate(c,b):
 assert set(c)==set(b)|{KEY} and CENTERKEY not in c
 m=c[KEY];assert m['profile']==PROFILE and m['parent_source_SHA']==SOURCE_SHA and m['source_envs']==20000 and m['expert']=='E1_WAVE50'
 assert m['CPU_prepared_only'] and not m['production_adopted'] and not list(walk(m))
 assert c['independent_terrain_expert']=='E1_WAVE50' and c['sensor_DR_state']['n']==20000
 assert c['E1_WAVE50_initial_source_sha256']==b['E1_WAVE50_initial_source_sha256']
 for k in b:
  if k not in ('actor_state_dict','optimizer_state_dict'):assert same(c[k],b[k]),k
 a=c['actor_state_dict'];o=b['actor_state_dict']
 for k in o:
  if k=='mlp.6.weight':assert torch.equal(a[k][0],o[k][1]) and torch.equal(a[k][1:],o[k][1:])
  elif k=='mlp.6.bias':assert torch.equal(a[k][0],o[k][1]-torch.tensor(2*(1.0843-.005),dtype=o[k].dtype)) and torch.equal(a[k][1:],o[k][1:])
  else:assert same(a[k],o[k]),k
 co=c['optimizer_state_dict'];bo=b['optimizer_state_dict'];assert same(co['param_groups'],bo['param_groups']) and set(co['state'])==set(bo['state'])
 for pid,s in bo['state'].items():
  assert set(s)==set(co['state'][pid])
  for field,x in s.items():
   y=co['state'][pid][field]
   if pid in (7,8) and field in ('exp_avg','exp_avg_sq'):assert torch.equal(y[0],torch.zeros_like(x[0])) and torch.equal(y[1:],x[1:])
   else:assert same(x,y),(pid,field)
 assert counts(c)==counts(b)
def stats(x):return dict(min=float(x.min()),mean=float(x.mean()),median=float(x.median()),max=float(x.max()))
try:
 rng=torch.get_rng_state().clone();nprng=digest(np.random.get_state())
 original=accept_source(SOURCE);fp=digest(original);candidate=copy.deepcopy(original)
 a=candidate['actor_state_dict'];b=original['actor_state_dict']
 a['mlp.6.weight'][0].copy_(b['mlp.6.weight'][1]);a['mlp.6.bias'][0].copy_(b['mlp.6.bias'][1]-torch.tensor(2*(1.0843-.005),dtype=b['mlp.6.bias'].dtype))
 for pid in (7,8):
  for field in ('exp_avg','exp_avg_sq'):candidate['optimizer_state_dict']['state'][pid][field][0].zero_()
 candidate[KEY]=dict(profile=PROFILE,parent_source_SHA=SOURCE_SHA,source_envs=20000,expert='E1_WAVE50',parent_old_initializer_KEY=OLDKEY,parent_old_initializer_metadata_exact=True,
  desired_initial_crank_minus_hip_mean_rad=-1.0793,margin_inside_original_lower_rad=.005,only_initial_left_meanrow0_from_actualhiprow1=True,bias_shift_raw=-2*(1.0843-.005),
  std_all6_actual_original_preserved=[float(x) for x in b['distribution.std_param']],only_Adam7_8_meanrow0_moments_cleared=True,all17_Adamstep_and_std_param0_moments_preserved=True,
  original6action_clip_scale_CADprocessor_unchanged=True,no_live_coupling_teacher_heading_truth_gate=True,full20k99perenv_DR_globalnamed_privateRNG_history_exact=True,
  CPU_prepared_only=True,production_adopted=False,GPU_frozen_factor_passed=False,qualified50=False,only_future_new3060_originalWave_full80_frozen_single_factor=True,
  future_actual_all20k_fullrestore_native_PPO_admission_NOT_RUN=True,not_exact_physical_q_or_executed_trajectory_preservation=True)
 validate(candidate,original)
 rows=dict(walk(original));newrows=dict(walk(candidate))
 for k,x in rows.items():
  if x.numel():assert x.untyped_storage().data_ptr()!=newrows[k].untyped_storage().data_ptr(),k
 negative=[]
 for label,mut in [('wrong_profile',lambda c:c[KEY].update(profile='wrong')),('wrong_parent',lambda c:c[KEY].update(parent_source_SHA='0'*64)),('wrong_expert',lambda c:c.update(independent_terrain_expert='E0')),('wrong_marker_expert',lambda c:c[KEY].update(expert='E0')),('wrong_marker_numenv',lambda c:c[KEY].update(source_envs=512)),('wrong_initialsource',lambda c:c.update(E1_WAVE50_initial_source_sha256='0'*64))]:
  x=dict(candidate);x[KEY]=copy.deepcopy(candidate[KEY]);mut(x)
  try:validate(x,original)
  except AssertionError:negative.append(dict(case=label,strict_rejected=True))
  else:raise AssertionError('Wrongcandidate accepted: '+label)
 center=D/'candidate_cpu_v1/own20k_left_joint_center_keep_saved_std_CPU_prepared.pt'
 centerindex=witness(center)
 try:accept_source(center)
 except AssertionError:negative.append(dict(case='failed_center_checkpoint_rejected_as_parent',strict_rejected=True,actual_candidate_index=centerindex))
 else:raise AssertionError('Failedcenter parent accepted')
 assert len(negative)==7
 N=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014'
 revp=N/'reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json';rev=json.loads(revp.read_bytes());assert rev['passed'] and rev['source_SHA']==SOURCE_SHA
 raw=Path(rev['raw']['local_path']);assert sha(raw)==rev['raw']['sha256']
 with np.load(raw) as z:action=torch.from_numpy(z['action']).double();processed=torch.from_numpy(z['processed_action']).double();target=torch.from_numpy(z['guarded_leg_targets']).double();groups=z['group_ids'].copy()
 assert torch.equal(action.clip(-6,6),processed)
 delta=float(a['mlp.6.bias'][0].double()-b['mlp.6.bias'][1].double());planned_mean=(action[:,:,1]+delta).float().double()
 joint=.5*(planned_mean.clip(-6,6)-processed[:,:,1]);lower_margin=joint+1.0843;upper_margin=.85-joint
 assert bool((lower_margin>0).all()) and bool((upper_margin>0).all())
 requested_left=planned_mean.clip(-6,6)*.5
 proposed_guarded_left=torch.maximum(requested_left,processed[:,:,1]*.5-1.0843);proposed_guarded_left=torch.minimum(proposed_guarded_left,processed[:,:,1]*.5+.85)
 targetdiff=proposed_guarded_left-target[:,:,0]
 sigma=b['distribution.std_param'][0].double();hip=processed[:,:,1]
 lo=hip-1.0843/.5;hi=hip+.85/.5;assert bool((lo>-6).all()) and bool((hi<6).all())
 prob=lambda mu:.5*(torch.special.erfc((lo-mu)/(sigma*2**.5))-torch.special.erfc((hi-mu)/(sigma*2**.5)))
 currentp=prob(action[:,:,0]);plannedp=prob(planned_mean)
 assert bool((plannedp>=0).all()) and bool((plannedp<=1).all())
 per=[]
 for i in range(80):per.append(dict(env=i,group=int(groups[i]),actual_raw_hip_domain=stats(action[:,i,1]),planned_mean_raw_left_domain=stats(planned_mean[:,i]),planned_clipped_scaled_joint_difference_rad=stats(joint[:,i]),planned_lower_margin_rad=stats(lower_margin[:,i]),planned_upper_margin_rad=stats(upper_margin[:,i]),difference_from_original_effective_guarded_left_target_rad=stats(targetdiff[:,i]),current_conditional_legal_probability=stats(currentp[:,i]),planned_conditional_legal_probability=stats(plannedp[:,i])))
 # Allrealhip proof: scaled shiftedclip difference lies in[.5delta,0].
 analytic_bound=[.5*delta,0.];assert analytic_bound[0]>-1.0843
 center_review=W/'MOD4_3060_LEFT_CENTER_KEEPSTD_FULL80_FACTOR_20261014/reports/CENTER_FACTOR_DIRECT_PARENT2B_FULL80_PREFIX_ACTUAL_REVIEW.json'
 center_r=json.loads(center_review.read_bytes());assert center_r['passed']
 torch.save(candidate,MODEL)
 with MODEL.open('r+b') as f:os.fsync(f.fileno())
 disk=torch.load(MODEL,map_location='cpu',weights_only=False);assert same(candidate,disk);validate(disk,original)
 assert digest(original)==fp and sha(SOURCE)==SOURCE_SHA and torch.equal(torch.get_rng_state(),rng) and digest(np.random.get_state())==nprng and not torch.cuda.is_initialized()
 manifest=dict(epoch=time.time(),candidate_id='whole20k2b_left_initial_lower_margin005_keep_actualstd_CPU_only_v1',profile=PROFILE,new_private_KEY=KEY,source=witness(SOURCE),candidate=witness(MODEL),CPU_counts=counts(disk),
  allowed_changes=['left meanWrow0 copied actual hipWrow1','left meanbias=actualhipbias−2.1586','Adam7/8 row0 exp_avg,exp_avg_sq zero','new independent nonTensor privateKEY'],
  all195_inherited_tensors_independent_storage=True,std_all6_and_stdMoments_all17steps_exact=True,all_other5heads_trunk_critic_whole20k_DR_RNG_state_exact=True,old13KEY_exact_and_no_centerKEY=True,source_tree_fingerprint_before_after_exact=fp,
  actual_std0=float(sigma),actual_hipbias=float(b['mlp.6.bias'][1]),actual_candidate_leftbias=float(a['mlp.6.bias'][0]),actual_delta_raw=delta,
  actual_saved120000_hip_raw_domain=stats(action[:,:,1]),actual_saved120000_mean_joint_difference_rad=stats(joint),actual_saved120000_lower_margin_rad=stats(lower_margin),actual_saved120000_upper_margin_rad=stats(upper_margin),actual_saved120000_diff_to_parent_guarded_target_rad=stats(targetdiff),
  all_real_rawhip_analytic_mean_joint_bound_rad=analytic_bound,all_real_rawhip_min_lower_margin_rad=analytic_bound[0]+1.0843,all_real_rawhip_min_upper_margin_rad=.85,
  conditional_probability_definition='Fixed saved clipped actual hipmean, original6diagonalNormal leftstd unchanged; not sampled fulljoint/control execution or transit probability.',all80_actual=per,residual7=[x for x in per if x['env'] in [6,15,21,69,72,67,70]],
  no_policy_obs_poststep_actor_replay=True,candidate_samehidden_mean_math_not_GPU_linearKernel_byteexact_claim=True,not_actual_q_or_physical_pose_trajectory_preservation=True,
  CPU_disk_roundtrip_actual_exact=True,CPU_RNG_numpyRNG_before_after_exact=True,negative7_actual_identity_cases=negative,
  center_factor_rejected_actual_report=witness(center_review),center_failed_source_not_adopted=True,center_failure_summary='parent2b22forward25reverse -> center4forward0reverse ordinary179, rootactual completepaired result',
  risks=['Copying hip finalrow loses original learned left-head features.', 'Even .005rad change in target difference is not exact actualq or trajectory preservation.', 'Nearlower mean yields about half conditional leftdraws below CADlower at currentstd; legal mean does not remove exploration clipping.', 'Frozen factor success is required before deciding any further boundedlearning; no production adoption.'],
  prepared_only=True,next_use_only_new3060_originalWave_full80_frozen_factor=True,future_initial_rootq30_params_recipes_assignment_RNG_queue_exactpair_REQUIRED=True,future_GPU_actor_physical_query_contact_COMhardware_actual_REQUIRED=True,
  original1500controls15s80env6000callbacks_040approach_50tenwaves_1N_before_after200mm_unchanged=True,production_adopted=False,GPU_frozen_factor_passed=False,newPPO=False,qualified50=False,
  no_SSH_GPU_PPO_budget_Git_or_installedSDK_mutation=True,Git_archive_pending_root_owner=True)
 mp=ROOT/'CANDIDATE_NEAR_LOWER_CPU_PREPARED_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf8')
 rp=R/'NEAR_LOWER_MARGIN005_CANDIDATE_CPU_ACTUAL_REVIEW.json'
 rp.write_text(json.dumps(dict(epoch=time.time(),passed=True,source=witness(SOURCE),candidate=witness(MODEL),manifest=witness(mp),source_script=witness(__file__),full107finite99perenv_actual=True,all195storage_independent=True,CPUdisk_exact=True,negative7_rejected=True,only_CPU_prepared=True,production_adopted=False,GPU_factor_NOT_run=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 print(json.dumps(dict(candidate=witness(MODEL),report=str(rp),actual_delta=delta,joint_mean=stats(joint),parent_effective_target_difference=stats(targetdiff),conditional_probability=stats(plannedp),CPU_prepared_only=True)))
except Exception:
 (R/f'NEAR_LOWER_CPU_ORIGINAL_ERROR_{time.time_ns()}.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=witness(__file__),no_GPU=True,original_false_retained=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 raise
