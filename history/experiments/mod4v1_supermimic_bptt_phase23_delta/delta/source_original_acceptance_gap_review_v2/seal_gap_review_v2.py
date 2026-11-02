"""Append-only new-directory text review seal; no SDK/model/native execution."""
from pathlib import Path
import ast
import datetime as dt
import hashlib
import json
import re

OUT=Path(__file__).resolve().parent
MANIFEST=OUT/'DELIVERABLES_SHA256_V2.json'
if MANIFEST.exists():raise RuntimeError('Already sealed; use a new output version')

def blob_record(p):
    raw=p.read_bytes()
    return dict(name=p.name,path=str(p.resolve()),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())

def create(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

inputs=json.loads((OUT/'AUDIT_INPUTS_SHA256_V2.json').read_text(encoding='utf-8'))['files']
line_counts={}
for row in inputs:
    p=Path(row['path']);raw=p.read_bytes()
    assert p.suffix.lower() in ('.md','.py','.json')
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA256'],row['id']
    line_counts[str(p.resolve())]=len(raw.decode('utf-8-sig').splitlines())
assert len(inputs)==33
findings=json.loads((OUT/'ACCEPTANCE_AUTHORITY_FINDINGS_V2.json').read_text(encoding='utf-8'))
for role in ('E0','SLOPE_INDEPENDENT50'):
    assert findings['roles'][role]['original_atomic_predicate'] is None
    assert findings['roles'][role]['original_binary_denominator'] is None
    assert findings['roles'][role]['binary_skill_rate'] is None
assert findings['roles']['SLOPE_INDEPENDENT50']['task_contract_is_original_TASK_equal_published_CPU_text'] is True
assert all(v==0 for v in findings['native_or_checkpoint_operations'].values())
tests=json.loads((OUT/'CPU_TEST_RESULTS_V2.json').read_text(encoding='utf-8'))
assert tests['passed'] is True and tests['tests']==15 and tests['failures']==tests['errors']==0
sources=['build_gap_evidence_v2.py','test_scalar_nonidentifiability_v2.py','seal_gap_review_v2.py']
for name in sources:
    p=OUT/name;text=p.read_text(encoding='utf-8')
    compile(text,str(p),'exec') # compile only, no execution/import of audited source.
    tree=ast.parse(text)
    for node in ast.walk(tree):
        roots=[]
        if isinstance(node,ast.Import):roots=[v.name.split('.')[0] for v in node.names]
        elif isinstance(node,ast.ImportFrom):roots=[(node.module or '').split('.')[0]]
        assert not any(v in ('torch','numpy','isaaclab','isaacsim','warp') for v in roots)
report=OUT/'ORIGINAL_E0_S50_ACCEPTANCE_GAPS_SOURCE_V2.md'
text=report.read_text(encoding='utf-8')
allowed_new={str((OUT/name).resolve()) for name in ['ACCEPTANCE_AUTHORITY_FINDINGS_V2.json','AUDIT_INPUTS_SHA256_V2.json','test_scalar_nonidentifiability_v2.py','CPU_TEST_RESULTS_V2.json']}
links=[]
for target in re.findall(r'\]\(<([^>]+)>\)',text):
    path_text,sep,anchor=target.partition('#');p=Path(path_text).resolve();key=str(p)
    assert key in line_counts or key in allowed_new,('unapproved link',target)
    assert p.is_file(),target
    if sep:
        m=re.fullmatch(r'L(\d+)(?:-L?(\d+))?',anchor);assert m,target
        start=int(m.group(1));end=int(m.group(2) or m.group(1))
        if key not in line_counts:line_counts[key]=len(p.read_text(encoding='utf-8').splitlines())
        assert 1<=start<=end<=line_counts[key],target
    links.append(target)
verification=dict(kind='BOUNDED_ORIGINAL_ACCEPTANCE_GAP_SOURCE_REVIEW_SEAL_NOT_NATIVE',
                  input_text_files_SHA_unchanged=len(inputs),old_contract_or_source_writes=0,
                  compiled_new_source_files=len(sources),audited_source_execution=False,
                  report_links_and_line_ranges_valid=len(links),CPU_tests=15,CPU_passed=True,
                  E0_original_predicate=None,S50_original_predicate=None,
                  E0_binary_denominator=None,S50_binary_denominator=None,
                  original_S50_TASK_equals_published_CPU_task_contract=True,
                  no_PT_stat_hash_open_or_SDK_Torch_GPU_native_remote_C_account_lock_Git=True)
create('SOURCE_REVIEW_VERIFICATION_V2.json',verification)
names=sources+['AUDIT_INPUTS_SHA256_V2.json','ACCEPTANCE_AUTHORITY_FINDINGS_V2.json','CPU_TEST_RESULTS_V2.json','ORIGINAL_E0_S50_ACCEPTANCE_GAPS_SOURCE_V2.md','SOURCE_REVIEW_VERIFICATION_V2.json']
records=[blob_record(OUT/name) for name in names]
bundle=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
create(MANIFEST.name,dict(kind='NEW_TEXT_SOURCE_REVIEW_DELIVERABLES_V2',created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),files=records,
                          bundle_SHA256=bundle,self_excluded=True))
print(json.dumps(dict(verification=verification,manifest=blob_record(MANIFEST),bundle_SHA256=bundle,files_including_manifest=len(records)+1),ensure_ascii=False))
