from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;T=R.parent.parent
p=R/'prepare_closed56_pair57_future58_handoff_once.py';s=p.read_text('utf8')
edits={
 'CN,AN,FN=56,57,58':'CN,AN,FN=57,58,59',
 "storage_name='CLOSED56_OLD54_53_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'":"storage_name='CLOSED57_OLD55_56_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'",
 "archive_old=C/'append_current_clearance_v4_closed55_pair56_ordinary_once.py'":"archive_old=C/'append_current_clearance_v4_closed56_pair57_ordinary_once.py'",
 "base=='c641dd78cb0113bf4d7e127aef59aca2254dc840'":"base=='a39640f55e0207347573629a09e3947d3434ac7e'",
 "R/'ACTUAL56_SAME_REWARD_PAIRED_LATEST55_SOURCE_PPO_AND_WARNING_ACTUAL.json'":"R/'ACTUAL57_SAME_REWARD_PAIRED_LATEST56_SOURCE_PPO_AND_WARNING_ACTUAL.json'",
 'old54_53_minimal_relocation=storage':'old55_56_minimal_relocation=storage',
 "R/'CLOSED56_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'":"R/'CLOSED57_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'",
 'verified old54/53 NPZ':'verified old55/56 NPZ',
}
for a,b in edits.items():assert a in s,a;s=s.replace(a,b)
# Regenerate only the archive predecessor block, with exact actual source IDs.
a=s.index(" oldname='NEXT_ACTUAL");b=s.index(' pattern=re.compile(',a)
s=s[:a]+''' oldname='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED56_118_76_OLD54_53_PEER_PAIR57_BOTH_PPO_WORK_ORDER.json';oldkind='V4_closed56_118_76PPO_old54_53_peer_pair57_bothPPO'
 replacements={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024':P.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V57_20261024':N.name,oldname:name,oldkind:f'V4_closed{CN}_{h["updates"]}_{e["updates"]}PPO_old55_56_peer_pair{AN}_bothPPO'}
 for key in replacements:assert key in archive,key
'''+s[b:]
# Current stage names and prompt use the selected storage pair; the archive oldname above stays historical.
s=s.replace('}_OLD54_53_PEER_PAIR{AN}','}_OLD55_56_PEER_PAIR{AN}')
s=s.replace('新unused missing-only旧54 paired与旧53 paired','新unused missing-only旧55 paired与旧56 paired')
a=s.index('旧54三0/116/117现72');b=s.index('所有preupdate/PT/FINAL/source/error/log保留',a)
s=s[:a]+'''旧55三0/112/113现72 PEER_TLS_CLOSED57_OLD55_MINIMAL_V4；旧56仅0现72 PEER_TLS_CLOSED57_OLD56_MINIMAL_V4，116/117仍210。本窗57三0/116/117仍210。旧54三0/116/117在CLOSED56_OLD54；旧53三分CLOSED55_OLD53的0/113与CLOSED56_OLD53的112。52三在CLOSED55_OLD52；51三在CLOSED54_OLD51；42三分CLOSED53_OLD42与CLOSED54_OLD42；47三分原0与CLOSED53_OLD47；43/45/49/48/46/44三已72按receipt分目录；26三、39仅117/118、36仅113/114仍210，各0已72。41/28/32/35/31/29/27三72、30一份72其余按receipt，old11累计107全部consume不盲选。'''+s[b:]
s=s.replace('B/same_authorized_session_compressed_transport_v30.py','B/same_authorized_session_compressed_transport_v31.py')
s=s.replace('v30仅在v29新增relocate_missing_closed54_53_after_closed56_TLS_V4_once.py','v31仅在v30新增relocate_missing_closed55_56_after_closed57_TLS_V4_once.py')
tree=ast.parse(s)
assert 'CN,AN,FN=57,58,59' in s and '}_OLD55_56_PEER_PAIR{AN}' in s
assert "archive_old=C/'append_current_clearance_v4_closed56_pair57_ordinary_once.py'" in s
assert "storage_name='CLOSED57_OLD55_56_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'" in s
assert 'actual{FN}GO/PPO' in s and 'previousowner={AN}PAIR' in s
q=R/'prepare_closed57_pair58_future59_handoff_once.py';assert not q.exists();q.write_text(s,'utf8')
with (R/'CLOSED57_HANDOFF_GENERATED_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_executed_yet=True,source=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_source=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),closed57_current58_future59_storage55_56_and_prior_archive56_57=True,all_old_sources_preserved=True,no_host_query_or_training_mutation=True),f,indent=2)
print(q)
