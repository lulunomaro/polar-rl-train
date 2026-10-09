"""Accept only returned actual interfaces, not queued jobs or training ability."""
from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
actual=read(R/'D7_SDK_CURRENT_ACTUAL.json');jobs={j['id']:j for j in actual['jobs']};prefix='clk2500-closure-episode-d3-'
accepted={};pending=[];held=[]
for label in ('90-d7-chassis-pd-frame-sdk','91-d7-com-sdk-off','91-d7-com-sdk-on','92-d7-com-buffer-sdk-on','92-d7-com-rotation-roundtrip-sdk-on','92-d7-com-inertia-roundtrip-sdk-on'):
 job=prefix+label;row=jobs.get(job);res=(row or {}).get('result')
 if res is None:pending.append(job);continue
 if res['phase']!='complete':held.append(dict(job=job,result=res));continue
 assert res['exit_code']==0 and not res['errors'] and not res['error_files']
 m=row['manifest'];folder=R/'windows'/job;p=read(folder/'probe.json')
 for name in ('probe.json','result.json'):
  proof=row['files'][name];assert proof['bridge_bytes_exact'] and hashlib.sha256((folder/name).read_bytes()).hexdigest()==proof['sha256']
 assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']=='df0654a6eaf7c62933b869043a340333391f60b44fae184ef0bb458c1f1fc4e5'
 assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and m['no_learning'] and not m['canonical_write_authority'] and not res['new_learning']
 assert p['steps']==m['steps']==300 and m['num_envs']==10 and p['seed']==m['seed']==20261002
 assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
 assert not p['nonfinite'] and all(p['per_environment']['alive'])
 actor=p['frozen_architecture_audit'];assert actor['variant']=='A0' and not actor['actor_receives_teacher'] and not actor['actor_receives_critic'] and actor['optimizer_updates']==0 and actor['actual_command_error']==0
 sensor=p['sensor_actual_manager_audit'];assert sensor['actor35'] and sensor['critic38_clean'] and sensor['formula_max_error']<2e-6
 params=p.get('mild_initial_parameters') or p['initial_parameter_audit'];final=p.get('mild_final_parameters') or p['final_parameter_audit'];assert params['actual_parameters_pass'] and final['actual_parameters_pass']
 if label.startswith('90'):
  a=p['D7_nominal_chassis_PD_initial'];b=p['D7_nominal_chassis_PD_final']
  assert a['actual_PhysX_and_buffer_local_COM_exact'] and b['actual_PhysX_and_buffer_local_COM_exact']
  assert a['independent_link_to_world_COM_formula_max_error_m']<1e-5 and b['independent_link_to_world_COM_formula_max_error_m']<1e-5
  assert p['D7_actual_contact_callbacks']==1200 and p['D7_local_COM_xyz_unchanged_across_D0_reset']
  assert a['parameter_setter_calls']==b['parameter_setter_calls']==0
  s=a['static'];bid=s['chassis_index'];assert s['body_names'][bid]==s['chassis_name']=='chassis'
  accepted[label]=dict(chassis_index=bid,body_names=s['body_names'],local_COM_xyz_initial=s['local_COM_pose_xyz_xyzw'][0][bid][:3],
                       chassis_mass_fraction=a['chassis_mass_fraction'],explicit_PD=s['explicit_PD'],actual_contact_callbacks=1200,
                       frame_formula_max_error_m=max(a['independent_link_to_world_COM_formula_max_error_m'],b['independent_link_to_world_COM_formula_max_error_m']),
                       raw_principal_axis_quaternion_changed_across_D0_reset=p['D7_raw_principal_axis_quaternion_changed_across_D0_reset'],
                       local_COM_xyz_did_not_change=True,no_parameter_setters=True,SDK_interface_only=True,files=row['files'])
 else:
  proof=p['D7_actual_chassis_COM_SDK'];assert proof['controls']==300 and proof['actual_contact_callbacks']==1200
  assert proof['action_group_callbacks']=={'legs':1200,'wheels':1200}
  assert proof['world_COM_frame_formula_max_error_m']<1e-5
  assert proof['selected_parent_reset']['other_COM_rows_and_private_state_exact'] and proof['selected_parent_reset']['selected_episode_once']
  if label=='92-d7-com-inertia-roundtrip-sdk-on':
   assert proof['isolated_COM_reset']['mass_joint_state_D5_D6_global_RNG_exact_inertia_original_tolerance_pass']
   for detail in (proof['isolated_COM_reset'],proof['CUDA_disk_roundtrip']):assert detail['inertia_absolute_roundtrip_error']<detail['original_frozen_D0_inertia_tolerance']==1e-6
  else:assert proof['isolated_COM_reset']['mass_inertia_joint_state_D5_D6_and_global_RNG_unchanged']
  if label in ('92-d7-com-rotation-roundtrip-sdk-on','92-d7-com-inertia-roundtrip-sdk-on'):
   for detail in (proof['isolated_COM_reset'],proof['CUDA_disk_roundtrip']):
    q=detail['physical_rotations_preserved_float32_roundtrip'];assert q['rotation_preserved_within_dtype_roundtrip'] and q['normalized_double_quaternion_max_component_delta']<=8*q['dtype_epsilon'] and q['no_task_or_hardware_tolerance_change']
  else:assert proof['isolated_COM_reset']['current_all_body_quaternions_exact']
  assert proof['isolated_COM_reset']['whole_robot_COM_mass_weighted_formula_max_error_m']<1e-5
  assert proof['CUDA_disk_roundtrip']['actual_CUDA_delta_episode_three_private_RNG_disk_roundtrip_exact'] and proof['CUDA_disk_roundtrip']['subsequent_selected_private_draw_exact']
  assert proof['actual_audit']['actual_PhysX_local_pose_and_buffer_exact'] and proof['learning_optimizer_updates']==0
  accepted[label]=dict(actual_SDK=proof,files=row['files'])
report=dict(epoch=time.time(),accepted=accepted,pending=pending,held=held,worker=actual['worker_actual'],current_worker_attention=actual['attention'],
            old88_89_failed_reader_evidence_preserved=True,original91_on_failure_held_not_passed=True,
            COM_actual_off_on_accepted='91-d7-com-sdk-off' in accepted and any(x in accepted for x in ('91-d7-com-sdk-on','92-d7-com-buffer-sdk-on','92-d7-com-rotation-roundtrip-sdk-on','92-d7-com-inertia-roundtrip-sdk-on')),
            nominal_actual_interface_accepted='90-d7-chassis-pd-frame-sdk' in accepted,
            D7_fullcheckpoint_PPO_and_learning=False,PD_randomization_SDK=False,new_GPU_PPO_or_budget_transactions_by_review=0)
(R/'D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(accepted=list(accepted),pending=pending,held=[r['job'] for r in held],worker_attention=actual['attention'])))
