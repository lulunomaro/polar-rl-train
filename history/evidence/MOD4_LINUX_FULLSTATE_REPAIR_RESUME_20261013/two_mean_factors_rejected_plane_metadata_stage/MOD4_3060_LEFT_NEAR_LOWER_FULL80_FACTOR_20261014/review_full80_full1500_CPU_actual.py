"""Full native80 placement, query, callback, contact/COM/hardware data admission only."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=sorted((D/'reports').glob('REFERENCE17B_CURRENT_ACTUAL_*.json'))[-1];j=json.loads(src.read_bytes());c=j['outputs']['COMPLETE_ACTUAL.json'];ex=j['states']['PARENT_EXIT_RECEIPT.json']
assert c and c['passed_data_contract'] and c['num_envs']==80 and c['steps']==1500 and c['callbacks']==6000 and not c['native120_not_full15s'] and c['no_PPO'] and not c['qualification_claimed']
assert ex['exit_code']==0 and not ex['original_error_present'] and j['shared_actual_OS_lock_free'] and all(not p['running'] for p in j['actual_PID_identities'])
rows=j['local_collected_files']
def row(suffix):return next(r for r in rows if r['relative'].endswith(suffix))
rawrow=row('/route_raw.npz');assert H(rawrow['local_path'])==rawrow['sha256']==c['raw']['sha256']
with np.load(rawrow['local_path']) as z:data={k:z[k].copy() for k in z.files}
assert all(np.isfinite(v).all() for v in data.values()) and data['root'].shape==(1500,80,13) and data['q'].shape==(1500,80,30) and data['policy_obs'].shape==(1500,80,35)
groups=np.arange(80)%3;targets=np.asarray([.3,-.3,0.],dtype=np.float32)[groups]
assert np.array_equal(groups,data['group_ids']) and np.array_equal(targets,data['targets_m_s'])
assert np.array_equal(data['command'][:,:,0],np.broadcast_to(targets,(1500,80))) and not data['command'][:,:,1:].any()
assert np.array_equal(data['processed_action'],np.clip(data['action'],-6.,6.))
reportrow=row('/probe.json');report=json.loads(Path(reportrow['local_path']).read_bytes());assert H(reportrow['local_path'])==reportrow['sha256']==c['original_report']['sha256']
assert report['protocol']=='approved_E1_G4_derived50mm_worldmesh_actualray_approach040_fullroute_behavior_v2' and report['checkpoint_sha256']==c['checkpoint_sha256']=='6235d44aa144a73e46d8326187c7fdf1e406a2d0b00ee6d21922b18f198f3bce'
scope=report['route_scope'];assert scope['size_m']==[9.,9.] and scope['tile_rows']==(np.arange(80)//2).tolist() and scope['flat_support_margin_m']==.4
assert len(set(scope['tile_cols']))==2 and np.array_equal(np.asarray(scope['tile_cols'])[0::2],np.repeat(scope['tile_cols'][0],40))
centers=np.asarray(scope['tile_centers']);starts=centers.copy();half=scope['wave_x_halfspan_m'];starts[groups==0,0]-=half+.4;starts[groups==1,0]+=half+.4
assert np.array_equal(starts,np.asarray(scope['requested_starts']))
initial=np.asarray(report['initial']['root']);assert initial.shape==(80,13) and np.max(abs(initial[:,:2]-starts.astype(np.float32)))<=1e-6 and not initial[:,7:].any()
assert np.asarray(report['initial']['q']).shape==(80,30)
names=report['reason_names'];ordinary=('bad_orientation','base_contact','low_base','closure');trunc=('time_out','rough_route_boundary')
assert set(names)==set(ordinary+trunc+('mimic',))
o=data['reasons'][...,[names.index(x) for x in ordinary]].any(-1);t=data['reasons'][...,[names.index(x) for x in trunc]].any(-1)
assert np.array_equal(o,data['terminated']) and np.array_equal(t,data['truncated']) and not data['reasons'][...,names.index('mimic')].any()
done=o|t;mask=~done[:-1];assert np.array_equal(data['before_root'][1:][mask],data['root'][:-1][mask]) and np.array_equal(np.diff(data['episode'],axis=0),done[:-1].astype(data['episode'].dtype))
force=data['physical_wheel_force_N'];assert force.shape==(6000,80,2,3)
mean=np.maximum(force.reshape(1500,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
contacterror=float(abs(mean-data['impulse']/np.float32(.01)).max());assert contacterror<=.1
tau=data['physical_hardware_actual_applied_effort'];low=data['physical_hardware_torque_speed_lower'];high=data['physical_hardware_torque_speed_upper'];assert tau.shape==(6000,80,6) and np.array_equal(tau,np.clip(tau,low,high))
hardware=j['outputs']['SUBSTEP_HARDWARE_COM_ACTUAL.json'];assert hardware['callbacks']==6000 and hardware['motor_torque_speed_bounds_exact'] and hardware['COM_frame_max_error_m']<1e-5
queryrow=row('/probe.json.worldmesh_query.npz');assert H(queryrow['local_path'])==queryrow['sha256']==c['query']['sha256']
with np.load(queryrow['local_path']) as z:qe=float(abs(z['actual_sampled_ground']-z['expected_actual_ground']).max());assert z['world_triangles'].shape[0]==80 and qe<=1e-6
assert report['independent_ground_max_error_m']<=1e-6 and report['height_reward_formula_max_error']<=1e-6 and data['mimic'].max()<=.01
stdout=row('/worker.log');b=Path(stdout['local_path']).read_bytes();assert H(stdout['local_path'])==stdout['sha256']
assert all(x not in b for x in (b'Contacts have been dropped',b'buffer overflow detected',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))
q=D/'reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json';assert not q.exists()
v=dict(epoch=time.time(),passed=True,collector=dict(path=str(src),sha256=H(src)),source_SHA=c['checkpoint_sha256'],num_envs=80,controls=1500,callbacks=6000,cohorts=[27,27,26],original9m_mirror80_geometry_and040approach_exact=True,all_initial_q30_XY_zero_velocity_and_actual_parameter_recipes_saved=True,actual_actor_nine_GPU_source_exact=j['outputs']['FROZEN_POLICY_SOURCE_ACTUAL.json'],raw=rawrow,query=queryrow,original_full_report=reportrow,all_finite=True,reason_and_prereset_episode_coverage_exact=True,ordinary=int(o.sum()),truncation_unique=int(t.sum()),contact_integral_error_N=contacterror,ground_query_error_m=qe,COM_error_m=hardware['COM_frame_max_error_m'],all6000_native_motor_bounds_exact=True,original_missing_EXIT_NATURAL_preserved=j['outputs']['EXIT_NATURAL.json'] is None,actual_parent_child_exited_and_shared_OSlockfree=True,full1500_original_data_contract_actual_passed=True,qualification_not_claimed=True,no_PPO_or_budgetaction=True,qualified50=False)
q.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(q),passed=True,controls=1500,envs=80,query_error=qe,ordinary=v['ordinary'],full1500_actual_data_complete=True)))
