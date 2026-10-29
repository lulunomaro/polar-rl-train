"""After actual116 closure/initialCPU only: summarize saved JSON and UTF8 curves.
No checkpoint, physical raw, GPU, SDK, SSH or account action.
"""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
Q=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False,ensure_ascii=False)
def mean(rows,key):return sum(x['fudan_real_reward_tracking']['components']['selected_optimization_terms'][key] for x in rows)/len(rows)
closed=read(Q/'reports/TWO116_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json')
cpu=read(Q/'reports/TWO116_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json')
assert cpu['passed'] and cpu['NEW_formal_loads']==2 and cpu['shared_normal86_loads']==1 and cpu['input_native114_loads']==0
assert closed['all_two_original_owner_nodes_workers_out'] and closed['canonical_None'] and closed['original_owner_private72_shared_locks_free']
assert set(closed['published'])=={'h1','h1_seed28'} and closed['original_fee_seconds']==sum(closed['original_fee_by_slot'].values())
models={};curves={}
for role,pub in closed['published'].items():
    row=pub['original_producer'];events=row['original_H1_events']['original270_completed_control_events']
    assert pub['twohost_complete_SHA'] and pub['NEW_formal_transfer_count']==1 and events['diagnostic_valid'] and events['invalid_rows']==0 and not events['diagnostic_write_errors']
    models[role]=dict(SHA=pub['SHA'],bytes=pub['bytes'],local_path=pub['local_path'],remote_path=pub['path'],native_iteration=row['updates'],world_updates=row['world_updates'],policy_updates=row['policy_updates'],new_counters=row['native88_migration_window']['counters'],events=events,twohost_SHA_passed=True,formal_transfer_count=1)
    prefix='h1_slot/' if role=='h1' else 'seed28_slot/'
    refs=[x for x in closed['all_original_texts_full_case_safe'] if x['relative'].startswith(prefix) and x['relative'].endswith('/ACTUAL_H1_CONVERGENCE_CURVE.jsonl')]
    assert len(refs)==1
    ref=refs[0];raw=Path(ref['local_path']).read_bytes();assert len(raw)==ref['bytes'] and hashlib.sha256(raw).hexdigest()==ref['SHA']
    data=[json.loads(x) for x in raw.splitlines()];assert data
    keys={'command_world_velocity','both_wheel_height_270_with_forward_command','supported_top_landing','supported_top_quiet','original_nonrequest_recovery'}
    maximum_sum_error=0
    for x in data:
        c=x['fudan_real_reward_tracking']['components'];assert set(c['selected_optimization_terms'])==keys
        maximum_sum_error=max(maximum_sum_error,abs(c['total']-sum(c['selected_optimization_terms'].values())))
        e=x['events'];assert e['diagnostic_valid'] and e['invalid_rows']==0 and not e['diagnostic_write_errors']
    assert maximum_sum_error<2e-8
    assert all(a['epoch']<b['epoch'] and a['completed_control_rows']<=b['completed_control_rows'] for a,b in zip(data,data[1:]))
    earliest={}
    for name in ('takeoff_count','landing_count','recovery_count'):
        x=next((x for x in data if x['events']['events'][name]>0),None)
        earliest[name]=None if x is None else dict(global_fresh_completed_control_rows=x['completed_control_rows'],policy_updates=x['policy_updates'],counter=x['events']['events'][name],not_episode_age_or_exact_event_time=True)
    first,last=data[:100],data[-100:]
    curves[role]=dict(source=ref,rows=len(data),first_control=data[0]['completed_control_rows'],last_curve_control=data[-1]['completed_control_rows'],formal_controls=events['complete_control_rows'],maximum_component_sum_error=maximum_sum_error,
        first100_population_control_means={k:mean(first,k) for k in sorted(keys)},last100_population_control_means={k:mean(last,k) for k in sorted(keys)},first_nonzero_sampled_rows=earliest,
        not_per_episode_returns_or_success_rates=True,last_curve_not_whole_formal_coverage=True,no_model_or_physics_raw_read=True)
put('CLOSED116_FULL_CURVES_SELECTED_OBJECTIVE_TEXT_ONLY_ACTUAL.json',dict(epoch=time.time(),curves=curves,source_is_saved_original_UTF8=True,no_checkpoint_GPU_SDK_or_SSH_action=True))
put('CURRENT_CLOSED116_TWO_QUALIFIED_DIRECT_WHEEL_HEIGHT_FORMALS_ACTUAL.json',dict(schema='mod4.actual116.closed.initialCPU.v1',epoch=time.time(),actual_closed=True,models=models,initial_two_NEW_plus_one_shared86=cpu,
    original_fee_by_slot=closed['original_fee_by_slot'],original_fee_seconds=closed['original_fee_seconds'],closing_remaining_snapshot=closed['closing_remaining_snapshot'],
    actual_original_owner_nodes_workers_out_waits_CNone_private_shared_locks_free_at_collection=True,not_permanent_GPU_availability=True,
    genuine270_recovery_counter_observed={k:v['events']['events']['recovery_count'] for k,v in models.items()},not_frozen_policy_skill_graduation=True,
    reward116_source_before_use_and_actual_GPU_precontrol_receipts_retained=True,all_old_false_and_once_preserved=True,
    no_extra_model_or_raw_reads_for_this_summary=True,latest_qualified_native_method116_not_normalPPO=True,
    next='Use actual counter/forward/height results to choose a new narrowly typed diagnostic. Do not blindly repeat an unchanged learning window, cold restart, fake airborne reset, scripted force, or relabel reward increase as270 skill.'))
print(json.dumps(dict(actual_closed=True,models={k:v['SHA'] for k,v in models.items()},fees=closed['original_fee_by_slot'],recovery={k:v['events']['events']['recovery_count'] for k,v in models.items()})))
