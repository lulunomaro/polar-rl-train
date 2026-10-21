from pathlib import Path
import ast, hashlib, json, shutil, subprocess, time

T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports'
P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022'
N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022'
F=T/'H1_STEP270_E3_PAIR_V6_20261022'
C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';G=W/'polar-rl-train'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

a=read(N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
proof=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
assert a['passed'] and proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
assert proof['models']['h1']['final']['SHA']=='d512b3acdd50527a2c60afb620ab8708a3bb6650e1f686928284cc667e623e9f'
assert proof['models']['h1']['Adam']==675020
assert not F.exists();(F/'reports').mkdir(parents=True);shutil.copytree(N/'controllers',F/'controllers')
tree=ast.parse((T/'prepare_pair_V2_reserved_workflow_source_once.py').read_text('utf8'))
prep=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PREP' for t in x.targets))
ast.parse(prep);(F/'prepare_pair_from_actual_closed_pair_CPU_once.py').write_text(prep,encoding='utf8',newline='\n')
for name in ('deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py'):
    shutil.copy2(N/name,F/name);ast.parse((F/name).read_text('utf8'))
cfg=dict(sequence=6,cohort_id=F.name,previous_stage_dir=str(N),previous_actual_run_id=q['run_id'],owner_root='/mnt/mod4_linux_durable_20261013/H1step270_joint_2210v6/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_joint_2210v6/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_joint_2210v6/recovery'))
put(F/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
future=dict(epoch=time.time(),source_AST_reserved_only=True,no_future_model_source_prepared=True,no_remote_Task_or_GO=True,requires_both_actual_complete_models_CPU_cost_allout=True,controller_bytes_exact=all(H(p)==H(N/'controllers'/p.name) for p in (F/'controllers').glob('*.py')),generic_closed_samephase_loader_keeps_current_known_term_health_bytes=True,no_classifier_transition_reapplied=True,source_files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in F.rglob('*') if p.is_file()])
put(R/'PAIR_V6_RESERVED_SAMEPHASE_WORKFLOW_SOURCE_CPU_ACTUAL.json',future)
v=dict(epoch=time.time(),latest_V95_overrides_V94_pair3_active_classifier_uninstalled=True,current_stage=str(N),current_actual_run_id=q['run_id'],owner=q['owner_identity'],nodes=q['nodes'],roots=q['roots'],actual_GO=a['source210']['current']['go'],actual_workers=dict(h1=a['source210']['H1_worker'],recovery=a['source72']['worker']),first_positive_PPO_snapshot=dict(h1=a['source210']['current']['rows']['h1']['latest_save'],recovery=a['source72']['latest_save']),identity_resource_and_PPO_are_snapshots_not_permanent_alive_or_future_FINAL=True,previous_pair_complete_models_wholeCPU_original_cost_allout=proof,previous_H1_health_unknown1_and_stop_preserved_not_relabelled=True,previous_H1_early_stop_original=read(P/'reports/H1_EARLY_COMPLETE_FINAL_AND_STOP_REASON_ACTUAL.json'),installed_known_ordinary_term_classifier_CPU=read(R/'H1_ARENA_KNOWN_ORDINARY_TERM_HEALTH_CLASSIFIER_CPU_ACTUAL.json'),classifier_repair_actual_installed_source_CPU=read(N/'reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json'),classifier_repair_actual_closed_phase_admission=read(N/'reports/H1_CLOSED_SAME_STEP270_PHASE_PRODUCTION_CPU_ADMITTED_ACTUAL.json'),H1_source_new_complete_FINAL14_Adam675020_not_failed_prefix_or_old_fallback=True,H1_new_current_PPO_Adam675040=True,E2_learning_deferred=True,no_270mm_or_graduation_result=True,no_native_query_or_GPU_admission_replay=True,all_current_preparer_deployer_sourceCPU_firstmetadata_consumed=True,current_unused_collector=str(N/'collect_pair_complete_finals_original_cost_bounded_once.py'),current_unused_reviewer=str(N/'review_pair_complete_models_original_cost_CPU_once.py'),collector_only_max_actual_nominal_end_minus_current_le900=True,one_finite210max900_then72max210=True,future_pair6_reserved_only=future,future_pair6_preparer=str(F/'prepare_pair_from_actual_closed_pair_CPU_once.py'),future_models_dynamic_latest_actual_fullSHA_Adam_sourcefilename_samephase=True,no_hotpatch_or_second_writer=True,total1548000_eight_extensions_reserve7800_unchanged=True,all_previous_cleanup_and_relocations_consumed_no_new_cleanup=True,old_errors_false_and_unused_drafts_preserved=True,ordinary_only_no_record_tag=True)
put(R/'NEXT_ACTUAL_H1_FINAL14_CPU_CLASSIFIER_INSTALLED_BOTH_PPO_V95_WORK_ORDER.json',v)
s=(C/'append_H1_early_FINAL_classifier_E3_pair_V94_ordinary_once.py').read_text('utf8')
s=s.replace("P=T/'E3_bridge_continuation_V7'","P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022'")
s=s.replace("P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'","P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'")
s=s.replace("B/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'","B/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'")
s=s.replace("kind='H1_actual_arena_repair_FINAL14_known_ordinary_term_classifier_CPU_E3_pair_active'","kind='H1_FINAL14_wholeCPU_cost_settled_known_term_classifier_installed_both_actual_PPO'")
s=s.replace('previous_E3_bridge7_closed=proof','previous_pair_complete_wholeCPU_original_cost=proof')
s=s.replace('H1_early_saved_FINAL14_producer_only=True,H1_current_learning=False,H1_arena_repair_remote_installed=True,H1_known_term_classifier_repair_not_installed=True','previous_H1_FINAL14_wholeCPU_passed=True,H1_current_first_actual_PPO_snapshot=True,H1_arena_repair_remote_installed=True,H1_known_term_classifier_repair_installed_source_CPU=True')
s=s.replace('deferred=[]',"deferred=['e2']")
assert 'H1_known_term_classifier_repair_not_installed=True' not in s
ast.parse(s);name='append_H1_FINAL14_CPU_classifier_installed_both_PPO_V95_ordinary_once.py'
(C/name).open('x',encoding='utf8').write(s)
head=subprocess.run(['git','-C',str(G),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
args=dict(destination='H1_FINAL14_CPU_CLASSIFIER_INSTALLED_BOTH_PPO_V95_20261022',base_HEAD=head,title='Record complete H1 and E3 sources, settled costs, and installed known-term repair with both actual PPO')
put(C/'reports/V95_CLOSED_CLASSIFIER_BOTH_PPO_ORDINARY_ARCHIVE_ARGS.json',args)
print(json.dumps(dict(future_reserved=str(F),work_order=True,archive_helper=str(C/name),configuration=args)))
