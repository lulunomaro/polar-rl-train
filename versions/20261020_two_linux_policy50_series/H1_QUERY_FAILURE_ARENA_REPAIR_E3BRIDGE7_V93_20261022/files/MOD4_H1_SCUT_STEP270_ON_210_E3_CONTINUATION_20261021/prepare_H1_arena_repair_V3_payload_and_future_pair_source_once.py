from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_PAIR_V1_20261021';N=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022';R=T/'reports'
assert not N.exists();(N/'reports').mkdir(parents=True)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_bytes())
shutil.copytree(P/'controllers',N/'controllers')
dest=N/'payloads/h1';shutil.copytree(P/'payloads/h1',dest)
repair=read(R/'H1_STEP270_RECORDED_ARENA_EXIT_AND_QUERY_DIAGNOSTIC_REPAIR_CPU_ACTUAL.json');assert repair['passed_recorded_CPU_regression'] and repair['candidate_not_installed']
shutil.copy2(T/'production_candidate_V2_ARENA_EXIT_UNINSTALLED/h1_step270_sdk_runtime_candidate.py',dest/'h1_step270_sdk_runtime_candidate.py')
shutil.copy2(R/'H1_STEP270_RECORDED_ARENA_EXIT_AND_QUERY_DIAGNOSTIC_REPAIR_CPU_ACTUAL.json',dest/'H1_ARENA_EXIT_RECORDED_CPU_REPAIR_ACTUAL.json')
loader=dest/'admitted_existing_same_source_native_CPU_v1.py';s=loader.read_text('utf8')
needle="    validate(proof, spec, manifest, reports)"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n    repair=read(B/'H1_ARENA_EXIT_RECORDED_CPU_REPAIR_ACTUAL.json')\n    assert repair['passed_recorded_CPU_regression'] and repair['unexpected_query_misses_still_global_reject_with_saved_bad_rows']\n    assert H(B/'h1_step270_sdk_runtime_candidate.py')==repair['source']['SHA']\n    assert manifest['H1_arena_exit_repair_CPU_SHA']==H(B/'H1_ARENA_EXIT_RECORDED_CPU_REPAIR_ACTUAL.json')")
s=s.replace('production_source_and_RSL_CPU_bound=True,','production_source_and_RSL_CPU_bound=True, arena_exit_recorded_CPU_repair_bound=True,')
ast.parse(s);loader.write_text(s,encoding='utf8')
task=read(dest/'job0/TASK.json');(dest/'TASK_V1_FAILED_HISTORY_UNMODIFIED.json').write_text(json.dumps(task,indent=2),encoding='utf8')
spec=dict(read(P/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['specs']['h1'])
task.update(id=N.name+'_h1',GPU_UUID=spec['GPU_UUID'],execution_backend='source210',source_H1_actual_latest_Adamstep=674740,source_repair_restart_from_last_qualified_complete_FINAL=True,failed_pair_V1_13_updates_preserved_not_claimed_FINAL=True,source_owned_completed_updates=42,only_added_finite_authored_floor_failure_termination=True)
(dest/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
oldm=read(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prior={x['relative']:x for x in oldm['files']};rows=[]
for p in sorted(dest.rglob('*')):
 if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
 rel=p.relative_to(dest).as_posix();sha=prior[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else H(p)
 rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
m=dict(oldm,files=rows,H1_arena_exit_repair_CPU_SHA=H(dest/'H1_ARENA_EXIT_RECORDED_CPU_REPAIR_ACTUAL.json'),same_complete_source_and_original_task_except_finite_arena_failure_termination=True)
(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');spec['manifest_SHA']=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
source=read(R/'STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json')['source']
hp=dict(epoch=time.time(),passed_H1_payload_source_and_reuse_binding_CPU_only=True,payload=str(dest),spec=spec,source=source,manifest_SHA=spec['manifest_SHA'],original_native3_and_query9_reused=True,H1_failed_pair_not_a_new_FINAL_source=True,repair_source_SHA=repair['source']['SHA'],not_installed_or_GO=True)
(N/'reports/H1_STEP270_PAYLOAD_AND_EXISTING_NATIVE_QUERY_BINDING_CPU_V2_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(hp,indent=2))
cfg=dict(sequence=3,cohort_id=N.name,previous_stage_dir=str(T/'E3_bridge_continuation_V7'),previous_actual_run_id=read(T/'E3_bridge_continuation_V7/reports/RECOVERY_BRIDGE_DETACHED_ACTUAL.json')['run_id'],owner_root='/mnt/mod4_linux_durable_20261013/H1step270_repair_2210v3/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_repair_2210v3/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_repair_2210v3/recovery'))
(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
prep=(P/'prepare_pair_with_actual_closed_bridge5_CPU_once.py').read_text('utf8');ast.parse(prep)
(N/'prepare_pair_with_actual_closed_bridge7_CPU_once.py').write_text(prep,encoding='utf8')
deploy=(P/'deploy_pair_new_original_writer_bounded_once.py').read_text('utf8').replace("previous_owner='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2110v5/owner'","previous_owner=q['previous_owner_root']")
deploy=deploy.replace("receipt=json.loads((R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes())","receipt=json.loads((R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes());q['previous_owner_root']='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2210v7/owner'")
needle="assert json.loads((previous_owner/'COHORT_FINAL.json').read_bytes())['original_cost_settled']"
extra="""
failed=owned/'H1step270_joint_2110v1/h1';fe=json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((failed/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert fe['actual_all_own_children_waited'] and fr['terminal_all_own_children_waited'] and fr['original_error'] and fr['final'] is None
assert not any(p.pid!=os.getpid() and any(x.startswith(str(failed)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
"""
assert deploy.count(needle)==1;deploy=deploy.replace(needle,needle+'\n'+extra);ast.parse(deploy)
(N/'deploy_pair_new_original_writer_bounded_once.py').write_text(deploy,encoding='utf8')
for name in ('collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py'):shutil.copy2(P/name,N/name)
report=dict(epoch=time.time(),H1_local_payload_prepared_only=True,H1_restart_from_last_qualified_complete_hour16_source_SHA=source['SHA'],H1_Adam=674740,failed_phase_updates13_Adam675000_not_FINAL_preserved=True,H1_no_remote_Task_or_GO=True,E3_bridge7_still_current_no_future_E3_source_prepared=True,pair3_unused_workflow_AST_only=True,requires_current_E3_actual_complete_FINAL_CPU_cost_allout_and_fresh_original_resources=True,controller_files_byteexact=all(H(p)==H(P/'controllers'/p.name) for p in (N/'controllers').glob('*.py')),native_query_GPU_not_replayed=True,manifest_SHA=spec['manifest_SHA'],next_unused_preparer=str(N/'prepare_pair_with_actual_closed_bridge7_CPU_once.py'))
with (R/'H1_ARENA_REPAIR_V3_LOCAL_PAYLOAD_AND_UNUSED_PAIR_WORKFLOW_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
