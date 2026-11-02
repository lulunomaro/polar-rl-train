"""Seal only this NEW historical-text append. No historical entry execution."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re

OUT=Path(__file__).resolve().parent;R=OUT.parent
EXPECTED='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
V2SHA='ed6f85dec66c449c689eae0322b4391a9bc893306a3c29c40372472f96f9ad22'
if (OUT/'DELIVERABLES_SHA256_V3.json').exists():raise RuntimeError('Already sealed; append in a new version')
def record(p):
    raw=p.read_bytes()
    return dict(name=p.name,path=str(p.resolve()),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest())
def put(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
source=R/'discovery/exact_referenced_master_plan_v3/MOD4_MOE_MASTER_PLAN.md'
receipt=R/'reports/EXACT_REFERENCED_ORIGINAL_MASTER_PLAN_TEXT_V3.json'
raw=source.read_bytes();text=raw.decode('utf-8-sig');lines=text.splitlines()
assert len(raw)==47599 and hashlib.sha256(raw).hexdigest()==EXPECTED
capture=json.loads(receipt.read_text(encoding='utf-8'))
assert Path(capture['path']).resolve()==source.resolve()
assert capture['bytes']==capture['published_bytes']==47599
assert capture['SHA']==capture['published_SHA']==EXPECTED
assert capture['exact_match_to_published_formals189_evidence'] is True
reference=Path(capture['reference'])
assert reference.is_relative_to(R.parent/'mod4v1_experts_fulldr_rm70_20261101') and reference.suffix=='.json'
reference_dict=json.loads(reference.read_text(encoding='utf-8'))
assert any(v.get('bytes')==47599 and v.get('SHA')==EXPECTED for v in reference_dict['evidence'])
assert len(lines)==360 and '2026-10-07' in lines[6]
assert 'E0' in lines[78] and 'E1' in lines[79] and 'E2' in lines[80]
assert 'SLOPE_INDEPENDENT50' not in text
assert '90%/95%/100%' in lines[220] and '不重新建立任意' in lines[220]
assert 'tol=max(0.03,0.1V)' in lines[222] and '0.2 rad/s' in lines[222]
assert '20261002/20261003' in lines[228] and '不覆盖' in lines[228]
assert '复用必须匹配' in lines[238]
v2=R/'source_original_acceptance_gap_review_v2/DELIVERABLES_SHA256_V2.json'
assert record(v2)['SHA256']==V2SHA
v2files=json.loads(v2.read_text(encoding='utf-8'))['files'];assert len(v2files)==8
for row in v2files:
    p=Path(row['path']);assert p.parent.resolve()==v2.parent.resolve()
    actual=record(p);assert actual['bytes']==row['bytes'] and actual['SHA256']==row['SHA256']
finding=OUT/'MASTER_PLAN_APPEND_FINDINGS_V3.json'
f=json.loads(finding.read_text(encoding='utf-8'))
for key,value in f['append_to_V2'].items():
    if key not in ('formerly_unjoined_exact_MasterPlan_reference_now_locally_joined','V2_nine_files_unchanged_required'):assert value is None,key
assert f['optional_NEW_protocol_template_DISABLED']['enabled'] is False
assert all(v==0 for v in f['operations'].values())
report=OUT/'EXACT_MASTER_PLAN_ACCEPTANCE_APPEND_V3.md'
allowed={source.resolve(),receipt.resolve(),v2.resolve(),finding.resolve()};nlinks=0
for target in re.findall(r'\]\(<([^>]+)>\)',report.read_text(encoding='utf-8')):
    path,sep,anchor=target.partition('#');p=Path(path).resolve();assert p in allowed and p.is_file()
    if sep:
        m=re.fullmatch(r'L(\d+)(?:-L?(\d+))?',anchor);assert m
        start=int(m.group(1));end=int(m.group(2) or m.group(1))
        assert 1<=start<=end<=len(p.read_text(encoding='utf-8-sig').splitlines())
    nlinks+=1
compile(Path(__file__).read_text(encoding='utf-8'),__file__,'exec') # no exec/import of original code
put('SOURCE_APPEND_VERIFICATION_V3.json',dict(kind='EXACT_HISTORICAL_REFERENCE_APPEND_NOT_RUNTIME',
    source_exact_bytes_SHA_match=True,source_lines=360,source_inputs=[record(source),record(receipt),record(reference)],
    old_V2_nine_files_SHA_unchanged=True,report_links_and_line_ranges_valid=nlinks,
    E0_fullrole_atomic_predicate=None,E0_binary_denominator=None,S50_atomic_predicate=None,S50_cohort=None,S50_binary_denominator=None,
    NEW_protocol_template_enabled=False,native_SDK_Torch_GPU_PT_C_remote_Git_or_old_file_writes=0))
files=[record(OUT/name) for name in ['MASTER_PLAN_APPEND_FINDINGS_V3.json','EXACT_MASTER_PLAN_ACCEPTANCE_APPEND_V3.md','seal_append_v3.py','SOURCE_APPEND_VERIFICATION_V3.json']]
bundle=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
put('DELIVERABLES_SHA256_V3.json',dict(kind='SOURCE_ACCEPTANCE_GAP_APPEND_V3',created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),files=files,bundle_SHA256=bundle,self_excluded=True))
print(json.dumps(dict(source_exact=True,V2_nine_files_unchanged=True,links=nlinks,files_including_manifest=5,
    manifest=record(OUT/'DELIVERABLES_SHA256_V3.json'),bundle_SHA256=bundle,report=record(report),native=0),ensure_ascii=False))
