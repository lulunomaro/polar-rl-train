"""NEW frozen V2 source/mirror payload with exact unchanged-function checks; no native."""
from pathlib import Path,PurePosixPath
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;out=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V2.json';assert not out.exists()
H=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda v:H(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode())
cache={};payload={}
def safe(rel):
 p=PurePosixPath(rel);assert not p.is_absolute()and ':'not in rel and '\\'not in rel and all(x not in('','.','..')for x in p.parts)and p.suffix.lower()in('.py','.json','.md','.txt');return p

def raw_at(rel):
 p=R.joinpath(*safe(rel).parts);assert p.resolve().is_relative_to(R)and not p.is_symlink()
 if rel not in cache:cache[rel]=p.read_bytes()
 return cache[rel]
def add(alias,local,row):
 safe(alias);b=raw_at(local);assert(len(b),H(b))==(row['bytes'],row.get('SHA256',row.get('sha256'))),local
 if alias in payload:assert payload[alias]['local_relative']==local
 payload[alias]=dict(local_relative=local,bytes=len(b),SHA256=H(b))
def package(folder,root,count,seal_sha=None):
 rel=folder+'/SOURCE_SEAL.json';b=raw_at(rel)
 if seal_sha:assert H(b)==seal_sha
 s=json.loads(b);assert s['content_root_sha256']==root and canonical(s['files'])==root
 rows=[dict(relative=k,**v)for k,v in s['files'].items()]if isinstance(s['files'],dict)else s['files'];assert len(rows)==count
 for row in rows:add('source_mirror/'+folder+'/'+row['relative'],folder+'/'+row['relative'],row)
 add('source_mirror/'+rel,rel,dict(bytes=len(b),SHA256=H(b)));return s
folder='source_phase1_capture_materializer_v2'
ms=package(folder,'3be49fa9fb8654af427aecafcf9e0bf2a4f211d868b9170d734b6beccf9a790d',10,'399b18c25437f2c22d84aa89dbe50805206848f4f1f8751c6a2f1638f1a61e24')
mirror=json.loads(raw_at(folder+'/SOURCE_MIRROR_INPUTS.json'));assert mirror['file_count']==len(mirror['files'])==263
for row in mirror['files']:add('source_mirror/'+row['relative'],row['relative'],row)
package('source_phase1_capture_controller_v1','3166b4e9a97e97bb596a56dd68162e73f5c357e279ca4c0f47779e47c4a40292',5,'0f8f7ecb86bdd9d45433eec6dd7b1d120ed41479487b2cf155a9dcff79cd8f22')
funcs=lambda b:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(b).body if isinstance(n,ast.FunctionDef)}
a=funcs(raw_at('source_phase1_capture_materializer_v1/stage_phase1_capture_v1.py'));b=funcs(raw_at(folder+'/stage_phase1_capture_v2.py'));allowed={'load_sources','metadata_validate','preflight_summary','stage'};assert set(a)==set(b)and {k for k in a if a[k]!=b[k]}<=allowed
assert raw_at(folder+'/static_source_helpers_v1.py')==raw_at('source_phase1_capture_materializer_v1/static_source_helpers_v1.py')
old=raw_at('source_bound_only_native_integration_v1/stage_bound_only_native_v1.py');assert(len(old),H(old))==(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40');c=funcs(old);helpers=funcs(raw_at(folder+'/static_source_helpers_v1.py'));assert len(helpers)==17 and all(c[k]==v for k,v in helpers.items())
for rel,raw in cache.items():
 if rel.endswith('.py'):ast.parse(raw)
v=dict(kind='NEW_PHASE1_CAPTURE_SOURCE_PAYLOAD_VERIFIED_NOT_ADMISSION_V2',source_derivation_version=2,epoch=time.time(),materializer_content_root=ms['content_root_sha256'],source_mirror_required_files=263,source_files=len(payload),files=payload,full17_helper_AST_equal=True,materializer_only_four_whitelisted_functions_changed=True,worker_source_version=2,actual_prepare_preflight_stage_parent_SDK_PT_raw_canonical_operations=0,gate1='UNKNOWN',capture_interface_passed=False,stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(report=str(out),files=len(payload),text_bytes=sum(x['bytes']for x in payload.values()),helpers=17,unchanged_materializer_core_AST=True,actual_preflight=False,gate1='UNKNOWN'),indent=2))
