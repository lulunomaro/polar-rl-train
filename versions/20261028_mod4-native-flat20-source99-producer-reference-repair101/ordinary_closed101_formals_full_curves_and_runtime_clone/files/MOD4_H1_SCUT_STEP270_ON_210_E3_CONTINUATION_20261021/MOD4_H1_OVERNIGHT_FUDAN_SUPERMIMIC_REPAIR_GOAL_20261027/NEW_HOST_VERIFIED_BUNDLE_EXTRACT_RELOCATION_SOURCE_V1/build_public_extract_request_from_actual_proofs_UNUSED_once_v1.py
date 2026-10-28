"""Future local public-request builder, not SSH, credentials or archive/model reader."""
from pathlib import Path
import argparse,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent
CALLER=L/'NEW_HOST_DIRECT_HTTPS_BUNDLE_PULL_CANDIDATE_SOURCE_V1/reports/DIRECT_ALL29_ARTIFACT_PULL_AND_ORIGINAL_ENDING_RETURNED_ACTUAL.json'
PACK=L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json'
DEST='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1'

def envelope(path):
 raw=path.read_bytes();return dict(path=str(path),SHA=hashlib.sha256(raw).hexdigest(),raw_UTF8=raw.decode('utf8'))

def build(fresh_actual_source_allout):
 caller=envelope(CALLER);value=json.loads(caller['raw_UTF8']);source=envelope(fresh_actual_source_allout);sv=json.loads(source['raw_UTF8']);pack=json.loads(PACK.read_bytes())
 assert value['passed_all_artifacts_only'] and value['worker_waited']['actual_waited'] and value['worker_waited']['returncode']==0 and value['source_and_target_SSH_sequential_and_closed'] and value['receiver_complete']['passed_all_artifact_chunks_only'] and value['source_service_ending']['terminal']['listener_closed']
 assert sv['kind']=='MOD4_PROVEN72_EXPORT_AND_TLS_SOURCE_ALL_OWNOUT_ACTUAL_V1' and sv['passed'] and sv['all_known_recorded_out'] and sv['caller_receipt_SHA']==caller['SHA'] and sv['source_service_terminal']==value['source_service_ending']['terminal']
 assert pack['bundle_passed'] and pack['all_original_recorded_out'] and pack['producer']['producer_SHA']==sv['producer_SHA']==value['producer_SHA']=='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
 scope=[x for x in pack['full_original_texts'] if x['path'].endswith('/PROVEN72_RUNTIME_EXPORT_INPUT_SCOPE_ACTUAL.json')];assert len(scope)==1 and scope[0]['stable'] and scope[0]['SHA']==sv['input_scope_SHA'] and json.loads(scope[0]['UTF8'])['logical_input_bytes']==sv['logical_input_bytes']
 core=B/'strict_archive_and_narrow_relocation_core_v1.py';binding=B/'EXACT_ORIGINAL_LAUNCHERS_AND_FIVE_EDITABLE_BINDING_V1.json'
 return dict(kind='MOD4_VERIFIED_PROVEN72_NEW_COPY_EXTRACT_RELOCATE_V1',request_id='PROVEN72_EXTRACT_RELOCATE_'+str(time.time_ns()),maximum_seconds=1800,destination=DEST,actual_direct_caller=caller,fresh_actual_source_allout=source,producer=pack['producer'],logical_input_bytes=sv['logical_input_bytes'],core_SHA=hashlib.sha256(core.read_bytes()).hexdigest(),portability_binding_SHA=hashlib.sha256(binding.read_bytes()).hexdigest(),source_only_builder_not_executed_extract=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--fresh-source-allout-report',required=True,type=Path);a=p.parse_args();request=build(a.fresh_source_allout_report);R.mkdir(exist_ok=True)
 with (R/'ACTUAL_PROOFS_BOUND_PUBLIC_EXTRACT_REQUEST_UNUSED.json').open('x',encoding='utf8') as f:json.dump(request,f,indent=2)
 print(json.dumps(dict(request_id=request['request_id'],public_request=str(R/'ACTUAL_PROOFS_BOUND_PUBLIC_EXTRACT_REQUEST_UNUSED.json'),network_or_extraction_executed=False)))

if __name__=='__main__':main()
