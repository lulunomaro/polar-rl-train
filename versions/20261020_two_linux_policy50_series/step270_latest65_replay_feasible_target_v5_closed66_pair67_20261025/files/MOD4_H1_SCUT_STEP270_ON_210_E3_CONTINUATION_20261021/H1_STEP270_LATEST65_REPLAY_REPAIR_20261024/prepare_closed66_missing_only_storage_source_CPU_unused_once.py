from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024';R=S/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024/relocate_missing_current65_old63_26_after_closed65_TLS_V5_once.py'
a=old.read_text('utf8')
a=a.replace("N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';", "T=Path(__file__).resolve().parent.parent;N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024';W=T.parent;R=N/'reports';")
a=a.replace("stages=[N,T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023']", "stages=[N,T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V26_20261023',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V30_20261023']")
a=a.replace("['CLOSED65_CURRENT65_MINIMAL','CLOSED65_OLD63_MINIMAL','CLOSED65_OLD26_MINIMAL']", "['CLOSED66_CURRENT66_MINIMAL','CLOSED66_OLD26_MINIMAL','CLOSED66_OLD30_MINIMAL']")
a=a.replace('CLOSED65_CURRENT65_OLD63_26','CLOSED66_CURRENT66_OLD26_30').replace('current65_old63_26','current66_old26_30')
q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());m=json.loads((Path(q['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());payload=sum(r['bytes'] for r in m['files'])
planning=payload+16*1024**2
a=a.replace('known_H1_manifest_bytes=63476533','known_H1_manifest_bytes='+str(payload)).replace('80253749',str(planning))
a=a.replace('min(4*1024**3,','min(20*1024**3,')
# Preserve actual local producer/target schemas, V5 protocol, sumonce and original guards.
assert '2268000' in a and "len(c['budget_extensions'])==9" in a and 'forensic_tls_peer_transfer_V96_V5_NINTH.py' in a
ast.parse(a);dest=S/'relocate_missing_current66_old26_30_after_closed66_TLS_V5_unused_once.py'
with dest.open('x',encoding='utf8') as f:f.write(a)
oldwrapper=B/'same_authorized_session_compressed_transport_v49.py';newwrapper=B/'same_authorized_session_compressed_transport_v50.py';w=oldwrapper.read_text('utf8')
needle="        'read_actual_delayed_leg_action_SDK_source_unused_once.py',";assert w.count(needle)==1
v=w.replace(needle,needle+"\n        '"+dest.name+"',")
assert ast.dump(ast.parse(v.replace("        '"+dest.name+"',\n","")))==ast.dump(ast.parse(w))
with newwrapper.open('x',encoding='utf8') as f:f.write(v)
with (R/'CLOSED66_MISSING_ONLY_CURRENT66_OLD26_30_STORAGE_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source=str(dest),SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),old30_0_complete_on72_only_by_receipt=True,old30_117_118_candidates_only_until_fresh_stat=True,old26_remaining_one_candidate_only_until_fresh_stat=True,current66_three_original_NPZ_still210_by_actual_blocked_receipt=True,source_target_fresh_capacity_before_new_controller=True,selected_min_count_then_min_bytes=True,known_H1_payload_bytes=payload,copy_planning_bytes=planning,copy_planning_not_new_training_gate=True,original25_GiB_guard_after_real_payload_copy=True,protocol_V5_SHA='786064012058a6fb642da821e6fab0c625e6c9077373482fe857a5251fb69545',wrapper=str(newwrapper),wrapper_SHA=hashlib.sha256(newwrapper.read_bytes()).hexdigest(),budget2268000_nine_no_extra_grant=True),f,indent=2)
with (R/'LOCAL_OLD_PRODUCER_SCHEMA_READER_KEYERROR_AND_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_error="KeyError: index in local producer row; index is in retention_status, producer row keys are path/bytes/SHA/controls/preupdate_source",original_stderr_preserved_in_chat=True,corrected_reader_used_retention_status_and_path=True,no_old_raw_model_or_training_read=True,not_original_assert_pass=True),f,indent=2)
print(json.dumps(dict(source=str(dest),payload_bytes=payload,planning_bytes=planning,wrapper=str(newwrapper))))

