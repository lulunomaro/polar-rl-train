from pathlib import Path
import ast,hashlib,json,time,tomllib
R=Path(__file__).resolve().parent;T=R.parent.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
a=json.loads((R/'CURRENT56_WITH_UNUSED_DRAFT_SCOPE_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes())
p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');v=tomllib.loads(p.read_text('utf8'))
assert v['prompt']==a['prompt'] and v['status']==a['status'] and v['rrule']==a['rrule']
target=v.get('target_thread_id',v.get('targetThreadId'));assert target==a['targetThreadId'],list(v)
helper=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'read_capture_index(p,G)' in s and 'write_capture_index' in s
assert 'RESOURCE_V55_20261024' in s and 'RESOURCE_V56_20261024' in s
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED55_114_75_OLD52_53_PEER_PAIR56_BOTH_PPO_WORK_ORDER.json';assert name in s
cfg=json.loads((C/'reports/CURRENT_CLEARANCE_V4_CLOSED55_PAIR56_ORDINARY_CONFIG.json').read_bytes())
assert cfg['destination']=='current_clearance_v4_closed55_pair56_20261024' and cfg['title']=='Archive closed55 complete models, verified old52/53 NPZ relocation and paired56'
assert not (C/'reports/append_current_clearance_v4_closed55_pair56_ordinary_once_STARTED_ACTUAL.json').exists()
report=dict(epoch=time.time(),passed=True,actual_monitor_readback=True,prompt_exact=True,ACTIVE=True,hourly=True,original_target=target,ordinary_AST=True,ordinary_config=cfg,part_aware_complete_capture_index=True,work_order=name,source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),no_training_host_query_or_binary_rehash=True)
with (R/'CURRENT56_MONITOR_EXACT_READBACK_AND_ORDINARY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
