"""Explicitly authorized CPU candidate only; no deployment/GPU/PPO/SSH/Git.

Standalone new-root preparation; immutable original2b whole20k remains source.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import copy,hashlib,json,time,traceback
import torch,numpy as np
W=Path(r'C:/Users/lulu/Desktop/claude/mjcf');D=Path(__file__).resolve().parent
ROOT=D/'candidate_cpu_v1';assert not ROOT.exists(),'Once only: no overwrite/recreate candidate root'
ROOT.mkdir();R=ROOT/'reports';R.mkdir()
SOURCE=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt'
SOURCESHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
KEY='LINUX20K_LEFT_JOINT_CENTER_KEEP_SAVED_STD_INITIALIZATION_V1'
OLDKEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
PROFILE='left_initial_joint_interval_center_keep_saved_std_v1'
MODEL=ROOT/'own20k_left_joint_center_keep_saved_std_CPU_prepared.pt'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def witness(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def walk(v,k=''):
 if torch.is_tensor(v):yield k,v
 elif isinstance(v,dict):
  for n,x in v.items():yield from walk(x,k+'/'+str(n))
 elif isinstance(v,(list,tuple)):
  for n,x in enumerate(v):yield from walk(x,k+'/'+str(n))
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
   for k in sorted(x,key=lambda q:str(q)):visit(k);visit(x[k])
  elif isinstance(x,(tuple,list)):
   for y in x:visit(y)
  else:h.update(repr(x).encode())
 visit(v);return h.hexdigest()
def counts(ck):
 rows=list(walk(ck));floats=[(k,t) for k,t in rows if t.is_floating_point()]
 assert len(floats)==107 and all(bool(torch.isfinite(t).all()) for k,t in floats)
 per=[(k,t) for k,t in rows if t.ndim and t.shape[0]==20000];assert len(per)==99
 return dict(tensors=len(rows),finite_floating_tensors=len(floats),perenv_fields=len(per),saved_envs=20000)
def validate_identity(c,source):
 assert c['sensor_DR_state']['n']==20000 and c['independent_terrain_expert']=='E1_WAVE50'
 assert c['E1_WAVE50_initial_source_sha256']==source['E1_WAVE50_initial_source_sha256']
 mark=c[KEY]
 assert mark['profile']==PROFILE and mark['parent_source_SHA']==SOURCESHA
 assert mark['source_envs']==20000 and mark['expert']=='E1_WAVE50'
 assert mark['CPU_prepared_only'] and not mark['GPU_frozen_factor_passed'] and not mark['production_adopted']
 assert same(c[OLDKEY],source[OLDKEY]) and not list(walk(mark))
 assert counts(c)==counts(source)
def validate_changes(c,b):
 assert set(c)==set(b)|{KEY}
 for k in b:
  if k not in ('actor_state_dict','optimizer_state_dict'):assert same(c[k],b[k]),k
 ca=c['actor_state_dict'];ba=b['actor_state_dict']
 for k in ba:
  if k=='mlp.6.weight':
   assert torch.equal(ca[k][0],ba[k][1]) and torch.equal(ca[k][1:],ba[k][1:])
  elif k=='mlp.6.bias':
   assert torch.equal(ca[k][0],ba[k][1]-torch.tensor(.2343,dtype=ba[k].dtype)) and torch.equal(ca[k][1:],ba[k][1:])
  else:assert same(ca[k],ba[k]),k
 bo=b['optimizer_state_dict'];co=c['optimizer_state_dict']
 assert same(bo['param_groups'],co['param_groups']) and set(bo['state'])==set(co['state'])
 for pid,old in bo['state'].items():
  new=co['state'][pid];assert set(old)==set(new)
  for field,val in old.items():
   if pid in (7,8) and field in ('exp_avg','exp_avg_sq'):
    assert torch.equal(new[field][0],torch.zeros_like(val[0])) and torch.equal(new[field][1:],val[1:])
   else:assert same(new[field],val),(pid,field)
 assert same(ca['distribution.std_param'],ba['distribution.std_param'])
 validate_identity(c,b)
try:
 rng=torch.get_rng_state().clone();numpy_rng=digest(np.random.get_state())
 assert SOURCE.stat().st_size==19044152 and sha(SOURCE)==SOURCESHA
 original=torch.load(SOURCE,map_location='cpu',weights_only=False);original_fingerprint=digest(original);counts(original)
 assert KEY not in original and float(original['actor_state_dict']['distribution.std_param'][0])==.6773233413696289
 plan=copy.deepcopy(original)
 a=plan['actor_state_dict'];b=original['actor_state_dict']
 a['mlp.6.weight'][0].copy_(b['mlp.6.weight'][1]);a['mlp.6.bias'][0].copy_(b['mlp.6.bias'][1]-torch.tensor(.2343,dtype=b['mlp.6.bias'].dtype))
 for pid in (7,8):
  for field in ('exp_avg','exp_avg_sq'):plan['optimizer_state_dict']['state'][pid][field][0].zero_()
 plan[KEY]=dict(profile=PROFILE,parent_source_SHA=SOURCESHA,source_envs=20000,expert='E1_WAVE50',original_accepted35_initial_source_SHA=original['E1_WAVE50_initial_source_sha256'],
   source_old_initializer_KEY=OLDKEY,original_old_initializer_metadata_retained_exact=True,
   desired_initial_crank_minus_hip_mean_rad=-.11715,only_initial_meanrow0_W_from_actualhiprow1_and_bias_shift_raw=-.2343,
   actual_saved_std_all6_preserved=[float(x) for x in b['distribution.std_param']],
   only_Adam_meanrow0_param7_8_exp_avg_exp_avg_sq_cleared=True,Adam_std_param0_moments_and_all17_steps_preserved=True,
   all_99_perenv_whole20k_fields_DR_RNG_hist_terrain_entry_direction_route_lifetime_preserved_exact=True,
   no_live_action_coupling_teacher_heading_correction=True,original6action_clip_scale_CADprocessor_reward_DR_clock_hardware_unchanged=True,
   CPU_prepared_only=True,GPU_frozen_factor_passed=False,production_adopted=False,qualified50=False,
   actual_all20k_action_offset_defaultq_scale_requires_future_contract=True,
   future_fullstate_GPU_restore_NEW_KEY_CPUCUDA_disk_roundtrip_episode_plus_one_NOT_RUN=True,
   current_next_use_only_new3060_original_full80_frozen_single_factor=True)
 validate_changes(plan,original)
 oldrows=dict(walk(original));newrows=dict(walk(plan))
 independent=[]
 for k,old in oldrows.items():
  new=newrows[k]
  assert old.device.type=='cpu' and new.device.type=='cpu'
  if old.numel():assert old.untyped_storage().data_ptr()!=new.untyped_storage().data_ptr(),k
  independent.append(k)
 negative=[]
 for case,mut in [
  ('wrong_profile',lambda c:c[KEY].update(profile='wrong_profile')),
  ('wrong_parent_SHA',lambda c:c[KEY].update(parent_source_SHA='0'*64)),
  ('wrong_expert',lambda c:c.update(independent_terrain_expert='E0')),
  ('wrong_marker_expert',lambda c:c[KEY].update(expert='E0')),
  ('wrong_marker_numenv',lambda c:c[KEY].update(source_envs=512)),
  ('wrong_ancestral_initial_source',lambda c:c.update(E1_WAVE50_initial_source_sha256='0'*64))]:
  # Isolated metadata views; no tensor writes and no expensiveRNG fixture.
  x=dict(plan);x[KEY]=copy.deepcopy(plan[KEY]);mut(x)
  try:validate_identity(x,original)
  except AssertionError:negative.append(dict(case=case,strict_rejected=True))
  else:raise AssertionError('Wrong identity accepted: '+case)
 assert len(negative)==6
 torch.save(plan,MODEL)
 with MODEL.open('r+b') as f:os.fsync(f.fileno())
 disk=torch.load(MODEL,map_location='cpu',weights_only=False)
 assert same(plan,disk);validate_changes(disk,original)
 assert digest(original)==original_fingerprint and sha(SOURCE)==SOURCESHA
 assert torch.equal(torch.get_rng_state(),rng) and digest(np.random.get_state())==numpy_rng and not torch.cuda.is_initialized()
 mathproof=D/'reports/JOINT_CENTER_KEEP_ACTUAL_STD_CPU_MATH_ACTUAL_REVIEW.json'
 math=json.loads(mathproof.read_bytes());assert math['passed'] and math['source']['sha256']==SOURCESHA
 manifest=dict(epoch=time.time(),candidate_id='whole20k2b_left_initial_center_keep_actualstd_CPU_only_v1',profile=PROFILE,new_private_KEY=KEY,
   source=witness(SOURCE),candidate=witness(MODEL),math_actual_reference=witness(mathproof),fullstate_cpu_counts=counts(disk),
   source_fulltree_fingerprint_before_after_exact=original_fingerprint,
   original_old_initializer_metadata_exact=True,all_other5_mean_std_sharedtrunk_critic_DR_RNG_fields_exact=True,
   all195_inherited_tensor_storage_independent_from_parent_source=True,independent_storage_field_paths=independent,
   exact_allowed_changes=['actor.mlp.6.weight.row0 copied actual hiprow1','actor.mlp.6.bias[0]=actual hipbias−.2343','Adam state7/8 exp_avg,exp_avg_sq row0 cleared','independent new private KEY metadata only'],
   Adam_all17_steps_and_std_param0_moments_exact=True,all107_floating_and99perenv_preserved=True,
   new_metadata_contains_no_tensor=True,actual_disk_roundtrip_CPU_exact=True,CPU_RNG_numpy_RNG_before_after_exact=True,
   negative_identity_actual_cases=negative,
   next_use='ONLY new3060 frozen50mm full80 single-factor evaluation, no new training/full20kGPU resume from this CPU candidate',
   future_actual_firstphysics_root_q30_fullparameters_assignment_recipes_RNG_queue_exactpair_REQUIRED_not_claimed=True,
   future_GPU_actor_actual_source_tensors_exact_and_native_physical_query_contact_COM_hardware_REQUIRED_not_claimed=True,
   future_full1500_80env_6000callback_040approach_tenwaves_1N_before_after200mm_original_thresholds_REQUIRED=True,
   remaining_three_skills_query_failure_kept_no_tolerance_relaxation=True,
   prepared_only=True,approved_production_source=False,GPU_frozen_factor_passed=False,new_PPO=False,qualified50=False,
   no_live_coupling_teacher_heading_truth_gate_rewardhardware_DR_clock_processor_change=True,
   no_SSH_GPU_or_budget_Gitcommit=True,Git_archive_pending_root_owner=True)
 (ROOT/'CANDIDATE_CPU_PREPARED_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 result=dict(epoch=time.time(),passed=True,manifest=witness(ROOT/'CANDIDATE_CPU_PREPARED_MANIFEST.json'),source=witness(SOURCE),candidate=witness(MODEL),whole107finite99perenv_actual=True,disk_CPU_exact=True,all195_tensor_storage_independent=True,all_other_inherited_fields_and_std_optimizer_steps_exact=True,negative6_strict_rejected=True,no_CPU_RNG_draw_no_CUDA=True,prepared_only=True,production_adopted=False,GPU_factor_NOT_run=True,Git_archive_pending_root_owner=True,source_script=witness(__file__))
 (R/'CENTER_KEEPSTD_CANDIDATE_FULLSTATE_CPU_ACTUAL_REVIEW.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(dict(candidate=result['candidate'],report=str(R/'CENTER_KEEPSTD_CANDIDATE_FULLSTATE_CPU_ACTUAL_REVIEW.json'),counts=counts(disk),std0=float(disk['actor_state_dict']['distribution.std_param'][0]),only_CPU_prepared=True,no_GPU=True)))
except Exception:
 (R/f'CPU_CANDIDATE_ORIGINAL_ERROR_{time.time_ns()}.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=witness(__file__),no_GPU_or_SSH=True,original_false_retained=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8')
 raise
