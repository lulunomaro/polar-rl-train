"""Review actual SDK raw independently; retain every inherited skill flag."""
from pathlib import Path
import json,hashlib,time,math
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
actual=read(R/'NOMINAL_SPRING_SDK_CURRENT_ACTUAL.json')
assert actual['complete'] and actual['result']['exit_code']==0 and not actual['result']['errors']
job=actual['job'];rawpath=R/'windows'/job/'probe.json';v=read(rawpath)
assert sha(rawpath)==actual['files']['probe.json']['sha256']
assert all(actual['files'][x]['bridge_return_exact'] for x in ('probe.json','result.json'))
assert v['steps']==300 and v['seconds']==3 and not v['nonfinite'] and v['resets']==0 and v['physics_pass']
assert v['mild_initial_parameters']['actual_parameters_pass'] and v['mild_final_parameters']['actual_parameters_pass']
audit=v['D5_nominal_spring_actual_SDK'];assert audit['initial_parameters']==audit['final_parameters']
assert v['D5_nominal_spring_physical_write_delta']==v['actual_physics_callback_delta']==1200
assert audit['readback_calls']==1202 and audit['preload_active_environment_writes']==12000 and audit['initial_or_reset_neutral_warmup_environment_writes']==20
assert audit['SDK_implicit_effort_is_approximate_not_separate_PhysX_drive_force'] and not audit['hardware_force_stroke_measurement']
assert not audit['nominal_parameters_changed'] and audit['no_D5_randomization_or_training'] and audit['PPO_updates']==0
assert v['physical_action_delay_audit']['callback_counts']==dict(legs=1200,wheels=1200)
assert v['physical_action_delay_audit']['application_formula_max_error']==0
s=v['sensor_actual_manager_audit'];assert s['actor35'] and s['critic38_clean'] and s['command_lastaction_mode_wheel_slots_exact'] and s['same_tick_draws_unchanged'] and s['formula_max_error']==0
assert v['sensor_platform_sdk']['selected_reset']==dict(ids=[1,4,7],other_bias_episode_exact=True,global_tick_unchanged=True)
architecture=v['frozen_architecture_audit'];assert architecture['actual_command_error']==0 and not architecture['actor_receives_teacher'] and not architecture['actor_receives_critic'] and architecture['optimizer_updates']==0
ranges={k:[math.inf,-math.inf] for k in ('q_m','qd_m_s','actual_target_m','elastic_estimate_N','viscous_estimate_N','feedforward_N','SDK_computed_approximate_total_N','SDK_clipped_approximate_total_N')}
error=0.;rows=0
for row in audit['per_physical_write']:
    for i,active in enumerate(row['preload_active']):
        for j in range(2):
            q,qd,target,td,ff=(row[k][i][j] for k in ('q_m','qd_m_s','actual_target_m','actual_target_qd_m_s','feedforward_N'))
            expected=3500*(target-q)+3*(td-qd)+ff
            computed=row['SDK_computed_approximate_total_N'][i][j]
            clipped=row['SDK_clipped_approximate_total_N'][i][j]
            error=max(error,abs(expected-computed),abs(max(-2000,min(2000,expected))-clipped))
            assert all(math.isfinite(x) for x in (q,qd,target,td,ff,computed,clipped))
            if active:
                assert abs(target-audit['nominal_preload_target_m'][j])<=1e-7
                for k in ranges:
                    x=row[k][i][j];ranges[k]=[min(ranges[k][0],x),max(ranges[k][1],x)]
                rows+=1
assert rows==24000 and error<=.001
review=dict(epoch=time.time(),job=job,source=actual['result']['checkpoint'],runtime_archive_sha256=actual['result']['runtime_archive_sha256'],
    nominal_model_unchanged=True,scope='Same3060/2.5ms32-4/A0/white_v3/D1-D4/10env300control3s nominal gas-drive SI and approximate-effort SDK readback only',
    actual_physical_write_and_contact_delta=1200,readback_calls=1202,extra_initial_reset_writes_outside_timed_physics=2,
    initial_final_parameters=audit['initial_parameters'],nominal_preload_target_m=audit['nominal_preload_target_m'],
    active_preload_environment_writes=12000,neutral_initial_reset_environment_writes=20,
    active_preload_value_ranges=ranges,independent_double_formula_vs_SDK_float32_max_error_N=error,
    SDK_float32_computed_clipped_formula_error_N=[audit['SDK_computed_approximate_formula_error_N'],audit['SDK_clipped_approximate_formula_error_N']],
    cache_direct_PhysX_q_error_m=audit['cache_vs_direct_physx_joint_position_error_m'],
    unit='gas prismatic q m / qd m_s / stiffness N_m / damping N_s_m / effort N',
    actual_task_resets=0,nonfinite=False,closure_mm=v['max_closure_after_grace_m']*1000,mimic_rad=v['max_mimic_after_grace_rad'],
    actual_action_group_callbacks=dict(legs=1200,wheels=1200),actual_target_error=0,
    clean_critic_commands_lastaction_preserved=True,selected_sensor_reset_contract=v['sensor_platform_sdk']['selected_reset'],
    no_teacher_input_or_PPO=True,raw_and_results=actual['files'],
    process_wall_seconds=actual['result']['physics_process_wall_seconds'],transfer_seconds=actual['result']['transfer_seconds'],
    two_second_sampled_GPU_memory_mib=actual['result']['observed_GPU_memory_mib'],not_continuous_peak=True,
    nominal_parameter_readback_scope_accepted=True,
    effort_semantics='Installed ImplicitActuator computed/applied effort is an approximate spring+viscous+feedforward estimate and clip, not separately measured PhysX implicit drive force, constraint reaction or hardware force.',
    installed_primary_source=read(R/'INSTALLED_SPRING_SDK_SOURCE.json'),
    actual_separate_PhysX_drive_force_measured=False,actual_constraint_reaction_force_measured=False,
    hardware_force_stroke_calibrated=False,full_joint_range_hardware_stroke_certified=False,
    inherited_skill_flags={k:v[k] for k in ('physics_pass','strict_pass','strict_pass_window','strict_pass_window_5ms')},
    ten_env_three_second_interface_is_not_skill_graduation=True,D5_pressure_SDK_or_learning_deployed=False,
    pressure_CPU_component=read(R/'SPRING_PRESSURE_CPU_PASSED.json'),
    next_required=['actual independent episode stiffness setter and implicit-actuator-model consistency; no change to preload/damping/limits/armature',
        'actual CUDA state/RNG disk restore and selected reset; initial admission vs full resume and new physical episode explicit',
        'native20k parameter/callback/model/force semantics and necessary newscope128x2/20kx4 completePPO discard',
        'explicit missing hardware calibration; only approved uncalibrated engineering pressure, never physical force-stroke certification',
        'unique bounded executor at own fullsave, exited children, closed prior launch authority, two locks and clear active boundary'])
(R/'D5_NOMINAL_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
report=f'''# D5 nominal spring SDK readback completed; pressure training is not deployed

The existing3060 worker completed10 environments/300 control steps/3s from the full behavior-reviewed D4 model28633.1200 physical writes and1200 contact callbacks matched. Installed PhysX stiffness/damping/effort limit/armature and buffered properties read3500N/m,3Ns/m,2000N,.002 and remained exact initially/finally. Existing float32 preload target is.220639437m; neutral initial/reset writes are recorded separately.

The independent q/qd/target formula agrees with the installed SDK approximate computed/clipped effort within{error:.9g}N (SDK's own float32 formula error0). Actual active-preload sampled elastic estimate range is{ranges['elastic_estimate_N'][0]:.6f}–{ranges['elastic_estimate_N'][1]:.6f}N. These are software estimates at observed joint states, not separate PhysX drive force, constraint reaction, physical gas stroke or measured hardware force. No nominal parameter was changed to meet300–700N.

Task resets0/nonfinitefalse, maximum closure{review['closure_mm']:.6f}mm and mimic{review['mimic_rad']:.9f}rad. D1–D4 actor/clean critic/command/last action/readback and both1200 action group callbacks passed; selected sensor reset and other rows/global clock were preserved. Original skill flags remain;10env3s is an interface check. Processwall{review['process_wall_seconds']:.3f}s;2s sampled memory2854MiB is not a continuous peak. Two returned JSON files were byte-SHA verified.

The first ±10% independent spring-stiffness pressure component passed10 target Torch2.10 CPU contracts without CUDA initialization, physical writes or PPO. Actual pressure setter/CUDA lifecycle/full learning resume/native20k/newscope PPO and the next unique controller are still required. Hardware force-stroke calibration is absent. Current243-source4090 D4 training and the worker are unchanged.
'''
(R/'D5_NOMINAL_ACTUAL_SDK_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(accepted=review['nominal_parameter_readback_scope_accepted'],closure_mm=review['closure_mm'],ranges=ranges,formula_error=error,hardware_calibration=False,D5_learning=False)))
