from pathlib import Path
import ast,hashlib,json,re,time
O=Path(__file__).resolve().parent.parent;T=O.parent;R=O/'reports'
old=R/'prepare_closed54_pair55_future56_handoff_checked_V3_once.py'
s=old.read_text('utf8')
# Simultaneous substitutions keep original and successor identities distinct.
mapping={
 'RESOURCE_V54_20261024':'RESOURCE_V55_20261024',
 'RESOURCE_V55_20261024':'RESOURCE_V56_20261024',
 'RESOURCE_V56_20261024':'RESOURCE_V57_20261024',
 'H1step270_reward_tuckclear4_2410v55':'H1step270_reward_tuckclear4_2410v56',
 'H1step270_reward_tuckclear4_2410v56':'H1step270_reward_tuckclear4_2410v57',
 'CURRENT54':'CURRENT55','CURRENT55':'CURRENT56',
 'CLOSED54':'CLOSED55','CLOSED55':'CLOSED56',
 'review_closed54':'review_closed55','review_closed55':'review_closed56',
 'ACTUAL55':'ACTUAL56','LATEST54':'LATEST55','Qualified54':'Qualified55',
 'NEXT56':'NEXT57','actual55_both_closed':'actual56_both_closed',
 'OLD51_42':'OLD52_53','old51_42':'old52_53',
 'same_authorized_session_compressed_transport_v28.py':'same_authorized_session_compressed_transport_v29.py',
 '旧51 paired/旧42 H1only':'旧52 paired/旧53 paired',
 '53health=':'55health=','53collector完整returned':'55collector完整returned',
}
pat=re.compile('|'.join(re.escape(x) for x in sorted(mapping,key=len,reverse=True)))
s=pat.sub(lambda m:mapping[m[0]],s)
# Natural-language stage numbers are transformed only inside the prompt prefix.
a=s.index(' prefix=f"""');b=s.index('\n"""',a)
part=s[a:b]
part=re.sub(r'(?<![A-Za-z0-9_])(54|55|56)(?![A-Za-z0-9_])',lambda m:str(int(m[0])+1),part)
# The explicit field labels above already identify the closed55 measurements.
part=part.replace('56health=','55health=').replace('56collector完整returned','55collector完整returned')
part=part.replace('actual55_both_closed','actual56_both_closed')
part=part.replace('v27只在v26加本轮old42/47 missingstorage精确basename','v29只在v28加本轮old52/53 missingstorage精确basename')
x=part.index('新helper/两批消费不重hash传。');y=part.index('所有preupdate/PT/FINAL/source/errors/log继续210',x)
part=part[:x]+'''新helper/两批消费不重hash传。52三0/112/113现72 PEER_TLS_CLOSED55_OLD52_MINIMAL_V4；53仅0/113现72 PEER_TLS_CLOSED55_OLD53_MINIMAL_V4，112仍210。本窗55三0/112/113与54三0/116/117仍210。51三已72 CLOSED54_OLD51；42三已72分CLOSED53_OLD42与CLOSED54_OLD42目录；47三已72分原0与CLOSED53_OLD47目录；43/45/49/48/46/44三已72但分批目录按receipt；26三、39仅117/118、36仅113/114仍210，39/36各0已72；41/28/32/35/31/29/27三72、30一份72其余按receipt；old11累计107各receipt消费不盲重选。'''+part[y:]
# Explicit predecessor references must follow the current actual owner.
part=part.replace('previousowner=55PAIR','previousowner=56PAIR')
s=s[:a]+part+s[b:]
# Tail is prose, separate from executable stage names.
s=s.replace('本轮54完整/安全转存/55两首PPO','本轮55完整/安全转存/56两首PPO')
s=s.replace("source=(C/'append_current_clearance_v4_closed53_pair54_ordinary_once.py').read_text('utf8')", "source=(C/'append_current_clearance_v4_closed54_pair55_ordinary_once.py').read_text('utf8')")
# Replace the archive-generation block explicitly, avoiding historical-number edits.
a=s.index(" oldname='NEXT_ACTUAL");b=s.index('\n print(J(',a)
s=s[:a]+''' oldname='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED54_118_74_OLD51_42_PEER_PAIR55_BOTH_PPO_WORK_ORDER.json'
 replacements={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V54_20261024':P.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024':N.name,oldname:name,'V4_closed54_118_74PPO_old51_42_peer_pair55_bothPPO':f"V4_closed55_{h['updates']}_{e['updates']}PPO_old52_53_peer_pair56_bothPPO"};pattern=re.compile('|'.join(re.escape(x) for x in sorted(replacements,key=len,reverse=True)));source=pattern.sub(lambda m:replacements[m[0]],source);ast.parse(source)
 assert 'from capture_index_ordered_parts_v1 import read_capture_index,write_capture_index' in source and name in source
 dest=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py';assert not dest.exists();dest.write_text(source,'utf8');base=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip()
 put(C/'reports/CURRENT_CLEARANCE_V4_CLOSED55_PAIR56_ORDINARY_CONFIG.json',dict(destination='current_clearance_v4_closed55_pair56_20261024',base_HEAD=base,title='Archive closed55 complete models, verified old52/53 NPZ relocation and paired56'))'''+s[b:]
ast.parse(s)
assert "P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V57_20261024'" in s
assert "read(P/'reports/CLOSED55_OLD52_53_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')" in s
assert "CURRENT_CLEARANCE_TUCK_V4_CURRENT55_CLOSED_HEALTH_RETENTION_EPISODE_CPU_ACTUAL.json" in s
assert '55health=' in s and '55collector完整returned' in s
assert 'gateBJT={gate}' in s and 'previousowner=56PAIR' in s
assert 'ACTUAL56_SAME_REWARD_PAIRED_LATEST55_SOURCE_PPO_AND_WARNING_ACTUAL.json' in s
assert 'NEXT57_CURRENT_CLEARANCE_V4_PAIRED_PREDECESSOR_SOURCE_AST_ACTUAL.json' in s
assert 'CURRENT56_FINAL_MONITOR_UPDATE_ARGS_ACTUAL.json' in s
assert "name=f\"NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED55_" in s
dest=R/'prepare_closed55_pair56_future57_handoff_once.py';assert not dest.exists();dest.write_text(s,'utf8')
with (R/'CLOSED55_UNUSED_HANDOFF_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_executed_yet=True,source=str(old),source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),new_source=str(dest),SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),actual_closed55_current56_future57_storage52_53_labels=True,original_historical_source_preserved=True,no_host_query_training_or_budget_write=True),f,indent=2)
print(dest)
