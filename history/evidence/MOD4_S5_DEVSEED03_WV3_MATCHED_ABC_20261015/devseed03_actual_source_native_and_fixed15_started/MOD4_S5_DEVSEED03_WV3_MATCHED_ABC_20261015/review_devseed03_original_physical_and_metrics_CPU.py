"""Strict data review and unchanged old behavior facts. Never launches or connects."""
from pathlib import Path
import argparse,hashlib,json,math,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;C=D/'payload/cpu_contracts';sys.path[:0]=[str(C),str(D/'payload')]
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
 assert not (O/'ORIGINAL_ERROR.json').exists()
 text=(folder/'worker.log').read_text(encoding='utf8',errors='replace').lower()
 assert not any(word in text for word in ('traceback (most recent call last)','gpu collision stack overflow','physx error','contacts dropped','patches dropped','cuda out of memory'))
 kind=c['kind'];N={'flat':80,'spin':88,'world':88}[kind];S=c['steps'];assert S in (120,1500)
 assert c['num_envs']==N and c['callbacks']==S*4 and c['no_PPO'] and not c['qualification_claimed']
 # The inherited flat source retains its original field schema without a top-level profile.
 assert p['seed']==20261003 and p['steps']==S
 assert c['probe']['sha256']==H(O/'probe.json')
 manifest=read(D/'payload/RETENTION_CPU_MANIFEST_V8.json')
 assert c['checkpoint_sha256'] in {row['sha256'] for row in manifest['sources'].values()}
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
 query=O/'retention_plane_query_actual.json';assert H(query)==p['native_readonly_witness']['actual_plane_query']['sha256']
 q=read(query)
 for phase in ('initial','final'):
  row=q[phase];assert row['tolerance_m']==1e-6 and row['authored_plane']['type']=='Plane' and row['authored_plane']['axis']=='Z' and len(row['query_rows'])==N
  assert row['scene_query_support_requested'] and row['actual_USD_scene_query_support']
  allhits=O/Path(row['allhits_evidence']['path']).name;assert H(allhits)==row['allhits_evidence']['sha256'] and allhits.stat().st_size==row['allhits_evidence']['bytes']
  original_hits=read(allhits);assert original_hits['complete_all_envs'] and len(original_hits['all_rays'])==N
  assert row['source_reference_only'] is True and row['actual_shape_local_pose_read'] is False
  assert row['public_source_to_installed_binary_bitexact_proven'] is False and row['reference_defined_from_reported_hits'] is False
  assert row['captured_RNG_before']==row['captured_RNG_after'] and row['original_V6_fullcase_failed_unchanged'] is True
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
 out=dict(kind=kind,num_envs=N,steps=S,checkpoint_sha256=c['checkpoint_sha256'],data=native,full_behavior_review=S==1500,old_original_flags=p['native_readonly_witness']['old_original_flags'],original_report_sha256=H(O/'probe.json'),initial=initial)
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

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True);parser.add_argument('--boundary',required=True);parser.add_argument('--output',required=True);parser.add_argument('--baseline-attempt');parser.add_argument('--baseline-boundary');args=parser.parse_args()
 out=Path(args.output);assert not out.exists()
 result=audit_case(args.attempt,read(args.boundary))
 if args.baseline_attempt:
  assert args.baseline_boundary;baseline=audit_case(args.baseline_attempt,read(args.baseline_boundary));assert baseline['kind']==result['kind'] and baseline['steps']==result['steps']
  assert baseline['checkpoint_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
  assert result['checkpoint_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
  for key in ('root','q30','physical_parameters','phase'):
   assert baseline['initial'][key]==result['initial'][key],('Actual initial pair differs',key)
  aq=baseline['initial']['plane_query'];bq=result['initial']['plane_query']
  for key in ('authored_plane','tolerance_m','scene_query_support_requested','actual_USD_scene_query_support','actual_USD_and_native_actor_metadata','source_reference'):
   assert aq[key]==bq[key],('Actual plane authority pair differs',key)
  assert aq['loaded_PhysX_binary_fingerprints']['files']==bq['loaded_PhysX_binary_fingerprints']['files'],'Actual loaded PhysX binary identity differs across pair'
  assert len(aq['query_rows'])==len(bq['query_rows'])
  for ar,br in zip(aq['query_rows'],bq['query_rows']):
   for key in ('env_id','origin','resolved_plane_path','identity_resolution'):assert ar[key]==br[key]
   for key in ('position','normal','distance','collision'):assert ar['hit'][key]==br['hit'][key]
  # Both complete query receipt files remain independently byteSHA verified;
  # per-attempt evidence paths/hashes are identities of distinct saved receipts.
  result=dict(candidate=result,baseline=baseline,actual_initial_root_q30_parameters_recipes_RNG_queues_exact=True)
 report=dict(epoch=time.time(),trial_id='S5_DEVSEED03_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW',result=result,original_false_and_failure_prefix_preserved=True,no_GPU_no_SSH_no_PPO=True,qualification_not_claimed=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(output=str(out),review_complete=True,qualification_not_claimed=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R=D/'reports';R.mkdir(exist_ok=True);p=R/('CPU_ACTUAL_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_no_SSH=True),indent=2),encoding='utf8');raise
