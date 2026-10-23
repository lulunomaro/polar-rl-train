from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V42_20261023'
s=(P/'relocate_missing_closed36_28_after_closed41_TLS_V4_once.py').read_text('utf8')
s=s.replace('CLOSED41_OLD36_28','CLOSED42_OLD39_41').replace("label='CLOSED41_OLD'+('36' if batch==0 else '28')","label='CLOSED42_OLD'+('39' if batch==0 else '41')")
s=s.replace("stages=[T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V28_20261023']", "stages=[T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023',T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023']")
s=s.replace("oldp=read(stage/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')", "oldp=read(stage/'reports'/('H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json' if stage.name=='H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023' else 'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'))")
s=s.replace("oq=read(stage/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')", "oq=read(stage/'reports'/('H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json' if stage.name=='H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023' else 'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'))")
assert "label='CLOSED42_OLD'+('39' if batch==0 else '41')" in s;ast.parse(s)
dest=N/'relocate_missing_closed39_41_after_closed42_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,encoding='utf8')
wrapper=(B/'same_authorized_session_compressed_transport_v7.py').read_text('utf8');needle='relocate_missing_closed36_28_after_closed41_TLS_V4_once.py';assert wrapper.count(needle)==1
wrapper=wrapper.replace(repr(needle),repr(needle)+','+repr(dest.name));assert dest.name in wrapper;ast.parse(wrapper)
out=B/'same_authorized_session_compressed_transport_v8.py';assert not out.exists();out.write_text(wrapper,encoding='utf8')
with (R/'CLOSED42_OLD39_41_MINIMAL_STORAGE_AND_WRAPPER_V8_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,helper=str(dest),helper_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),same_combined_capacity_guard_and_minimum_file_count_then_bytes_selection=True,old39_pair_and_old41_H1_only_proof_schema_explicit=True,TLS_core_byteexact_SHA=hashlib.sha256((T/'forensic_tls_peer_transfer_V96_V4.py').read_bytes()).hexdigest(),only_new_wrapper_allowlist_basename=dest.name,not_executed_yet=True),f,indent=2)
print(json.dumps(dict(prepared=True,helper=str(dest),wrapper=str(out))))
