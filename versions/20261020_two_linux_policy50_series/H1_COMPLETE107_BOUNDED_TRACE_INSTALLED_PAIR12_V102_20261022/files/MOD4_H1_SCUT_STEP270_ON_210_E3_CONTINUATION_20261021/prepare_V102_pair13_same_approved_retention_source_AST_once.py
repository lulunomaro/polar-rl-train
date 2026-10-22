from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;R=T/'reports';N=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V12_20261022';F=T/'H1_STEP270_E3_BOUNDED_TRACE_PAIR_V13_20261022'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
a=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json');assert a['passed'] and a['actual_finite_returned']
q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert not F.exists();F.mkdir();(F/'reports').mkdir();shutil.copytree(N/'controllers',F/'controllers')
names=('prepare_pair_from_actual_closed_pair_with_approved_retention_CPU_once.py','deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py','relocate_actual_closed_H1_forensics_peer_TLS_bounded_once.py')
for name in names:
 shutil.copy2(N/name,F/name);ast.parse((F/name).read_text('utf8'));assert H(F/name)==H(N/name)
cfg=dict(sequence=13,cohort_id=F.name,previous_stage_dir=str(N),previous_actual_run_id=q['run_id'],previous_actual_owner=a['source210']['owner'],owner_root='/mnt/mod4_linux_durable_20261013/H1step270_boundedtrace_2210v13/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_boundedtrace_2210v13/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_boundedtrace_2210v13/recovery'),human_approved_future_trace_retention=True)
put(F/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
put(R/'V102_SAME_APPROVED_RETENTION_PAIR13_UNUSED_WORKFLOW_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),source_AST_reserved_only=True,current_pair12_actual_two_GO_positive_PPO=True,config=cfg,entry=str(F/names[0]),future_source_not_prepared_no_remote_Task_GO_or_cost=True,requires_current_two_FINAL_CPU_cost_allout_original_resources=True,same_approved_trace_adapter_loader_byteexact_continuation=True,closed_source_loader=str(T/'closed_step270_approved_trace_retention_source_CPU_v1.py'),no_repeat_transition_12CPU_native_query_or_GPU=True,actual_retention_success_still_requires_first_pair12_closed_index_receipts_and_directory_stat=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in F.rglob('*') if p.is_file()]))
print(json.dumps(dict(future_pair13_reserved_only=True,entry=str(F/names[0]))))
