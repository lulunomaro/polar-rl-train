"""Offline H1 mean-repair final frozen data/phase/source audit; no remote connection or learning."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
torch.set_num_threads(4)
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'frozen_public4_final_linux_v1/payload';C=Q/'frozen_shared/runtime/isaac/mod4';sys.path[:0]=[str(Q),str(C)]
from h1_public4_finite_final_source_guard_v1 import validate_H1_source
from h1_takeoff_progress_phase_v2 import H1TakeoffProgressPhaseV2
from h1_authored_full_collider_plane_reference_v1 import evaluate
from represented_native_plane_CPU_component_v2 import represented_plane_from_readonly_metadata,compare_actual_hit_readonly

H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def main():
 collection=Path(sys.argv[1]);j=read(collection);assert not j.get('original_transport_error') and j['parent_child_launcher_actual_absent'] and j['actual_selected_private_fcntl_free'] and not j['original_error']
 def path(name):return Path(next(row['local_path'] for row in j['files'] if row.get('local_path') and row['relative'].endswith('/'+name)))
 for row in j['files']:
  if row.get('local_path'):assert Path(row['local_path']).stat().st_size==row['bytes'] and H(row['local_path'])==row['SHA']
 complete=read(path('COMPLETE_ACTUAL.json'));probe=read(path('probe.json'));exitrow=read(path('PARENT_EXIT_RECEIPT.json'));route=read(path('H1_SINGLE_POLICY_CONTROL_ACTUAL.json'));reset=read(path('H1_FRESH80_ORIGINAL_GROUND_RESET_ACTUAL.json'));dr=read(path('H1_ACTUAL_WHITE_V3_AND_DR_READBACK.json'));S=complete['steps'];N=80
 assert S in (120,1500) and complete['num_envs']==N and complete['callbacks']==4*S and complete['kind']=='jump' and complete['no_PPO'] and not complete['qualification_claimed']
 assert exitrow['actual_child_returncode']==0 and not exitrow['canonical_budget_written'] and not exitrow['original_errors'] and exitrow['complete'] and exitrow['all_actual_own_children_waited']
 assert H(path('probe.json'))==complete['probe']['sha256'];raw=path('retention_full_control_substep_actual.npz');assert H(raw)==complete['raw']['sha256'];source=Q/'source/H1_public4_finite_final.pt';assert H(source)==complete['checkpoint_sha256']==reset.get('source_SHA',complete['checkpoint_sha256'])==read(Q/'H1_PUBLIC4_FINAL_LINUX4090_MANIFEST_V1.json')['source']['SHA']
 cfg=read(path('ACTUAL_RUNTIME_CONFIG_READBACK.json'))['actual'];assert cfg['num_envs']==80 and cfg['mimic']==.01 and cfg['closure']==.002 and cfg['physics_dt']==.0025 and cfg['decimation']==4 and cfg['episode_seconds']>=15
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in z.files}
 with np.load(path('H1_SINGLE_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k] for k in z.files}
 for k,x in {**a,**b}.items():
  if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
 assert a['root'].shape==(S,N,13) and a['q'].shape==(S,N,30) and a['policy_obs'].shape==(S,N,35)
 assert np.array_equal(a['policy_obs'],b['shared_obs']) and np.array_equal(a['raw_actor_action'],b['raw_action']) and np.array_equal(a['processed_action'],b['clipped_action'])
 assert np.array_equal(np.clip(a['raw_actor_action'],-6,6),a['processed_action']) and np.array_equal(a['vec_clipped_action'],a['processed_action']) and not a['command'].any() and not a['policy_obs'][...,:3].any()
 assert np.array_equal(a['before_root'][1:],a['after_reset_root'][:-1]);done=a['terminated']|a['truncated'];assert np.array_equal(a['episode'][1:]-a['episode'][:-1],done[:-1].astype(np.int64))
 assert np.array_equal(a['root'][:-1][~done[:-1]],a['before_root'][1:][~done[:-1]])
 last=np.zeros((N,6),np.float32)
 for t in range(S):assert np.array_equal(last,a['policy_obs'][t,:,22:28]);last=a['processed_action'][t].copy();last[done[t]]=0
 reasons=probe['native_readonly_witness']['reason_names'];timeouts=probe['native_readonly_witness']['reason_time_out'];assert set(reasons)<=set(('time_out','bad_orientation','base_contact','closure','mimic','low_base','tunnel_roof_hit'))
 assert np.array_equal(a['terminated'],np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if not timeouts[n]],-1).any(-1));assert np.array_equal(a['truncated'],np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if timeouts[n]],-1).any(-1))
 force=a['substep_force'];assert force.shape==(4*S,N,2,3);integral=np.maximum(force[...,2].reshape(S,4,N,2),0.).astype(np.float64).sum(1)*.0025;impulse_error=float(abs(integral-a['impulse']).max());assert impulse_error<=1e-6
 wheel=[reset['contact_names'].index(n) for n in ('left_wheel','right_wheel')];force_error=float(abs(a['substep_H1_all31_contact_force'][:,:,wheel]-a['substep_H1_wheel_raw']).max());assert force_error<=.1
 assert a['substep_H1_root13'].shape==(S*4,N,13) and a['substep_H1_q30'].shape==(S*4,N,30) and a['substep_H1_all31_contact_force'].shape==(S*4,N,31,3)
 lo=a['substep_torque_speed_lower'];hi=a['substep_torque_speed_upper'];tau=a['substep_actual_applied_effort'];assert tau.shape==lo.shape==hi.shape==(4*S,N,6) and np.array_equal(tau,np.clip(tau,lo,hi))
 constants=probe['native_readonly_witness']['hardware_model_constants'];offset=0
 for name,width in [('legs',4),('wheels',2)]:
  v={k:np.asarray(x,np.float32) for k,x in constants[name].items()};vel=a['substep_cached_pre_actuator_velocity'][...,offset:offset+width];bounded=np.clip(vel,-v['_vel_at_effort_lim'],v['_vel_at_effort_lim']);upper=np.minimum(v['_saturation_effort']*(1-bounded/v['velocity_limit']),v['effort_limit']);lower=np.maximum(v['_saturation_effort']*(-1-bounded/v['velocity_limit']),-v['effort_limit']);assert np.array_equal(upper,hi[...,offset:offset+width]) and np.array_equal(lower,lo[...,offset:offset+width]);offset+=width
 assert a['substep_COM_frame_error_m'].max()<1e-5 and a['mimic'].max()<=.01 and a['post_reset_mimic'].max()<=.01
 # Original H1 strict FP64 authored reference and FP32 actor CPU tolerances.
 shapes=reset['authored34_shapes'];assert len(shapes)==34;geometry64=geometry_GPU=0.
 for start in range(0,4*S,32):
  pos=a['substep_H1_witness_body_pos'][start:start+32];quat=a['substep_H1_witness_body_quat_xyzw'][start:start+32];assert pos.shape[1:]==(N,31,3)
  expected=evaluate(torch.from_numpy(pos.reshape(-1,31,3)).double(),torch.from_numpy(quat.reshape(-1,31,4)).double(),shapes).numpy().reshape(pos.shape[:2]+(34,));geometry_GPU=max(geometry_GPU,float(abs(expected-a['substep_H1_all34_clearance'][start:start+32]).max()))
 assert geometry_GPU<=1e-6,('Original H1 authored geometry strict reference',geometry_GPU)
 rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False);validate_H1_source(ck);sd=ck['actor_state_dict'];mean_error=0.;flat=a['policy_obs'].reshape(-1,35);actual=a['raw_actor_action'].reshape(-1,6)
 for start in range(0,len(flat),4096):
  y=torch.from_numpy(flat[start:start+4096])
  for i in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'],sd[f'mlp.{i}.bias'])
   if i<6:y=torch.nn.functional.elu(y)
  mean_error=max(mean_error,float((torch.from_numpy(actual[start:start+4096])-y).abs().max()))
 actor_strict_pass=bool(mean_error<=1e-4) # original false retained; independent remaining checks continue only diagnostically
 phase=H1TakeoffProgressPhaseV2(N,'cpu');phase_error=0.
 for t in range(S):
  mode=phase.public_mode();assert np.array_equal(mode.numpy(),b['declared_actual_public_modes'][t]);assert np.array_equal(torch.nn.functional.one_hot(mode,7).float().numpy(),a['policy_obs'][t,:,28:35]);phase.begin_control()
  for callback_index in range(4):
   k=t*4+callback_index;root=torch.from_numpy(a['substep_H1_root13'][k]);out=phase.physical(wheel_N=torch.from_numpy(a['substep_H1_wheel_norm_N'][k]),wheel_clear_m=torch.from_numpy(a['substep_H1_wheel_clearance'][k]),all_min_clear_m=torch.from_numpy(a['substep_H1_all34_clearance'][k]).amin(-1),nonwheel_max_N=torch.from_numpy(a['substep_H1_nonwheel_max'][k]),root_vz=root[:,9],root_planar_speed=torch.from_numpy(a['substep_H1_root_planar_speed'][k]),roll=torch.from_numpy(a['substep_H1_roll'][k]),pitch=torch.from_numpy(a['substep_H1_pitch'][k]),yaw=torch.from_numpy(a['substep_H1_yaw'][k]))
   for key in ('takeoff','landing','recovery','prepared','prelaunch_proxy_gate'):assert np.array_equal(out[key].numpy(),a['substep_H1_'+key][k]),(k,key)
   for key in ('event_delta','prelaunch_proxy_delta'):phase_error=max(phase_error,float(abs(out[key].numpy()-a['substep_H1_'+key][k]).max()))
  assert np.array_equal(phase.request_for_action.numpy(),a['H1_public_request'][t]);phase.finish_control_before_selected_reset()
  for key,val in phase.tensors().items():
   saved=a['H1_phase_'+key][t]
   if val.is_floating_point():phase_error=max(phase_error,float(abs(val.numpy()-saved).max()))
   else:assert np.array_equal(val.numpy(),saved),(t,key)
  for key,val in [('event_expected',phase.event_control),('event_applied',phase.event_control),('progress_expected',phase.progress_control),('progress_applied',phase.progress_control)]:phase_error=max(phase_error,float(abs(val.numpy()-a['H1_'+key][t]).max()))
  assert phase_error<=1e-6,(t,phase_error);phase.reset(torch.from_numpy(np.flatnonzero(done[t])))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 q=read(path('retention_plane_query_actual.json'));querymax=0.;z0false=0
 for name in ('initial','final'):
  row=q[name];assert len(row['query_rows'])==80 and row['tolerance_m']==1e-6 and row['captured_RNG_before']==row['captured_RNG_after'];reference=represented_plane_from_readonly_metadata(row['actual_USD_and_native_actor_metadata']);assert reference==row['source_reference'] and row['native_binding_actual']['sha256']==j['actual_Linux_backend']['native_binding']['SHA']
  hits=path(Path(row['allhits_evidence']['path']).name);assert H(hits)==row['allhits_evidence']['sha256'];allhits=read(hits);assert allhits['complete_all_envs'] and len(allhits['all_rays'])==80
  for hit in row['query_rows']:
   cmp=compare_actual_hit_readonly(reference,hit['hit']);assert cmp==hit['independent_source_reference_comparison'] and cmp['represented_query_within_original_1e6'] and cmp['normal_crosscheck_maxabs']<=1e-6
  z0false+=row['ideal_Z0_failure_count']
 assert q['initial']['source_reference']==q['final']['source_reference'] and q['initial']['actual_USD_and_native_actor_metadata']==q['final']['actual_USD_and_native_actor_metadata'] and q['initial']['loaded_PhysX_binary_fingerprints']['files']==q['final']['loaded_PhysX_binary_fingerprints']['files']
 assert dr['actual_parameter_audit']['profile']=='white_v3' and dr['actual_parameter_audit']['actual_parameters_pass'] and route['actor9_STD_initial_final_literalexact'] and route['controls']==route['provider_calls']==S and route['optimizer_updates']==0
 first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:];events={}
 for key in ('takeoff','landing','recovery'):
  events[key]=int((a['substep_H1_'+key].reshape(S,4,N).any(1)&valid).any(0).sum())
 out=dict(epoch=time.time(),passed_complete_data_and_source_CPU=actor_strict_pass,actor_CPU_raw_mean_original1e4_passed=actor_strict_pass,all_other_original_source_phase_physics_checks_passed=True,strict_actor_failure_not_waived=True,steps=S,callbacks=4*S,num_envs=N,source_SHA=H(source),all_saved_actor_rows=S*N,all_saved_physical_rows=S*N*4,all_saved_actor_CPUmean_maxabs=mean_error,original_H1_CPUmean_tolerance1e4=True,CPU_GPU_not_bitexact=True,phase_float_reference_maxabs=phase_error,original_H1_authored34_geometry_reference_maxabs=geometry_GPU,full31_wheel_force_maxabs=force_error,positiveZ_impulse_maxabs=impulse_error,original_query1e6_COM1e5_mimic01_closure002_hardware_guards_retained=True,ideal_Z0_false_count_preserved=z0false,missing_EXIT_NATURAL_preserved=not j['actual_natural_exit_marker_present'],ordinary=int(a['terminated'].sum()),truncations=int(a['truncated'].sum()),first_episode_before_failed_control_events=events,actual_parent_child_out_private_fcntl_free=True,zeroPPO_zerocharge=True,not_jump_skill_graduation_from_data_contract_alone=True,Linux72_actual_backend_not_Windows3060_proof=True,source_PhysX_authored_reference_not_cookedShapeLocal_or_manifold_proof=True)
 dest=R/('H1_PUBLIC4FINAL_LINUX72_'+str(S)+'_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_STRICT_ACTOR_FALSE_DIAGNOSTIC_V2_ACTUAL.json')
 with dest.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_PUBLIC4_FINAL_PARTIAL_DIAGNOSTIC_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),not_qualification_or_GPU_replay=True),f,indent=2)
  raise
