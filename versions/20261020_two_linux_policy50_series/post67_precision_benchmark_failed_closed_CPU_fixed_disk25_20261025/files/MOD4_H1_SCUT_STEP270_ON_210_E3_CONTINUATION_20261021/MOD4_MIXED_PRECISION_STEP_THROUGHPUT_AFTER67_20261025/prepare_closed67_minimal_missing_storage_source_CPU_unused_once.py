from pathlib import Path
import ast,hashlib,json,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=T/'H1_STEP270_LATEST65_REPLAY_REPAIR_20261024/relocate_missing_current66_old26_30_after_closed66_TLS_V5_unused_once.py'
a=old.read_text('utf8').replace('H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024','H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025')
needle="stages=[N,T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023']";assert a.count(needle)==1;a=a.replace(needle,"stages=[N,T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023']")
a=a.replace("['CLOSED66_CURRENT66_MINIMAL','CLOSED66_OLD26_MINIMAL','CLOSED66_OLD30_MINIMAL']","['CLOSED67_CURRENT67_MINIMAL','CLOSED67_OLD30_MINIMAL']")
a=a.replace('CLOSED66_CURRENT66_OLD26_30','CLOSED67_CURRENT67_OLD30')
N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025';q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());p=Path(q['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';manifest=json.loads(p.read_bytes());size=sum(r['bytes'] for r in manifest['files']);a=a.replace('known_H1_manifest_bytes=63476480','known_H1_manifest_bytes='+str(size)).replace('80253696',str(size+16*1024**2));ast.parse(a)
dest=M/'relocate_missing_current67_old30_after_closed67_TLS_V5_unused_once.py'
with dest.open('x',encoding='utf8') as f:f.write(a)
oldw=B/'same_authorized_session_compressed_transport_v50.py';neww=B/'same_authorized_session_compressed_transport_v51.py';w=oldw.read_text('utf8');needle="        'relocate_missing_current66_old26_30_after_closed66_TLS_V5_unused_once.py',";assert w.count(needle)==1
new=w.replace(needle,needle+"\n        '"+dest.name+"',");assert ast.dump(ast.parse(new.replace("        '"+dest.name+"',\n","")))==ast.dump(ast.parse(w))
with neww.open('x',encoding='utf8') as f:f.write(new)
with (R/'CLOSED67_CURRENT67_OLD30_MISSING_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source=str(dest),source_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),wrapper=str(neww),wrapper_SHA=hashlib.sha256(neww.read_bytes()).hexdigest(),current67_three_and_old30_last118_candidates_not_existence_proof=True,local_receipts_show_other_qualified_V20plus_retained_NPZ_already_migrated=True,original25GiB_guard_and_TLS_V5_2268000_9_unchanged=True,known_H1_payload_bytes=size,copy_planning_bytes=size+16*1024**2,no_new_training_gate=True),f,indent=2)
print(json.dumps(dict(helper=str(dest),known_payload_bytes=size,copy_planning_bytes=size+16*1024**2)))

