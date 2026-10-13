"""Independent CPU review of complete first3060 120-control physical baseline."""
from pathlib import Path
import json,hashlib,time,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=sorted(R.glob('DIRECT3060_BASELINE120_CURRENT_ACTUAL_*.json'))[-1]
j=json.loads(q.read_bytes());c=j['outputs']['COMPLETE_ACTUAL.json'];exit=j['states']['PARENT_EXIT_RECEIPT.json']
assert c and c['passed_data_contract'] and c['no_PPO'] and c['qualification_claimed'] is False
assert c['checkpoint_sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
assert exit['exit_code']==0 and exit['complete_data_contract_present'] and not exit['original_error_present']
assert j['outputs']['ORIGINAL_ERROR.json'] is None and j['shared_actual_OS_lock_free'] is True
assert all(not p['running'] for p in j['actual_PID_identities'])
assert j['outputs']['EXIT_NATURAL.json'] is None and exit['natural_app_close_present'] is False
assert any('SimulationContext cleared' in p['tail'] for p in j['logs'])
rawrow=next(r for r in j['local_collected_files'] if r['relative'].endswith('route_raw.npz'))
queryrow=next(r for r in j['local_collected_files'] if r['relative'].endswith('worldmesh_query.npz'))
assert H(rawrow['local_path'])==rawrow['sha256']==c['raw']['sha256'] and rawrow['bytes']==c['raw']['bytes']
assert H(queryrow['local_path'])==queryrow['sha256']==j['outputs']['QUERY_ACTUAL.json']['sha256']
with np.load(rawrow['local_path']) as z:
 data={k:z[k].copy() for k in z.files}
assert all(np.isfinite(v).all() for v in data.values())
assert data['root'].shape==data['before_root'].shape==(120,8,13)
assert data['q'].shape==(120,8,30) and data['policy_obs'].shape==(120,8,35)
assert data['physical_wheel_force_N'].shape==(480,8,2,3)
assert not data['terminated'].any() and not data['truncated'].any() and not data['reasons'].any()
assert not data['episode'].any() and np.array_equal(data['before_root'][1:],data['root'][:-1])
assert np.array_equal(data['action'],data['factor_action']) and np.array_equal(data['processed_action'],np.clip(data['action'],-6.,6.))
assert np.all(data['command'][:,:7,0]==np.float32(.3)) and not data['command'][:,:7,1:].any() and not data['command'][:,7].any()
assert np.array_equal(data['group_ids'],np.array([0,0,0,0,0,0,0,2]))
physical=data['physical_wheel_force_N'].reshape(120,4,8,2,3)
integral=np.maximum(physical[...,2],0).sum(1)*np.float32(.0025)
integral_mean_error=float(abs(integral-data['impulse']).max())/.01
assert integral_mean_error<=.1
tau=data['physical_hardware_actual_applied_effort'];lower=data['physical_hardware_torque_speed_lower'];upper=data['physical_hardware_torque_speed_upper']
assert tau.shape==lower.shape==upper.shape==(480,8,6) and np.array_equal(tau,np.clip(tau,lower,upper))
assert np.max(data['closure'])<=.002 and np.max(data['mimic'])<=.01
assert c['callbacks']==480 and c['steps']==120 and c['ordinary_union']==c['truncation_union']==0
hw=j['outputs']['SUBSTEP_HARDWARE_COM_ACTUAL.json'];assert hw['callbacks']==480 and hw['motor_torque_speed_bounds_exact']
assert hw['COM_frame_max_error_m']<1e-5 and hw['link_local_COM_PhysX_buffer_exact']
with np.load(queryrow['local_path']) as z:
 queryerror=float(abs(z['actual_sampled_ground']-z['expected_actual_ground']).max())
 assert queryerror<=1e-6 and np.isfinite(z['world_triangles']).all()
assert c['ground_error_m']<=1e-6 and c['reward_formula_error']<=1e-6
initial=c['initial'];assert len(initial['root_xyzw'])==8 and len(initial['q'])==8
states=initial['parameters']['complete_current_queue_states'];assert set(states)=={'sensor','feedback_delay','physical_action_queue','spring','gas','chassis_COM','explicit_PD'}
rng=initial['parameters']['actual_captured_RNG_bytes'];assert rng
for p,row in rng.items():
 b=bytes.fromhex(row['hex']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
report=dict(epoch=time.time(),passed=True,scope='new3060 ownbackend first120 data/physical admission only',
 own_source91d_SHA=c['checkpoint_sha256'],collector=dict(path=str(q),sha256=H(q)),raw_actual=rawrow,query_actual=queryrow,
 controls=120,envs=8,env_steps=960,callbacks=480,physical_seconds_perenv=1.2,
 ordinary0=True,truncation0=True,reason_coverage_exact=True,all_nonreset_before_after_root_byteexact=True,
 original_raw_actor_and_clipped6_physical_input_preserved=True,raw_allfinite=True,
 ground_query_error_m=queryerror,reward_formula_error_m=c['reward_formula_error'],contact_integral_mean_error_N=integral_mean_error,
 closure_max_m=float(data['closure'].max()),mimic_max_rad=float(data['mimic'].max()),
 all480_substep_original_motor_bounds_exact=True,COM_frame_max_error_m=hw['COM_frame_max_error_m'],COM_original_tolerance_m=1e-5,
 actual_initial_fullqueue_containers=list(states),captured_RNG_streams=len(rng),actual_RNG_bytes_saved_not_just_SHA=True,
 actual_parent_cost_seconds=exit['unique_actual_parent_load_run_save_exit_seconds'],worker_control_loop_seconds=c['wall_seconds'],
 measured_controls_per_control_loop_wall_second=120/c['wall_seconds'],
 actual_all_locator_processes_exited=True,actual_shared_OSlock_free=True,
 original_EXIT_NATURAL_missing_retained=True,parent_original_natural_app_close_present_false_retained=True,
 lifecycle_independent_evidence='complete durable raw + parent exit0 + SimulationContext cleared + all exact PID identities exited + native shared lock free; no fabricated app.close return marker',
 no_PPO_no_trainingFullDRresume_no_budget_write=True,not_full15s_or_whole_route_qualification=True,
 next_1500_baseline_or_D3_requires_separate_root_lease=True,other_backend_results_not_asserted_exact=True)
out=R/'DIRECT3060_BASELINE120_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json';assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:report[k] for k in ['passed','controls','envs','callbacks','ground_query_error_m','contact_integral_mean_error_N','closure_max_m','mimic_max_rad','COM_frame_max_error_m','captured_RNG_streams','actual_parent_cost_seconds','original_EXIT_NATURAL_missing_retained']},ensure_ascii=False),flush=True)
