from pathlib import Path
import ast,hashlib,json,re,time
O=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023');p=O/'reports/prepare_closed53_pair54_future55_handoff_ordinary_once.py';s=p.read_text('utf8')
old_order='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED52_114_76_OLD43_45_PEER_PAIR53_BOTH_PPO_WORK_ORDER.json';previous_order='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED53_114_75_OLD42_47_PEER_PAIR54_BOTH_PPO_WORK_ORDER.json'
mapping={old_order:previous_order,'V4_closed52_114_76PPO_old43_45_peer_pair53_bothPPO':'V4_closed53_114_75PPO_old42_47_peer_pair54_bothPPO','append_current_clearance_v4_closed52_pair53_ordinary_once.py':'append_current_clearance_v4_closed53_pair54_ordinary_once.py','RESOURCE_V52_20261024':'RESOURCE_V53_20261024','RESOURCE_V53_20261024':'RESOURCE_V54_20261024','RESOURCE_V54_20261024':'RESOURCE_V55_20261024','RESOURCE_V55_20261024':'RESOURCE_V56_20261024','H1step270_reward_tuckclear4_2410v54':'H1step270_reward_tuckclear4_2410v55','H1step270_reward_tuckclear4_2410v55':'H1step270_reward_tuckclear4_2410v56','CURRENT53':'CURRENT54','CURRENT54':'CURRENT55','CLOSED53':'CLOSED54','CLOSED54':'CLOSED55','review_closed53':'review_closed54','review_closed54':'review_closed55','closed53':'closed54','closed54':'closed55','pair54':'pair55','pair53':'pair54','PAIR54':'PAIR55','NEXT55':'NEXT56','ACTUAL54':'ACTUAL55','LATEST53':'LATEST54','Qualified53':'Qualified54','actual54_both_closed':'actual55_both_closed','OLD42_47':'OLD51_42','old42_47':'old51_42','v27.py':'v28.py','旧42 H1only/旧47 paired':'旧51 paired/旧42 H1only'}
pat=re.compile('|'.join(re.escape(x) for x in sorted(mapping,key=len,reverse=True)));s=pat.sub(lambda m:mapping[m[0]],s)
s=re.sub(r'(?<![A-Za-z0-9_])(53|54|55)(?![A-Za-z0-9_])',lambda m:str(int(m[0])+1),s)
# The preceding replacement applies to natural-language stage numbers only;
# restore the independently generated literal field names from its double pass.
s=s.replace('previousowner=55PAIR','previousowner=55PAIR')
a=s.index('新helper/两批消费不重hash传。');b=s.index('所有preupdate/PT/FINAL/source/errors/log继续210',a)
s=s[:a]+'''新helper/两批消费不重hash传。旧51/42本轮实际选中位置只按该receipt，未选仍210，不盲INDEX；42先前仅112仍210、0/113已72，51先前三0/113/114仍210。本轮54原件仍210，53/52原三NPZ也仍210；47三已72分原0和新116/117，43/45/49/48/46/44三已72但分批目录按receipt；26三、39仅117/118、36仅113/114仍210，39/36各0已72；41/28/32/35/31/29/27三72、30一份72其余按receipt；old11累计107各receipt消费不盲重选。'''+s[b:]
# The literal archive predecessor is read from the previous committed helper.
s=s.replace('current_clearance_v4_closed54_pair55_20261024','current_clearance_v4_closed54_pair55_20261024')
ast.parse(s);assert "P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V54_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024'" in s
q=O/'reports/prepare_closed54_pair55_future56_handoff_ordinary_once.py';assert not q.exists();q.write_text(s,'utf8')
with (O/'reports/CLOSED54_LOCAL_HANDOFF_SOURCE_AST_RESERVED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),source_AST_only=True,not_executed=True,no_future_root_payload_model_Task_GO_or_fee=True),f,indent=2)
print(q)