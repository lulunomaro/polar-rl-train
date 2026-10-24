from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent
p=R/'prepare_closed57_pair58_future59_handoff_once.py';s=p.read_text('utf8')
edits={
 'CN,AN,FN=57,58,59':'CN,AN,FN=58,59,60',
 "storage_name='CLOSED57_OLD55_56_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'":"storage_name='CLOSED58_OLD56_57_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'",
 "archive_old=C/'append_current_clearance_v4_closed56_pair57_ordinary_once.py'":"archive_old=C/'append_current_clearance_v4_closed57_pair58_ordinary_once.py'",
 "base=='a39640f55e0207347573629a09e3947d3434ac7e'":"base=='f92d66697faf8d508650b9b71c1670d387bb348e'",
 "R/'ACTUAL57_SAME_REWARD_PAIRED_LATEST56_SOURCE_PPO_AND_WARNING_ACTUAL.json'":"R/'ACTUAL58_SAME_REWARD_PAIRED_LATEST57_SOURCE_PPO_AND_WARNING_ACTUAL.json'",
 'old55_56_minimal_relocation=storage':'old56_57_minimal_relocation=storage',
 "R/'CLOSED57_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'":"R/'CLOSED58_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'",
 'verified old55/56 NPZ':'verified old56/57 NPZ',
 '本窗0/116/117与配套仍210':"本窗{J(health['retention']['retained_indices'])}与配套仍210",
 '/4份安全转存/':'/5份安全转存/',
}
for a,b in edits.items():assert a in s,a;s=s.replace(a,b)
a=s.index(" oldname='NEXT_ACTUAL");b=s.index(' pattern=re.compile(',a)
s=s[:a]+''' oldname='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED57_118_76_OLD55_56_PEER_PAIR58_BOTH_PPO_WORK_ORDER.json';oldkind='V4_closed57_118_76PPO_old55_56_peer_pair58_bothPPO'
 replacements={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V57_20261024':P.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V58_20261024':N.name,oldname:name,oldkind:f'V4_closed{CN}_{h["updates"]}_{e["updates"]}PPO_old56_57_peer_pair{AN}_bothPPO'}
 for key in replacements:assert key in archive,key
'''+s[b:]
s=s.replace('}_OLD55_56_PEER_PAIR{AN}','}_OLD56_57_PEER_PAIR{AN}')
s=s.replace('新unused missing-only旧55 paired与旧56 paired','新unused missing-only旧56 paired与旧57 paired')
a=s.index('旧55三0/112/113现72');b=s.index('所有preupdate/PT/FINAL/source/error/log保留',a)
s=s[:a]+'''旧56剩余116/117现72 PEER_TLS_CLOSED58_OLD56_MINIMAL_V4，0在前批CLOSED57_OLD56，故56三全72分目录；旧57三0/116/117现72 PEER_TLS_CLOSED58_OLD57_MINIMAL_V4。本窗58三0/117/118仍210。旧55三在CLOSED57_OLD55；旧54三在CLOSED56_OLD54；旧53三分CLOSED55_OLD53的0/113与CLOSED56_OLD53的112。52三在CLOSED55_OLD52；51三在CLOSED54_OLD51；42三分CLOSED53_OLD42与CLOSED54_OLD42；47三分原0与CLOSED53_OLD47；43/45/49/48/46/44三已72按receipt分目录；26三、39仅117/118、36仅113/114仍210，各0已72。41/28/32/35/31/29/27三72、30一份72其余按receipt，old11累计107全部consume不盲选。'''+s[b:]
s=s.replace('B/same_authorized_session_compressed_transport_v31.py','B/same_authorized_session_compressed_transport_v32.py').replace('v31仅在v30新增relocate_missing_closed55_56_after_closed57_TLS_V4_once.py','v32仅在v31新增relocate_missing_closed56_57_after_closed58_TLS_V4_once.py')
ast.parse(s)
assert 'CN,AN,FN=58,59,60' in s and '}_OLD56_57_PEER_PAIR{AN}' in s
assert "archive_old=C/'append_current_clearance_v4_closed57_pair58_ordinary_once.py'" in s
assert "storage_name='CLOSED58_OLD56_57_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'" in s
assert 'actual{FN}GO/PPO' in s and 'previousowner={AN}PAIR' in s and "本窗{J(health['retention']['retained_indices'])}" in s
q=R/'prepare_closed58_pair59_future60_handoff_once.py';assert not q.exists();q.write_text(s,'utf8')
with (R/'CLOSED58_HANDOFF_GENERATED_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_executed_yet=True,source=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_source=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),closed58_current59_future60_storage56_57_prior_archive57_58=True,current_retained_indices_from_actual_health=True,all_old_sources_preserved=True,no_host_query_or_training_mutation=True),f,indent=2)
print(q)
