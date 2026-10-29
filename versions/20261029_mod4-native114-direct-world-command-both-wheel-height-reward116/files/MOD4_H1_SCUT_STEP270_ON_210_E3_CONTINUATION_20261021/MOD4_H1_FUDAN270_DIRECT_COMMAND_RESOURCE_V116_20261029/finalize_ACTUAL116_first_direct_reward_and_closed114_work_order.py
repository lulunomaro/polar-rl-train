from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
C=L/'TWO116_DIRECT_COMMAND_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
Q114=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
first=Q/'reports/TWO116_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json';f=read(first)
assert f['actual_finite_returned'] and all(x['passed_first_NEW_native_policy'] for x in f['results'].values())
alias=R/first.name;assert not alias.exists();alias.write_bytes(first.read_bytes());assert H(alias)==H(first)
put(R/'ACTUAL116_FIRST_AGGREGATE_EXACT_ALIAS_FOR_FROZEN_NORMAL_COLLECTOR.json',dict(source=str(first),alias=str(alias),bytes=alias.stat().st_size,SHA=H(alias),no_remote_first_replay_or_model_read=True))
actual=read(C/'reports/TWO116_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json');owner=actual['identities']['owner']['exact_identity']
bound=dict(owner=owner,run_id=f['run_id'],go=f['go']);put(R/'KNOWN_ACTIVE116_AUTHORITY_BINDING_FOR_SERIAL_EXPERT_EVALUATION.json',bound)
roles={}
for k,x in f['results'].items():
    positive=x['positive'];components=positive['fudan_real_reward_tracking']['components'];terms=components['selected_optimization_terms']
    assert set(terms)=={'command_world_velocity','both_wheel_height_270_with_forward_command','supported_top_landing','supported_top_quiet','original_nonrequest_recovery'}
    assert abs(components['total']-sum(terms.values()))<1e-7
    assert positive['producer']['command_reward116']==f['go'][k]['fudan_step_task']['command_reward116']
    roles[k]=dict(passed_first_NEW_native_policy=True,counters=positive['native88_migration_window']['counters'],events=positive['original_task_events'],
        actual_last_complete_control_population_mean_components=components,GPU_snapshot=x['GPU_snapshot'],node=x['node'],worker=x['worker'],
        actual_GPU_reward116_precontrol_guard_was_checked=True,readback_raw_values_not_exported_by_first_observer=True,not_continuous_alive_FINAL_skill_or_causal_learning_gain=True)
zone=timezone(timedelta(hours=8));times={k:datetime.fromtimestamp(v,zone).isoformat() for k,v in f['normal_closing_gates'].items()}
put(R/'CURRENT_ACTUAL116_TWO_DIRECT_COMMAND_FIRST_NEW_UPDATES_AND_NORMAL_CLOSING_WORK_ORDER.json',dict(schema='mod4.actual116.direct_command.first.v1',epoch=time.time(),run_id=f['run_id'],owner=owner,owner_root=actual['owner_root'],node_roots=actual['node_roots'],actual_signed_go=f['go'],roles=roles,
    selected_reward='world velocity command + BOTH own wheel-bottom270 target near both wheel front edges with forward motion + actual top support/quiet; generic flight/body height/tuck/extension diagnostic only',
    source_before_use='28 source counterexamples +26 Task/GO negatives +133 ownFK mapping; two actual SDK/fullstate/RSL/norms3opts CPU admissions;44controller negatives;actualGPU readback before first control',
    normal_closing_gates=f['normal_closing_gates'],normal_closing_BJT=times,normal_collector=str(Q/'collect_TWO116_fudan270_formals_original_cost_normal900_UNUSED_once.py'),
    initial_NEW_formal_CPU=str(Q/'review_TWO116_NEW_fudan270_formals_shared_witness_initial_CPU_UNUSED_once.py'),normal_sources_FROZEN_UNUSED=True,
    next='Only signed maxnominal-now<=900 LOCAL+remote and freshLOCALexactCIM/globalseriallease before selected normal collector; original850owner180nodes1140total;allout/waits/CNone/locks/unique raworiginalfees sumonce/twoNEWformals transfer1each/fulltwohostSHA;then2NEWformal1each+ONEsharednormal86/input114PT0 initialCPU. Do not reobservefirst or downloadmodel early.',
    latest_qualified_formal_still114_until116_final_and_initialCPU=True,no_real270_skill_proof=True,fullFINAL_cost_pending=True,
    scope='first240controls=2.4s not full20s episode; early events allzero not proof of subsequent full window. Actual logged selected terms differ from old diagnostic jump_reward.'))
closed=read(Q114/'reports/TWO114_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json');cpu=read(Q114/'reports/TWO114_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json');assert cpu['passed']
rows={}
for k,pub in closed['published'].items():
    row=pub['original_producer'];events=row['original_H1_events']['original270_completed_control_events']
    rows[k]=dict(SHA=pub['SHA'],bytes=pub['bytes'],local_path=pub['local_path'],remote_path=pub['path'],native_iteration=row['updates'],world_updates=row['world_updates'],policy_updates=row['policy_updates'],events=events,
        twohost_complete_SHA=pub['twohost_complete_SHA'],formal_transfer_count=pub['NEW_formal_transfer_count'])
put(R/'CURRENT_CLOSED114_TWO_QUALIFIED_FORMALS_ZERO_PLATFORM_SUCCESS_ACTUAL.json',dict(epoch=time.time(),actual_closed=True,models=rows,initial_two_NEW_and_one_shared86=cpu,
    original_fee_by_slot=closed['original_fee_by_slot'],original_fee_seconds=closed['original_fee_seconds'],closing_remaining_snapshot_PRE116=closed['closing_remaining_snapshot'],
    original_owner_nodes_workers_out_CNone_private_shared_locks_free_observed_at_collection=True,not_permanent_resource_availability=True,
    current_new116_is_separate_actual_GO=True,all_original_UTF8_remains_in_original_collector_directory=True,no_extra_model_or_raw_reads_for_this_work_order=True))
print(json.dumps(dict(actual116_first_both_pass=True,run_id=f['run_id'],owner=owner['pid'],normal_closing_BJT=times,closed114_native_h1=rows['h1']['SHA'])))
