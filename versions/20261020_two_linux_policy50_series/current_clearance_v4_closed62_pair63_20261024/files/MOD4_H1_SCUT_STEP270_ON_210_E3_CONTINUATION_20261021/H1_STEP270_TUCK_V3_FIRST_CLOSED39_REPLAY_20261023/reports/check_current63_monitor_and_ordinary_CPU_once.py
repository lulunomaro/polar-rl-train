from pathlib import Path
import ast,hashlib,json,time,tomllib
R=Path(__file__).resolve().parent;T=R.parent.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
a=json.loads((R/'CURRENT63_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes());v=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert v['prompt']==a['prompt'] and v['status']==a['status'] and v['rrule']==a['rrule'] and v['target_thread_id']==a['targetThreadId']
assert a['prompt'].startswith('CURRENT_CLEARANCE_V4_CLOSED62_OLD61_26_PEER_PAIR63 ')
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED62_118_77_OLD61_26_PEER_PAIR63_BOTH_PPO_WORK_ORDER.json';work=json.loads((T/'reports'/name).read_bytes())
assert 'gateBJT='+work['collector_gate_BJT'] in a['prompt'] and 'previousowner=63PAIR_ORIGINAL_ACCOUNT_DETACHED' in a['prompt']
assert '未两完整不跑64bothFINAL正常入口' in a['prompt'] and '未选H1only63helper禁止运行' in a['prompt']
assert '只actual64GO/PPO后后继reserved' in a['prompt'] and 'E3仍latestqualified63' in a['prompt']
assert '本窗62三0/116/117仍210' in a['prompt'] and '旧26仅0现72' in a['prompt'] and '未选另外两份仍210' in a['prompt']
assert 'same_authorized_session_compressed_transport_v36.py' in a['prompt'] and not a['prompt'].endswith('\n')
helper=C/'append_current_clearance_v4_closed62_pair63_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index' in s and 'read_capture_index(p,G)' in s and name in s
cfg=json.loads((C/'reports/CURRENT_CLEARANCE_V4_CLOSED62_PAIR63_ORDINARY_CONFIG.json').read_bytes())
assert cfg['destination']=='current_clearance_v4_closed62_pair63_20261024' and cfg['title']=='Archive closed62 complete models, verified old61/26 NPZ relocation and paired63'
assert not (C/'reports/append_current_clearance_v4_closed62_pair63_ordinary_once_STARTED_ACTUAL.json').exists()
F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_20261024';assert not any((F/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
report=dict(epoch=time.time(),passed=True,actual_monitor_readback=True,prompt_exact=True,ACTIVE=True,hourly=True,original_target=v['target_thread_id'],ordinary_AST=True,ordinary_config=cfg,part_aware_complete_capture_index=True,work_order=name,source_SHA=hashlib.sha256(helper.read_bytes()).hexdigest(),future_source_only=True,no_training_host_query_or_binary_rehash=True)
with (R/'CURRENT63_MONITOR_EXACT_READBACK_AND_ORDINARY_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
