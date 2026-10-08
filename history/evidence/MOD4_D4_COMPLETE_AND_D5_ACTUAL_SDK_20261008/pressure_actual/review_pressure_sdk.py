"""Independent pressure SDK lifecycle/parameter/force-estimate review."""
from pathlib import Path
import json,time,math,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=read(R/'PRESSURE_SDK_CURRENT_ACTUAL.json');assert index['attention'] is None
assert all(x['complete'] and x['result']['phase']=='complete' and not x['result']['errors'] and not x['result']['error_files'] for x in index['jobs'])
cases=[];raws=[]
for row in index['jobs']:
    path=R/'windows'/row['job']/'probe.json';v=read(path);assert sha(path)==row['files']['probe.json']['sha256']
    assert all(row['files'][n]['bridge_return_exact'] for n in ('probe.json','result.json'))
    assert v['steps']==300 and v['seconds']==3 and not v['nonfinite'] and v['resets']==0 and v['physics_pass']
    assert v['mild_initial_parameters']['actual_parameters_pass'] and v['mild_final_parameters']['actual_parameters_pass']
    a=v['D5_pressure_adapter_actual_SDK'];force=v['D5_pressure_spring_actual_SDK']
    assert v['actual_physics_callback_delta']==v['D5_nominal_spring_physical_write_delta']==1200
    assert v['physical_action_delay_audit']['callback_counts']==dict(legs=1200,wheels=1200) and v['physical_action_delay_audit']['application_formula_max_error']==0
    assert a['actual_PhysX_buffer_and_implicit_model_error_N_m']==0 and a['preload_damping_force_limit_armature_unchanged']
    assert len(a['actual_factor'])==10 and all(.9<=x<=1.1 for pair in a['actual_factor'] for x in pair)
    assert a['episode']==[3,4,3,3,4,3,3,4,3,3]
    assert a['reset_rows'][-1]['ids']==[1,4,7] and all(all(r[k] for k in ('other_rows_parameter_state_exact','global_CPU_CUDA_RNG_untouched','global_physical_control_clock_unchanged')) for r in a['reset_rows'])
    disk=a['CUDA_disk_roundtrip'];assert disk['actual_device']=='cuda:0' and all(disk[k] for k in ('CUDA_state_factor_two_RNG_disk_exact','next_selected_draw_exact','actor_same_tick_exact','joint_state_exact','physical_resume_not_claimed'))
    for p in (force['initial_parameters'],force['final_parameters']):
        assert all(3150<=x<=3850 for pair in p['physx_stiffness_N_m'] for x in pair)
        assert p['buffered_stiffness_N_m']==p['physx_stiffness_N_m']
        assert all(x==3 for pair in p['physx_damping_N_s_m'] for x in pair) and all(x==2000 for pair in p['physx_drive_effort_limit_N'] for x in pair)
        assert all(abs(x-.002)<1e-9 for pair in p['physx_armature'] for x in pair)
    assert force['final_parameters']['physx_stiffness_N_m']==a['actual_stiffness_N_m']
    if not a['enabled']:assert all(x==1 for pair in a['actual_factor'] for x in pair)
    else:
        for p in (v['mild_initial_parameters'],v['mild_final_parameters']):
            expected=p['D5_actual_stiffness_expected_value_audit']
            assert all(expected[k] for k in ('independent_D5_state_source','PhysX_buffer_implicit_model_exact','original_nominal_reference_restored','other_D0_checks_unchanged'))
            assert p['errors']['gas_springs_stiffness_error']==0
    s=v['sensor_actual_manager_audit'];assert all(s[k] for k in ('actor35','critic38_clean','command_lastaction_mode_wheel_slots_exact','same_tick_draws_unchanged')) and s['formula_max_error']==0
    assert v['frozen_architecture_audit']['optimizer_updates']==0 and not v['frozen_architecture_audit']['actor_receives_teacher']
    error=0.;ranges={k:[math.inf,-math.inf] for k in ('q_m','qd_m_s','stiffness_N_m','elastic_estimate_N','viscous_estimate_N','SDK_computed_approximate_total_N')}
    for r in force['per_physical_write']:
        for i,active in enumerate(r['preload_active']):
            for j in range(2):
                k,d,q,qd,target,td,ff=(r[key][i][j] for key in ('stiffness_N_m','damping_N_s_m','q_m','qd_m_s','actual_target_m','actual_target_qd_m_s','feedforward_N'))
                expected=k*(target-q)+d*(td-qd)+ff
                error=max(error,abs(expected-r['SDK_computed_approximate_total_N'][i][j]),abs(max(-2000,min(2000,expected))-r['SDK_clipped_approximate_total_N'][i][j]))
                assert all(math.isfinite(x) for x in (k,d,q,qd,target,td,ff,expected))
                if active:
                    assert target==force['nominal_preload_target_m'][j]
                    for key in ranges:
                        x=r[key][i][j];ranges[key]=[min(ranges[key][0],x),max(ranges[key][1],x)]
    assert error<=.001
    cases.append(dict(job=row['job'],result=row['result'],source=row['result']['checkpoint'],files=row['files'],actual_callback_and_write_count=1200,
        actual_action_callbacks=dict(legs=1200,wheels=1200),audit=a,force_sample_ranges=ranges,independent_formula_max_error_N=error,
        initial_parameters=force['initial_parameters'],final_parameters=force['final_parameters'],original_preload_target_m=force['nominal_preload_target_m'],
        task_resets=0,nonfinite=False,closure_mm=v['max_closure_after_grace_m']*1000,mimic_rad=v['max_mimic_after_grace_rad'],
        all_original_skill_flags_preserved={k:v[k] for k in ('physics_pass','strict_pass','strict_pass_window','strict_pass_window_5ms')}))
    raws.append(v)
assert raws[0]['reset_root_before_physics']==raws[1]['reset_root_before_physics'] and raws[0]['reset_joint_pos_before_physics']==raws[1]['reset_joint_pos_before_physics']
assert raws[0]['physical_action_initial_episode_assignments']==raws[1]['physical_action_initial_episode_assignments']
assert raws[0]['sensor_recipe']==raws[1]['sensor_recipe'] and raws[0]['feedback_delay_recipe']==raws[1]['feedback_delay_recipe']
review=dict(epoch=time.time(),scope='3060/A0/model28633/2.5ms32-4/white_v3/D1-D4/two10env300control3s cases; D5 stiffness-only engineering SDK',cases=cases,
    SDK_limited_parameter_lifecycle_scope_accepted=True,actual_initial_root_30q_D1D4_assignments_exact=True,
    valid_off67_reused=True,new_on68_pressure_aware_audit_delta_disclosed=True,across_package_dynamic_bitexact_not_claimed=True,
    previous66_index_error_and67_fixed_nominal_observer_failure_retained=True,unexecuted66_on_not_counted_as_passed_or_executed=True,
    stiffness_source='Independent left/right episodefactor.9–1.1 times original3500N/m; actual PhysX and implicit model exactly match independentD5 state',
    preload_damping_armature_forcecap_unchanged=True,all_other_D0_checks_preserved=True,
    force_semantics='SDK effort estimate is elastic+viscous+feedforward with clip; not separate actual PhysX drive force, constraint reaction or hardware measurement',
    hardware_force_stroke_calibration=False,D5_closedloop_skill_graduation=False,D5_learning_executor_deployed=False,
    full_PPO_checkpoint_and_newepisode_resume_verified=False,native20k_or_newscope_complete_PPO_verified=False,
    next_required=['Integrate full spring CUDA RNG/state/actualparams with D1-D4 actorcriticstdoptimizer/global-named saved contracts and explicit newphysicalepisode',
        'Native20k actualparameters/callbacks/model/contact units and necessary genuinelynewrange128x2/20kx4 fullPPO discard under unique safe authority',
        'Use actual complete behavior-reviewed D4 source and correctworld directly; no repeated clock45min or same-rangepreflight',
        'Uncalibrated engineering pressure only; no nominal retune or force-stroke hardware certification'])
(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
report=f'''# Independent spring-stiffness pressure SDK accepted in its limited interface scope

The valid67-off SDK was reused. A new68-on observer verifies actual stiffness against independentD5 state while retaining every other D0 mass/inertia/material/COM/PD/armature/friction check and restoring the original nominal observer reference. This is an explicit source delta between the two immutable archives, not a same-archive/dynamic-bitexact claim. The prior66 CUDA-name-index and67 fixed3500 observer rejections/raw remain;66-on was never executed or counted as passed.

Both10env/300control/3s cases completed1200 real physical writes/contact callbacks and1200 callbacks for each D4 action group. Actual PhysX stiffness, articulation buffer and implicit-actuator estimate model matched each independent left/right episodefactor.9–1.1×3500N/m exactly. Original preload/damping3Ns/m/forcecap2000N/armature.002 remained. Selected[1,4,7] reset changed only selected pressure rows; other parameters/global CPU-CUDA streams/control-physical clock stayed exact. ActualCUDA factor/twoRNG disk restoration, next selected draw, same-tick actor and joint state passed.

Off/on closure maxima are{cases[0]['closure_mm']:.6f}/{cases[1]['closure_mm']:.6f}mm; both taskresets0/nonfinitefalse, mimic{cases[0]['mimic_rad']:.9f}/{cases[1]['mimic_rad']:.9f}rad. Independent formula errors are{cases[0]['independent_formula_max_error_N']:.9g}/{cases[1]['independent_formula_max_error_N']:.9g}N. Actor35, clean critic38 and actions6, commands/lastaction and D1–D4 recipes and initialroot/30q/action assignments passed. Final closedloop physical states may differ; original skillflags remain and3s interface checks do not certify graduation. Four returnedJSONs were byte-SHA verified.

The observed SDK spring/viscous effort is an approximation, not separately measured PhysXdrive force/constraint reaction/hardware force. Hardwareforce-stroke calibration is absent. D5 fullPPO resume/native20k/newscope PPO/controller are not deployed or proved by this SDK. Current4090 D4block3 continued unchanged throughout. The new explicit spring-audit demandworker preserved original files/errors/taskXML and all completedjobs, uses the same singleGPU lock and has no periodic/boottrigger/canonicalwrite/traininglaunch authority.
'''
(R/'D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(accepted=True,closure_mm=[x['closure_mm'] for x in cases],stiffness_ranges=[x['force_sample_ranges']['stiffness_N_m'] for x in cases],formula_error=[x['independent_formula_max_error_N'] for x in cases],D5_learning=False)))
