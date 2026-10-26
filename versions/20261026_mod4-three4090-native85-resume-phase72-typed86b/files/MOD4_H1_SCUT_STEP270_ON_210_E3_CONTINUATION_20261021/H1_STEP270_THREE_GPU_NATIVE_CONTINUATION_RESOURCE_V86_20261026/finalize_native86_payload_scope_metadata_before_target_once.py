from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;D=N/'payloads/e2';R=N/'reports';contract_path=D/'NATIVE86_SOURCE_CONTRACT_ACTUAL.json';manifest_path=D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old_contract=contract_path.read_bytes();old_manifest=manifest_path.read_bytes();c=json.loads(old_contract);m=json.loads(old_manifest)
assert c['source_review_revision']==4 and c['actual_installed86_SDK_CPU_passed'] is False
with (R/'NATIVE86_PREPARED_CONTRACT_V4_BEFORE_SCOPE_METADATA_CORRECTION.json').open('xb') as f:f.write(old_contract)
c['source_review_revision']=5;c['historical_frozen_candidate_no_payload_or_GO']=c['no_payload_Task_GO_or_real_model_access'];c['no_payload_Task_GO_or_real_model_access']=False
c['scope_flags_at_contract_publication']=dict(local_payload_and_Task_prepared=True,GO=False,actual_target_installed_CPU=False,native_model_opaque_copy_for_new_payload=True,no_torch_model_load_or_local_model_hash=True)
c['root_exact_controller_and_Task_finalization_complete']=True
contract_path.write_text(json.dumps(c,indent=2),'utf8')
for r in m['files']:
 if r['relative']=='NATIVE86_SOURCE_CONTRACT_ACTUAL.json':r.update(bytes=contract_path.stat().st_size,SHA=H(contract_path))
manifest_path.write_text(json.dumps(m,indent=2),'utf8')
q=json.loads((R/'NATIVE86_EXACT_PAYLOAD_SOURCE_BINDING_LOCAL_NONMODEL_CPU_ACTUAL.json').read_bytes());q['spec']['native_source_contract_SHA']=H(contract_path);q['spec']['manifest_SHA']=H(manifest_path);q['scope']='payload scope metadata revision5 before target install; originalV4/local-source receipt retained';q['previous_manifest_SHA']=hashlib.sha256(old_manifest).hexdigest();q['previous_contract_SHA']=hashlib.sha256(old_contract).hexdigest();q['source_review_revision']=5;q['no_actual_installed86_SDK_or_Task_GO']=False;q['local_Task_exists_but_no_GO']=True
with (R/'NATIVE86_FINALIZED_LOCAL_PAYLOAD_V5_SOURCE_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
print(json.dumps({'source_revision':5,'manifest_SHA':q['spec']['manifest_SHA'],'no_actual_target_or_GO':True}))
