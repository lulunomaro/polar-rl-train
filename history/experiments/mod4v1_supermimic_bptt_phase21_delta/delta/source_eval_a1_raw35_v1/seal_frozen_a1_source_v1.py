"""Append-only source seal. Reads bounded sources/old V5 seal and own tiny fixtures."""
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

B=Path(__file__).resolve().parent;R=B.parent;T=R.parent/'mod4v1_experts_fulldr_rm70_20261101'

def record(path):
    raw=path.read_bytes()
    return dict(name=path.name,path=str(path),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())

def put(name,obj):
    with (B/name).open('x',encoding='utf-8') as file:json.dump(obj,file,ensure_ascii=False,indent=2);file.write('\n')

def main():
    assert not (B/'DELIVERABLES_SHA256_V1.json').exists(),'sealed output exists; use a NEW version'
    sources=[R/'source_runtime/native_supermimic_bridge.py',R/'source_core_review/evidence/networks.py',
      R/'source_core_review/evidence/learner.py',R/'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py',
      R/'source_resume_runtime_v2/resume_runtime_contracts_v3.py',R/'source_command_review_v1/command_tracking_torch_candidate_v1.py',
      R/'source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py',
      T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/MINIMAL_SOURCE_FILE_MAP_AND_INTERFACES_V1.json',
      T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/generic_eval_metadata.py',
      T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_RETENTION_EVAL_SOURCE_V3/parallel_eval_safe.py',
      T/'NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py',
      T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py',
      T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_fresh_runtime_bridge.py',
      R/'source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json']
    inputs=[record(p) for p in sources]
    old=R/'source_app_close_semantics_v5/DELIVERABLES_SHA256_V5.json'
    assert record(old)['SHA256']=='c363463155bfd47cc6e781be3bec3f243479d6758ca11391f3bca0d3d5868311'
    previous=json.loads(old.read_text(encoding='utf-8'))
    for entry in previous['files']:
        now=record(Path(entry['path']));assert (now['bytes'],now['SHA256'])==(entry['bytes'],entry['SHA256'])
    put('AUDIT_INPUTS_SHA256_V1.json',dict(kind='BOUNDED_SOURCE_INPUTS_NOT_MODEL_OR_RAW_DATA',files=inputs,old_V5_manifest=record(old),old_V5_sealed_entries_unchanged=len(previous['files'])))
    tests=json.loads((B/'CPU_TEST_RESULTS_V1.json').read_text(encoding='utf-8'))
    assert tests['passed'] is True and tests['tests']==26 and tests['failures']==tests['errors']==0
    names=['frozen_a1_raw35_v1.py','test_frozen_a1_raw35_stdlib_v1.py','remote_cpu_synthetic_check_v1.py','seal_frozen_a1_source_v1.py']
    for name in names:compile((B/name).read_text(encoding='utf-8'),str(B/name),'exec')
    document=(B/'FROZEN_A1_RAW35_INTEGRATION_SOURCE_V1.md').read_text(encoding='utf-8');links=re.findall(r'\]\(<([^>]+)>\)',document)
    for link in links:
        path,_,fragment=link.partition('#');target=Path(path);assert target.is_file(),link
        if fragment:
            numbers=list(map(int,re.findall(r'\d+',fragment)));assert all(0<x<=len(target.read_text(encoding='utf-8').splitlines()) for x in numbers),link
    own=[]
    for path in sorted((B/'CPU_SYNTHETIC_CASES_V1').glob('*/production/checkpoints/*_complete.pt')):
        assert path.resolve().is_relative_to(B/'CPU_SYNTHETIC_CASES_V1')
        raw=path.read_bytes();assert b'OWN_STDLIB_JSON_FIXTURE_NOT_TORCH_OR_PRODUCTION_WEIGHTS' in raw
        own.append(dict(path=str(path.relative_to(B)),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()))
    put('OWN_SYNTHETIC_FILES_SHA256_V1.json',dict(kind='ONLY_NEW_TINY_JSON_FIXTURES_NOT_TORCH_PT',files=own))
    verification=dict(kind='A1_RAW35_FROZEN_SOURCE_NOT_ACTUAL_EVALUATION',stdlib_tests=26,passed=True,
        old_V5_sealed_entries_unchanged=len(previous['files']),bounded_source_files_hashed=len(inputs),compiled_without_import=len(names),
        report_links_and_line_ranges_valid=len(links),own_tiny_JSON_fixture_files=len(own),
        Torch_SDK_GPU_native_original_PT_C_account_Git_or_training_operations=0,
        remote_CPU_Torch_script_executed=False,actual_A1_checkpoint_or_frozen_eval=None)
    put('SOURCE_REVIEW_VERIFICATION_V1.json',verification)
    ordered=['frozen_a1_raw35_v1.py','test_frozen_a1_raw35_stdlib_v1.py','remote_cpu_synthetic_check_v1.py','API_CONTRACT_SOURCE_V1.json',
      'CPU_TEST_RESULTS_V1.json','CPU_TEST_EXECUTION_HISTORY_V1.json','FROZEN_A1_RAW35_INTEGRATION_SOURCE_V1.md','seal_frozen_a1_source_v1.py',
      'AUDIT_INPUTS_SHA256_V1.json','OWN_SYNTHETIC_FILES_SHA256_V1.json','SOURCE_REVIEW_VERIFICATION_V1.json']
    files=[record(B/name) for name in ordered];bundle=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    put('DELIVERABLES_SHA256_V1.json',dict(kind='NEW_ONLY_FROZEN_A1_RAW35_SOURCE_V1',created_at_UTC=datetime.now(timezone.utc).isoformat(),
        files=files,bundle_SHA256=bundle,self_excluded=True,actual_evaluation=None))
    print(json.dumps(dict(verification=verification,seal=record(B/'DELIVERABLES_SHA256_V1.json'),bundle_SHA256=bundle),ensure_ascii=False))

if __name__=='__main__':main()
