"""SCUT-inspired learning admission; performance diagnostics never veto a rate step.

The MOD4 task's existing actual termination/reset and hardware envelope remain.
This is not a port of SCUT's robot, 40-degree/20-tick reset, or rewards.
"""
import math
VERSION='scut_curriculum_v4_performance_diagnostic'
SCUT_COMMIT='b8ff79f3df855faf9dc92f4a282bd80c42649466'

SPIN_FIELDS=('yaw_rate','yaw_error','speed_error','tilt','height_error','delta','d2',
 'left_fz','right_fz','guide_force','base_force','wheel_rating_clip','leg_rating_clip',
 'left_slip','right_slip','spin_translation_speed','peak_tilt','maximum_gap_m',
 'longest_both_low_s','net_signed_turns','absolute_turns','root_xy_excursion_m','stop_yaw_abs')
FLAT_FIELDS=('speed','vel_error','tilt','max_tilt','height_error','delta','d2','guide_force',
 'base_force','left_mean_fz_substep','right_mean_fz_substep','left_support_slip_control',
 'right_support_slip_control','longest_both_low_force_s_substep','left_gap_max_control_m',
 'right_gap_max_control_m','stop_abs_speed','wheel_rating_clip_fraction','leg_rating_clip_fraction')
CONTACT_FIELDS=('loaded_samples','valid_ticks','loaded_time_mean_tangent_speed',
 'loaded_impulse_weighted_tangent_speed','longest_loaded_over015_s','mean_normal_force_N',
 'max_normal_z_error','max_com_link_point_velocity_error')

def finite(x):
    return isinstance(x,(int,float)) and math.isfinite(x)

def parameters(r):
    initial=r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
    final=r.get('final_parameter_audit') or r.get('mild_final_parameters')
    # The original flat nominal validator has no DR audit. Other profiles require both.
    if initial is None and final is None:return r.get('mode')=='deterministic_policy'
    return bool(initial and final and initial.get('actual_parameters_pass') is True
                and final.get('actual_parameters_pass') is True)

def _evidence(r,kind='spin',minimum_seconds=15):
    reasons=[]
    def require(ok,why):
        if not ok:reasons.append(why)
    steps=r.get('steps');seconds=r.get('seconds')
    require(r.get('nonfinite') is False,'nonfinite_or_missing_simulation_status')
    require(isinstance(steps,int) and steps>=100,'incomplete_steps')
    require(finite(seconds) and seconds>=minimum_seconds,'insufficient_observation_duration')
    require(finite(seconds) and isinstance(steps,int) and abs(seconds-steps*.01)<1e-6,'control_duration_inconsistent')
    pe=r.get('per_environment') or {};alive=r.get('alive') if kind=='spin' else pe.get('alive')
    gids=r.get('group_ids') if kind=='spin' else pe.get('group_ids')
    n=len(alive) if isinstance(alive,list) else 0
    require(n>0,'missing_survival_evidence')
    require(n>0 and all(v is True for v in alive),'actual_task_termination')
    require(isinstance(gids,list) and len(gids)==n,'missing_group_index')
    fields=SPIN_FIELDS if kind=='spin' else FLAT_FIELDS
    for key in fields:
        values=pe.get(key)
        require(isinstance(values,list) and len(values)==n and all(finite(v) for v in values),'missing_or_nonfinite_'+key)
    # Finite diagnostics are required even when their magnitudes do not affect admission.
    for key,values in pe.items():
        require(isinstance(values,list) and len(values)==n and all(finite(v) for v in values),'invalid_array_'+key)
    closure_key='max_closure_m' if kind=='spin' else 'max_closure_after_grace_m'
    mimic_key='max_mimic_rad' if kind=='spin' else 'max_mimic_after_grace_rad'
    for key,limit in ((closure_key,.002),(mimic_key,.01)):
        require(finite(r.get(key)) and 0<=r[key]<=limit,'MOD4_model_integrity_'+key)
    require(parameters(r),'actual_parameter_readback_failed')
    groups=r.get('groups') or []
    require(bool(groups),'missing_command_groups')
    expected=set(range(len(groups)))
    require(isinstance(gids,list) and set(gids)==expected,'group_coverage_incomplete')
    if isinstance(gids,list):
        require(all(gids.count(g)>= (2 if minimum_seconds<15 else 8) for g in expected),'group_samples_incomplete')
    if kind=='flat':
        require(r.get('mode')=='deterministic_policy','wrong_flat_protocol')
        require(r.get('resets')==0,'actual_flat_task_reset')
        constants={g.get('command_vx') for g in groups if g.get('profile')=='constant'}
        require({0.,.3,.6,1.,-1.5,1.5}.issubset(constants),'missing_flat_training_groups')
    else:
        require(r.get('mode')=='frozen_deterministic_spin_rate_probe','wrong_spin_protocol')
        first=r.get('first_failure_step')
        require(isinstance(first,list) and len(first)==n and all(v==steps for v in first),'actual_first_failure')
        sub=r.get('substep_contact_readback') or {};cp=sub.get('per_environment') or {}
        from physics_clock import validate_clock
        try:clock=validate_clock(sub.get('sampling_s'));decimation=clock['decimation']
        except ValueError:clock=None;decimation=0
        require(clock is not None and sub.get('callbacks')==steps*decimation,'incomplete_substep_capture')
        for key in CONTACT_FIELDS:
            a=cp.get(key)
            require(isinstance(a,list) and len(a)==n and all(isinstance(row,list) and len(row)==2 and all(finite(v) for v in row) for row in a),'invalid_contact_'+key)
        if not any(x.startswith('invalid_contact_') for x in reasons):
            for i in range(n):
                for w in (0,1):
                    require(cp['loaded_samples'][i][w]>0 and cp['valid_ticks'][i][w]==(steps-50)*decimation,'contact_capture_missing_env'+str(i))
                    control=pe.get('left_fz' if w==0 else 'right_fz',[float('nan')]*n)[i]
                    require(finite(control) and abs(cp['mean_normal_force_N'][i][w]-control)<=.1
                        and cp['max_normal_z_error'][i][w]<=.01 and cp['max_com_link_point_velocity_error'][i][w]<=.001,
                        'contact_readback_inconsistent_env'+str(i))
    for key in ('reset_joint_pos_before_physics','reset_root_before_physics'):
        value=r.get(key)
        require(isinstance(value,list) and len(value)==n and all(isinstance(row,list) and len(row)>0 and all(finite(v) for v in row) for row in value),'invalid_initial_'+key)
    return dict(version=VERSION,pass_=not reasons,reasons=list(dict.fromkeys(reasons)),
        performance_numbers_are_diagnostic=True,old_physical_smoke=r.get('physical_smoke_pass'),
        original_spin_skill_pass=r.get('spin_skill_pass'),legacy_spin_skill_pass=r.get('spin_skill_pass_legacy_reference'),
        original_flat_strict_window=r.get('strict_pass_window'),actual_task_reset_unchanged=True,
        observations=n,seconds=seconds,source_commit=SCUT_COMMIT,
        scope='Learning admission using actual task failure and MOD4 numerical/model/data integrity. Finite performance magnitudes and saturation usage are diagnostics. Hardware clipping remains enforced in the task. Not SCUT robot/physics equivalence or real-robot certification.')

def evidence(r,kind='spin',minimum_seconds=15):
    try:return _evidence(r,kind,minimum_seconds)
    except (KeyError,IndexError,TypeError,ValueError,ZeroDivisionError) as error:
        return dict(version=VERSION,pass_=False,reasons=['malformed_evidence: '+str(error)])

def assess(r):return evidence(r,'spin')
def assess_flat(r):return evidence(r,'flat')

def fullscale(r):
    failures=[]
    def require(ok,name):
        if not ok:failures.append(name)
    require(r.get('num_envs')==20000 and r.get('steps')==120 and r.get('seconds')==1.2,'wrong_fullscale_protocol')
    require(r.get('policy_frozen') is True and r.get('ppo_performed') is False,'non_frozen_physics_probe')
    require(r.get('nonfinite') is False and r.get('terminations')==0,'actual_fullscale_failure')
    for key,limit in (('max_closure_m',.002),('max_mimic_rad',.01)):
        require(finite(r.get(key)) and 0<=r[key]<=limit,'MOD4_model_integrity_'+key)
    require(r.get('plane_type')=='Plane' and r.get('ground_z_m')==0.,'wrong_ground')
    require(parameters(r),'fullscale_parameter_readback')
    contact=r.get('raw_contact_evidence') or {}
    require(contact.get('loaded_ground_contacts',0)>0 and contact.get('loaded_downward_ground_contacts')==0,'invalid_loaded_ground_contact')
    require(finite(contact.get('minimum_loaded_ground_normal_z')) and contact['minimum_loaded_ground_normal_z']>=-.1,'invalid_ground_normal')
    for key in ('max_tilt_deg','max_height_error_m'):
        require(finite(r.get(key)),'nonfinite_'+key)
    require(finite(contact.get('max_abs_ground_separation_m')),'nonfinite_ground_separation')
    return dict(version=VERSION,pass_=not failures,reasons=failures,old_combined=r.get('pass'),
                tilt_height_gap_are_diagnostics=True,scope='Same simulator and hardware envelope; actual resets/numerical/model/material/contact correctness only.')

def target_evidence(r,target):
    """Separate factual target tracking; never used to block intermediate curricula."""
    p=assess(r);rows=[]
    for g in r.get('groups',[]):
        if g.get('profile')!='spin' or abs(g.get('wz',0))!=target:continue
        ids=[i for i,gid in enumerate(r.get('group_ids',[])) if gid==g['group_id']]
        values=[r['per_environment']['yaw_rate'][i] for i in ids]
        rows.append(dict(command=g['wz'],observed=values,within_absolute_02=sum(abs(v-g['wz'])<=.2 for v in values),count=len(ids)))
    ok=p['pass_'] and len(rows)==2 and all(row['within_absolute_02']/row['count']>=.8 for row in rows)
    return dict(pass_=bool(ok),rows=rows,target_rad_s=target,scope='Final requested signed rate within 0.2rad/s in >=80% of each direction; factual target confirmation separate from curriculum advancement.')
