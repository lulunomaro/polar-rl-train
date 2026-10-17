"""Offline E3 frozen data/phase/source audit; no remote connection or learning."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
torch.set_num_threads(4)
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'e3_closed85_frozen_prepared_v2/payload';C=Q/'frozen_shared/runtime/isaac/mod4';sys.path[:0]=[str(Q),str(C)]
from recovery_closed85_source_guard_v1 import validate_E3_source
from e3_public_recovery_phase_v1 import RecoveryPhase
from h1_authored_full_collider_plane_reference_v1 import evaluate
from represented_native_plane_CPU_component_v2 import represented_plane_from_readonly_metadata,compare_actual_hit_readonly
from e3_plane_reference_104_v1 import NATIVE_BINDING_SHA256
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def main():
 collection=Path(sys.argv[1]);j=read(collection);assert not j.get('original_transport_error') and j['parent_child_launcher_actual_absent'] and j['shared_OS_lock_free'] and not j['original_error']
 def path(name):return Path(next(row['local_path'] for row in j['files'] if row.get('local_path') and row['relative'].endswith('/'+name)))
 for row in j['files']:
  if row.get('local_path'):assert Path(row['local_path']).stat().st_size==row['bytes'] and H(row['local_path'])==row['SHA']
 complete=read(path('COMPLETE_ACTUAL.json'));probe=read(path('probe.json'));exitrow=read(path('PARENT_EXIT_RECEIPT.json'));route=read(path('E3_SINGLE_POLICY_CONTROL_ACTUAL.json'));reset=read(path('E3_FRESH104_EXPLICIT_LEGAL_FALL_RESET_ACTUAL.json'));dr=read(path('E3_ACTUAL_WHITE_V3_AND_DR_READBACK.json'));S=complete['steps'];N=104
 assert S in (120,1500) and complete['num_envs']==N and complete['callbacks']==4*S and complete['kind']=='recovery' and complete['no_PPO'] and not complete['qualification_claimed']
 assert exitrow['exit_code']==0 and not exitrow['canonical_budget_written'] and not exitrow['original_error_present'] and exitrow['complete_data_contract_present']
 assert H(path('probe.json'))==complete['probe']['sha256'];raw=path('retention_full_control_substep_actual.npz');assert H(raw)==complete['raw']['sha256'];source=Q/'source/E3_closed85.pt';assert H(source)==complete['checkpoint_sha256']==reset.get('source_SHA',complete['checkpoint_sha256'])=='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208'
 cfg=read(path('ACTUAL_RUNTIME_CONFIG_READBACK.json'))['actual'];assert cfg['num_envs']==104 and cfg['mimic']==.01 and cfg['closure']==.002 and cfg['physics_dt']==.0025 and cfg['decimation']==4 and cfg['episode_seconds']>=15
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in z.files}
 with np.load(path('E3_SINGLE_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k] for k in z.files}
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
 force=a['substep_force'];assert force.shape==(4*S,N,2,3);integral=np.maximum(force[...,2].reshape(S,4,N,2),0.).astype(np.float64).sum(1)*.0025;impulse_error=float(abs(integral-a['impulse']).max());assert impulse_error/.01<=.1
 wheel=[reset['contact_names'].index(n) for n in ('left_wheel','right_wheel')];force_error=float(abs(a['substep_E3_all31_force'][:,:,wheel]-a['substep_E3_wheel_raw']).max());assert force_error<=.1
 assert a['substep_E3_root13'].shape==(S*4,N,13) and a['substep_E3_q30'].shape==(S*4,N,30) and a['substep_E3_all31_force'].shape==(S*4,N,31,3)
 lo=a['substep_torque_speed_lower'];hi=a['substep_torque_speed_upper'];tau=a['substep_actual_applied_effort'];assert tau.shape==lo.shape==hi.shape==(4*S,N,6) and np.array_equal(tau,np.clip(tau,lo,hi))
 constants=probe['native_readonly_witness']['hardware_model_constants'];offset=0
 for name,width in [('legs',4),('wheels',2)]:
  v={k:np.asarray(x,np.float32) for k,x in constants[name].items()};vel=a['substep_cached_pre_actuator_velocity'][...,offset:offset+width];bounded=np.clip(vel,-v['_vel_at_effort_lim'],v['_vel_at_effort_lim']);upper=np.minimum(v['_saturation_effort']*(1-bounded/v['velocity_limit']),v['effort_limit']);lower=np.maximum(v['_saturation_effort']*(-1-bounded/v['velocity_limit']),-v['effort_limit']);assert np.array_equal(upper,hi[...,offset:offset+width]) and np.array_equal(lower,lo[...,offset:offset+width]);offset+=width
 assert a['substep_COM_frame_error_m'].max()<1e-5 and a['mimic'].max()<=.01 and a['post_reset_mimic'].max()<=.01
 # Reuse both original independent FP64 authored-geometry references. Actual GPU
 # FP32 residual is a separate diagnostic, exactly as in the admitted E3 protocol.
 M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';sp=importlib.util.spec_from_file_location('original_E3_native_CPU_reference',M/'payload/recovery/native_CPU.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
 shapes=reset['authored34_shapes'];assert len(shapes)==34;geometry64=geometry_GPU=0.
 for start in range(0,4*S,32):
  pos=a['substep_E3_witness_body_pos'][start:start+32];quat=a['substep_E3_witness_body_quat_xyzw'][start:start+32];assert pos.shape[1:]==(N,31,3);expected=old.clearance(pos,quat,shapes);other=evaluate(torch.from_numpy(pos.reshape(-1,31,3)).double(),torch.from_numpy(quat.reshape(-1,31,4)).double(),shapes).numpy().reshape(expected.shape);geometry64=max(geometry64,float(abs(expected-other).max()));geometry_GPU=max(geometry_GPU,float(abs(expected-a['substep_E3_witness_clear34'][start:start+32]).max()))
 assert geometry64<=1e-6
 rng=torch.get_rng_state().clone();ck=torch.load(source,map_location='cpu',weights_only=False);validate_E3_source(ck);sd={k:v.double() for k,v in ck['actor_state_dict'].items()};ratio=mean_error=0.;flat=a['policy_obs'].reshape(-1,35);actual=a['raw_actor_action'].reshape(-1,6)
 for start in range(0,len(flat),4096):
  y=torch.from_numpy(flat[start:start+4096]).double();enclosure=torch.zeros_like(y);u=2.**-24
  for i in (0,2,4,6):
   weight=sd[f'mlp.{i}.weight'];bias=sd[f'mlp.{i}.bias'];ops=2*weight.shape[1]+3;gamma=ops*u/(1-ops*u);mag=torch.nn.functional.linear(y.abs(),weight.abs(),bias.abs());prop=torch.nn.functional.linear(enclosure,weight.abs(),None);enclosure=prop+gamma*(mag+prop);y=torch.nn.functional.linear(y,weight,bias)
   if i<6:y=torch.nn.functional.elu(y);enclosure+=8*u*(1+y.abs())
  error=(torch.from_numpy(actual[start:start+4096]).double()-y).abs();assert (error<=enclosure).all();ratio=max(ratio,float((error/(enclosure+np.finfo(np.float64).tiny)).max()));mean_error=max(mean_error,float(error.max()));assert not ((y+10*(enclosure+1)-y).abs()<=enclosure).all()
 phase=RecoveryPhase(N,'cpu');angles=torch.tensor([-90.,-60.,-30.,30.,60.,90.]);theta=torch.where(phase.recipe<12,angles[phase.recipe.clamp(max=11)%6],0.)*torch.pi/180;upright=(1+torch.cos(theta))/2;phase.reset(torch.arange(N),upright);phase_error=0.
 for t in range(S):
  mode=phase.mode();assert np.array_equal(mode.numpy(),b['declared_actual_public_modes'][t]);assert np.array_equal(torch.nn.functional.one_hot(mode,7).float().numpy(),a['policy_obs'][t,:,28:35]);phase.begin();root=torch.from_numpy(a['E3_root13'][t]);phase.update(torch.from_numpy(a['E3_gravity_z'][t]),root[:,7:10].norm(dim=-1),root[:,10:13].norm(dim=-1))
  for name in ('recipe','age','stable','credited','request'):assert np.array_equal(getattr(phase,name).numpy(),a['E3_phase_'+name][t]),(t,name)
  phase_error=max(phase_error,float(abs(phase.peak.numpy()-a['E3_phase_peak'][t]).max()),float(abs(phase.delta.numpy()-a['E3_event_delta'][t]).max()));assert phase_error<=1e-6;ids=torch.from_numpy(np.flatnonzero(done[t]));phase.reset(ids,upright[ids])
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 q=read(path('retention_plane_query_actual.json'));querymax=0.;z0false=0
 for name in ('initial','final'):
  row=q[name];assert len(row['query_rows'])==104 and row['tolerance_m']==1e-6 and row['captured_RNG_before']==row['captured_RNG_after'];reference=represented_plane_from_readonly_metadata(row['actual_USD_and_native_actor_metadata']);assert reference==row['source_reference'] and row['native_binding_actual']['sha256']==NATIVE_BINDING_SHA256
  hits=path(Path(row['allhits_evidence']['path']).name);assert H(hits)==row['allhits_evidence']['sha256'];allhits=read(hits);assert allhits['complete_all_envs'] and len(allhits['all_rays'])==104
  for hit in row['query_rows']:
   cmp=compare_actual_hit_readonly(reference,hit['hit']);assert cmp==hit['independent_source_reference_comparison'] and cmp['represented_query_within_original_1e6'] and cmp['normal_crosscheck_maxabs']<=1e-6
  z0false+=row['ideal_Z0_failure_count']
 assert q['initial']['source_reference']==q['final']['source_reference'] and q['initial']['actual_USD_and_native_actor_metadata']==q['final']['actual_USD_and_native_actor_metadata'] and q['initial']['loaded_PhysX_binary_fingerprints']['files']==q['final']['loaded_PhysX_binary_fingerprints']['files']
 assert dr['actual_parameter_audit']['profile']=='white_v3' and dr['actual_parameter_audit']['actual_parameters_pass'] and route['actor9_STD_initial_final_literalexact'] and route['controls']==route['provider_calls']==S and route['optimizer_updates']==0
 out=dict(epoch=time.time(),passed_complete_data_and_source_CPU=True,steps=S,callbacks=4*S,num_envs=N,source_SHA=H(source),all_saved_actor_rows=S*N,all_saved_physical_rows=S*N*4,actor_FP32_enclosure_max_ratio=ratio,all_saved_actor_CPUmean_maxabs=mean_error,CPU_GPU_not_bitexact=True,source_phase_original_request_age_reset_stable_credited_reconstruction=True,phase_float_reference_maxabs=phase_error,source_phase_float_reference_tolerance1e6_not_physical_guard_change=True,all104_body31_authored34_two_independent_CPU_FP64_reference_maxabs=geometry64,original_GPU_FP32_geometry_residual_diagnostic=geometry_GPU,original_GPU_geometry_within1e6=geometry_GPU<=1e-6,full31_wheel_force_maxabs=force_error,positiveZ_impulse_maxabs=impulse_error,original_query1e6_COM1e5_mimic01_closure002_hardware_guards_retained=True,ideal_Z0_false_count_preserved=z0false,missing_EXIT_NATURAL_preserved=not exitrow['natural_app_close_present'],ordinary=int(a['terminated'].sum()),truncations=int(a['truncated'].sum()),actual_parent_child_launcherout_and_MSVCRTfree=True,zeroPPO_zerocharge=True,not_selfrescue_skill_graduation=True,source_PhysX_authored_reference_not_cookedShapeLocal_or_manifold_proof=True)
 dest=R/('E3_CLOSED85_'+str(S)+'_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json')
 with dest.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FROZEN_ALLROW_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),not_qualification_or_GPU_replay=True),f,indent=2)
  raise
