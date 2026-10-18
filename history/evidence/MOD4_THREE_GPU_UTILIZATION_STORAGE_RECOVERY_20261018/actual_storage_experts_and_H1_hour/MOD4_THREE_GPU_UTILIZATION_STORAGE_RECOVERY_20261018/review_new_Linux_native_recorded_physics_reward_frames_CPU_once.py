"""Independent CPU audit of actual recorded native observations; explicit missing internal fields."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports'
import numpy as np,torch
torch.set_num_threads(4)
def read(p):return json.loads(Path(p).read_bytes())
def load_module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def audit(kind):
 j=read(R/(kind+'_LINUX_V4_NEW_NATIVE120_COMPLETE_OR_PENDING_COLLECTION_ACTUAL.json'));meta=j['metadata'];assert j['terminal_at_snapshot'] and meta['private_fcntl_current_free'] and not meta['own_processes'] and 'native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json' not in meta['rows'];Q=B/(kind+'_linux_reward_frame_v4');sys.path[:0]=[str(Q),str(Q/'frozen_shared/runtime/isaac/mod4'),str(Q/'frozen_shared/runtime')]
 def path(name):return Path(next(r['local_path'] for r in j['files'] if r['relative'].endswith('/'+name)))
 for row in j['files']:assert row['twohost_complete_SHA'] and Path(row['local_path']).stat().st_size==row['bytes']
 complete=read(path('COMPLETE_ACTUAL.json'));p=read(path('probe.json'));S=complete['steps'];N=88 if kind=='E2' else 104;assert S==120 and complete['num_envs']==N and complete['callbacks']==4*S and complete['no_PPO']
 with np.load(path('retention_full_control_substep_actual.npz'),allow_pickle=False) as z:a={k:z[k] for k in z.files}
 for k,x in a.items():
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
 assert a['root'].shape==(S,N,13) and a['q'].shape==(S,N,30) and a['policy_obs'].shape==(S,N,35) and a['substep_force'].shape==(S*4,N,2,3)
 assert np.array_equal(np.clip(a['raw_actor_action'],-6,6),a['processed_action']) and np.array_equal(a['vec_clipped_action'],a['processed_action']);done=a['terminated']|a['truncated'];assert np.array_equal(a['before_root'][1:],a['after_reset_root'][:-1]) and np.array_equal(a['episode'][1:]-a['episode'][:-1],done[:-1].astype(np.int64));last=np.zeros((N,6),np.float32)
 for t in range(S):assert np.array_equal(last,a['policy_obs'][t,:,22:28]);last=a['processed_action'][t].copy();last[done[t]]=0
 reasons=p['native_readonly_witness']['reason_names'];timeouts=p['native_readonly_witness']['reason_time_out'];assert np.array_equal(a['terminated'],np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if not timeouts[n]],-1).any(-1)) and np.array_equal(a['truncated'],np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if timeouts[n]],-1).any(-1))
 impulse=np.maximum(a['substep_force'][...,2].reshape(S,4,N,2),0.).astype(np.float64).sum(1)*.0025;force_error=float(abs(impulse-a['impulse']).max())/.01;assert force_error<=.1
 tau=a['substep_actual_applied_effort'];lo=a['substep_torque_speed_lower'];hi=a['substep_torque_speed_upper'];assert tau.shape==lo.shape==hi.shape==(S*4,N,6) and np.array_equal(tau,np.clip(tau,lo,hi));constants=p['native_readonly_witness']['hardware_model_constants'];offset=0
 for name,width in [('legs',4),('wheels',2)]:
  c={k:np.asarray(x,np.float32) for k,x in constants[name].items()};vel=a['substep_cached_pre_actuator_velocity'][...,offset:offset+width];bounded=np.clip(vel,-c['_vel_at_effort_lim'],c['_vel_at_effort_lim']);upper=np.minimum(c['_saturation_effort']*(1-bounded/c['velocity_limit']),c['effort_limit']);lower=np.maximum(c['_saturation_effort']*(-1-bounded/c['velocity_limit']),-c['effort_limit']);assert np.array_equal(upper,hi[...,offset:offset+width]) and np.array_equal(lower,lo[...,offset:offset+width]);offset+=width
 assert a['substep_COM_frame_error_m'].max()<1e-5 and a['mimic'].max()<=.01 and a['post_reset_mimic'].max()<=.01
 cfg=read(path('ACTUAL_RUNTIME_CONFIG_READBACK.json'))['actual'];assert cfg['mimic']==.01 and cfg['closure']==.002 and cfg['physics_dt']==.0025 and cfg['decimation']==4 and cfg['episode_seconds']>=15
 ref=load_module(kind+'_independent_plane_CPU',Q/'represented_native_plane_CPU_component_v2.py');query=read(path('retention_plane_query_actual.json'));expected_binding=read(Q/'EXPECTED_ACTUAL_LINUX_DIAGNOSTIC_BACKEND_V1.json')['native_binding'];query_error=0.
 for phase in ('initial','final'):
  x=query[phase];assert x['tolerance_m']==1e-6 and len(x['query_rows'])==N and x['captured_RNG_before']==x['captured_RNG_after'];reference=ref.represented_plane_from_readonly_metadata(x['actual_USD_and_native_actor_metadata']);assert reference==x['source_reference'] and x['native_binding_actual']['sha256']==expected_binding['SHA']
  for hit in x['query_rows']:
   cmp=ref.compare_actual_hit_readonly(reference,hit['hit']);assert cmp==hit['independent_source_reference_comparison'] and cmp['represented_query_within_original_1e6'] and cmp['normal_crosscheck_maxabs']<=1e-6
 assert query['initial']['source_reference']==query['final']['source_reference'] and query['initial']['loaded_PhysX_binary_fingerprints']['files']==query['final']['loaded_PhysX_binary_fingerprints']['files']
 manifest=read(Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json');source=Q/manifest['source_relative'];ck=torch.load(source,map_location='cpu',weights_only=False);guard=load_module(kind+'_source_guard_CPU',Q/('e2_closed112_source_guard_CPU_v1.py' if kind=='E2' else 'recovery_closed85_source_guard_v1.py'));getattr(guard,'validate_'+kind+'_source')(ck);sd=ck['actor_state_dict'];flat=a['policy_obs'].reshape(-1,35);actual=a['raw_actor_action'].reshape(-1,6);meanmax=ratio=0.
 for start in range(0,len(flat),4096):
  y=torch.from_numpy(flat[start:start+4096].copy());target=torch.from_numpy(actual[start:start+4096]);enclosure=torch.zeros_like(y,dtype=torch.float64)
  if kind=='E3':y=y.double()
  for layer in (0,2,4,6):
   w=sd[f'mlp.{layer}.weight'];b=sd[f'mlp.{layer}.bias']
   if kind=='E3':
    w=w.double();b=b.double();u=2.**-24;ops=2*w.shape[1]+3;gamma=ops*u/(1-ops*u);mag=torch.nn.functional.linear(y.abs(),w.abs(),b.abs());prop=torch.nn.functional.linear(enclosure,w.abs(),None);enclosure=prop+gamma*(mag+prop)
   y=torch.nn.functional.linear(y,w,b)
   if layer<6:
    y=torch.nn.functional.elu(y)
    if kind=='E3':enclosure+=8*2.**-24*(1+y.abs())
  err=(target.double()-y.double()).abs();meanmax=max(meanmax,float(err.max()))
  if kind=='E2':assert np.allclose(y.numpy(),target.numpy(),atol=1e-4,rtol=3e-5)
  else:assert (err<=enclosure).all();ratio=max(ratio,float((err/(enclosure+np.finfo(np.float64).tiny)).max()))
 geometry64=None;phase_error=None;missing=[]
 if kind=='E3':
  reset=read(path('E3_FRESH104_EXPLICIT_LEGAL_FALL_RESET_ACTUAL.json'));old=load_module('original_E3_geometry_numpy_reference',W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017/payload/recovery/native_CPU.py');geom=load_module('original_E3_geometry_torch_reference',Q/'h1_authored_full_collider_plane_reference_v1.py');geometry64=0.
  for i in range(0,4*S,32):
   pos=a['substep_E3_witness_body_pos'][i:i+32];quat=a['substep_E3_witness_body_quat_xyzw'][i:i+32];x=old.clearance(pos,quat,reset['authored34_shapes']);y=geom.evaluate(torch.from_numpy(pos.reshape(-1,31,3)).double(),torch.from_numpy(quat.reshape(-1,31,4)).double(),reset['authored34_shapes']).numpy().reshape(x.shape);geometry64=max(geometry64,float(abs(x-y).max()))
  assert geometry64<=1e-6
  from e3_public_recovery_phase_v1 import RecoveryPhase
  ph=RecoveryPhase(N,'cpu');angles=torch.tensor([-90.,-60.,-30.,30.,60.,90.]);theta=torch.where(ph.recipe<12,angles[ph.recipe.clamp(max=11)%6],0.)*torch.pi/180;upright=(1+torch.cos(theta))/2;ph.reset(torch.arange(N),upright);phase_error=0.
  for t in range(S):
   assert np.array_equal(torch.nn.functional.one_hot(ph.mode(),7).float().numpy(),a['policy_obs'][t,:,28:35]);ph.begin();root=torch.from_numpy(a['E3_root13'][t]);ph.update(torch.from_numpy(a['E3_gravity_z'][t]),root[:,7:10].norm(dim=-1),root[:,10:13].norm(dim=-1));assert np.array_equal(ph.request.numpy(),a['E3_request'][t]) and np.array_equal(ph.age.numpy(),a['E3_age_after'][t]);phase_error=max(phase_error,float(abs(ph.peak.numpy()-a['E3_peak'][t]).max()),float(abs(ph.delta.numpy()-a['E3_event_delta'][t]).max()));assert phase_error<=1e-6;ph.reset(torch.from_numpy(np.flatnonzero(done[t])),upright[torch.from_numpy(np.flatnonzero(done[t]))])
  missing=[name for name in ('E3_phase_stable','E3_phase_credited') if name not in a]
 reward=read(path('ACTUAL_LOADED_REWARD_TERMS_WEIGHTS_PARAMS_SOURCE.json'));obs=read(path('ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json'))
 with np.load(path('actual_reward_frame_legacy_readouts.npz'),allow_pickle=False) as z:frames={k:z[k] for k in z.files}
 assert obs['controls']==S and np.array_equal(frames['root_state_w'],a['after_reset_root']) and frames['step_reward'].shape[:2]==(S,N)
 for k,x in frames.items():
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
 return dict(epoch=time.time(),expert=kind,passed_recorded_native_data_source_physics_CPU=True,steps=S,num_envs=N,policy_rows=S*N,physical_rows=4*S*N,actor_CPU_reference_maxabs=meanmax,E3_original_FP32_enclosure_ratio=ratio,actor_reference_original_E2_or_E3_protocol_not_H1_exception=True,geometry_dual64_reference_maxabs=geometry64,source_phase_available_fields_error=phase_error,missing_original_internal_phase_fields=missing,missing_fields_not_fabricated_or_claimed_directly_observed=True,not_original_full_internal_counter_audit_or_skill_graduation=True,source_SHA=manifest['source_SHA'],mean_load_impulse_error_N=force_error,COM_original1e5_hardware_and_query1e6_mimic01_closure002_retained=True,actual_reward_terms=reward['terms'],legacy_active_presence={n:bool(frames[n+'_active_present'].any()) for n in ('_mod4_jump','_mod4_spin','_mod4_recovery')},ordinary=int(a['terminated'].sum()),truncation=int(a['truncated'].sum()),actual_parent_children_out_and_private_fcntl_free=True,no_optimizer_GPU_PPO_charge_or_new_threshold=True,all_new_large_checksums_already_twohost_verified_not_rehashed_for_archive=True)
if __name__=='__main__':
 try:
  rng=torch.get_rng_state().clone();results=[]
  for kind in ('E2','E3'):
   value=audit(kind)
   with (R/(kind+'_LINUX_NATIVE120_RECORDED_PHYSICS_REWARD_CPU_ACTUAL.json')).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
   results.append({k:value[k] for k in ('expert','passed_recorded_native_data_source_physics_CPU','actor_CPU_reference_maxabs','ordinary','missing_original_internal_phase_fields','legacy_active_presence')})
  assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();print(json.dumps(results),flush=True)
 except BaseException:
  with (R/('NEW_LINUX_RECORDED_NATIVE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_threshold_change=True),f,indent=2)
  raise
