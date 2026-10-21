from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_REPAIR_PAIR_V3_20261022';OLD=T/'H1_STEP270_E3_PAIR_V4_20261022';N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022';R=T/'reports'
read=lambda p:json.loads(Path(p).read_bytes());H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert read(R/'H1_ARENA_KNOWN_ORDINARY_TERM_HEALTH_CLASSIFIER_CPU_ACTUAL.json')['passed_known_task_term_CPU_classification'] and not N.exists()
(N/'reports').mkdir(parents=True);shutil.copytree(P/'controllers',N/'controllers')
q=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');cfg=dict(sequence=5,cohort_id=N.name,previous_stage_dir=str(P),previous_actual_run_id=q['run_id'],owner_root='/mnt/mod4_linux_durable_20261013/H1step270_healthrepair_2210v5/owner',roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_healthrepair_2210v5/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_healthrepair_2210v5/recovery'))
(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
loader=(T/'closed_step270_same_phase_production_source_CPU_v1.py').read_text('utf8')
needle="    prior={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']}"
loader=loader.replace(needle,needle+"\n    repair=read(B/'H1_KNOWN_ORDINARY_TASK_TERM_CLASSIFIER_CPU_ACTUAL.json')\n    source=read(B/'H1_KNOWN_TASK_TERM_SOURCE_STOP_ACTUAL.json')\n    assert repair['passed_known_task_term_CPU_classification'] and repair['normalized_rest_AST_exact'] and repair['all_other_unknown_mimic_nonfinite_callback_guards_unchanged']\n    assert source['only_original_unknown_is_known_arena_exit'] and not source['original_health_relabelled_pass']")
needle="            assert row['SHA']==prior[row['relative']]['SHA'] and row['bytes']==prior[row['relative']]['bytes']"
replacement="""            if row['relative']==repair['relative']:
                assert row['SHA']==repair['candidate']['SHA'] and prior[row['relative']]['SHA']==repair['original']['SHA']
            else:
                assert row['SHA']==prior[row['relative']]['SHA'] and row['bytes']==prior[row['relative']]['bytes']"""
assert loader.count(needle)==1;loader=loader.replace(needle,replacement);ast.parse(loader)
(T/'closed_step270_known_task_term_classifier_source_CPU_v1.py').open('x',encoding='utf8').write(loader)
prep=(OLD/'prepare_pair_from_actual_closed_pair_CPU_once.py').read_text('utf8')
needle=" shutil.copy2(T/'closed_step270_same_phase_production_source_CPU_v1.py',dest/'closed_production_continuation_CPU_v2.py')"
assert needle in prep
prep=prep.replace(needle,needle.replace('closed_step270_same_phase_production_source_CPU_v1.py','closed_step270_known_task_term_classifier_source_CPU_v1.py'))
needle="   proofname='CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json'"
extra="""   repair=read(T/'reports/H1_ARENA_KNOWN_ORDINARY_TERM_HEALTH_CLASSIFIER_CPU_ACTUAL.json')
   assert repair['passed_known_task_term_CPU_classification']
   early=read(P/'reports/H1_EARLY_COMPLETE_FINAL_AND_STOP_REASON_ACTUAL.json')
   healthrows=[json.loads(text) for name,text in early['actual_early_H1_complete_texts'].items() if name.endswith('CLOCK_TRAINING_HEALTH.json')]
   assert len(healthrows)==1;health=healthrows[0]
   assert health['unknown_task_reset_events']==health['termination_events_by_reason']['h1_step270_arena_exit']==1 and health['integrity_task_reset_events']==0 and not health['nonfinite_observed'] and health['termination_reason_coverage_exact'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']==1344
   recorded=json.loads(early['actual_early_H1_complete_texts']['job0/production/FINAL.json'])['final'];assert recorded['SHA']==final['SHA'] and not recorded['failed_partial_prefix']
   shutil.copy2(T/'health_classifier_candidate_V1_UNINSTALLED/clock_training_health.py',dest/repair['relative'])
   (dest/'H1_KNOWN_ORDINARY_TASK_TERM_CLASSIFIER_CPU_ACTUAL.json').write_text(json.dumps(repair,indent=2),encoding='utf8')
   source_stop=dict(actual_original_health=health,only_original_unknown_is_known_arena_exit=True,original_health_relabelled_pass=False,source_checkpoint_complete_final_finite_CPU_independent=proof['models']['h1'],original_actual_cost_unchanged=True,new_known_label_only_ordinary_in_new_unused_worker=True)
   (dest/'H1_KNOWN_TASK_TERM_SOURCE_STOP_ACTUAL.json').write_text(json.dumps(source_stop,indent=2),encoding='utf8')
"""
assert prep.count(needle)==1;prep=prep.replace(needle,extra+needle);ast.parse(prep)
(N/'prepare_pair_from_actual_closed_pair_known_term_CPU_once.py').write_text(prep,encoding='utf8')
for name in ('deploy_pair_new_original_writer_bounded_once.py','collect_pair_first_actual_GO_positive_PPO_once.py','collect_pair_complete_finals_original_cost_bounded_once.py','review_pair_complete_models_original_cost_CPU_once.py'):
 shutil.copy2(OLD/name,N/name);ast.parse((N/name).read_text('utf8'))
v=dict(epoch=time.time(),future_workflow_source_AST_only=True,no_future_models_prepared_remote_Task_or_GO=True,requires_current_pair_actual_both_complete_FINAL_wholeCPU_original_cost_allout=True,H1_early_FINAL14_Adam675020_producer_only_until_wholeCPU=True,original_health_unknown1_stop_not_relabelled_pass=True,only_changed_runtime_file_health_ordinary_term_name_exact_AST=True,all_other_unknown_mimic_nonfinite_guards_retained=True,new_runtime_file_old_SHA='565f7b4549dc0c8fcb2875a5ba48fd5d1bcf5df7cac3929984cf39ee15ceb482',new_runtime_file_SHA='853b4050a9a8c98925f8e80e56ee2d847fcd288f92dda8f99bf49bfdbf82c46e',new_source_loader=H(T/'closed_step270_known_task_term_classifier_source_CPU_v1.py'),controllers_byteexact=all(H(p)==H(P/'controllers'/p.name) for p in (N/'controllers').glob('*.py')),supersedes_unused_pair4_without_classification_fix=True,no_current_worker_owner_hotpatch=True,no_repeated_GPU_native_or_query=True)
with (R/'PAIR_V5_KNOWN_TASK_TERM_CLASSIFIER_UNUSED_WORKFLOW_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
