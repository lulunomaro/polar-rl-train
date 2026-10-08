"""Independent actual gas damping reset/readback/state proof; retain old flags."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
current=read(R/'D6_ACTUAL_DAMPING_SDK_CURRENT.json');assert current['GAS_DAMPING_REVIEW_WORKER_ATTENTION.json'] is None
raws=[];cases=[]
for kind in ('off','on'):
    job='clk2500-closure-episode-d3-81-d6-gas-sdk-index-'+kind;row=current['jobs'][job]
    assert not row['pending'] and row['bridge_bytes_exact'] and row['result']['phase']=='complete'
    result=row['result'];assert result['exit_code']==0 and not result['errors'] and not result['error_files']
    folder=R/'windows'/job;p=read(folder/'probe.json');assert sha(folder/'probe.json')==row['files']['probe.json']['sha256']
    assert p['steps']==300 and p['seconds']==3 and p['resets']==0 and not p['nonfinite'] and p['physics_pass']
    assert p['mild_initial_parameters']['actual_parameters_pass'] and p['mild_final_parameters']['actual_parameters_pass']
    s=p['D6_actual_gas_damping_SDK'];assert s['controls']==300 and s['actual_contact_callbacks']==1200
    assert s['action_group_callbacks']==dict(legs=1200,wheels=1200)
    assert p['physical_action_delay_audit']['application_formula_max_error']==0
    assert s['selected_parent_reset']['only_selected_D6_rows_changed'] and s['selected_parent_reset']['selected_episode_incremented_once']
    assert s['isolated_D6_reset']['D5_state_and_joint_state_global_CPU_CUDA_RNG_control_physics_clocks_unchanged']
    assert all(s['CUDA_disk_roundtrip'].values())
    audit=s['actual_audit'];assert audit['actual_PhysX_buffer_implicit_model_exact'] and audit['D5_stiffness_expected_state_exact']
    assert audit['motor_PD_passive_damping_friction_preload_force_cap_armature_unchanged']
    assert audit['enabled']==(kind=='on') and s['learning_optimizer_updates']==0
    for label in ('initial_assignment','final_assignment'):
        v=s[label];assert all(.9<=f<=1.1 for pair in v['factor'] for f in pair)
        assert all(2.7<=x<=3.3 for pair in v['actual_damping_Ns_m'] for x in pair)
        if kind=='off':assert all(f==1 for pair in v['factor'] for f in pair) and all(x==3 for pair in v['actual_damping_Ns_m'] for x in pair)
    assert s['final_assignment']['episode']==[3,5,3,3,5,3,3,5,3,3]
    for params in (p['mild_initial_parameters'],p['mild_final_parameters']):
        a=params['D6_actual_gas_damping_expected_value_audit'];assert all(a.values())
    actor=p['sensor_actual_manager_audit'];assert actor['actor35'] and actor['critic38_clean'] and actor['same_tick_draws_unchanged'] and actor['formula_max_error']==0
    assert p['frozen_architecture_audit']['optimizer_updates']==0 and not p['frozen_architecture_audit']['actor_receives_teacher']
    assert p['spring_pressure_audit']['preload_force_limit_armature_unchanged'] and p['spring_pressure_audit']['D6_gas_damping_varies_separately']
    cases.append(dict(job_id=job,result=result,files=row['files'],actual_SDK=s,task_resets=p['resets'],nonfinite=p['nonfinite'],
        max_closure_mm=p['max_closure_after_grace_m']*1000,max_mimic_rad=p['max_mimic_after_grace_rad'],
        original_flags={k:p[k] for k in ('physics_pass','strict_pass','strict_pass_window','strict_pass_window_5ms')}));raws.append(p)
for name in ('reset_joint_pos_before_physics','reset_root_before_physics','mild_initial_parameters','physical_action_initial_episode_assignments',
    'spring_pressure_initial_episode_assignments','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe'):
    assert raws[0][name]==raws[1][name],name
review=dict(epoch=time.time(),SDK_limited_damping_parameter_lifecycle_scope_accepted=True,cases=cases,
    actual_initial_root_30q_D0_D5_parameters_and_assignments_exact=True,final_dynamic_bitexact_not_claimed=True,
    four_returned_probe_result_JSON_bytes_exact=True,gas_damping_bounds_Ns_m=[2.7,3.3],nominal_gas_damping_Ns_m=3.,
    friction_randomization_completed=False,hardware_force_stroke_or_friction_calibration=False,
    full_PPO_resume_pending=True,newscope_native20k_and_complete_PPO_pending=True,D6_learning_executor_deployed=False,
    original80_off_CPU_PhysX_index_reader_failure_preserved=True,original80_on_not_run_not_passed=True,
    no_D5_training_or_budget_changes=True)
(R/'D6_GAS_DAMPING_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
print(json.dumps(dict(SDK_scope_accepted=True,cases=len(cases),callbacks_per_case=1200,
    closure_mm=[x['max_closure_mm'] for x in cases],range_Ns_m=cases[1]['actual_SDK']['actual_audit']['actual_damping_range_Ns_m'],D6_learning=False)))
