from pathlib import Path
import ast,json,time
T=Path(__file__).resolve().parent;P=T/'H1_STEP270_E3_PAIR_V7_20261022';OLD=T/'E3_bridge_continuation_V7';B=T/'E3_bridge_continuation_V8'
assert not B.exists();(B/'reports').mkdir(parents=True)
q=json.loads((P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
cfg=dict(epoch=time.time(),sequence=8,cohort_id='H1_COMMAND_AUDIT_REPAIR_RECOVERY_BRIDGE_20261022_V8',previous_stage_dir=str(P),previous_actual_run_id=q['run_id'],previous_actual_owner=q['owner_identity'],roots=dict(recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1s270_E3bridge_2210v8/recovery'),owner_root='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2210v8/owner',original_writer_and_budget_only=True,H1_failed_not_admitted=True)
with (B/'NEXT_COHORT_RESERVED_SOURCE_CONFIG_NO_TOKEN.json').open('x',encoding='utf8') as f:json.dump(cfg,f,indent=2)
for p in OLD.glob('*.py'):
    if p.name.startswith(('prepare_actual_','review_bridge7_')):continue
    s=p.read_text('utf8')
    if p.name=='deploy_actual_recovery_bridge_original_writer_once.py':
        needle='/mnt/mod4_linux_durable_20261013/H1step270_joint_2110v1/owner';assert s.count(needle)==1;s=s.replace(needle,q['owner_root'])
    ast.parse(s);(B/p.name).open('x',encoding='utf8').write(s)
s=(OLD/'prepare_actual_recovery_bridge7_from_closed_pair_E3_CPU_once.py').read_text('utf8');ast.parse(s);(B/'prepare_actual_recovery_bridge8_from_closed_pair7_E3_CPU_once.py').open('x',encoding='utf8').write(s)
s=(OLD/'review_bridge7_contract_nested_AST_CPU_once.py').read_text('utf8');s=s.replace("P=B.parent/'E3_bridge_continuation_V5'","P=B.parent/'E3_bridge_continuation_V7'");ast.parse(s);(B/'review_bridge8_contract_nested_AST_CPU_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(new_unused_workflow=str(B),current_pair7_h1_failed_not_a_source=True,no_remote_Task_or_GO=True)))
