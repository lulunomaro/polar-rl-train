"""Strict data review and unchanged old behavior facts. Never launches or connects."""
from pathlib import Path
import argparse,hashlib,json,math,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;Q=D/'e2_closed101_frozen_prepared_v7/payload';C=Q/'cpu_contracts';sys.path[:0]=[str(C),str(Q),str(Q/'frozen_shared/runtime/isaac/mod4')]
from world_cycle_metrics import measure_world_cycles
from world_progress_contract import target
from scut_curriculum_gate_v4 import evidence
from represented_native_plane_CPU_component_v2 import represented_plane_from_readonly_metadata,compare_actual_hit_readonly
from retention_plane_reference_v8 import NATIVE_BINDING_SHA256
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())


def audit_case(folder,boundary):
 folder=Path(folder);O=folder/'output';p=read(O/'probe.json');c=read(O/'COMPLETE_ACTUAL.json');x=read(folder/'PARENT_EXIT_RECEIPT.json')
 assert x['exit_code']==0 and x['no_PPO'] and not x['canonical_budget_written'] and not x['original_error_present'] and x['complete_data_contract_present']
 assert boundary['actual_parent_absent'] and boundary['actual_child_absent'] and boundary['shared_OS_lock_free']
 assert not any((O/n).exists() for n in ('ORIGINAL_ERROR.json','ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json'))
 text=(folder/'worker.log').read_text(encoding='utf8',errors='replace').lower()
 assert not any(word in text for word in ('traceback (most recent call last)','gpu collision stack overflow','physx error','contacts dropped','patches dropped','cuda out of memory'))
 kind=c['kind'];N={'flat':80,'spin':88,'world':88}[kind];S=c['steps'];assert S in (120,1500)
 assert c['num_envs']==N and c['callbacks']==S*4 and c['no_PPO'] and not c['qualification_claimed']
 # The inherited flat source retains its original field schema without a top-level profile.
 assert p['seed']==20260928 and p['steps']==S
 assert p['native_readonly_witness']['DR_profile']=='white_v3'
 if kind=='flat':
  if p['mild_initial_parameters'] is None or p['mild_final_parameters'] is None:
   assert p['mild_initial_parameters'] is None and p['mild_final_parameters'] is None
   assert p['chassis_PD_audit']['parameter_auditor']['profile']=='white_v3'
  else:
   assert p['mild_initial_parameters']['profile']==p['mild_final_parameters']['profile']=='white_v3'
 else:
  assert p['profile']==p['initial_parameter_audit']['profile']==p['final_parameter_audit']['profile']=='white_v3'
 assert c['probe']['sha256']==H(O/'probe.json')
 manifest=read(Q/'RETENTION_CPU_MANIFEST_V8.json')
 assert c['checkpoint_sha256']=='61b9ee57c2f96c9a167fb61122a782ad2b17d28c6227dfa89f9de67ed5d3d84e'
 raw=O/Path(c['raw']['path']).name;assert raw.stat().st_size==c['raw']['bytes'] and H(raw)==c['raw']['sha256']
 with np.load(raw,allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 for k,row in a.items():
  if row.dtype.kind in 'fc':assert np.isfinite(row).all(),k
 assert a['root'].shape==(S,N,13) and a['q'].shape==(S,N,30) and a['policy_obs'].shape==(S,N,35)
 assert a['raw_actor_action'].shape==a['vec_clipped_action'].shape==a['processed_action'].shape==(S,N,6)
 assert np.array_equal(np.clip(a['raw_actor_action'],-6.,6.),a['vec_clipped_action'])
 assert np.array_equal(a['vec_clipped_action'],a['processed_action'])
 reasons=p['native_readonly_witness']['reason_names'];is_timeout=p['native_readonly_witness']['reason_time_out']
 expected_term=np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if not is_timeout[n]],-1).any(-1)
 expected_timeout=np.stack([a['reasons'][...,i] for i,n in enumerate(reasons) if is_timeout[n]],-1).any(-1)
 assert np.array_equal(expected_term,a['terminated']) and np.array_equal(expected_timeout,a['truncated'])
 assert np.array_equal(a['policy_obs'][...,:3],a['command'])
 initial=p['native_readonly_witness']['first_physics_initial']
 assert np.array_equal(a['before_root'][0],np.asarray(initial['root'],dtype=np.float32)) and np.array_equal(a['before_q'][0],np.asarray(initial['q30'],dtype=np.float32))
 assert np.array_equal(a['before_root'][1:],a['after_reset_root'][:-1])
 done=a['terminated']|a['truncated'];assert np.array_equal(a['episode'][1:]-a['episode'][:-1],done[:-1].astype(np.int64))
 assert np.array_equal(a['root'][:-1][~done[:-1]],a['before_root'][1:][~done[:-1]])
 f=a['substep_force'];assert f.shape==(S*4,N,2,3)
 integral=np.maximum(f[...,2].reshape(S,4,N,2),0.).astype(np.float64).sum(1)*.0025
 mean_error=float(np.max(abs(integral-a['impulse']))/.01);assert mean_error<=.1
 applied=a['substep_actual_applied_effort'];lo=a['substep_torque_speed_lower'];hi=a['substep_torque_speed_upper']
 assert applied.shape==lo.shape==hi.shape==(S*4,N,6)
 assert np.array_equal(applied,np.clip(applied,lo,hi))
 constants=p['native_readonly_witness']['hardware_model_constants'];offset=0
 for name,width in [('legs',4),('wheels',2)]:
  row={k:np.asarray(v,dtype=np.float32) for k,v in constants[name].items()};vel=a['substep_cached_pre_actuator_velocity'][...,offset:offset+width]
  bounded=np.clip(vel,-row['_vel_at_effort_lim'],row['_vel_at_effort_lim'])
  expected_upper=np.minimum(row['_saturation_effort']*(1.-bounded/row['velocity_limit']),row['effort_limit'])
  expected_lower=np.maximum(row['_saturation_effort']*(-1.-bounded/row['velocity_limit']),-row['effort_limit'])
  assert np.array_equal(expected_upper,hi[...,offset:offset+width]) and np.array_equal(expected_lower,lo[...,offset:offset+width]),name
  offset+=width
 assert float(a['substep_COM_frame_error_m'].max())<1e-5
 assert float(a['mimic'].max())<=.01 and float(a['post_reset_mimic'].max())<=.01
 config=read(O/'ACTUAL_RUNTIME_CONFIG_READBACK.json')['actual'];assert config['mimic']==.01 and config['closure']==.002 and config['physics_dt']==.0025 and config['decimation']==4 and config['episode_seconds']>=15 and config['num_envs']==88
 binding=read(O/'ACTUAL_SIGNED4_AUDIT_BINDINGS_BEFORE_PHYSICS.json');assert binding['owned_periodic_and_public_both_bound_signed4'] and binding['public_probe_audit_module']=='e2_closed109_signed4_audit_v5'
 query=O/'retention_plane_query_actual.json';assert H(query)==p['native_readonly_witness']['actual_plane_query']['sha256']
 q=read(query)
 for phase in ('initial','final'):
  row=q[phase];assert row['tolerance_m']==1e-6 and row['authored_plane']['type']=='Plane' and row['authored_plane']['axis']=='Z' and len(row['query_rows'])==N
  assert row['scene_query_support_requested'] and row['actual_USD_scene_query_support']
  allhits=O/Path(row['allhits_evidence']['path']).name;assert H(allhits)==row['allhits_evidence']['sha256'] and allhits.stat().st_size==row['allhits_evidence']['bytes']
  original_hits=read(allhits);assert original_hits['complete_all_envs'] and len(original_hits['all_rays'])==N
  assert row['source_reference_only'] is True and row['actual_shape_local_pose_read'] is False
  assert row['public_source_to_installed_binary_bitexact_proven'] is False and row['reference_defined_from_reported_hits'] is False
  assert row['captured_RNG_before']==row['captured_RNG_after'] and row['original_V7_fullcase_failed_unchanged'] is True
  independent=represented_plane_from_readonly_metadata(row['actual_USD_and_native_actor_metadata'])
  assert independent==row['source_reference']==original_hits['reference']
  assert row['native_binding_actual']['sha256']==NATIVE_BINDING_SHA256==manifest['V7_actual_native_binding']['sha256']
  binary=row['loaded_PhysX_binary_fingerprints'];assert binary['core_PhysX_plugin_identified'] is True and binary['own_already_loaded_PhysX_named_modules_only'] is True
  assert binary['all_physics_engine_binaries_globally_claimed'] is False
  assert len({r['normalized_path'] for r in binary['files']})==len(binary['files']) and binary['files']
  assert row['physics_engine_plugin_all_DLLs_pinned'] is False
  for hit in row['query_rows']:
   assert hit['resolved_plane_path']=='/World/ground/geometry/mesh'
   comparison=compare_actual_hit_readonly(independent,hit['hit'])
   assert comparison==hit['independent_source_reference_comparison']
   assert comparison['represented_query_within_original_1e6'] and comparison['normal_crosscheck_maxabs']<=1e-6
   assert hit['original_ideal_Z0_within_1e6']==(abs(hit['hit']['position'][2])<=1e-6)
   assert hit['original_ideal_normalZ1_within_1e6']==(abs(hit['hit']['normal'][2]-1.)<=1e-6)
  assert row['ideal_Z0_failure_count']==sum(not r['original_ideal_Z0_within_1e6'] for r in row['query_rows'])
 initial_reference=q['initial'];final_reference=q['final']
 for key in ('actual_USD_and_native_actor_metadata','source_reference'):
  assert initial_reference[key]==final_reference[key],('Actual Plane actor or metadata changed within case',key)
 assert initial_reference['loaded_PhysX_binary_fingerprints']['files']==final_reference['loaded_PhysX_binary_fingerprints']['files'],'Actual already loaded PhysX binary set changed within case'
 native=dict(raw_sha256=H(raw),all_controls_and_substeps_finite=True,actual_q30_policy35_action6_exact=True,no_reset_teleport_credit=True,mean_load_integral_error_N=mean_error,DC_hardware_actual_bounds_exact=True,COM_frame_original1e5_passed=True,actual_represented_plane_query_1e6_passed=True,query_source_reference_only=True,native_shape_local_pose_not_directly_read=True,public_source_to_binary_bitexact_not_proven=True,actual_original_ideal_Z0_false_count=sum(q[k]['ideal_Z0_failure_count'] for k in ('initial','final')),ordinary=int(a['terminated'].sum()),truncation=int(a['truncated'].sum()),complete_data_contract=True,missing_original_EXIT_NATURAL_preserved=not x['natural_app_close_present'])
 out=dict(seed=p['seed'],profile='white_v3',kind=kind,num_envs=N,steps=S,checkpoint_sha256=c['checkpoint_sha256'],data=native,full_behavior_review=S==1500,old_original_flags=p['native_readonly_witness']['old_original_flags'],original_report_sha256=H(O/'probe.json'),initial=initial)
 out['actual_white_v3_parameter_readbacks']=audit_white_v3(p)
 if S==1500:
  out['unchanged_v4_evidence']=evidence(p,'spin' if kind=='world' else kind,15)
  if kind=='flat':
   out['straight']=[dict(command=g['command_vx'],error=g['vel_error'],steady_error=g['steady_vel_error'],original_strict=g['strict_pass']) for g in p['groups'] if g['profile']=='constant' and abs(g['command_vx'])==1.5]
  if kind=='spin':
   out['pure4pi']=[]
   for g in p['groups']:
    if g['profile']=='spin' and abs(abs(g['wz'])-4*math.pi)<1e-6:
     ids=[i for i,gid in enumerate(p['group_ids']) if gid==g['group_id']];values=[p['per_environment']['yaw_rate'][i] for i in ids]
     out['pure4pi'].append(dict(command=g['wz'],values=values,within_original_absolute02_count=sum(abs(v-g['wz'])<=.2 for v in values),count=len(ids)))
  if kind=='world':
   legacy_metrics=p['world_cycle_metrics'];assert len(legacy_metrics)==64
   metrics=[];prefix_rows=[]
   for row in legacy_metrics:
    i=row['env_id'];failure=np.flatnonzero(done[:,i]);last=int(failure[0]) if len(failure) else S
    xy=np.concatenate((a['before_root'][0,i,:2][None],a['root'][:last,i,:2]));heading=np.concatenate((np.asarray(a['heading'][0,i])[None],a['heading'][:last,i]))
    # Derive exact first heading from actual first-physics xyzw root quaternion.
    quat=a['before_root'][0,i,3:7].astype(np.float64);qx,qy,qz,qw=quat;heading[0]=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
    times=np.arange(len(xy))*.01;direction=row['world_direction_rad'];sign=1 if row['command_yaw_rad_s']>0 else -1
    m=measure_world_cycles(times,xy,heading,direction,sign,-1);m.update({k:row[k] for k in ('env_id','group_id','command_yaw_rad_s','world_direction_rad','goal_m_s')})
    cross=(xy-xy[0])@np.array([-math.sin(direction),math.cos(direction)]);m['cross_peak_to_peak_m']=float(np.ptp(cross));metrics.append(m)
    dedrift=cross-(cross[-1]/times[-1])*times if times[-1]>0 else cross
    prefix_rows.append(dict(env_id=i,first_failure_control=last,valid_prefix_controls=last,whole_valid_prefix_duration_s=float(times[-1]),cross_dedrift_peak_to_peak_m=float(np.ptp(dedrift)),dedrift_definition='whole valid prefix endpoint linear cross drift subtracted; diagnostic only, no new acceptance threshold',all_actual_complete_cycles=m['cycles'],incomplete_tail_duration_s=m.get('partial_tail_duration_s'),post_failure_or_reset_samples_used=False))
   corrected=dict(p);corrected['world_cycle_metrics']=metrics
   original_target=target(corrected,.5)
   out.update(fullsignedcircle_actual_prefix=metrics,whole_signedcircle_original_target=original_target,all_valid_prefixes=prefix_rows,world_count=sum(x['pass_'] for x in original_target['rows']),world_sample_count=64,world_original_tolerance_m_s=max(.03,.1*.5),no_new_dedrift_threshold=True,legacy_poststep_trace_metrics_preserved=legacy_metrics)
 return out

def audit_white_v3(p):
 n=p['native_readonly_witness']['fixture_envs'];assert n==88
 for audit in (p['initial_parameter_audit'],p['final_parameter_audit']):
  assert audit['profile']=='white_v3' and audit['actual_parameters_pass'] and audit['legacy_full_dr_disabled'];assert audit['registered_ranges']==dict(mass=[.9,1.1],motor=[.9,1.1],friction=[.7,1.])
  assert audit['errors']['mass_relative_error']<1e-5 and all(v<1e-6 for k,v in audit['errors'].items() if k!='mass_relative_error')
  assert audit['num_envs']==88 and audit['material_buckets']==33
 original=[]
 for v in (p['native_readonly_witness']['first_physics_initial']['physical_parameters'],p['native_readonly_witness']['final_physical_parameters']):
  factor=np.asarray(v['mild_factor']);nominal=np.asarray(v['mild_nominal'],bool);mu=np.asarray(v['mild_mu']);assert factor.shape==nominal.shape==mu.shape==(88,) and factor.min()>=.9-1e-6 and factor.max()<=1.1+1e-6 and (factor[nominal]==1).all()
  buckets=np.concatenate(([.9],np.linspace(.7,1.,32)));assert np.min(abs(mu[:,None]-buckets),axis=1).max()<1e-6 and (abs(mu[nominal]-.9)<1e-6).all()
  for name in ('legs','wheels'):
   gains=np.asarray(v['motors'][name]['episode_scale']);assert np.array_equal(gains,np.asarray(v['mild_outputs'][name])) and gains.min()>=.9-1e-6 and gains.max()<=1.1+1e-6 and (gains[nominal]==1).all() and (np.asarray(v['motors'][name]['step_scale'])==1).all()
  mass=np.asarray(v['mass']);inertia=np.asarray(v['inertia']);assert mass.shape[0]==inertia.shape[0]==88
  base_mass=mass/factor[:,None];base_inertia=inertia/factor[:,None,None];assert np.max(abs(base_mass-base_mass[:1]))<1e-5 and np.max(abs(base_inertia-base_inertia[:1]))<1e-6;original.append((base_mass,base_inertia))
  assert np.isfinite(np.asarray(v['COM'])).all() and np.max(abs(np.asarray(v['spring'])-1))<=.100001 and np.max(abs(np.asarray(v['gas'])-1))<=.100001
  for values in v['PD'].values():assert np.min(values)>=.95-1e-6 and np.max(values)<=1.05+1e-6
 assert np.max(abs(original[0][0]-original[1][0]))<1e-5 and np.max(abs(original[0][1]-original[1][1]))<1e-6
 return dict(actual_white_v3_ranges_and_nominal_mask_and_motor_scales_CPU=True,source_bound_simulator_readback_not_hardware_calibration=True,not_full_training20k_DR_restore=True)

def main():
 import os,torch
 os.environ['CUDA_VISIBLE_DEVICES']='';torch.set_num_threads(4)
 steps=int(sys.argv[1]);assert steps in (120,1500);R=D/'reports';case='e2closed101_signed4_'+('native120' if steps==120 else 'full1500')+'_v7';j=read(R/('E2_CLOSED101_'+('NATIVE120' if steps==120 else 'FULL1500')+'_V7_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'));assert j['case']==case and j['parent_child_launcher_actual_absent'] and j['shared_OS_lock_free'] and j['original_error'] is None
 files=j['files']
 for row in files:
  if row.get('local_path'):assert H(row['local_path'])==row['SHA'] and Path(row['local_path']).stat().st_size==row['bytes']
 def path(name):return Path(next(x['local_path'] for x in files if x['relative'].endswith('/'+name)))
 folder=path('PARENT_EXIT_RECEIPT.json').parent;physical=audit_case(folder,dict(actual_parent_absent=True,actual_child_absent=True,shared_OS_lock_free=True));assert physical['steps']==steps
 route=read(path('E2_CLOSED101_SINGLE_POLICY_CONTROL_ACTUAL.json'));src=read(path('E2_CLOSED101_SINGLE_POLICY_SOURCE_ACTUAL.json'));assert route['controls']==steps and route['all9_initial_final_actor_STD_exact'] and route['only_single_actor_forward'] and route['no_gate_or_other_expert_forward'] and route['optimizer_updates']==0 and src['no_construction_CPUCUDA_RNG_draw'] and route['source_SHA']==src['source_SHA']==physical['checkpoint_sha256']
 with np.load(path('E2_CLOSED101_SINGLE_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k].copy() for k in z.files}
 with np.load(path('retention_full_control_substep_actual.npz'),allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 assert np.array_equal(b['shared_obs'],a['policy_obs']) and np.array_equal(b['raw_action'],a['raw_actor_action']) and np.array_equal(b['clipped_action'],a['processed_action']);normal=np.zeros((steps,88,7),np.float32);normal[...,0]=1;assert np.array_equal(normal,b['shared_obs'][...,28:35]);last=np.zeros((88,6),np.float32)
 for t in range(steps):assert np.array_equal(last,b['shared_obs'][t,:,22:28]);last=a['processed_action'][t].copy();last[a['terminated'][t]|a['truncated'][t]]=0
 source=Q/'source/E2_closed101.pt';assert H(source)==physical['checkpoint_sha256'];ck=torch.load(source,map_location='cpu',weights_only=False);state=ck['actor_state_dict'];rng=torch.get_rng_state().clone();error=0.;flat=b['shared_obs'].reshape(-1,35)
 with torch.inference_mode():
  for i in range(0,len(flat),4096):
   mean=torch.from_numpy(flat[i:i+4096].copy())
   for layer in (0,2,4,6):
    mean=torch.nn.functional.linear(mean,state[f'mlp.{layer}.weight'],state[f'mlp.{layer}.bias'])
    if layer!=6:mean=torch.nn.functional.elu(mean)
   expected=b['raw_action'].reshape(-1,6)[i:i+len(mean)];error=max(error,float(abs(mean.numpy()-expected).max()));assert np.allclose(mean.numpy(),expected,atol=1e-4,rtol=3e-5)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 probe=read(path('probe.json'));g=np.arange(88)%11;assert list(probe['group_ids'])==list(g)
 heading=2*np.arctan2(a['before_root'][...,5],a['before_root'][...,6])
 # Exact xyzw yaw reference, including tilted poses.
 q=a['before_root'][...,3:7].astype(np.float64);qx,qy,qz,qw=np.moveaxis(q,-1,0);heading=np.arctan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
 directions=np.array([0,0,0,0,0,math.pi/2,math.pi/2,math.pi/3,math.pi/3,math.pi,math.pi]);yaw=np.array([0,0,0,4,-4,4,-4,4,-4,4,-4],np.float32)[g];assert np.array_equal(a['command'][...,2],np.broadcast_to(yaw,(steps,88))) and not a['command'][...,1].any();moving=g>=3
 pose_reference_error=abs(np.cos(heading[:,moving]-directions[g[moving]])-a['command'][:,moving,0]);initial_pose_reference_max=float(pose_reference_error[0].max());later_pose_reference_max=float(pose_reference_error[1:].max())
 tracepath=path(Path(probe['whole_trace']['path']).name);assert H(tracepath)==probe['whole_trace']['sha256']
 with np.load(tracepath,allow_pickle=False) as z:actual_heading=z['heading'].copy()
 assert actual_heading.shape==(steps+1,88);not_ended=~(a['terminated']|a['truncated']);assert np.array_equal(actual_heading[1:][not_ended],a['heading'][not_ended])
 expected=np.cos(actual_heading[:-1,moving].astype(np.float64)-directions[g[moving]]);command_error=float(abs(expected-a['command'][:,moving,0]).max());assert command_error<=1e-5
 source_heading_authority=dict(actual_predecision_heading_w_trace_used_all_rows_including_first=True,trace_SHA=H(tracepath),pose_XYZW_first_reference_false_max=initial_pose_reference_max,pose_XYZW_later_reference_max=later_pose_reference_max,initial_heading_w_vs_root_state_quat_discrepancy_cause_not_proven=True,original_CPU_first_pose_reference_failure_retained=True,no_physical_threshold_or_saved_raw_changed=True)
 out=dict(epoch=time.time(),passed=True,case=case,controls=steps,callbacks=steps*4,num_envs=88,source_SHA=physical['checkpoint_sha256'],all_saved_actor_rows_CPU_reconstructed=True,CPU_GPU_mean_max_error=error,not_bitexact=True,source9STD_initial_final_exact=True,normal35_last_actual_clipped6_selectedreset_exact=True,signed4_worldVpoint5_reference_error=command_error,source_heading_reference=source_heading_authority,physical=physical,parent_child_launcher_actual_absent_and_shared_lock_free=True,native_not_full1500_qualification=steps==120,no_PPO_no_canonical=True,all_legacy_false_retained=True)
 dest=R/('E2_CLOSED101_'+('NATIVE120' if steps==120 else 'FULL1500')+'_V7_ALL_PHYSICAL_SOURCE_CPU_ACTUAL.json');assert not dest.exists();dest.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,controls=steps,callbacks=steps*4,CPUmeanmax=error,reference_error=command_error,no_skill_promotion_claim=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('E2_CLOSED101_V7_PHYSICAL_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),old_raw_and_false_retained_no_GPU_replay=True),indent=2),encoding='utf8');raise
