from pathlib import Path
import ast,json,shutil,time
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_PAIR_V1_20261021';OLD=T/'E3_bridge_continuation_V5';B=T/'E3_bridge_continuation_V7'
assert not B.exists();(B/'reports').mkdir(parents=True)
q=json.loads((P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
cfg=dict(epoch=time.time(),sequence=7,cohort_id='H1_QUERY_REPAIR_RECOVERY_BRIDGE_20261022_V7',previous_stage_dir=str(P),previous_actual_run_id=q['run_id'],previous_actual_owner=q['owner_identity'],roots=dict(recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1s270_E3bridge_2210v7/recovery'),owner_root='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2210v7/owner',original_writer_and_budget_only=True,H1_failed_not_admitted=True)
(B/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
for p in OLD.glob('*.py'):
 if p.name.startswith('prepare_actual_') or p.name.startswith('review_bridge5_'):continue
 text=p.read_text('utf8')
 if p.name=='deploy_actual_recovery_bridge_original_writer_once.py':
  text=text.replace('/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2110v4/owner',q['owner_root']).replace("set(co['go'])=={'recovery'}","set(co['go'])=={'h1','recovery'}")
 ast.parse(text);(B/p.name).write_text(text,encoding='utf8')
prep=(OLD/'prepare_actual_recovery_bridge5_from_closed_bridge4_CPU_once.py').read_text('utf8')
prep=prep.replace("shutil.copytree(P/'two_policy50_original_account_controllers',controllers)","shutil.copytree(B.parent/'E3_bridge_continuation_V5/two_policy50_original_account_controllers',controllers)")
ast.parse(prep);(B/'prepare_actual_recovery_bridge7_from_closed_pair_E3_CPU_once.py').write_text(prep,encoding='utf8')
review=(OLD/'review_bridge5_contract_nested_AST_CPU_once.py').read_text('utf8').replace("P=B.parent/'E3_bridge_continuation_V4'","P=B.parent/'E3_bridge_continuation_V5'")
review=review.replace("proof=json.loads((P/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())","proof=json.loads((Path(json.loads((B/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').read_bytes())['previous_stage_dir'])/'reports/TWO50_CURRENT_COHORT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())")
ast.parse(review);(B/'review_bridge7_contract_nested_AST_CPU_once.py').write_text(review,encoding='utf8')
print(json.dumps(dict(prepared_workflow_only=str(B),no_GO=True,failed_H1_not_a_source=True)))
