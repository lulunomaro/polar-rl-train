from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_PAIR_V11_20261022';F=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V12_20261022';C=T/'trace_retention_candidate_V1_UNINSTALLED'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
cpu=read(R/'V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json');assert cpu['passed'] and len(cpu['cases'])==12
approval=dict(epoch=time.time(),approved=True,approval_scope='future_new_root_first1_latest2_prefix_pairs_plus_current_failure_v1',human_question_item_id='["request_user_input_async","call_81a54352e37243789220e6d6adc18eaf",0]',human_reply='允许新目录采用有界保留（推荐）',effective_only_after_current_pair11_actual_complete_save_cost_allout=True,no_current_training_hotpatch=True,existing_raw_originals_untouched=True,all_FINAL_source_failed_models_fulltext_errors_costs_and_producer_path_bytes_SHA_history_retained=True,future_older_intermediate_raw_and_matching_preupdate_pairs_pruned_not_recoverable=True,candidate_trace_SHA=cpu['candidate_trace']['SHA'],candidate_adapter_SHA=cpu['candidate_adapter']['SHA'],CPU_report_SHA=H(R/'V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json'),policy=cpu['policy'])
put(R/'V101_HUMAN_EXPLICIT_FUTURE_TRACE_RETENTION_APPROVAL_ACTUAL.json',approval)
generic=(T/'closed_step270_same_phase_production_source_CPU_v1.py').read_text('utf8');loader=generic.replace('import hashlib,json,os,psutil','import ast,hashlib,json,os,psutil')
needle="    cpu=read(B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')";assert loader.count(needle)==1
extra="""    approved=read(B/'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json');retention=read(B/'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json')
    assert approved['approved'] and approved['approval_scope']=='future_new_root_first1_latest2_prefix_pairs_plus_current_failure_v1'
    assert retention['passed'] and retention['original_trace_AST_exact_except_two_append_nodes']
    assert approved['candidate_trace_SHA']==retention['candidate_trace']['SHA'] and approved['candidate_adapter_SHA']==retention['candidate_adapter']['SHA']
    current={x['relative']:x for x in m['files']};trace='h1_production_control_prefix_trace_v1.py';adapter='h1_prefix_pair_retention_v1.py'
    assert H(B/trace)==current[trace]['SHA']==retention['candidate_trace']['SHA']
    assert H(B/adapter)==current[adapter]['SHA']==retention['candidate_adapter']['SHA']
    assert H(old/trace)==prior[trace]['SHA']
    if prior[trace]['SHA']==retention['original_trace']['SHA']:
        tree=ast.parse((B/trace).read_text('utf8'));assert isinstance(tree.body[-2],ast.ImportFrom) and tree.body[-2].module=='h1_prefix_pair_retention_v1'
        assert isinstance(tree.body[-1],ast.Assign) and ast.unparse(tree.body[-1])=='H1ControlPrefixTrace.persist = wrap_trace_persist(H1ControlPrefixTrace.persist)'
        assert ast.dump(ast.Module(body=tree.body[:-2],type_ignores=[]),include_attributes=False)==ast.dump(ast.parse((old/trace).read_text('utf8')),include_attributes=False)
    else:
        assert prior[trace]['SHA']==retention['candidate_trace']['SHA'] and prior[adapter]['SHA']==retention['candidate_adapter']['SHA'] and H(old/adapter)==prior[adapter]['SHA']
    for row in m['files']:
        rel=row['relative']
        if rel.endswith('.py') and rel in prior and rel not in (trace,'closed_production_continuation_CPU_v2.py'):
            assert row['SHA']==prior[rel]['SHA'] and row['bytes']==prior[rel]['bytes']
"""
loader=loader.replace(needle,extra+needle);ast.parse(loader);lp=T/'closed_step270_approved_trace_retention_source_CPU_v1.py';lp.open('x',encoding='utf8').write(loader)
assert not F.exists();F.mkdir();(F/'reports').mkdir();shutil.copytree(N/'controllers',F/'controllers')
for name in ('deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py','relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py'):
    shutil.copy2(N/name,F/name);ast.parse((F/name).read_text('utf8'))
# Keep the previously reserved CPU reader and append only descriptive metadata,
# reusing the passed source. No second checkpoint load or admission gate.
history=N/'reserved_history';history.mkdir(exist_ok=True);shutil.copy2(N/'review_pair_complete_models_original_cost_CPU_once.py',history/'review_pair_CPU_V1_UNUSED_BEFORE_EPISODE_METADATA.py')
descriptive=T/'H1_STEP270_E3_PAIR_V10_20261022/review_pair_complete_models_original_cost_CPU_once.py';shutil.copy2(descriptive,N/'review_pair_complete_models_original_cost_CPU_once.py');shutil.copy2(descriptive,F/'review_pair_complete_models_original_cost_CPU_once.py')
shutil.copy2(N/'prepare_pair_from_actual_closed_pair_CPU_once.py',F/'prepare_pair_from_actual_closed_pair_CPU_UNAPPROVED_FULL_TRACE_UNUSED_HISTORY.py')
s=(N/'prepare_pair_from_actual_closed_pair_CPU_once.py').read_text('utf8')
needle=" cfg=read(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json');P=Path(cfg['previous_stage_dir'])";assert s.count(needle)==1
s=s.replace(needle,needle+"\n approved=read(T/'reports/V101_HUMAN_EXPLICIT_FUTURE_TRACE_RETENTION_APPROVAL_ACTUAL.json');retention=read(T/'reports/V101_FUTURE_BOUNDED_TRACE_PAIR_RETENTION_CANDIDATE_CPU_ACTUAL.json');assert approved['approved'] and retention['passed'] and approved['candidate_trace_SHA']==retention['candidate_trace']['SHA'] and approved['candidate_adapter_SHA']==retention['candidate_adapter']['SHA']")
needle="   shutil.copy2(T/'closed_step270_same_phase_production_source_CPU_v1.py',dest/'closed_production_continuation_CPU_v2.py')";assert s.count(needle)==1
replacement="""   shutil.copy2(T/'closed_step270_approved_trace_retention_source_CPU_v1.py',dest/'closed_production_continuation_CPU_v2.py')
   for name in ('h1_production_control_prefix_trace_v1.py','h1_prefix_pair_retention_v1.py'):
    shutil.copy2(T/'trace_retention_candidate_V1_UNINSTALLED'/name,dest/name)
   (dest/'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json').write_text(json.dumps(approved,indent=2),encoding='utf8')
   (dest/'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json').write_text(json.dumps(retention,indent=2),encoding='utf8')"""
s=s.replace(needle,replacement)
needle="task.update(qualified_source_fallback_after_failed_pair7=False,";assert s.count(needle)==1;s=s.replace(needle,"task.update(approved_future_prefix_retention_policy=retention['policy'] if key=='h1' else None,qualified_source_fallback_after_failed_pair7=False,")
ast.parse(s);prep=F/'prepare_pair_from_actual_closed_pair_with_approved_retention_CPU_once.py';prep.open('x',encoding='utf8').write(s)
det=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');actual=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');assert actual['passed']
cfg=dict(sequence=12,cohort_id=F.name,previous_stage_dir=str(N),previous_actual_run_id=det['run_id'],previous_actual_owner=actual['source210']['owner'],owner_root='/mnt/mod4_linux_durable_20261013/H1step270_boundedtrace_2210v12/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_boundedtrace_2210v12/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_boundedtrace_2210v12/recovery'),human_approved_future_trace_retention=True)
put(F/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
report=dict(epoch=time.time(),source_AST_reserved_only=True,human_explicitly_approved=True,not_installed_no_future_model_Task_GO_or_cost=True,requires_pair11_actual_two_FINAL_wholeCPU_cost_allout_and_original_resources=True,entry=str(prep),closed_source_loader=dict(path=str(lp),SHA=H(lp),accepts_only_known_original_to_candidate_transition_or_byteexact_candidate_continuation=True),same_runtime352d_health853b_worker_PPO_account_and_physics_unchanged=True,no_native_query_GPU_reexecution=True,original_trace_all_method_AST_exact=True,descriptive_CPU_reader_only_single_existing_load=True,config=cfg,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in F.rglob('*') if p.is_file()],candidate_not_yet_actual_retention_success=True,actual_retention_requires_first_new_cohort_closed_text_index_intents_receipts_review=True)
put(R/'V101_APPROVED_TRACE_RETENTION_PAIR12_UNUSED_WORKFLOW_SOURCE_AST_ACTUAL.json',report)
print(json.dumps(dict(human_approval_recorded=True,future_pair12_reserved_only=True,new_entry=str(prep),no_current_hotpatch=True)))
