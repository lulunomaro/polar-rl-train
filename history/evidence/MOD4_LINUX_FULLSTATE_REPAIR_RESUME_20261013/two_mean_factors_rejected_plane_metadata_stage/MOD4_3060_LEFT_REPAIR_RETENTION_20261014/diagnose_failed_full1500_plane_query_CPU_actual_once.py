"""Retained failed1500 data analysis; no original verdict changes or GPU replay."""
from pathlib import Path
import ast,hashlib,json,time
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';out=R/'FAILED_FULL1500_V6_NATIVE_PLANE_QUERY_CPU_DIAGNOSIS.json';assert not out.exists()
collection_path=R/'retention_baseline1aa_flat_1500_v6_CURRENT_ACTUAL_1791949743916981900.json';collection=json.loads(collection_path.read_bytes())
A=D/'actual_collections/retention_baseline1aa_flat_1500_v6/1791949743916981900/attempts/retention_baseline1aa_flat_1500_v6';O=A/'output'
def h(path):
 digest=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
 return digest.hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
needed=[O/'probe.json',O/'retention_full_control_substep_actual.npz',O/'QUERY_first_physics_ALLHITS_ACTUAL.json',O/'QUERY_final_ALLHITS_ACTUAL.json',O/'ORIGINAL_ERROR.json',A/'PARENT_EXIT_RECEIPT.json']
index=[]
for path in needed:
 row=next(x for x in collection['collected_files'] if Path(x['local_path']).resolve()==path.resolve())
 assert row['two_host_byteSHA_exact'] and row['sha256']==h(path) and row['bytes']==path.stat().st_size
 index.append(dict(path=str(path),bytes=path.stat().st_size,sha256=h(path)))
parent=read(A/'PARENT_EXIT_RECEIPT.json');assert parent['exit_code']==1 and parent['original_error_present'] and not parent['complete_data_contract_present'] and parent['no_PPO'] and not parent['canonical_budget_written']
assert collection['shared_OS_lock_free'] and not any(collection['actual_PID_identities'].values())
p=read(O/'probe.json');assert p['steps']==1500 and p['seed']==20261002 and p['nonfinite'] is False and p['resets']==0
with np.load(O/'retention_full_control_substep_actual.npz',allow_pickle=False) as archive:raw={k:archive[k].copy() for k in archive.files}
assert raw['root'].shape==(1500,80,13) and raw['q'].shape==(1500,80,30) and raw['policy_obs'].shape==(1500,80,35)
assert raw['substep_force'].shape==(6000,80,2,3)
for k,value in raw.items():
 if value.dtype.kind in 'fc':assert np.isfinite(value).all(),k
assert np.array_equal(np.clip(raw['raw_actor_action'],-6.,6.),raw['vec_clipped_action']) and np.array_equal(raw['vec_clipped_action'],raw['processed_action'])
assert np.array_equal(raw['policy_obs'][...,:3],raw['command'])
assert np.array_equal(raw['before_root'][1:],raw['after_reset_root'][:-1]) and not raw['terminated'].any() and not raw['truncated'].any() and not raw['reasons'].any()
assert np.array_equal(raw['before_root'][1:],raw['root'][:-1]) and not raw['episode'].any()
force=np.maximum(raw['substep_force'].reshape(1500,4,80,2,3)[...,2],0.).astype(np.float64).sum(1)*.0025
mean_error=float(np.max(abs(force-raw['impulse']))/.01);assert mean_error<=.1
assert np.array_equal(raw['substep_actual_applied_effort'],np.clip(raw['substep_actual_applied_effort'],raw['substep_torque_speed_lower'],raw['substep_torque_speed_upper']))
assert float(raw['substep_COM_frame_error_m'].max())<1e-5
physics_data_salvage=dict(full1500_raw_retained=True,controls=1500,callbacks=6000,num_envs=80,all_finite=True,raw_policy_vs_clip_vs_manager_exact=True,actual_policy35_command_exact=True,all_no_reset_prefixes_retained=True,ordinary=0,truncation=0,mean_load_integral_error_N=mean_error,actual_DC_bounds_passed=True,COM_original1e5_passed=True,raw_max_closure_m=float(raw['closure'].max()),raw_max_mimic_rad=float(raw['mimic'].max()),original_flags={k:p.get(k) for k in ('strict_pass','strict_pass_window','physics_pass','nonfinite','resets')},constant_signed15_speed=[{k:g[k] for k in ('command_vx','vel_error','steady_vel_error','strict_pass')} for g in p['groups'] if g['profile']=='constant' and abs(g['command_vx'])==1.5],scope='Read-only retained behavior/numerical facts, not original fullcase PASS or COMPLETE repair')
query_summaries=[];all_rows=[]
for name in ('QUERY_first_physics_ALLHITS_ACTUAL.json','QUERY_final_ALLHITS_ACTUAL.json'):
 query=read(O/name);rows=[]
 assert query['actual_USD_scene_query_support'] is True and query['authored_plane']['point']==[0.,0.,0.] and query['authored_plane']['normal']==[0.,0.,1.]
 for ray in query['all_rays']:
  selected=min(ray['selected_plane_hits'],key=lambda x:x['hit']['distance']);hit=selected['hit'];assert not ray['serializer_errors'] and selected['resolved_plane_path']=='/World/ground/geometry/mesh'
  rows.append(dict(phase=query['phase'],env_id=ray['env_id'],origin=ray['origin'],position=hit['position'],normal=hit['normal'],distance=hit['distance'],actual_rigid_body=hit['rigid_body'],actual_collision=hit['collision']))
 pts=np.asarray([x['position'] for x in rows]);norm=np.asarray([x['normal'] for x in rows]);orig=np.asarray([x['origin'] for x in rows]);dist=np.asarray([x['distance'] for x in rows]);offset=np.einsum('ij,ij->i',pts,norm)
 assert np.array_equal(pts[:,2],(orig[:,2].astype(np.float32)-dist.astype(np.float32)).astype(np.float64))
 query_summaries.append(dict(name=name,complete_all_envs=query.get('complete_all_envs',False),actual_ray_count=len(rows),xyz_range=[pts.min(0).tolist(),pts.max(0).tolist()],reported_normal_unique=np.unique(norm,axis=0).tolist(),distance_ulp_at10m=float(np.spacing(np.float32(10.))),point_Z_equals_float32_origin_minus_distance_exact=True,reported_normal_dot_hit_diagnostic_plane_offset_range=[float(offset.min()),float(offset.max())],all_rows=rows))
 all_rows+=rows
assert len(query_summaries[0]['all_rows'])==80 and not query_summaries[1]['complete_all_envs']
points=np.asarray([x['position'] for x in all_rows]);normals=np.asarray([x['normal'] for x in all_rows]);origins=np.asarray([x['origin'] for x in all_rows]);observed_distance=np.asarray([x['distance'] for x in all_rows]);observed_z=points[:,2]
# Diagnostic only: this uses the actual reported normal and assumes d=0.
# It cannot independently validate geometry or become the expected query plane.
n=normals.astype(np.float32);o=origins.astype(np.float32)
predicted_dist=((n*o).sum(-1)/n[:,2]).astype(np.float32);predicted_z=(o[:,2]-predicted_dist).astype(np.float32)
exact_reconstruction=dict(only_diagnostic_not_independent_ground_expectation=True,assumed_plane_offset_zero=True,reported_normal_used=True,exact_distance_matching_count=int((predicted_dist.astype(np.float64)==observed_distance).sum()),exact_Z_matching_count=int((predicted_z.astype(np.float64)==observed_z).sum()),sample_count=len(all_rows),maximum_Z_residual_m=float(np.max(abs(predicted_z.astype(np.float64)-observed_z))),maximum_distance_residual_m=float(np.max(abs(predicted_dist.astype(np.float64)-observed_distance))))
env1=query_summaries[1]['all_rows'][1];rn=np.asarray(env1['normal'],dtype=np.float64);xy=np.asarray(env1['origin'][:2]);hypothesis_z=-float(np.dot(rn[:2],xy)/rn[2])
short_ray_diagnostics=[]
for height in (10.,1.,.1):
 origin=np.asarray([*xy,height],dtype=np.float32);normal=np.asarray(rn,dtype=np.float32);distance=np.float32((normal*origin).sum()/normal[2]);z=np.float32(origin[2]-distance)
 short_ray_diagnostics.append(dict(readonly_origin_z_m=height,origin_ulp_m=float(np.spacing(np.float32(height))),hypothetical_normal_plane_z_m=hypothesis_z,predicted_float32_hit_z_m=float(z),original_world_Z1e6_would_pass=bool(abs(z)<=1e-6),actual_short_ray_not_run=True,not_independent_geometry_or_admission=True))
stub_report=R/'INSTALLED_RAYCAST_HIT_API_STUB_ACTUAL_1791948423570368200.json';stub=read(stub_report)['rows'][0];module=ast.parse(stub['text'])
transform_methods=[]
for cls in module.body:
 if isinstance(cls,ast.ClassDef) and cls.name in ('PhysX','PhysXSceneQuery','IPhysxSimulation'):
  for fn in cls.body:
   if isinstance(fn,ast.FunctionDef) and any(key in fn.name for key in ('transformation','shape_pose','shape_transform')):transform_methods.append(dict(owner=cls.name,method=fn.name,AST=ast.unparse(fn)))
spawn=D.parent/'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload/runtime/isaac/mod4/ground_plane_candidate.py';assert "plane.CreateAttribute('axis',Sdf.ValueTypeNames.Token).Set('Z')" in spawn.read_text(encoding='utf8')
report=dict(epoch=time.time(),trial_id='FAILED_FULL1500_V6_NATIVE_PLANE_QUERY_DIAGNOSIS_CPU_ACTUAL',original_failure_preserved=True,original_fullcase_pass=False,original_COMPLETE_missing=True,original_parent_cost_seconds=parent['unique_actual_parent_load_run_save_exit_seconds'],no_PPO_canonical_excluded=True,two_host_evidence=index,physics_data_salvage=physics_data_salvage,query_summaries=query_summaries,diagnostic_float32_reconstruction=exact_reconstruction,short_readonly_ray_hypotheses=short_ray_diagnostics,
 conclusion=dict(observed_first80_then_final_env1_world_Z_original1e6_failure=True,reported_normal_X_2powminus23_and_Z1plus2powminus23_consistent_across_all_retained_hits=True,both_micro_tilt_and_10m_float32_cancellation_supported_not_only_cancellation=True,physical_tilt_not_independently_proven_from_actual_shape_transform=True,shorter_origin_alone_not_predicted_to_pass_env1_original_world_Z_bound=True,cannot_infer_expected_plane_from_same_hits=True,cannot_use_idealZ_fallback_or_tol2e6=True),
 source_evidence=dict(nativePlane_source=dict(path=str(spawn),sha256=h(spawn),authoring='USD Plane axis Z, no explicit transform authored in spawn; actual USD world transform captured identity'),actual_installed_stub=dict(report=str(stub_report),report_sha256=h(stub_report),actual_stub_sha256=stub['sha256']),available_transform_methods=transform_methods,no_saved_actual_native_shape_local_pose=True,no_frozen_SDK_Plane_axis_conversion_math_available=True),
 minimal_next_proposal=dict(status='CPU proposal only, no GPU package or launch',axis='Readonly actual native Plane pose/query representation diagnosis, preserving all worldground1e6 comparisons',required_independent_expectation='Actual geometry kind plus actor and shape-local native pose, or exact frozen SDK authoring-to-native Plane conversion arithmetic. Actor pose alone is insufficient unless actual shape local pose and local Plane convention are independently identified.',available_actor_pose_getter='PhysX.get_rigidbody_transformation(actual retained rigid_body=/World/ground/geometry/mesh), returns ret_val, worldposition,xyzw rotation; actual runtime call not yet performed',isolating_query_comparison='At identical XY, compare actual rays with originZ10/1/.1 without changing objects/steps/cache/RNG; retain every actual hit, use authored0 only as strict original anchor and prohibit deriving a replacement expected Plane from fitted hits',must_not_replay_failed_V6_fullcase=True,do_not_advance_on_shorter_ray_assumption=True,no_Plane_to_Mesh_change_in_current_fixed_scope=True),
 no_SSH_no_GPU_no_PPO_no_delete_no_hotpatch=True,no_budget_operations=True,thresholds_and_old_flags_unchanged=True,pending_Git_by_root=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),original_fullcase_pass=False,physics_data_salvage={k:physics_data_salvage[k] for k in ('controls','callbacks','ordinary','truncation','constant_signed15_speed')},diagnostic_float32_reconstruction=exact_reconstruction,short_readonly_ray_hypotheses=short_ray_diagnostics,conclusion=report['conclusion']),ensure_ascii=False))
