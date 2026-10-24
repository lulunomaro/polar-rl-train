from pathlib import Path
import ast,hashlib,json,re,time
O=Path(__file__).resolve().parent.parent;T=O.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V60_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V59_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
payload=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1'];known=sum(x['bytes'] for x in read(Path(payload)/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']);plan=known+16*1024**2
oldscope=read(P/'reports/CLOSED59_UNUSED_OLD58_39_MISSING_STORAGE_SOURCE_AST_ACTUAL.json')
src=P/'relocate_missing_closed58_39_after_closed59_TLS_V4_once.py';s=src.read_text('utf8')
changes={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V58_20261024':'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V59_20261024','CLOSED59_OLD58_39':'CLOSED60_OLD59_39',"label='CLOSED59_OLD'+('58' if batch==0 else '39')":"label='CLOSED60_OLD'+('59' if batch==0 else '39')",str(oldscope['known_H1_manifest_bytes']):str(known),str(oldscope['install_copy_planning_bytes']):str(plan)}
for key in changes:assert key in s,key
pattern=re.compile('|'.join(re.escape(x) for x in sorted(changes,key=len,reverse=True)));s=pattern.sub(lambda m:changes[m[0]],s)
tree=ast.parse(s);inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));ast.parse(inv)
assert "stages=[T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V59_20261024',T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023']" in s
dest=N/'relocate_missing_closed59_39_after_closed60_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v33.py';w=old.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";assert w.count(needle)==1;w=w.replace(needle,needle+"\n        '"+dest.name+"',");ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v34.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),simultaneous_exact_replacements=changes,known_H1_manifest_bytes=known,install_copy_planning_bytes=plan,copy_planning_not_new_training_gate=True,sources=['closed59 paired retained0/116/117','closed39 paired only118 remains'],storage_only_not_checkpoint_fallback_or_motion_replay=True,fresh_joint_capacity_allout_locks_producer_stat_before_selected_hash=True,unselected_stat_only=True,TLS_protocol_not_changed_or_retested=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED60_UNUSED_OLD59_39_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=plan,source_AST=True)))
