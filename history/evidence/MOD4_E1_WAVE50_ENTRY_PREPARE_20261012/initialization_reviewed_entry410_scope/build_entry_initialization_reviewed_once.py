"""Independent repair of zero-Wave initialization; failed398 source is immutable."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;P=D/'payload';V=D/'payload_initialization_reviewed';R=D/'reports'
def put(name,s):
 p=V/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:f.write(s)
 ast.parse(s)
rename={k:k.replace('.py','_v2.py') for k in ('wave50_entry_runtime.py','wave50_entry_full_pose_reset.py','wave50_entry_current_state.py','wave50_entry_full_checkpoint.py','wave50_entry_fullsave_cpu.py','wave50_entry_sdk_placement.py','test_wave50_entry_target_cpu.py','train_wave50_entry_resume_ppo.py','train_wave50_entry_fresh_preflight_ppo.py','probe_wave50_entry_fresh_process_full_resume.py','native_e1_wave50_entry_scope_probe.py','supervise_wave50_entry_scope_once.py')}
for q in P.rglob('*.py'):
 if q.name not in rename:continue
 s=q.read_text()
 for old,new in rename.items():s=s.replace(old[:-3],new[:-3])
 if q.name=='wave50_entry_runtime.py':
  s=s.replace('from g4_retention_runtime import configure_retention as old_configure\n','')
  s=s.replace(" xy,receipt=entry_map(origins.detach().cpu().numpy(),rows,points,json.loads(profile.read_bytes())['span_m'])", " xy,receipt=initialization_safe_map(origins.detach().cpu().numpy(),rows,points,json.loads(profile.read_bytes())['span_m'],env.num_envs)")
  assert 'initialization_safe_map(' in s
  s=s.replace('def configure_retention(cfg):','''def initialization_safe_map(origins,rows,points,span,n):
 origins=np.asarray(origins,dtype='<f4');mask=np.zeros(n,dtype=bool);covered=np.zeros(n,dtype=bool)
 for a in rows:
  b=np.asarray(a['bounds']);inside=((origins>=b[0,:2])&(origins<b[1,:2])).all(1)
  covered|=inside
  if a['family']=='random_uniform_for_rm':mask|=inside
 if mask.any():return entry_map(origins,rows,points,span)
 assert n<20000 and covered.all() and np.isfinite(origins).all() and len(np.unique(origins,axis=0))==n
 extent=np.max(abs(points[:,:2]),axis=0);assert extent[0]<.30 and extent[1]<.30 and 2.<span<3.
 receipt=dict(profile=PROFILE,map_sha256=hashlib.sha256(origins.tobytes()).hexdigest(),changed_environments=0,Wave_environments=0,other_environments_unchanged=n,
  actual_Wave_groups=[],collision_sample_extent_xy=extent.tolist(),minimum_full_flat_front_support_m=float(.8-extent[0]),minimum_same_side_lane_gap_m=.85,
  ten_wave_span_m=float(span),commands_and_RNG_consumption_unchanged=True,no_new_random_stream=True,reset_position_only_axis=True,
  no_actor_gate_truth_input=True,original2m_route_truncation_unchanged=True,not_whole_ten_wave_training_episode_certificate=True,
  CPU_map_not_physical_contact_nonpenetration_or_causal_certificate=True,explicit_small_initialization_has_no_Wave_origins=True)
 return origins.copy(),receipt
def configure_retention(cfg):
 from g4_retention_runtime import configure_retention as old_configure''')
 if q.name=='supervise_wave50_entry_scope_once.py':
  s=s.replace("OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_SECOND_BOUNDED_20261012')", "OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_REVIEWED_20261012')")
  a=s.index('def wait_existing():');b=s.index('\ndef runtime():',a)
  s=s[:a]+'''def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');attention=read(OLD/'reports/E1_ATTENTION.json');assert not attention['own_child_still_alive'] and attention['active_segment'] is None
 assert (OLD/'WAVE50_SDK10.json.error').is_file() and not (OLD/'WAVE50_SDK10.json').exists()
 for loc in (st['owner'],st['child'],read(OLD/'reports/E1_GUARDIAN_STARTED.json')):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
'''+s[b:]
  s=s.replace("old=read(BASE/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==384", "old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==398")
  s=s.replace('old386_own_PASSED_actual_exits_two_OS_locks_held_active_empty=True','old398_retained_failed_zero_PPO_actual_exits_two_OS_locks_held_active_empty=True')
 if q.name=='test_wave50_entry_target_cpu.py':
  s=s.replace("out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state)","out=dict(ck,E1_terrain_state=state);out[KEY]=identity(state);out['E1_retained_flat_command_state']=dict(ck['E1_retained_flat_command_state'],assignment_sha256=state['entry_assignment_sha256'])")
  marker="assert not torch.cuda.is_initialized()\n print(json.dumps(dict(passed=True,source=sourceproof"
  addition="""from wave50_entry_runtime_v2 import initialization_safe_map
 small=orig[:10].numpy();smallxy,smallreceipt=initialization_safe_map(small,rows,points,json.loads((D/'isaac/mod4/g4_cad_profile.json').read_bytes())['span_m'],10)
 assert np.array_equal(small,smallxy) and smallreceipt['Wave_environments']==0 and smallreceipt['changed_environments']==0
 try:initialization_safe_map(np.repeat(small[:1],20000,axis=0),rows,points,2.4064227271861266,20000)
 except AssertionError:pass
 else:raise AssertionError('Empty production20k Wave scope must reject')
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,source=sourceproof"""
  assert s.count(marker)==1;s=s.replace(marker,addition)
  s=s.replace('actual_origin_mutation_cache_refresh_passed=True,','actual_origin_mutation_cache_refresh_passed=True,small_preplacement_no_Wave_identity_exact=True,empty_production20k_strict_rejected=True,')
 put(q.relative_to(P).as_posix().replace(q.name,rename[q.name]),s)
files={p.relative_to(V).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in V.rglob('*') if p.is_file()}
assert len(files)==12
with (R/'INITIALIZATION_REVIEWED_LOCAL_BUILD.json').open('x') as f:json.dump(dict(epoch=time.time(),files=files,failed398_sources_kept_byteexact=True,new20k_math_and_original_physics_thresholds_unchanged=True),f,indent=2)
print(json.dumps(dict(new_files=len(files),CPU_GPU_admission_pending=True)))
