from pathlib import Path
import ast,hashlib,json,time
O=Path(__file__).resolve().parent.parent;T=O.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V56_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
payload=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1'];known=sum(x['bytes'] for x in read(Path(payload)/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']);plan=known+16*1024**2
src=P/'relocate_missing_closed52_53_after_closed55_TLS_V4_once.py';s=src.read_text('utf8')
changes={'RESOURCE_V52_20261024':'RESOURCE_V54_20261024','CLOSED55_OLD52_53':'CLOSED56_OLD54_53',"label='CLOSED55_OLD'+('52' if batch==0 else '53')":"label='CLOSED56_OLD'+('54' if batch==0 else '53')",'63469819':str(known),'80247035':str(plan)}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
tree=ast.parse(s);inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));ast.parse(inv)
dest=N/'relocate_missing_closed54_53_after_closed56_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v29.py';w=old.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";assert w.count(needle)==1;w=w.replace(needle,needle+"\n        '"+dest.name+"',");ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v30.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),exact_replacements=changes,known_H1_manifest_bytes=known,install_copy_planning_bytes=plan,copy_planning_not_new_training_gate=True,sources=['closed54 paired retained0/116/117','closed53 paired only112 not previously moved'],fresh_joint_capacity_allout_locks_producer_stat_before_selected_hash=True,unselected_stat_only=True,TLS_protocol_not_changed_or_retested=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED56_UNUSED_OLD54_53_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=plan,source_AST=True)))
