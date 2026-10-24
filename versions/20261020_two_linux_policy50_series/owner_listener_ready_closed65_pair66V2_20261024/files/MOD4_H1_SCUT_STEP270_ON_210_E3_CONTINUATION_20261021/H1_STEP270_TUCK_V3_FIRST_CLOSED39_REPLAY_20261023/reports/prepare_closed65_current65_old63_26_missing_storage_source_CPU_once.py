from pathlib import Path
import ast,hashlib,json,time
O=Path(__file__).resolve().parent.parent;T=O.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_NINTH_V2_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
scope=read(P/'reports/CLOSED64_UNUSED_CURRENT64_OLD63_26_MISSING_STORAGE_SOURCE_AST_ACTUAL.json');src=P/'relocate_missing_current64_old63_26_after_closed64_TLS_V5_once.py';assert H(src)==scope['new_SHA']
payload=Path(read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1']);known=sum(x['bytes'] for x in read(payload/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']);plan=known+16*1024**2
s=src.read_text('utf8');changes={'CLOSED64_CURRENT64_OLD63_26':'CLOSED65_CURRENT65_OLD63_26','CLOSED64_CURRENT64_MINIMAL':'CLOSED65_CURRENT65_MINIMAL','CLOSED64_OLD63_MINIMAL':'CLOSED65_OLD63_MINIMAL','CLOSED64_OLD26_MINIMAL':'CLOSED65_OLD26_MINIMAL',f"known_H1_manifest_bytes={scope['known_H1_manifest_bytes']}":f'known_H1_manifest_bytes={known}',f"install_copy_planning_bytes={scope['install_copy_planning_bytes']}":f'install_copy_planning_bytes={plan}'}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
tree=ast.parse(s);inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));ast.parse(inv)
assert "stages=[N,T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023']" in s and '720000' not in s and '1548000' not in s
dest=N/'relocate_missing_current65_old63_26_after_closed65_TLS_V5_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v44.py';w=old.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";assert w.count(needle)==1;w=w.replace(needle,needle+"\n        '"+dest.name+"',");ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v45.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),known_H1_manifest_bytes=known,install_copy_planning_bytes=plan,copy_planning_not_new_training_gate=True,sources=['closed65 current retained0/116/117','closed63 only112 still210;0/113 already72','closed26 only currently remaining NPZ;0/118 moved'],fresh_joint_capacity_allout_locks_producer_stat_before_selected_hash=True,reuse_current65_hash_only_if_fresh_path_size_SHA_mtime_inode_match=True,unselected_stat_only=True,TLS_protocol_reused_without_retest=True,ninth_2268000_and_9_without_first_grant_compensation=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED65_UNUSED_CURRENT65_OLD63_26_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=plan,source_AST=True)))
