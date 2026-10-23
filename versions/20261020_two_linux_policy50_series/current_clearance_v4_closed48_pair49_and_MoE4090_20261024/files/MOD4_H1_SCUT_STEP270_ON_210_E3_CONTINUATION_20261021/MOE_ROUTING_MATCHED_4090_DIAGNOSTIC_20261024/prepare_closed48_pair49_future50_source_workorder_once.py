from pathlib import Path
import ast,datetime,hashlib,json,re,shutil,time,tomllib
D=Path(__file__).resolve().parent.parent/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023';T=D.parent;W=T.parent;R=D/'reports'
C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';K=W/'MOD4_STORAGE_WASTE_CLEANUP_SUBAGENTS_AUTHORIZED_20261023'
P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V48_20261023'
N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V49_20261023'
F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V50_20261024'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
J=lambda v:json.dumps(v,ensure_ascii=False)

def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def main():
    proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    health=read(R/'CURRENT_CLEARANCE_TUCK_V4_CURRENT48_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json')
    active=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
    resource=read(N/'reports/NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json')
    inv=read(P/'reports/PEER_FORENSICS_FRESH_SOURCE_ACTUAL.json');storage=read(P/'reports/CLOSED48_OLD46_45_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')
    sdk=read(N/'reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json')
    receipt=read(P/'reports/PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
    assert health['passed_checkpoint_health_and_recording_scope'] and active['passed'] and active['actual_finite_returned']
    assert read(N/'reports/RESOURCE_BRANCH_PREPARE_DECISION_ACTUAL.json')['paired'] is True
    assert storage['passed'] and storage['source_above_original_disk25'] and storage['source_free_after']>25*1024**3 and storage['all_own_storage_processes_actual_out']
    assert not (N/'reports/PAIR_CLOSING_COLLECTOR_STARTED_ACTUAL.json').exists()
    assert H(N/'collect_selected_pair_finals_unused_once.py')==H(P/'collect_selected_pair_finals_unused_once.py')
    collector=dict(epoch=time.time(),passed_source_AST_only=True,current_unused_collector=str(N/'collect_selected_pair_finals_unused_once.py'),SHA=H(N/'collect_selected_pair_finals_unused_once.py'),byteexact_from_actual_closed48_collector=True,existing_900_local_assert_and_precise_H1_log_snapshot_retained=True,no_new_collector_patch=True,not_executed=True)
    put(R/'UNUSED49_PAIRED_COLLECTOR_INHERITED_SOURCE_ACTUAL.json',collector)
    assert not F.exists();F.mkdir();(F/'reports').mkdir()
    for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(N/folder,F/folder)
    for p in N.glob('*.py'):
        s=p.read_text('utf8').replace('H1step270_reward_tuckclear4_2310v49','H1step270_reward_tuckclear4_2410v50').replace(P.name,N.name)
        ast.parse(s);(F/p.name).write_text(s,encoding='utf8')
    prep=(F/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8')
    assert "P=T/'"+N.name+"';E=T/'"+N.name+"'" in prep
    assert all(x in prep for x in ('PAIR_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json','PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json','PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json',"repair/'reference_sources'",'current_pair_closed_text/h1/job0/production'))
    assert N.name+'/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json' in (F/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py').read_text('utf8')
    for p in (N/'repair_sources').rglob('*'):
        if p.is_file():assert p.read_bytes()==(F/'repair_sources'/p.relative_to(N/'repair_sources')).read_bytes()
    assert H(F/'repair_sources/h1_step270_path_reward_v1.py')=='42a6a4bf690d474dcb2359609dfcb189df2b7aaf0ee229f74a286fcc3a9bda76'
    assert not any((F/x).exists() for x in ('controllers','payloads','current_pair_closed_models'))
    future=dict(epoch=time.time(),passed_source_AST_only=True,paired_predecessor=N.name,E_equals_P=True,both_latest_complete_models_only_after_actual49_both_closed_CPU=True,previous_owner_and_closing_pair_schema=True,no_stale48_or39_E3_fallback=True,repair_sources_byteexact=True,module_SHA=H(F/'repair_sources/h1_step270_path_reward_v1.py'),runtime_SHA=H(F/'repair_sources/h1_step270_sdk_runtime_candidate.py'),reference_copy_and_metadata_tuck1_7_and_bounded_H1_log_snapshot_retained=True,no_future_model_payload_Task_GO_or_fee=True,not_executed=True)
    put(R/'NEXT50_CURRENT_CLEARANCE_V4_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json',future)
    s=(D/'review_closed48_current_clearance_tuck_v4_health_retention_text_CPU_once.py').read_text('utf8').replace(P.name,N.name).replace('CURRENT48_CLOSED','CURRENT49_CLOSED').replace('CLOSED48_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_','CLOSED49_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_')
    ast.parse(s);reader=D/'review_closed49_current_clearance_tuck_v4_health_retention_text_CPU_once.py';assert not reader.exists();reader.write_text(s,encoding='utf8')
    go=active['source210']['current']['go'];gate_epoch=max(x['nominal_end_epoch'] for x in go.values())-900
    gate=datetime.datetime.fromtimestamp(gate_epoch,datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    warning='<unknown>:11: SyntaxWarning: "\\S" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\\\S"? A raw string is also an option.\n'
    installed=dict(epoch=time.time(),preparer_actual_returncode=0,preparer_stderr_verbatim=warning*2,not_training_failure=True,installed_H1_source=sdk,GO_PPO=active,latest_complete_sources=proof['models'],source_scope='Both actual complete48 models, independently settled; H1 same270phase/V4 and E3 same50Hz fullstate.',no_new_reward_or_record_experiment=True)
    put(R/'ACTUAL49_SAME_REWARD_PAIRED_INSTALLED_SOURCE_PPO_AND_WARNING_ACTUAL.json',installed)
    models=proof['models'];m=models['h1'];h=health['health'];ret=health['retention'];snap=m['H1_current_episode_snapshot']
    fallback=(P/'reports/PAIR_H1_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json').exists()
    timing=dict(epoch=time.time(),collector_started=read(P/'reports/PAIR_CLOSING_COLLECTOR_STARTED_ACTUAL.json')['epoch'],actual_terminal={k:v['actual_cost']['ended_epoch'] for k,v in models.items()},actual_collector_returned=receipt['epoch'],whole_CPU=proof['epoch'],health_CPU=health['epoch'],storage_snapshot=inv['epoch'],E3_resource=resource['epoch'],new_GO=go,no_idle_gap_charge_refund_or_second_account_write=True)
    put(R/'CLOSED48_ACTUAL_PAIR_COLLECTION_COST_AND_PAIR49_GO_TIMING_SCOPE_ACTUAL.json',timing)
    order=T/'reports/NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED48_118_76_FOUR_OLD_PEER_PAIR49_BOTH_PPO_AND_HUMAN_MOE_WORK_ORDER.json'
    put(order,dict(epoch=time.time(),latest_actual='CURRENT_CLEARANCE_V4_CLOSED48_FOUR_OLD_PEER_PAIR49',current=N.name,paired=True,closed48_pair_complete_CPU=proof,closed_health_retention=health,fresh_closed48_storage=inv,verified_four_old_NPZ_relocated=storage,current_GO_PPO_snapshot=active,E3_before_GO_resource_snapshot=resource,H1_saved_optimizer_LR=sdk['actual_optimizer_saved_LR'],collector_gate_epoch=gate_epoch,collector_gate_BJT=gate,current_unused_collector=collector,closed48_exact_log_snapshot_branch_executed=fallback,all_closed_full_texts=len(receipt['all_texts']),historical_local_preview_warning_from46='PowerShell JSON depth3 preview truncation; original full JSON unchanged and all full text returned, not a model or training error',future_source_AST_only=future,actual_timing_scope=timing,no_new_trial_or_reward=True,no_270mm_skill_graduation_claim=True))


if __name__=='__main__':main()
