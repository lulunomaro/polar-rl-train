"""Independent CPU artifact review. No connector, SDK import, or simulator launch."""
from pathlib import Path
import hashlib,json,numpy as np
from scipy.spatial.transform import Rotation
SOURCE='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
PROFILE='e3_yaw_pi_body_sign_same_world_fullfootprint_v1'
PROTOCOL='diagnostic_E3_yawpi_bodyflip_same_world_full80_original_physical_v1'
D=Path(__file__).resolve().parent;W=D.parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def exact_tree(a,b,path='root'):
 assert type(a)==type(b),(path,'type')
 if isinstance(a,dict):
  assert set(a)==set(b),(path,'keys')
  for k in a:exact_tree(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),(path,'length')
  for i,(x,y) in enumerate(zip(a,b)):exact_tree(x,y,path+'/'+str(i))
 else:assert a==b,(path,a,b)
def actual_row(rows,suffix,allow_closed_log_flag=False):
 x=[r for r in rows if r['relative'].replace('\\','/').endswith('/'+suffix)]
 assert len(x)==1,(suffix,len(x));x=x[0]
 assert x['remote_local_byteSHA_exact'] is True and (not x.get('mutable_pending',False) or (allow_closed_log_flag and suffix=='worker.log'))
 p=Path(x['local_path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],suffix
 return x
def pi_np(q):return np.stack((-q[:,1],q[:,0],q[:,3],-q[:,2]),-1)
def birth_receipt(r):
 assert r['profile']==PROFILE and r['original_full_reset_called_once'] is True
 assert r['full_collision_points']==25200 and r['full_q30_exact'] is True and r['XY_exact'] is True and r['zero_velocity_exact'] is True
 assert r['quaternion_changed_NOT_root30_byteexact'] is True and r['no_rng_draw'] is True and r['extra_physics_steps_forward_render_reset']==0
 assert r['original_clearance_m']==.002 and r['original_clearance_tolerance_m']==1e-5 and r['query_distance_m']==10.
 assert r['minimum_sampled_clearance_m']>=.002-1e-5 and r['legal_sampled_fullfootprint_not_continuous_collision_certificate'] is True
 ids=np.asarray(r['ids']);assert ids.ndim==1 and len(ids)>0 and len(np.unique(ids))==len(ids) and (ids>=0).all() and (ids<80).all()
 before=np.asarray(r['original_root_xyzw'],np.float32);after=np.asarray(r['factor_root_xyzw'],np.float32)
 assert before.shape==after.shape==(len(ids),13) and np.isfinite(before).all() and np.isfinite(after).all()
 assert np.array_equal(after[:,:2],before[:,:2]) and np.array_equal(after[:,7:],before[:,7:]) and not after[:,7:].any()
 assert np.array_equal(after[:,3:7],pi_np(before[:,3:7]))
 assert np.max(abs(np.linalg.norm(after[:,3:7],axis=-1)-1.))<=1e-6
 assert np.array_equal(np.asarray(r['root_Z_delta_m'],np.float32),after[:,2]-before[:,2])
 return ids,before,after
def independent_safe_z(ids,after,world_triangles,points):
 """Use authored float32 triangle vertices, never sampled GPU heights.
 Each selected Wave cell is the verified x-only extruded procedural mesh.
 Interpolate its independent surface in world X after checking its mesh topology.
 """
 rotations=Rotation.from_quat(after[:,3:7]).as_matrix().astype(np.float32)
 offsets=np.einsum('nij,pj->npi',rotations,points,dtype=np.float32)
 expected=[];min_clear=[]
 for local,env in enumerate(ids):
  tri=np.asarray(world_triangles[env],np.float32);flat=np.unique(tri.reshape(-1,3),axis=0)
  ys=np.unique(flat[:,1]);assert len(ys)==2 and np.isfinite(flat).all()
  xs=np.unique(flat[:,0]);assert len(flat)==2*len(xs)
  heights=[]
  for x in xs:
   vertices=flat[flat[:,0]==x];assert vertices.shape==(2,3) and np.array_equal(np.sort(vertices[:,1]),ys) and vertices[0,2]==vertices[1,2]
   heights.append(float(vertices[0,2]))
  rayxy=offsets[local,:,:2]+after[local,None,:2]
  assert rayxy[:,0].min()>=xs[0] and rayxy[:,0].max()<=xs[-1] and rayxy[:,1].min()>=ys[0] and rayxy[:,1].max()<=ys[1]
  ground=np.interp(rayxy[:,0].astype(np.float64),xs.astype(np.float64),np.asarray(heights,np.float64))
  predicted=float(np.max(ground+.002-offsets[local,:,2].astype(np.float64)))
  gap=after[local,2].astype(np.float64)+offsets[local,:,2].astype(np.float64)-ground
  assert abs(float(after[local,2])-predicted)<=1e-6,'Own fullfootprint safeZ differs from independent authored float32 surface'
  assert gap.min()>=.002-1e-5,'Fullfootprint sampled placement below original clearance'
  expected.append(predicted);min_clear.append(float(gap.min()))
 return dict(expected_Z_m=expected,actual_Z_error_max_m=float(np.max(abs(after[:,2]-np.asarray(expected)))),independent_min_clearance_m=min(min_clear),points_per_env=25200,query_Z_tolerance_m=1e-6,clearance_tolerance_m=1e-5)
def route_rows(data,report):
 steps=len(data['root']);scope=report['route_scope'];centers=np.asarray(scope['tile_centers']);half=scope['wave_x_halfspan_m'];wheel=[report['body_names'].index(x) for x in ('left_wheel','right_wheel')]
 mean=np.maximum(data['physical_wheel_force_N'].reshape(steps,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
 rows=[]
 for env in range(80):
  group=int(data['group_ids'][env]);sign=1 if group==0 else -1;episodes=[];complete=False;position=False
  for episode in np.unique(data['episode'][:,env]):
   selected=np.flatnonzero(data['episode'][:,env]==episode);failed=selected[data['terminated'][selected,env]]
   if len(failed):selected=selected[selected<failed[0]]
   if not len(selected):continue
   x=(data['COM_link_pos'][selected,env][:,wheel,0]-centers[env,0])*sign
   before=x.max(1)<-half-.2;after=x.min(1)>half+.2;load=mean[selected,env].min(1)>1.
   pos=bool(group!=2 and before.any() and after.any() and np.flatnonzero(before).min()<np.flatnonzero(after).max())
   contact=bool(group!=2 and (before&load).any() and (after&load).any() and np.flatnonzero(before&load).min()<np.flatnonzero(after&load).max())
   assert pos==contact,'Actual original1N support and signed wheel position disagree'
   complete|=contact;position|=pos
   episodes.append(dict(episode=int(episode),valid_first_control=int(selected[0]),valid_last_control=int(selected[-1]),valid_controls=len(selected),ordinary_failure_control=int(failed[0]) if len(failed) else None,valid_unfinished_prefix=group!=2 and not contact,signed_wheel_route_range=[float(x.min()),float(x.max())],before_position_controls=selected[before].tolist(),after_position_controls=selected[after].tolist(),before_double1N_controls=selected[before&load].tolist(),after_double1N_controls=selected[after&load].tolist(),position_complete=pos,contact_complete=contact,position_contact_agree=True))
  rows.append(dict(env=env,group=group,world_cohort='forward' if group==0 else 'reverse' if group==1 else 'standing',BODY_direction='reverse' if group==0 else 'forward' if group==1 else 'standing',standing_no_transit_requirement=group==2,position_complete=position,contact_complete=complete,all_valid_episodes=episodes))
 return rows
def review(collection_path,baseline_review_path,steps,native_admission=None):
 assert steps in (120,1500)
 col=read(collection_path);c=col['outputs']['COMPLETE_ACTUAL.json'];ex=col['states']['PARENT_EXIT_RECEIPT.json']
 assert c and c['passed_data_contract'] is True and c['num_envs']==80 and c['steps']==steps and c['callbacks']==steps*4
 assert c['protocol']==PROTOCOL and c['checkpoint_sha256']==SOURCE and c['no_PPO'] is True and c['qualification_claimed'] is False
 assert c['native120_not_full15s']==(steps==120) and ex['exit_code']==0 and ex['no_PPO'] is True and ex['canonical_budget_written'] is False and not ex['original_error_present']
 assert col['shared_actual_OS_lock_free'] is True and col['actual_PID_identities'] and all(x['running'] is False for x in col['actual_PID_identities'])
 assert col['outputs'].get('ORIGINAL_ERROR.json') is None
 files=col['local_collected_files'];rawrow=actual_row(files,'route_raw.npz');reportrow=actual_row(files,'probe.json');queryrow=actual_row(files,'probe.json.worldmesh_query.npz')
 assert rawrow['sha256']==c['raw']['sha256'] and reportrow['sha256']==c['original_report']['sha256'] and queryrow['sha256']==c['query']['sha256']
 report=read(reportrow['local_path']);assert report['protocol']==PROTOCOL and report['checkpoint_sha256']==SOURCE and report['steps']==steps and report['num_envs']==80 and report['seed']==20260928 and report['profile']=='white_v3' and report['new_learning'] is False and report['optimizer_updates']==0
 actor=col['outputs'].get('FROZEN_POLICY_SOURCE_ACTUAL.json') or read(actual_row(files,'FROZEN_POLICY_SOURCE_ACTUAL.json')['local_path'])
 assert actor['source_SHA']==SOURCE and actor['actual_actor_nine_GPU_tensors_source_exact'] is True and actor['only_actor_loaded'] is True and actor['source_saved_envs']==20000 and actor['fixture_envs']==80 and actor['no_PPO'] is True and actor['no_training_DR_projection'] is True
 with np.load(rawrow['local_path']) as z:data={k:z[k].copy() for k in z.files}
 assert all(np.isfinite(x).all() for x in data.values())
 for name,shape in [('root',(steps,80,13)),('before_root',(steps,80,13)),('q',(steps,80,30)),('policy_obs',(steps,80,35)),('physical_wheel_force_N',(steps*4,80,2,3))]:assert data[name].shape==shape,name
 groups=np.arange(80)%3;targets=np.array([-.3,.3,0],np.float32)[groups]
 assert np.array_equal(groups,data['group_ids']) and np.array_equal(targets,data['targets_m_s']) and np.array_equal(data['command'][:,:,0],np.broadcast_to(targets,(steps,80))) and not data['command'][:,:,1:].any()
 assert np.array_equal(data['processed_action'],np.clip(data['action'],-6.,6.))
 scope=report['route_scope'];assert scope['size_m']==[9.,9.] and scope['tile_rows']==(np.arange(80)//2).tolist() and scope['flat_support_margin_m']==.4 and scope['actual_query_ground_tolerance_m']==1e-6
 centers=np.asarray(scope['tile_centers']);starts=centers.copy();half=scope['wave_x_halfspan_m'];assert abs(half*2-2.406422727)<1e-8
 starts[groups==0,0]-=half+.4;starts[groups==1,0]+=half+.4;assert np.array_equal(starts,np.asarray(scope['requested_starts']))
 names=report['reason_names'];ordinary=('bad_orientation','base_contact','low_base','closure');trunc=('time_out','rough_route_boundary');assert set(names)==set(ordinary+trunc+('mimic',))
 o=data['reasons'][...,[names.index(x) for x in ordinary]].any(-1);t=data['reasons'][...,[names.index(x) for x in trunc]].any(-1)
 assert np.array_equal(o,data['terminated']) and np.array_equal(t,data['truncated']) and not data['reasons'][...,names.index('mimic')].any()
 done=o|t;assert np.array_equal(np.diff(data['episode'],axis=0),done[:-1].astype(data['episode'].dtype)) and np.array_equal(data['before_root'][1:][~done[:-1]],data['root'][:-1][~done[:-1]])
 mean=np.maximum(data['physical_wheel_force_N'].reshape(steps,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
 contacterror=float(abs(mean-data['impulse']/np.float32(.01)).max());assert contacterror<=.1
 tau=data['physical_hardware_actual_applied_effort'];assert tau.shape==(steps*4,80,6) and np.array_equal(tau,np.clip(tau,data['physical_hardware_torque_speed_lower'],data['physical_hardware_torque_speed_upper']))
 hw=col['outputs']['SUBSTEP_HARDWARE_COM_ACTUAL.json'];assert hw['callbacks']==steps*4 and hw['motor_torque_speed_bounds_exact'] is True and hw['COM_frame_max_error_m']<1e-5
 assert report['actual_physical_callbacks']==steps*4 and all(x==steps*4 for x in report['actual_action_callbacks'].values()) and report['physical_action_audit']['application_formula_max_error']==0
 assert report['independent_ground_max_error_m']<=1e-6 and report['height_reward_formula_max_error']<=1e-6 and data['mimic'].max()<=.01
 with np.load(queryrow['local_path']) as z:query={k:z[k].copy() for k in z.files}
 qe=float(abs(query['actual_sampled_ground']-query['expected_actual_ground']).max());assert qe<=1e-6 and query['world_triangles'].shape[0]==80 and np.isfinite(query['world_triangles']).all()
 baseline=read(baseline_review_path);assert baseline['passed'] is True and baseline['source_SHA']==SOURCE and baseline['controls']==1500 and baseline['callbacks']==6000
 br=read(baseline['original_report']['local_path']);assert sha(baseline['original_report']['local_path'])==baseline['original_report']['sha256']
 base_data=read(baseline['full_original_data_admission']['path']);assert base_data['passed'] is True and base_data['source_SHA']==SOURCE
 assert sha(base_data['query']['local_path'])==base_data['query']['sha256']
 with np.load(base_data['query']['local_path']) as z:
  assert np.array_equal(query['world_triangles'],z['world_triangles']) and np.array_equal(query['actual_world_ray_origins'],z['actual_world_ray_origins'])
 assert set(br['route_scope'])==set(scope)
 for key in scope:
  if key=='query_worldmesh_evidence':
   assert br['route_scope'][key]['bytes']==scope[key]['bytes'] and br['route_scope'][key]['sha256']==scope[key]['sha256']
  else:exact_tree(br['route_scope'][key],scope[key],'route_scope/'+key)
 for key in ('geometry','geometry_recipe','reason_names','declared_time_outs','body_names','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):exact_tree(br[key],report[key],key)
 sensor=report['sensor_recipe'];base_sensor=br['sensor_recipe'];dynamic_sensor_fields={'noise_draw_counts','max_abs_actual_bias_rad','bias_finite'}
 assert set(sensor)==set(base_sensor) and sensor['episode_leg_encoder_bias_bound_rad']==.0075 and sensor['bias_finite'] is True and sensor['max_abs_actual_bias_rad']<=.0075
 for key in sensor:
  if key not in dynamic_sensor_fields:exact_tree(base_sensor[key],sensor[key],'sensor_static_recipe/'+key)
 assert set(sensor['noise_draw_counts'])=={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'}
 assert len(set(sensor['noise_draw_counts'].values()))==1 and min(sensor['noise_draw_counts'].values())>=steps*80

 factor_row=actual_row(files,'YAWPI_FACTOR_FIRST_PHYSICS_ACTUAL.json');firstfactor=read(factor_row['local_path'])
 assert firstfactor['profile']==PROFILE and firstfactor['after_wrapper_reset'] is True and firstfactor['root30_NOT_baseline_byteexact'] is True and firstfactor['no_live_correction'] is True and firstfactor['no_PPO'] is True
 assert firstfactor['world_cohort_targets_m_s']==[.3,-.3,0.] and np.array_equal(np.asarray(firstfactor['body_targets_m_s'],np.float32),targets)
 first_row=actual_row(files,'FIRST_PHYSICS_INITIAL_ACTUAL.json');first=read(first_row['local_path']);assert first['values']==report['initial'] and first['readonly_no_setters_or_RNG'] is True
 initial=np.asarray(report['initial']['root'],np.float32);q0=np.asarray(report['initial']['q'],np.float32)
 assert np.array_equal(initial,data['before_root'][0]) and np.max(abs(initial[:,:2]-starts.astype(np.float32)))<=1e-6 and not initial[:,7:].any()
 for key in ('q','parameters','assignments','actual_all_physical_parameters','reset'):exact_tree(br['initial'][key],report['initial'][key],'initial/'+key)
 allbirths=report['yawpi_frame_factor']['all_actual_births'];prebirths=firstfactor['all_births_before_physics']
 assert allbirths[:len(prebirths)]==prebirths and prebirths[-1]==firstfactor['actual_last_birth']
 ids,origroot,factorroot=birth_receipt(prebirths[-1]);assert np.array_equal(ids,np.arange(80)) and np.array_equal(factorroot,initial) and np.array_equal(origroot,np.asarray(br['initial']['root'],np.float32))
 assert np.array_equal(q0,np.asarray(br['initial']['q'],np.float32))
 beforeheading=np.stack((1-2*(origroot[:,4]**2+origroot[:,5]**2),2*(origroot[:,3]*origroot[:,4]+origroot[:,6]*origroot[:,5])),-1)
 afterheading=np.stack((1-2*(factorroot[:,4]**2+factorroot[:,5]**2),2*(factorroot[:,3]*factorroot[:,4]+factorroot[:,6]*factorroot[:,5])),-1)
 worlderror=float(abs(beforeheading*np.array([.3,-.3,0.],np.float32)[groups,None]-afterheading*targets[:,None]).max());assert worlderror<=1e-7
 bank=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
 handoff=read(D/'reports/YAWPI_FRAME_FACTOR_CPU_HANDOFF_COMPLETE.json');actualfixture=read(handoff['CPU_actual_fixture']['path'])
 assert sha(bank)==actualfixture['actual_collision_bank']['sha256']
 with np.load(bank) as z:pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick].astype(np.float32)
 assert points.shape==(25200,3)
 birthreviews=[]
 for index,b in enumerate(allbirths):
  ids,origroot,after=birth_receipt(b);assert b['reset_index']==index
  active=np.array_equal(origroot[:,:2],starts[ids].astype(np.float32))
  witness=independent_safe_z(ids,after,query['world_triangles'],points) if active else None
  birthreviews.append(dict(reset_index=index,ids=ids.tolist(),target_full80_assignment_XY=active,independent_authored_mesh_fullfootprint=witness,constructor_other_cells_not_covered_by80_query_mesh=not active,native_getter_equal_requested_root_executed_assertion_bound_to_own_source=True,external_first_or_postreset_root_raw_witness_pending=True))
 cursor=len(prebirths)
 for step in range(steps):
  resetids=np.flatnonzero(done[step])
  if not len(resetids):continue
  assert cursor<len(allbirths),'Reset not evidenced by own factor birth receipt'
  ids,_,after=birth_receipt(allbirths[cursor]);assert np.array_equal(ids,resetids)
  if step+1<steps:
   assert np.array_equal(data['before_root'][step+1,ids],after),'Own native post-reset cached root getter differs from requested factor pose'
   birthreviews[cursor]['external_first_or_postreset_root_raw_witness_pending']=False
   birthreviews[cursor]['actual_external_root_raw_control']=step+1
  else:birthreviews[cursor]['final_last_control_reset_no_following_physics_frame_disclosed']=True
  cursor+=1
 assert cursor==len(allbirths),'Unexpected additional reset or teleport birth not matched to raw termination'
 birthreviews[len(prebirths)-1]['external_first_or_postreset_root_raw_witness_pending']=False;birthreviews[len(prebirths)-1]['actual_external_root_raw_control']=0
 assert all(x['independent_authored_mesh_fullfootprint'] is not None for x in birthreviews[len(prebirths)-1:]),'Physical birth lacks own target fullfootprint independent Z audit'
 started=col['outputs']['STARTED.json'];lease=started['lease'];snapshot=col['states']['SOURCE_SNAPSHOT_ACTUAL.json']
 assert lease['namespace']=='MOD4_E3_YAWPI_FRAME_FACTOR_20261014' and lease['checkpoint_sha256']==SOURCE and lease['GPU_lease_granted_by_root'] is True and lease['actual_shared_slot_idle_verified'] is True
 assert lease['case_parameters']==dict(steps=steps,num_envs=80,seed=20260928,body_sign=-1,world_sign=1,yaw_pi_body_flip=True,feedback_current=False,headless=True,device='cuda:0')
 for component in handoff['active_components']:
  expected=component['sha256'];name=component['relative'];assert sha(component['path'])==expected
  rows=[x for x in snapshot['files'] if Path(x['path']).name==name];assert len(rows)==1 and rows[0]['sha256']==expected and rows[0]['bytes']==component['bytes']
  rows=[x for x in lease['new_factor_components'] if x['relative']==name];assert len(rows)==1 and rows[0]['sha256']==expected
 assert lease['source_bundle_manifest_sha256']==handoff['original_shared_reference_manifest']['sha256']==snapshot['source_bundle_manifest_SHA']
 stdout=actual_row(files,'worker.log',allow_closed_log_flag=True);log=Path(stdout['local_path']).read_bytes();assert b'SimulationContext cleared' in log
 assert all(x not in log for x in (b'Contacts have been dropped',b'buffer overflow detected',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))
 native_binding=None
 if steps==1500:
  assert native_admission is not None,'Missing own new-factor native120 admission'
  native=read(native_admission);assert native['passed_actual_data_and_factor_admission'] is True and native['controls']==120 and native['callbacks']==480 and native['source_SHA']==SOURCE and native['factor_profile']==PROFILE and native['protocol']==PROTOCOL and native['qualified50'] is False
  assert native['active_component_SHA']=={x['relative']:x['sha256'] for x in handoff['active_components']}
  native_binding=dict(path=str(native_admission),sha256=sha(native_admission))
 per=route_rows(data,report);counts={str(g):sum(x['contact_complete'] for x in per if x['group']==g) for g in (0,1)}
 return dict(passed_actual_data_and_factor_admission=True,source_SHA=SOURCE,protocol=PROTOCOL,factor_profile=PROFILE,controls=steps,callbacks=steps*4,num_envs=80,cohorts=[27,27,26],collector=dict(path=str(collection_path),sha256=sha(collection_path)),raw=rawrow,query=queryrow,original_report=reportrow,first_physics_snapshot=first_row,factor_firstphysics_snapshot=factor_row,baseline_full80_review=dict(path=str(baseline_review_path),sha256=sha(baseline_review_path)),active_component_SHA={x['relative']:x['sha256'] for x in handoff['active_components']},native120_own_admission=native_binding,
 q30_XY_physicalparams_staticrecipes_captured_RNG_and_queue_exact_to_baseline=True,root30_byteexact_NOT_claimed=True,world_yaw_pi_quaternion_exact_permutation=True,actual_declared_safe_Z_delta_m=(initial[:,2]-np.asarray(br['initial']['root'],np.float32)[:,2]).tolist(),same_WORLD_heading_BODY_command_product_max_error=worlderror,physical_birth_safe_Z_and_complete25200point_footprint_original_tolerances_passed=True,all_birth_reviews=birthreviews,constructor_other_cell_birth_limit_disclosed=True,all_finite=True,actual_processed_action_original_clip6_exact=True,ordinary=int(o.sum()),truncation_unique=int(t.sum()),reason_and_episode_reset_union_exact=True,contact_integral_error_N=contacterror,ground_query_error_m=qe,COM_frame_error_m=hw['COM_frame_max_error_m'],all_substep_motor_bounds_exact=True,original_two_wheel_before_after200mm_and1N_margin=True,WORLD_forward_complete=counts['0'],WORLD_reverse_complete=counts['1'],standing26_no_transit_requirement=True,rows=per,all_valid_unfinished_prefixes_preserved=True,no_sameepisode_teleport_credit=True,original_missing_EXIT_NATURAL_preserved=col['outputs'].get('EXIT_NATURAL.json') is None,actual_parent_child_out_and_sharedlockfree=True,native120_only_NOT_full15s=steps==120,qualified50=False,qualified70=False,causal_production_adoption_NOT_claimed=True,no_PPO_or_budgetaction=True),data
