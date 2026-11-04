"""Parent readonly SOURCE identity check. No task imports or project tests."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;T=R.parent/'mod4v1_experts_fulldr_rm70_20261101';S=R/'source_phase1_typed_native_capture_v1';out=R/'reports/PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_VERIFY_V2.json';mark=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_STARTED_V2.json';assert not out.exists()and not mark.exists();H=lambda b:hashlib.sha256(b).hexdigest();cache={};ast_count=0
with mark.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='NEW_READONLY_FROZEN_SOURCE_AND_FINITE34_IDENTITIES_NOT_STATIC_BASELINE_OR_NATIVE'),f)
def read_source(p):
 global ast_count
 p=Path(p).resolve();assert p.is_relative_to(R)or p.is_relative_to(T);assert p.suffix.lower()in('.py','.json','.md','.txt','.yml','.yaml')
 if p not in cache:
  b=p.read_bytes();cache[p]=b
  if p.suffix.lower()=='.py':ast.parse(b.decode('utf-8-sig'),filename=str(p));ast_count+=1
 return cache[p]
raw=read_source(S/'SOURCE_SEAL.json');assert(len(raw),H(raw))==(3503,'f92384f7943d27a4d588316cfba129011ca47851571ff252040df4c740424966');seal=json.loads(raw);assert len(seal['files'])==15;assert H(json.dumps(seal['files'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==seal['content_root_sha256']=='e7ff849c171f2eddc1053c5d1fc0779c31d6f8df73937616a7482abb85e8b897'
for x in seal['files']:
 rel=PurePosixPath(x['relative']);assert len(rel.parts)==1 and not rel.is_absolute();b=read_source(S/x['relative']);assert(len(b),H(b))==(x['bytes'],x['sha256'])
abi=json.loads(read_source(S/'PRODUCER_ABI.json'));bundle=json.loads(read_source(S/'FINITE_SOURCE_BUNDLE.json'));rows=bundle['full_module_files'];assert len(rows)==34;assert len({x['install_relative']for x in rows})==34
for x in rows:
 rel=PurePosixPath(x['install_relative']);assert not rel.is_absolute()and'..'not in rel.parts;b=read_source(x['path']);assert(len(b),H(b))==(x['bytes'],x['SHA256'])
parent=read_source(S/'single_gpu_passive_capture_parent_v1.py');prior=read_source(R/'source_phase1_capture_worker_v4/single_gpu_passive_capture_parent_v1.py');assert parent==prior and H(parent)=='d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41';assert not seal['actual_SDK_or_native']and not seal['actual_Torch_CPU']and not seal['stage2_GO']and seal['gate1']=='UNKNOWN'
assert all(p.read_bytes()==b for p,b in cache.items())
v=dict(kind='PARENT_READONLY_TYPED_PRODUCER_FROZEN_SOURCE_IDENTITY_VERIFY_V2',epoch=time.time(),status='PASS_SOURCE_IDENTITIES_ONLY',sealed_members=15,content_root_sha256=seal['content_root_sha256'],finite_active_aliases=34,unique_source_paths=len(cache),unique_python_AST_parses=ast_count,whole_original_parent_bytes_equal=True,all_pinned_source_bytes_unchanged_after=True,source_identities=[dict(path=str(p),bytes=len(b),SHA256=H(b))for p,b in cache.items()],project_module_imports=0,project_tests_run=0,task_preflight_stage_or_entry_calls=0,actual_CPU_Torch_or_SDK_or_model_raw_C_resources=0,full_static_baseline_observed=False,source_review_semantic_scope='INDEPENDENT_BAC_STATIC_REVIEW_PENDING',gate1='UNKNOWN',exact=False,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:z for k,z in v.items()if k!='source_identities'},indent=2))
