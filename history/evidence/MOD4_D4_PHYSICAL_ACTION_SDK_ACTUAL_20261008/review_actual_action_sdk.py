"""Independent issue-to-first-apply timing/target checks on completed SDK raw data."""
from pathlib import Path
import json,time,hashlib,collections,sys
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
ev=read(R/'D3_EXISTING_ASYNC_CASES.json');assert not ev['attention'];jobs={j['id']:j for j in ev['jobs']}
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
report=dict(epoch=time.time(),scope='3060 two actual10env300control3s SDK cases; physical target delay0/2500/5000us,2.5ms32-4 with existing D3 feedback;not PPO or15s skill graduation',source_sha256='ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61',cases={},large_returned_files=[],new_learning_or_budget_operations=0,production234_unchanged=True)
probes={}
for label in ('00-off','01-on'):
    job='clk2500-closure-episode-d3-30-d4-sdk-'+label;j=jobs[job];folder=R/'windows'/job
    assert j['complete'] and j['result']['exit_code']==0 and not j['result']['errors'] and not j['result']['error_files']
    p=read(folder/'probe.json');m=read(folder/'manifest.json');res=read(folder/'result.json');probes[label]=p
    assert p==j['probe'] and res==j['result'] and m==j['manifest']
    assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==report['source_sha256'] and res['checkpoint']['finite_tensors']==84
    assert m['steps']==p['steps']==300 and m['num_envs']==10 and m['seed']==p['seed']==20261002
    assert m['physics_dt_s']==.0025 and m['solver_position']==32 and m['solver_velocity']==4 and m['control_dt_s']==.01
    assert m['no_learning'] and not m['canonical_write_authority'] and p['actual_physics_callbacks']==p['expected_physics_callbacks']==1200
    assert p['action_delay_callback_delta']==dict(legs=1200,wheels=1200)
    assert not p['nonfinite'] and p['resets']==0
    original_v4=evidence(p,'flat',3)
    assert not original_v4['reasons'] or original_v4['reasons']==['group_samples_incomplete'],original_v4
    s=p['sensor_actual_manager_audit'];a=p['frozen_architecture_audit'];assert s['actor35'] and s['critic38_clean'] and s['same_tick_draws_unchanged'] and s['command_lastaction_mode_wheel_slots_exact'] and s['formula_max_error']<=2e-6
    assert a['variant']=='A0' and a['actual_command_error']==0 and a['optimizer_updates']==0 and not a['actor_receives_teacher'] and not a['actor_receives_critic']
    assert all(p['action_delay_CUDA_disk_roundtrip'].values())
    audit=p['action_delay_actual_SDK'];assert audit['application_formula_max_error']<=1e-6 and audit['callback_counts']==dict(legs=1200,wheels=1200)
    assert audit['policy_requested_processed_targets_restored_after_apply'] and audit['original_legacy_delay_remains_disabled'] and audit['actual_apply_time_counter_minus1']
    reset=audit['reset_rows'];assert all(x['unselected_exact'] and x['global_physics_clock_preserved'] and x['selected_stale_pending_cleared'] and x['neutral_target_from_actual_default_q_or_zero_wheel'] for x in reset)
    assert any(x['group']=='legs' and x['env_ids']==[1,4,7] for x in reset) and any(x['group']=='wheels' and x['env_ids']==[1,4,7] for x in reset)
    groups={}
    for key,width in [('legs',4),('wheels',2)]:
        rows=audit['rows'][key];assert len(rows)==1200
        decisions={row['actual_apply_tick']:row['requested_processed_target'] for row in rows if row['actual_apply_tick']%4==0}
        assert len(decisions)==300;seen={};counts=collections.Counter();neutral_samples=0;max_age=0;max_target_error=0
        for tick,row in enumerate(rows):
            assert row['actual_apply_tick']==tick and row['physics_period_us']==2500 and row['control_period_us']==10000
            requested=row['requested_processed_target'];applied=row['actual_processed_target'];readback=row['actual_articulation_target']
            assert len(applied)==len(requested)==len(readback)==10 and all(len(x)==width for x in applied)
            assert row['same_group_targets_coherent']
            for env in range(10):
                assert applied[env]==readback[env];valid=row['valid_policy_command'][env];issue=row['command_issue_tick'][env];lat=row['actual_first_transition_delay_us'][env];age=row['held_command_sample_age_us'][env]
                assert row['neutral_reset_hold'][env]==(not valid)
                if valid:
                    assert issue in decisions and applied[env]==decisions[issue][env]
                    assert age==(tick-issue)*2500;max_age=max(max_age,age)
                    marker=(env,issue)
                    if marker not in seen:
                        first=(tick-issue)*2500;assert first==row['requested_delay_us'][env]==lat
                        assert first in ((0,) if label=='00-off' else (0,2500,5000));seen[marker]=first;counts[first]+=1
                    else:assert lat==seen[marker]
                else:
                    assert issue==lat==age==-1;neutral_samples+=1
                    if key=='wheels':assert applied[env]==[0.,0.]
        assert len(seen)==3000
        if label=='00-off':assert neutral_samples==0 and counts=={0:3000}
        else:assert set(counts)=={0,2500,5000}
        groups[key]=dict(actual_first_application_delay_us_counts={str(k):v for k,v in sorted(counts.items())},all3000commands_applied_at_requested_physics_boundary=True,actual_articulation_target_error=0,neutral_reset_hold_samples=neutral_samples,max_held_command_sample_age_us=max_age,holding_age_not_relabelled_as_transition_latency=True)
    for n in ('probe.json','result.json'):
        raw=(folder/n).read_bytes();h=hashlib.sha256(raw).hexdigest();assert h==j['sha256'][n];report['large_returned_files'].append(dict(job=job,name=n,sha256=h,bytes=len(raw)))
    report['cases'][label]=dict(groups=groups,task_resets=0,closure_mm=1000*p['max_closure_after_grace_m'],mimic_rad=p['max_mimic_after_grace_rad'],contact_callbacks=1200,manager_formula_error=s['formula_max_error'],queue_cuda_disk_roundtrip=p['action_delay_CUDA_disk_roundtrip'],selected_reset_rows=reset,original_v4_preserved=original_v4,original_flags={k:p.get(k) for k in ('physics_pass','strict_pass','strict_pass_window','strict_pass_window_5ms')},process_wall_seconds=res['physics_process_wall_seconds'],observed_GPU_memory_mib=res['observed_GPU_memory_mib'],memory_peak_is2s_sample_not_continuous=True,runtime_archive_sha256=res['runtime_archive_sha256'])
off=probes['00-off'];on=probes['01-on'];params=lambda p:p.get('initial_parameter_audit') or p.get('mild_initial_parameters')
report['paired_initial_state']=dict(root_exact=off['reset_root_before_physics']==on['reset_root_before_physics'],q_exact=off['reset_joint_pos_before_physics']==on['reset_joint_pos_before_physics'],parameters_exact=params(off)==params(on),D3_feedback_delay_assignment_exact=off['sensor_actual_manager_audit']['actual_feedback_sample_apply']==on['sensor_actual_manager_audit']['actual_feedback_sample_apply'])
assert all(report['paired_initial_state'].values())
report['decision']=dict(actual_D4_target_queue_SDK_scope_accepted=True,D4_PPO_or_learning_executor_deployed=False,not_allDR_or_sim2real_certified=True,need_4090_newrange20k_and_completePPO=True,current_D3_learning_continues_uninterrupted=True)
(R/'D4_ACTUAL_TARGET_QUEUE_SDK_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(cases=report['cases'],paired_initial_state=report['paired_initial_state'],decision=report['decision'])))
