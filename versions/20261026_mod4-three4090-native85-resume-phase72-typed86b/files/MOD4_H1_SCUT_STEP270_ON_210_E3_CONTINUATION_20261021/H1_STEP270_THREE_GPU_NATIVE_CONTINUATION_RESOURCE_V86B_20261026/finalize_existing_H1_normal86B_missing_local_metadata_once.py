from pathlib import Path
import copy,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;T=N.parent;D=N/'payloads/h1';R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert D.is_dir() and not (R/'NORMAL86B_H1_EXISTING_PREPARED_PAYLOAD_LOCAL_METADATA_ACTUAL.json').exists()
m=json.loads((D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());c=json.loads((D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json').read_bytes());original=json.loads((D/'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json').read_bytes())
sp=importlib.util.spec_from_file_location('normal_h1_metadata_only',D/'normal86_source_guard_v1.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
g.validate_inventory(m,original,c)
proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());model=proof['models']['h1'];final=model['final']
base=json.loads((P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());spec=copy.deepcopy(base['specs']['h1']);spec.update(normal86_continuation=True,source_SHA=final['SHA'],source_filename=m['source_filename'],source_Adamstep=model['Adam'],manifest_SHA=H(D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),normal_source_contract_SHA=H(D/'NORMAL86_SOURCE_CONTRACT_ACTUAL.json'),owner_authority_generation='MOD4_SINGLE_WRITER72_20261026',previous_runtime_root=str(Path(final['path']).parents[2]).replace('\\','/'),previous_exit_kind='node',owner_control_dependency_binding_SHA=H(D/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'))
g.identity(spec,'h1')
row=dict(passed=True,payload=str(D),root='/mnt/mod4_linux_durable_20261013/H1step270_three_gpu_native_cont_2610v86b/h1',spec=spec,source=final,original_manifest_SHA=c['original_manifest_SHA'],new_manifest_SHA=spec['manifest_SHA'],no_actual_target_SDK_or_GO=True)
out=dict(epoch=time.time(),passed=True,roles={'h1':row},no_model_load_or_local_model_hash=True,no_remote_or_GO=True,classification='Complete original H1 local payload already prepared before a local keyword-argument reader error; no rebuild, repeated copy or oldonce replay',original_error_retained=True)
with (R/'NORMAL86B_H1_EXISTING_PREPARED_PAYLOAD_LOCAL_METADATA_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(out,stream,indent=2)
print(json.dumps({'existing_H1_payload_metadata_validated':True,'no_GO':True}))
