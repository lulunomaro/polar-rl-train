from pathlib import Path
import ast,json,time
H=Path(__file__).resolve().parent;T=H.parent;F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
p=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024/relocate_missing_current65_old63_26_after_closed65_TLS_V5_once.py';s=p.read_text('utf8')
start=s.index(" proof=read(R/'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')");end=s.index(' assert read(T/\'reports/V96',start)
s=s[:start]+''' O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
 proof=read(O/'reports/HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json');current=read(O/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
 assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost'
 sources=[]
 for name in ('H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026','H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026'):
  stage=T/name;oldp=read(stage/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');oq=read(stage/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
  assert oldp['passed'] and oldp['all_owner_nodes_children_actual_out'] and oldp['original_canonical_cost_settled']
  sources.append(dict(source_root=oq['roots']['h1'],owner_root=oq['owner_root'],private_lock=oq['specs']['h1']['private_lock'],stage=name))
 q=read(T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026/reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 known_payload_bytes=sum(r['bytes'] for r in read(Path(q['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'])
 planning_bytes=known_payload_bytes+16*1024**2
''' +s[end:]
s=s.replace(" cache=read(R/'PEER_FORENSICS_FRESH_SOURCE_ACTUAL.json')"," cache=dict(files=[])")
s=s.replace('known_H1_manifest_bytes=63476533,install_copy_planning_bytes=80253749','known_H1_manifest_bytes=known_payload_bytes,install_copy_planning_bytes=planning_bytes')
s=s.replace('install_copy_planning_bytes=80253749','install_copy_planning_bytes=planning_bytes')
s=s.replace("['CLOSED65_CURRENT65_MINIMAL','CLOSED65_OLD63_MINIMAL','CLOSED65_OLD26_MINIMAL']","['CLOSED81O_FOR82Q_OLD80_MINIMAL','CLOSED81O_FOR82Q_OLD79C_MINIMAL']")
s=s.replace('CLOSED65_CURRENT65_OLD63_26','CLOSED81O_FOR82Q_OLD80_79C')
needle="read=lambda p:json.loads(Path(p).read_bytes());H=ops.H";assert needle in s
s=s.replace(needle,needle+"\nsys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route;d.t.connect=route.connect",1)
# Preserve the old local root variable H=ops.H used as SHA helper; no change to the protocol.
n='relocate_minimal_closed80_79c_NPZ_for82Q_same_approved_TLS_V5_unused_once.py';out=H/n;assert not out.exists();ast.parse(s);out.write_text(s,'utf8')
w=(B/'same_authorized_session_compressed_transport_v132.py').read_text('utf8');needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',";assert needle in w
wp=B/'same_authorized_session_compressed_transport_v133.py';assert not wp.exists();wp.write_text(w.replace(needle,needle+'\n        '+repr(n)+',',1),'utf8')
with (H/'reports/MINIMAL_CLOSED_NPZ_ONLY_RELOCATION_RESOURCE_SUPPORT_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_roots_only=['closed80/h1','closed79c/h1'],reuse_original_authorized_NPZ_only_peer_retention_protocol=True,no_new_PT_or_cache_deletion_scope=True,target_full_SHA_signed_HMAC_ack_before_source_duplicate_release=True,source_original_FINAL_model_PT_reports_logs_errors_untouched=True,canonical_None_original_locks_allout_required=True,receiver_above25GiB_and_original_source_postcopy25_guard_retained=True,minimum_file_count_then_bytes_selection=True,copy_planning_not_new_training_gate=True,no_reexecution_old_TLS_CPU_or_old_once=True),f,indent=2)
print(json.dumps(dict(prepared=n,no_transfer_yet=True)))
