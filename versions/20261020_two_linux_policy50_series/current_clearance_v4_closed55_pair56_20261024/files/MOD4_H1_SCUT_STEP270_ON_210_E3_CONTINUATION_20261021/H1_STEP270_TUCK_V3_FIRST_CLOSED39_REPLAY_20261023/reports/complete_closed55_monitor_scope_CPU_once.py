from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;O=R.parent;T=O.parent;C=T.parent/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88'
p=R/'CURRENT56_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json';v=json.loads(p.read_bytes())
v['prompt']+='\n本轮55本机handoff原草稿未执行，源码AST审查发现仅阶段说明标签残留并独立修正，checkedV2首次实际成功。CLOSED55_UNUSED_HANDOFF_SOURCE_AST_ACTUAL及CLOSED55_UNUSED_HANDOFF_LABEL_REVIEW_V2_AST_ACTUAL、原草稿与修正源码均保留同阶段ordinary归档；无hostquery/训练错误/费用变动，不重旧builder。prepare_closed55_pair56_future57_handoff_checked_V2_once.py现consume，不重helper/record/tag。\n'
assert v['prompt'].startswith('CURRENT_CLEARANCE_V4_CLOSED55_OLD52_53_PEER_PAIR56 ')
assert 'gateBJT=2026-10-24T08:26:37.063234+08:00' in v['prompt']
assert 'previousowner=56PAIR_ORIGINAL_ACCOUNT_DETACHED' in v['prompt']
assert '未两完整不跑57bothFINAL正常入口' in v['prompt']
assert '未选H1only56helper不运行' in v['prompt']
assert '当前56/future57 collector整字节继承55已执行版' in v['prompt']
assert '只actual57GO/PPO后后继reserved' in v['prompt']
assert v['targetThreadId']=='01a07a2d-9036-7531-a012-692df9f56353' and v['status']=='ACTIVE'
helper=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py';s=helper.read_text('utf8');ast.parse(s)
assert 'from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index' in s
name='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED55_114_75_OLD52_53_PEER_PAIR56_BOTH_PPO_WORK_ORDER.json'
assert name in s and (T/'reports'/name).is_file()
future=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V57_20261024'
assert not any((future/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
dest=R/'CURRENT56_WITH_UNUSED_DRAFT_SCOPE_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json';assert not dest.exists()
with dest.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
with (R/'CURRENT56_MONITOR_SOURCE_AND_ORDINARY_AST_PRETOOL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,arguments=str(dest),arguments_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),ordinary_helper=str(helper),ordinary_AST=True,part_aware_capture_index_reader=True,work_order=name,future_source_only=True,no_host_query_or_new_training=True),f,indent=2)
print(json.dumps(dict(passed=True,arguments=str(dest),future_source_only=True)))
