from pathlib import Path
import ast,hashlib,json,time,tomllib
R=Path(__file__).resolve().parent;T=R.parent.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
a=json.loads((R/'CLOSED63_BUDGET_BOUNDARY_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes());v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert v['prompt']==a['prompt'] and v['status']==a['status'] and v['rrule']==a['rrule'] and v['target_thread_id']==a['targetThreadId']
assert a['prompt'].startswith('CURRENT_CLEARANCE_V4_CLOSED63_ORIGINAL_BUDGET_BOUNDARY_NO64_GO ')
assert '边界未变静默DONT_NOTIFY' in a['prompt'] and '不自动追加第九次' in a['prompt'] and '不是远端deployer已运行后拒绝' in a['prompt']
assert '只有64actualGO/PPO后才能预留65' in a['prompt'] and 'source_only' not in a['prompt']
helper=C/'append_current_clearance_v4_closed63_budget_boundary_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index' in s and 'read_capture_index(p,G)' in s
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED63_114_76_ORIGINAL_BUDGET_BOUNDARY_NO64_GO_WORK_ORDER.json';work=json.loads((T/'reports'/name).read_bytes());assert name in s
assert work['original_budget_boundary']['remaining_at_actual_closed63_canonical_snapshot']<work['original_budget_boundary']['original_required_strictly_greater_than_seconds']
cfg=json.loads((C/'reports/CURRENT_CLEARANCE_V4_CLOSED63_BUDGET_BOUNDARY_ORDINARY_CONFIG.json').read_bytes());assert cfg['destination']=='current_clearance_v4_closed63_budget_boundary_20261024'
assert not (C/'reports/append_current_clearance_v4_closed63_budget_boundary_ordinary_once_STARTED_ACTUAL.json').exists()
F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_20261024';assert not any((F/x).exists() for x in ('payloads','controllers','current_pair_closed_models','reports/PAIR_DEPLOY_STARTED_ACTUAL.json','reports/NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json'))
assert not (T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024').exists()
report=dict(epoch=time.time(),passed=True,actual_monitor_readback=True,prompt_exact=True,ACTIVE=True,hourly=True,original_target=v['target_thread_id'],ordinary_AST=True,ordinary_config=cfg,part_aware_complete_capture_index=True,work_order=name,source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),original_budget_guard_preserved=True,no64_GO_no65_source=True,no_training_host_query_or_binary_rehash=True)
with (R/'CLOSED63_BUDGET_BOUNDARY_MONITOR_READBACK_AND_ORDINARY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
