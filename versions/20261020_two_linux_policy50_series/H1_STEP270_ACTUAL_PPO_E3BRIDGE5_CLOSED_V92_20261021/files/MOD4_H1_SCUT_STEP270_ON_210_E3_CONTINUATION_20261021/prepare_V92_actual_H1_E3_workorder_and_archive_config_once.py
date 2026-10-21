from pathlib import Path
import ast,datetime,hashlib,json,time
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';N=T/'H1_STEP270_E3_PAIR_V1_20261021'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
v=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');assert v['passed']
q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
closed=read(T/'E3_bridge_continuation_V5/reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
assert closed['passed'] and closed['original_canonical_cost_settled']
paths=[N/'collect_pair_complete_finals_original_cost_bounded_once.py',N/'review_pair_complete_models_original_cost_CPU_once.py',
       T/'closed_step270_same_phase_production_source_CPU_v1.py',T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py']
for p in paths:ast.parse(p.read_text('utf8'))
go=v['source210']['current']['go']
first={k:v['source210']['current']['rows'][k]['latest_save'] for k in ('h1','recovery')}
proof=dict(epoch=time.time(),latest_actual_V92_overrides_V91_H1_not_started_and_bridge5_active=True,
           current_stage=str(N),current_run_id=q['run_id'],owner=q['owner_identity'],roots=q['roots'],nodes=q['nodes'],
           actual_workers=dict(h1=v['source210']['H1_worker'],recovery=v['source72']['worker']),
           actual_GO=go,first_positive_PPO_snapshot=first,only_historical_identity_and_resource_snapshots_not_permanent_alive=True,
           actual_H1_step270_production_GO_positive_PPO=True,E3_same50Hz_continues=True,E2_learning_deferred=True,
           H1_source_hour16_SHA=q['sources']['h1']['SHA'],H1_source_Adam=674740,
           H1_source_actual_optimizer_LR=.000759375,H1_config_initial_LR=.0001,adaptive_and_saved_optimizer_inheritance=True,
           H1_new_task_270mm_success_not_yet_evaluated=True,no_new_jump_height_or_graduation_claim=True,
           E3_bridge5_closed_complete_model_CPU_and_cost=closed,
           reused_native3_query9_and_SDK_RSL_CPU_evidence=True,
           first_metadata_deployer_preparer_consumed_do_not_rerun=True,
           unused_closing_collector=str(paths[0]),unused_closing_CPU_reviewer=str(paths[1]),
           collector_start_only_if_max_nominal_end_minus_current_time_le_900=True,
           source210_max900_then_target72_max210_single_finite_transport=True,
           future_closed_samephase_support_AST_only=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in paths[2:]],
           no_next_pair_V2_source_model_or_remote_Task_or_GO_prepared=True,
           future_after_both_actual_complete_models_CPU_cost_allout='Fresh unused H1+recovery pair. Dynamically bind each latest closed actual fullSHA/Adam/filename and same task runtime. H1 closed continuation uses new H1_step270_task_state and reserved closed-step270 loader/target CPU, not old 674740-only initial-migration loader. No native/query replay.',
           old_E3_bridge6_reserved_only_not_current_H1_E3_continuation=True,
           threshold_scope_policy=str(W/'polar-rl-train/docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md'),
           all_failed_readers_and_unused_V1_manifest_preserved=True,
           original_one_writer_budget_1548000_eight_extensions_and7800_reserve_unchanged=True,
           ordinary_append_only_no_record_tag_or_binary_Git_rehash=True)
put(R/'NEXT_ACTUAL_H1_STEP270_PRODUCTION_PPO_E3_CONTINUING_V92_WORK_ORDER.json',proof)
cfg=dict(destination='H1_STEP270_ACTUAL_PPO_E3BRIDGE5_CLOSED_V92_20261021',
         base_HEAD='a8c20596e9626bbd76f48a85034115529ef4123b',
         title='Archive actual H1 step270 PPO admission and E3 bridge5 closure with all CPU reader repairs')
put(W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88/reports/V92_ACTUAL_H1_E3_ORDINARY_ARCHIVE_ARGS.json',cfg)
print(json.dumps(dict(workorder_V92_prepared=True,actual_H1_PPO=True,not_jump_PASS=True,
    save_deadlines_BJT={k:datetime.datetime.fromtimestamp(g['save_deadline'],datetime.timezone(datetime.timedelta(hours=8))).isoformat() for k,g in go.items()})))
