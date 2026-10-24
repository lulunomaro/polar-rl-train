from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent
p=R/'prepare_closed60_pair61_future62_handoff_once.py';s=p.read_text('utf8')
edits={
 'CN,AN,FN=60,61,62':'CN,AN,FN=61,62,63',
 "storage_name='CLOSED60_OLD59_39_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'":"storage_name='CLOSED61_OLD60_36_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'",
 "archive_old=C/'append_current_clearance_v4_closed59_pair60_ordinary_once.py'":"archive_old=C/'append_current_clearance_v4_closed60_pair61_ordinary_once.py'",
 "base=='d5d8efe7ead17e18b2267a5a49e71d0087f5125c'":"base=='8f3b74ea6786d21c19f9feca4e42b40c35ddbd97'",
 "R/'ACTUAL60_SAME_REWARD_PAIRED_LATEST59_SOURCE_PPO_AND_WARNING_ACTUAL.json'":"R/'ACTUAL61_SAME_REWARD_PAIRED_LATEST60_SOURCE_PPO_AND_WARNING_ACTUAL.json'",
 'old59_39_minimal_relocation=storage':'old60_36_minimal_relocation=storage',
 "R/'CLOSED60_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'":"R/'CLOSED61_HANDOFF_SOURCE_AST_AND_SCOPE_ACTUAL.json'",
 'verified old59/39 NPZ':'verified old60/36 NPZ',
 '/4份安全转存/':'/5份安全转存/',
}
for a,b in edits.items():assert a in s,a;s=s.replace(a,b)
a=s.index(" oldname='NEXT_ACTUAL");b=s.index(' pattern=re.compile(',a)
s=s[:a]+''' oldname='NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED60_114_75_OLD59_39_PEER_PAIR61_BOTH_PPO_WORK_ORDER.json';oldkind='V4_closed60_114_75PPO_old59_39_peer_pair61_bothPPO'
 replacements={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V60_20261024':P.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024':N.name,oldname:name,oldkind:f'V4_closed{CN}_{h["updates"]}_{e["updates"]}PPO_old60_36_peer_pair{AN}_bothPPO'}
 for key in replacements:assert key in archive,key
'''+s[b:]
s=s.replace('}_OLD59_39_PEER_PAIR{AN}','}_OLD60_36_PEER_PAIR{AN}')
s=s.replace('新unused missing-only旧59 paired与旧39 paired','新unused missing-only旧60 paired与旧36 paired')
a=s.index('旧59三0/116/117现72');b=s.index('所有preupdate/PT/FINAL/source/error/log保留',a)
s=s[:a]+'''旧60三0/112/113现72 PEER_TLS_CLOSED61_OLD60_MINIMAL_V4；旧36最后113/114现72 PEER_TLS_CLOSED61_OLD36_MINIMAL_V4，0在更早已迁目录，故36三全72分目录。本窗61三0/112/113仍210。旧59三在CLOSED60_OLD59；旧39的118在CLOSED60_OLD39，117在CLOSED59_OLD39，0在更早已迁目录，故39三全72分目录。旧58三在CLOSED59_OLD58；旧57三在CLOSED58_OLD57；旧56三分CLOSED57_OLD56的0与CLOSED58_OLD56的116/117；旧55三在CLOSED57_OLD55；旧54三在CLOSED56_OLD54；旧53三分CLOSED55_OLD53的0/113与CLOSED56_OLD53的112。52三在CLOSED55_OLD52；51三在CLOSED54_OLD51；42三分CLOSED53_OLD42与CLOSED54_OLD42；47三分原0与CLOSED53_OLD47；43/45/49/48/46/44三已72按receipt分目录；26三仍210。41/28/32/35/31/29/27三72、30一份72其余按receipt，old11累计107全部consume不盲选。'''+s[b:]
s=s.replace('B/same_authorized_session_compressed_transport_v34.py','B/same_authorized_session_compressed_transport_v35.py').replace('v34仅在v33新增relocate_missing_closed59_39_after_closed60_TLS_V4_once.py','v35仅在v34新增relocate_missing_closed60_36_after_closed61_TLS_V4_once.py')
oldnote='首次本机模板读取省略old59_39部分文件名导致Get-Content路径不存在，原命令/工具stderr与rg定位后成功更正均保留CLOSED60_LOCAL_TEMPLATE_FILENAME_READER_ORIGINAL_ERROR_ACTUAL；仅本机读者错误，无hostquery/训练变化/费用改写，不重旧helper。'
assert oldnote in s;s=s.replace(oldnote,'旧60本机模板文件名错误及postGit资产索引schema误断的原错/更正均consume，不重旧读者/补档；本轮无新读者错误。')
ast.parse(s)
assert 'CN,AN,FN=61,62,63' in s and '}_OLD60_36_PEER_PAIR{AN}' in s
assert "archive_old=C/'append_current_clearance_v4_closed60_pair61_ordinary_once.py'" in s
assert "storage_name='CLOSED61_OLD60_36_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json'" in s
assert 'actual{FN}GO/PPO' in s and 'previousowner={AN}PAIR' in s and "本窗{J(health['retention']['retained_indices'])}" in s
q=R/'prepare_closed61_pair62_future63_handoff_once.py';assert not q.exists();q.write_text(s,'utf8')
with (R/'CLOSED61_HANDOFF_GENERATED_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,not_executed_yet=True,source=str(p),source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_source=str(q),SHA=hashlib.sha256(q.read_bytes()).hexdigest(),closed61_current62_future63_storage60_36_prior_archive60_61=True,current_retained_indices_from_actual_health=True,old36_storage_only_not_checkpoint_fallback=True,all_old_sources_preserved=True,no_host_query_payload_GO_or_training_mutation=True,no_successor_reserved_before_current_actual_GO_PPO=True),f,indent=2)
print(q)
