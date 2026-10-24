from pathlib import Path
import ast,hashlib,json,re,time
O=Path(__file__).resolve().parent.parent;T=O.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V62_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
older=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023';h1only=(older/'reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').is_file();oldproof=read(older/'reports'/('H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json' if h1only else 'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'));assert oldproof['passed'] and oldproof['original_canonical_cost_settled'] and oldproof['all_owner_nodes_children_actual_out']
payload=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1'];known=sum(x['bytes'] for x in read(Path(payload)/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']);plan=known+16*1024**2
oldscope=read(P/'reports/CLOSED61_UNUSED_OLD60_36_MISSING_STORAGE_SOURCE_AST_ACTUAL.json')
src=P/'relocate_missing_closed60_36_after_closed61_TLS_V4_once.py';s=src.read_text('utf8')
changes={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V60_20261024':'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024','H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023':older.name,'CLOSED61_OLD60_36':'CLOSED62_OLD61_26',"label='CLOSED61_OLD'+('60' if batch==0 else '36')":"label='CLOSED62_OLD'+('61' if batch==0 else '26')",str(oldscope['known_H1_manifest_bytes']):str(known),str(oldscope['install_copy_planning_bytes']):str(plan)}
for key in changes:assert key in s,key
pattern=re.compile('|'.join(re.escape(x) for x in sorted(changes,key=len,reverse=True)));s=pattern.sub(lambda m:changes[m[0]],s)
tree=ast.parse(s);inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));ast.parse(inv)
assert "stages=[T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V61_20261024',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023']" in s
dest=N/'relocate_missing_closed61_26_after_closed62_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v35.py';w=old.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";assert w.count(needle)==1;w=w.replace(needle,needle+"\n        '"+dest.name+"',");ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v36.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),simultaneous_exact_replacements=changes,known_H1_manifest_bytes=known,install_copy_planning_bytes=plan,copy_planning_not_new_training_gate=True,sources=['closed61 paired retained0/112/113','closed26 '+('H1only' if h1only else 'paired')+' still-present retained NPZ only'],storage_only_not_checkpoint_fallback_or_motion_replay=True,fresh_joint_capacity_allout_locks_producer_stat_before_selected_hash=True,unselected_stat_only=True,TLS_protocol_not_changed_or_retested=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED62_UNUSED_OLD61_26_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=plan,older_H1only=h1only,source_AST=True)))
