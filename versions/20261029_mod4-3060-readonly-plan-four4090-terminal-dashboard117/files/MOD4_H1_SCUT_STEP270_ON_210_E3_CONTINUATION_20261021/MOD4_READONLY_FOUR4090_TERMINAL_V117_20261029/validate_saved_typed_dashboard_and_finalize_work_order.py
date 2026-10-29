"""Validate only saved117 reduced UTF8 snapshots and actual116/E2 publications."""
from pathlib import Path
import hashlib,json,math,time
M=Path(__file__).resolve().parent;T=M.parent;N=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=M/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert list((R/'selected_v6').glob('FINITE_SERIAL_COLLECTOR_RETURNED_*.json'))
visible=read(R/'selected_v5/ACTUAL3060_TERMINAL_VISIBLE_IN_INTERACTIVE_SESSION.json');assert visible['same_interactive_session'] and visible['known_console_visible'] and visible['original_terminal_identity_exact']
paths=sorted((R/'selected_v6').glob('SERIAL_SNAPSHOT_*_ACTUAL.json'));checks=0;max_sum_error=0
terms={'command_world_velocity','both_wheel_height_270_with_forward_command','supported_top_landing','supported_top_quiet','original_nonrequest_recovery'}
for path in paths:
    snap=read(path)['snapshot'];assert all(h['passed'] for h in snap['hosts'])
    gpus=[g['uuid'] for h in snap['hosts'] for g in h['gpus']];assert len(gpus)==len(set(gpus))==4
    for host in snap['hosts']:
        for job in host['jobs']:
            if not job.get('curve'):continue
            data=job['curve'];a,b=data[0],data[-1]
            expected=(b['controls']-a['controls'])/(b['epoch']-a['epoch']);speed=job['speed'];assert speed['controls_per_wall_second']==expected
            assert speed['transitions_per_wall_second']==expected*4096 and speed['callbacks_per_wall_second']==expected*4
            for row in data:
                assert set(row['terms'])==terms|{'total'} and all(math.isfinite(x) for x in row['terms'].values())
                err=abs(row['terms']['total']-sum(row['terms'][k] for k in terms));max_sum_error=max(max_sum_error,err);assert err<2e-8
                checks+=1
closed=read(N/'reports/CURRENT_CLOSED116_TWO_QUALIFIED_DIRECT_WHEEL_HEIGHT_FORMALS_ACTUAL.json');assert closed['actual_closed']
e2=read(L/'E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5/reports/E2_V5_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json')
put('FINAL_ACTUAL117_FOUR4090_TERMINAL_WORK_ORDER.json',dict(epoch=time.time(),remote_host='10.24.4.249',remote_root='D:/MOD4_async_eval/MOD4_PLAN_AND_FOUR4090_TERMINAL_20261029v117',visible_interactive_console_proof=visible,
    finite_serial_sampler_actual_returned=True,all_four_GPU_valid_snapshots=len(paths),actual_reduced_curve_rows_checked=checks,maximum_selected_terms_sum_error=max_sum_error,
    last_snapshot_path=str(paths[-1]),last_snapshot_SHA=hashlib.sha256(paths[-1].read_bytes()).hexdigest(),last_snapshot=read(paths[-1])['snapshot'],
    current116_closed_source=str(N/'reports/CURRENT_CLOSED116_TWO_QUALIFIED_DIRECT_WHEEL_HEIGHT_FORMALS_ACTUAL.json'),current116_closed=closed,
    E2_V5_full_terminal_source=str(L/'E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5/reports/E2_V5_TERMINAL_ORIGINAL_RETURNED_ACTUAL.json'),E2_V5_original_frozen_execution=e2['passed_original_frozen_execution'],
    oldexpert_savedtext_review=str(L/'E2_V5_FINAL_EARLY_COMMAND_SAVED_TEXT_REVIEW_20261029_V1/HANDOFF_FROZEN_E2_V5_SAVED_TEXT_COMPLETE_COMMAND_PROFILE_REVIEW.md'),
    actual_window_and_closed_state_timing_distinguished=True,display_snapshot_age_is_visible=True,no_indefinite_sampler_or_continuous_alive_claim=True,
    future_refresh_entry=str(M/'refresh_serial_dashboard_v6_typed_curve.py')+' --samples 1 --period 30',future_refresh_requires_fresh_LOCAL_exact_CIM_and_globalserial_lease_free=True,
    do_not_restart_original_visible_task_or_replay_deployment=True,no_model_raw_GPU_SSH_or_account_action_for_this_report=True))
print(json.dumps(dict(passed=True,four_GPU_snapshots=len(paths),curve_rows=checks,max_component_sum_error=max_sum_error)))
