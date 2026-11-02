"""Bounded source/output verification, no SDK import or filesystem discovery."""
import datetime
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def digest(p):
    b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),SHA256=hashlib.sha256(b).hexdigest())

def save(name,value):
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

result=json.loads((HERE/'CPU_TEST_RESULTS_V3.json').read_text(encoding='utf-8'))
assert result['passed'] and result['tests_run']==54 and result['failures']==result['errors']==0
assert result['SDK_imports']==result['torch_imports']==result['GPU_steps']==0

# Exact pre-existing sealed manifests and their own explicit output lists.
old_seals=[
    (ROOT/'source_reward_review_v1'/'DELIVERABLES_SHA256_V1.json','14f99ada274d03a1062082e7589fe5b03929d79381f8f4d5c00a4bdecc2dd188'),
    (ROOT/'source_bridge_reset_cache_review_v2'/'DELIVERABLES_SHA256_V2.json','b5b7f5f78eddbf7c9639e46b044df4289ac9eebf57c57750853b7c48951dcdc9'),
]
sealed_outputs=[]
for path,expected in old_seals:
    got=digest(path);assert got['SHA256']==expected,(path,'old seal changed')
    doc=json.loads(path.read_text(encoding='utf-8'))
    count=0
    for row in doc['files']:
        actual=digest(Path(row['path']))
        assert actual['SHA256']==row['SHA256'],(row['path'],'old sealed artifact changed')
        count+=1
    sealed_outputs.append(dict(manifest=str(path),SHA256=got['SHA256'],entries_verified=count,unchanged=True))

# Only the already bounded v2 source list is rehashed, not a tree traversal.
old_inputs=ROOT/'source_bridge_reset_cache_review_v2'/'AUDIT_INPUTS_SHA256_V2.json'
prior=json.loads(old_inputs.read_text(encoding='utf-8'))
inputs=[]
for row in prior['files']:
    path=Path(row['path']);actual=digest(path)
    assert actual['SHA256']==row['SHA256'],(str(path),'old bounded source changed')
    inputs.append(actual)
inputs.append(digest(old_inputs))
save('AUDIT_INPUTS_SHA256_V3.json',dict(kind='BOUNDED_PRIOR_SOURCE_INPUTS_AND_PIN_FILES_REVERIFIED',input_count=len(inputs),files=inputs))

report=HERE/'POSE_CACHE_RUNTIME_ADAPTER_V3_INTEGRATION.md'
text=report.read_text(encoding='utf-8');checked=[]
for destination in re.findall(r'\]\(<([^>]+)>\)',text):
    target,sep,fragment=destination.partition('#')
    path=Path(target);assert path.is_file(),destination
    if sep:
        match=re.fullmatch(r'L(\d+)(?:-L?(\d+))?',fragment);assert match,destination
        first=int(match.group(1));last=int(match.group(2) or first)
        lines=len(path.read_text(encoding='utf-8').splitlines())
        assert 1<=first<=last<=lines,(destination,lines)
    checked.append(destination)
verification=dict(kind='SOURCE_ADAPTER_VERIFICATION_NOT_NATIVE',CPU_tests=result['tests_run'],CPU_passed=True,
                  bounded_old_sources_reverified_unchanged=prior['input_count'],sealed_prior_outputs=sealed_outputs,
                  report_links_checked=len(checked),all_links_and_line_ranges_valid=True,
                  native_binding_verified=None,extra_SDK_imports=0,old_sources_or_outputs_written=False)
save('SOURCE_ADAPTER_VERIFICATION_V3.json',verification)

names=['pose_cache_runtime_adapter_v3.py','test_pose_cache_runtime_adapter_v3.py',
       'POSE_CACHE_RUNTIME_ADAPTER_V3_INTEGRATION.md','RUNTIME_ADAPTER_CONTRACT_V3.json',
       'CPU_TEST_RESULTS_V3.json','CPU_TEST_EXECUTION_HISTORY_V3.json',
       'AUDIT_INPUTS_SHA256_V3.json','SOURCE_ADAPTER_VERIFICATION_V3.json','seal_pose_cache_adapter_v3.py']
rows=[dict(name=n,**digest(HERE/n)) for n in names]
bundle=hashlib.sha256(''.join(row['name']+'\t'+row['SHA256']+'\n' for row in rows).encode()).hexdigest()
manifest=dict(kind='NEW_ONLY_MERGEABLE_SOURCE_ADAPTER_V3_SEAL',created_at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              output_directory=str(HERE),file_count_excluding_this_manifest=len(rows),files=rows,
              bundle_SHA256=bundle,manifest_self_excluded=True,native_binding_claim=None)
save('DELIVERABLES_SHA256_V3.json',manifest)
print(json.dumps(dict(verification=verification,manifest=digest(HERE/'DELIVERABLES_SHA256_V3.json'),bundle_SHA256=bundle,files=len(rows)+1),ensure_ascii=False))
