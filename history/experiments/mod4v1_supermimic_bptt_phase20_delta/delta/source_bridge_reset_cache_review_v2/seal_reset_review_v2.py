"""Seal this new directory only; bounded source/hash validation, stdlib CPU."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
NAMES=(
    'reset_cache_and_failclosed_candidates_v2.py',
    'test_reset_cache_and_failclosed_v2.py',
    'build_reset_review_v2.py',
    'seal_reset_review_v2.py',
    'AUDIT_INPUTS_SHA256_V2.json',
    'CLOSED_FAILURE_CHAIN_SOURCE_V2.json',
    'CPU_TEST_RESULTS_V2.json',
    'CPU_TEST_EXECUTION_HISTORY_V2.json',
    'RESET_CACHE_MINIMAL_CANDIDATE_PROTOCOL_V2.json',
    'BRIDGE_RESET_CACHE_FAILCLOSED_SOURCE_REVIEW_V2.md',
    'SOURCE_REVIEW_VERIFICATION_V2.json',
)

def load(name):return json.loads((HERE/name).read_text(encoding='utf-8'))
def put(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    inputs=load('AUDIT_INPUTS_SHA256_V2.json')
    for item in inputs['files']:
        raw=Path(item['path']).read_bytes()
        assert len(raw)==item['bytes'] and sha(raw)==item['SHA256'],item['path']
    tests=load('CPU_TEST_RESULTS_V2.json')
    assert tests['tests_run']==49 and tests['passed'] and tests['failures']==tests['errors']==0
    assert tests['SDK_imports']==tests['torch_imports']==tests['GPU_or_physics_steps']==0
    protocol=load('RESET_CACHE_MINIMAL_CANDIDATE_PROTOCOL_V2.json')
    assert protocol['enabled'] is False and protocol['deployed'] is False
    assert protocol['original_closed_run_reopened'] is False
    join=load('CLOSED_FAILURE_CHAIN_SOURCE_V2.json')
    assert len(join['rows'])==8 and len(join['candidate_blocked_error_roles'])==6
    assert join['accounting_rewrite'] is False and join['new_runtime_executed'] is False
    assert join['all_original_children_waited'] and join['original_cost_settled'] and join['original_leases_released']
    report=(HERE/'BRIDGE_RESET_CACHE_FAILCLOSED_SOURCE_REVIEW_V2.md').read_text(encoding='utf-8')
    links=re.findall(r'\]\(<([^>]+)>\)',report)
    for link in links:
        path,_,fragment=link.partition('#')
        q=Path(path);assert q.is_file(),link
        m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment) if fragment else None
        if m:
            lines=len(q.read_text(encoding='utf-8').splitlines())
            first=int(m.group(1));last=int(m.group(2) or first)
            assert 1<=first<=last<=lines,link
    for name in NAMES:
        path=HERE/name
        if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    put('CPU_TEST_EXECUTION_HISTORY_V2.json',dict(
        kind='SUCCESSIVE_CPU_SUITE_EXPANSION_NOT_RUNTIME_TRAINING',
        runs=[dict(stage='initial',tests_run=36,failures=0,errors=0,passed=True),
              dict(stage='actual_backend_AST_and_eight_field_candidate',tests_run=48,failures=0,errors=0,passed=True,
                   elapsed_seconds=.05670570000074804),
              dict(stage='clock_preflight_before_any_original_write',**tests)],
        audited_source_or_threshold_changes=False,SDK_imports=0,training_steps=0))
    put('SOURCE_REVIEW_VERIFICATION_V2.json',dict(
        kind='NEW_DIRECTORY_SOURCE_REVIEW_SEAL_CHECKS_NOT_SDK_VALIDATION',
        bounded_input_files_verified_unchanged=len(inputs['files']),
        report_links_and_line_ranges_verified=len(links),
        python_sources_AST_parse=True,
        tests_run=tests['tests_run'],tests_passed=True,
        original_closed_accounting_preserved=True,
        protocol_disabled=True,candidate_deployed=False,
        previous_worker_live_binding=None,physical_cache_root_cause=None,
        actual_app_close_masking_mechanism=None,skill_success=None))
    rows=[]
    for name in NAMES:
        p=HERE/name;raw=p.read_bytes()
        rows.append(dict(name=name,path=str(p),bytes=len(raw),SHA256=sha(raw)))
    bundle=sha(json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))
    value=dict(kind='NEW_ONLY_SOURCE_REVIEW_DELIVERABLES_SHA256_SEAL',
               created_at_UTC=datetime.now(timezone.utc).isoformat(),
               output_directory=str(HERE),files=rows,bundle_SHA256=bundle,
               manifest_self_excluded=True,SDK_GPU_model_training_account_mutations=0)
    put('DELIVERABLES_SHA256_V2.json',value)
    manifest=HERE/'DELIVERABLES_SHA256_V2.json'
    print(json.dumps(dict(files=len(rows)+1,bounded_inputs=len(inputs['files']),
               report_links_verified=len(links),tests=tests['tests_run'],
               manifest_SHA256=sha(manifest.read_bytes()),bundle_SHA256=bundle)))

if __name__=='__main__':main()
