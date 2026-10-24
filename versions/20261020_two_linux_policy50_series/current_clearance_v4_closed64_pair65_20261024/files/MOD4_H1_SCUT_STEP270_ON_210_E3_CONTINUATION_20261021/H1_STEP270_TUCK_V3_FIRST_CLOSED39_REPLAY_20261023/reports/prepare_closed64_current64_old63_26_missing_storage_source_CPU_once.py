from pathlib import Path
import ast,hashlib,json,time
O=Path(__file__).resolve().parent.parent;T=O.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_NINTH_V2_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
payload=Path(read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1']);known=sum(x['bytes'] for x in read(payload/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']);plan=known+16*1024**2
src=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V62_20261024/relocate_missing_closed61_26_after_closed62_TLS_V4_once.py';s=src.read_text('utf8')
tree=ast.parse(s);node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));inv=ast.literal_eval(node.value)
inv=inv.replace("==1548000 and len(c['budget_extensions'])==8","==2268000 and len(c['budget_extensions'])==9")
needle="for row in selected:\n h=hashlib.sha256()"
assert inv.count(needle)==1
inv=inv.replace(needle,"cache={r['path']:r for r in v['sha_cache']}\nfor row in selected:\n old=cache.get(row['path'])\n if old and all(old[k]==row[k] for k in ('bytes','SHA','mtime_ns','inode')):continue\n h=hashlib.sha256()")
lines=s.splitlines(keepends=True);lines[node.lineno-1:node.end_lineno]=['INVENTORY='+repr(inv)+'\n'];s=''.join(lines)
changes={
 "P=T/'forensic_tls_peer_transfer_V96_V4.py'":"P=T/'forensic_tls_peer_transfer_V96_V5_NINTH.py'",
 "d=ops.d\n":"d=ops.d\nops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','forensic_tls_peer_transfer_V96_V5_NINTH.py')\n",
 "stages=[T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023']":"stages=[N,T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023']",
 "31e6c729fad4c7e73e60843535f602f95ab0eec0b18f2cc24262d1167840dcd7":"786064012058a6fb642da821e6fab0c625e6c9077373482fe857a5251fb69545",
 'CLOSED62_OLD61_26':'CLOSED64_CURRENT64_OLD63_26',
 'known_H1_manifest_bytes=63469826':f'known_H1_manifest_bytes={known}',
 'install_copy_planning_bytes=80247042':f'install_copy_planning_bytes={plan}',
 "m=importlib.util.spec_from_file_location('memory'":"cache=read(R/'PEER_FORENSICS_FRESH_SOURCE_ACTUAL.json')\n m=importlib.util.spec_from_file_location('memory'",
 "dict(sources=sources,current_owner_root=":"dict(sha_cache=cache['files'],sources=sources,current_owner_root=",
 "label='CLOSED62_OLD'+('61' if batch==0 else '26')+'_MINIMAL'":"label=['CLOSED64_CURRENT64_MINIMAL','CLOSED64_OLD63_MINIMAL','CLOSED64_OLD26_MINIMAL'][batch]",
}
for old,new in changes.items():
 assert old in s,old
 s=s.replace(old,new)
ast.parse(s);ast.parse(inv)
assert '720000' not in s and '1548000' not in s and "len(c['budget_extensions'])==9" in inv
dest=N/'relocate_missing_current64_old63_26_after_closed64_TLS_V5_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v43.py';w=old.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";assert w.count(needle)==1;w=w.replace(needle,needle+"\n        '"+dest.name+"',");ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v44.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),known_H1_manifest_bytes=known,install_copy_planning_bytes=plan,copy_planning_not_new_training_gate=True,sources=['closed64 current retained0/112/113','closed63 only112/113 still210','closed26 only currently remaining NPZ;0/118 moved'],storage_only_not_checkpoint_fallback_or_motion_replay=True,fresh_joint_capacity_allout_locks_producer_stat_before_selected_hash=True,reuse_current64_hash_only_if_fresh_path_size_SHA_mtime_inode_match=True,unselected_stat_only=True,TLS_protocol_reused_without_retest=True,ninth_2268000_and_9_without_first_grant_compensation=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED64_UNUSED_CURRENT64_OLD63_26_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=plan,source_AST=True)))
