from pathlib import Path
import ast,hashlib,json,time,tomllib
R=Path(__file__).resolve().parent;T=R.parent.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
a=json.loads((R/'CURRENT60_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes());v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert v['prompt']==a['prompt'] and v['status']==a['status'] and v['rrule']==a['rrule'] and v['target_thread_id']==a['targetThreadId']
assert a['prompt'].startswith('CURRENT_CLEARANCE_V4_CLOSED59_OLD58_39_PEER_PAIR60 ')
assert 'gateBJT=2026-10-24T12:49:46.234415+08:00' in a['prompt'] and 'previousowner=60PAIR_ORIGINAL_ACCOUNT_DETACHED' in a['prompt']
assert '未两完整不跑61bothFINAL正常入口' in a['prompt'] and '未选H1only60helper禁止运行' in a['prompt']
assert '只actual61GO/PPO后后继reserved' in a['prompt'] and 'E3仍latestqualified60' in a['prompt']
helper=C/'append_current_clearance_v4_closed59_pair60_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index' in s and 'read_capture_index(p,G)' in s
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED59_118_75_OLD58_39_PEER_PAIR60_BOTH_PPO_WORK_ORDER.json';assert name in s and (T/'reports'/name).is_file()
cfg=json.loads((C/'reports/CURRENT_CLEARANCE_V4_CLOSED59_PAIR60_ORDINARY_CONFIG.json').read_bytes())
assert cfg['destination']=='current_clearance_v4_closed59_pair60_20261024' and cfg['title']=='Archive closed59 complete models, verified old58/39 NPZ relocation and paired60'
assert not (C/'reports/append_current_clearance_v4_closed59_pair60_ordinary_once_STARTED_ACTUAL.json').exists()
F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024';assert not any((F/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
report=dict(epoch=time.time(),passed=True,actual_monitor_readback=True,prompt_exact=True,ACTIVE=True,hourly=True,original_target=v['target_thread_id'],ordinary_AST=True,ordinary_config=cfg,part_aware_complete_capture_index=True,work_order=name,source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),future_source_only=True,no_training_host_query_or_binary_rehash=True)
with (R/'CURRENT60_MONITOR_EXACT_READBACK_AND_ORDINARY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
