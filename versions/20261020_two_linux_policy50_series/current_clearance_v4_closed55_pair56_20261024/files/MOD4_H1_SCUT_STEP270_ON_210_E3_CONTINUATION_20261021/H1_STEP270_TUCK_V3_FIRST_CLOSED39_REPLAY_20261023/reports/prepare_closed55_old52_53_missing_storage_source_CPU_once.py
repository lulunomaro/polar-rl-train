from pathlib import Path
import ast,hashlib,json,time
O=Path(__file__).resolve().parent.parent;T=O.parent
N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V55_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V54_20261024';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
assert read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')['passed']
assert read(N/'reports/PEER_FORENSICS_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json')['no_target_or_process_created']
payload=read(N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['payloads']['h1']
known=sum(x['bytes'] for x in read(Path(payload)/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'])
copy_plan=known+16*1024**2
src=P/'relocate_missing_closed51_42_after_closed54_TLS_V4_once.py';s=src.read_text('utf8')
changes={
 'RESOURCE_V51_20261024':'RESOURCE_V52_20261024',
 'RESOURCE_V42_20261023':'RESOURCE_V53_20261024',
 'CLOSED54_OLD51_42':'CLOSED55_OLD52_53',
 "label='CLOSED54_OLD'+('51' if batch==0 else '42')":"label='CLOSED55_OLD'+('52' if batch==0 else '53')",
 '63469824':str(known),'80247040':str(copy_plan),
}
for a,b in changes.items():
 assert a in s,a
 s=s.replace(a,b)
ast.parse(s)
tree=ast.parse(s)
inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets))
ast.parse(inv)
dest=N/'relocate_missing_closed52_53_after_closed55_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,'utf8')
old=B/'same_authorized_session_compressed_transport_v28.py';w=old.read_text('utf8')
needle="        'collect_selected_pair_finals_unused_once.py',"
assert w.count(needle)==1
w=w.replace(needle,needle+"\n        '"+dest.name+"',")
ast.parse(w)
wrapper=B/'same_authorized_session_compressed_transport_v29.py';assert not wrapper.exists();wrapper.write_text(w,'utf8')
report=dict(epoch=time.time(),passed_source_AST_only=True,not_executed_yet=True,source=str(src),source_SHA=H(src),new_helper=str(dest),new_SHA=H(dest),exact_replacements=changes,known_H1_manifest_bytes=known,install_copy_planning_bytes=copy_plan,copy_planning_not_new_training_gate=True,sources=['closed52 paired','closed53 paired'],fresh_joint_capacity_and_allout_locks_producer_stat_before_selected_hash=True,unselected_stat_only=True,TLS_protocol_not_changed_or_retested=True,wrapper=str(wrapper),wrapper_SHA=H(wrapper),wrapper_only_added_exact_basename=True,no_host_query_or_payload_GO_or_budget_write=True)
with (N/'reports/CLOSED55_UNUSED_OLD52_53_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(helper=str(dest),wrapper=str(wrapper),known_H1_manifest_bytes=known,copy_planning_bytes=copy_plan,source_AST=True)))
