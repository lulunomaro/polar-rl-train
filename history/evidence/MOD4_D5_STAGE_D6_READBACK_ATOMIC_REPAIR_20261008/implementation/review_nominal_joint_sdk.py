"""Accept only the new read-only damping/friction SDK scope, preserving skill flags."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
current=read(R/'D6_NOMINAL_JOINT_SDK_CURRENT.json');assert not current['pending']
job=current['job_id'];folder=R/'windows'/job;p=read(folder/'probe.json');m=read(folder/'manifest.json');res=read(folder/'result.json')
assert res['exit_code']==0 and not res['errors'] and not res['error_files'] and not res['new_learning']
assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']=='a9c0b8169077876e3d65211080e759b5d6ab4dfb306991095d5f849ac6290b66'
assert m['steps']==p['steps']==300 and m['num_envs']==10 and p['seconds']==3
for name,row in current['files'].items():
 assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==row['sha256']
 if name in ('probe.json','result.json'):assert row['automatic_bridge_return_bytes_exact']
assert p['D6_nominal_joint_property_inspection_only'] and p['D6_actual_contact_callback_delta']==1200
a=p['D6_nominal_joint_parameters_initial'];assert a==p['D6_nominal_joint_parameters_final']
assert a['gas_damping_drive_buffer_implicit_model_exact'] and a['static_dynamic_viscous_physx_buffer_exact']
assert a['parameter_setter_calls']==0 and not a['D6_randomization_deployed'] and not a['hardware_calibrated']
assert p['physical_action_delay_audit']['callback_counts']==dict(legs=1200,wheels=1200)
assert p['physical_action_delay_audit']['application_formula_max_error']==0 and not p['nonfinite']
assert p['resets']==0
names=a['joint_names'];drive=a['physx_damping'];models=a['actuator_model_damping'];gas=a['gas_joint_names']
assert drive==a['buffered_damping'] and all(row[names.index(j)]==3 for row in drive for j in gas)
friction={k:sorted(set(x for row in a[k] for x in row)) for k in ('static_friction','dynamic_friction','viscous_friction')}
assert all(v==[0.] for v in friction.values())
assert all(v==2. for row in models['legs']['values'] for v in row)
assert all(abs(v-.6)<1e-7 for row in models['wheels']['values'] for v in row)
assert all(drive[0][i]==0 for k in ('legs','wheels') for i in models[k]['joint_indices'])
cpu=read(R/'GAS_DAMPING_CPU_PASSED.json');assert cpu['passed'] and cpu['count']==9 and not cpu['CUDA_initialized']
k=(D/'reviewed_sources/installed_articulation_kernels.py').read_text(encoding='utf8')
assert 'friction_props[env_ids[i], joint_ids[j], 0] = out_friction' in k and 'friction_props[env_ids[i], joint_ids[j], 1] = out_dynamic_friction' in k and 'friction_props[env_ids[i], joint_ids[j], 2] = out_viscous_friction' in k
v=dict(epoch=time.time(),SDK_read_only_parameter_scope_accepted=True,job_id=job,source_checkpoint=res['checkpoint'],package_SHA=res['runtime_archive_sha256'],
 actual_contact_callbacks=1200,actual_action_callbacks=p['physical_action_delay_audit']['callback_counts'],reported_task_resets=p['resets'],
 actual_gas_damping_Ns_m=3.,actual_passive_damping_by_joint=dict(zip(names,drive[0])),
 actual_explicit_PD_derivative_gain_leg=2.,actual_explicit_PD_derivative_gain_wheel=.6,explicit_PD_is_separate_from_zero_PhysX_damping=True,
 actual_static_dynamic_viscous_friction_unique=friction,friction_units=dict(static_dynamic_revolute='N*m effort',static_dynamic_prismatic='N effort',viscous_revolute='N*m*s/rad',viscous_prismatic='N*s/m'),
 installed_actual_kernel_source=current['actual_installed_kernel_source'],no_parameter_writes=True,no_GPU_PPO_training=True,
 CPU_first_gas_damping_component=cpu,D6_first_subset='gas damping3Ns/m times independent left/right episode.9-1.1=2.7-3.3Ns/m',
 D6_actual_randomized_damping_SDK_pending=True,D6_full_checkpoint_native20k_PPO_executor_not_deployed=True,
 joint_friction_absolute_range_not_sourced=True,zero_times_factor_is_zero_not_friction_training=True,hardware_calibration_available=False,
 original_10env3s_skill_flags_not_changed=True,not_skill_graduation=True,original_strict_pass=p['strict_pass'],max_closure_m=p['max_closure_after_grace_m'],max_mimic_rad=p['max_mimic_after_grace_rad'],
 bridge_files=current['files'],result=res,no_4090_runtime_or_canonical_mutation=True)
(R/'D6_NOMINAL_ACTUAL_JOINT_SDK_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps({k:v[k] for k in ('SDK_read_only_parameter_scope_accepted','actual_contact_callbacks','actual_gas_damping_Ns_m','actual_static_dynamic_viscous_friction_unique','D6_first_subset','D6_actual_randomized_damping_SDK_pending')}))
