"""NEW local source verification/payload manifest only; never SDK, PT or dispatch."""
from pathlib import Path,PurePosixPath
import ast,json,hashlib,time
R=Path(__file__).resolve().parent
out=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V1.json'
assert not out.exists(),'Payload source purpose already consumed'
cache={};payload={}
def H(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return H(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode())
def safe(rel):
 p=PurePosixPath(rel);assert not p.is_absolute() and all(x not in ('','.','..') for x in p.parts) and ':' not in rel and '\\' not in rel
 assert p.suffix.lower() in ('.py','.json','.md','.txt'),'Text-source only before stat/read'
 return p

def raw_at(rel):
 p=safe(rel);path=R.joinpath(*p.parts);assert path.resolve().is_relative_to(R) and not path.is_symlink()
 if rel not in cache:cache[rel]=path.read_bytes()
 return cache[rel]
def add(remote,local,expected):
 safe(remote);raw=raw_at(local);sha=expected.get('SHA256',expected.get('sha256'));assert (len(raw),H(raw))==(expected['bytes'],sha),local
 if remote in payload:assert payload[remote]['local_relative']==local
 payload[remote]=dict(local_relative=local,bytes=len(raw),SHA256=H(raw))
def package(folder,root,members):
 rel=folder+'/SOURCE_SEAL.json';raw=raw_at(rel);seal=json.loads(raw);assert seal['content_root_sha256']==root and canonical(seal['files'])==root
 rows=seal['files'];rows=[dict(relative=k,**v)for k,v in rows.items()]if isinstance(rows,dict)else rows
 assert len(rows)==members
 for row in rows:add('source_mirror/'+folder+'/'+row['relative'],folder+'/'+row['relative'],row)
 add('source_mirror/'+rel,rel,dict(bytes=len(raw),SHA256=H(raw)))
 return seal
mfolder='source_phase1_capture_materializer_v1'
ms=package(mfolder,'c5544ff6d42cfba26df3c9f47b3dd33edc4fb086918718147f3313459c5a666b',10)
mirror=json.loads(raw_at(mfolder+'/SOURCE_MIRROR_INPUTS.json'));assert mirror['file_count']==len(mirror['files'])==259
for row in mirror['files']:add('source_mirror/'+row['relative'],row['relative'],row)
package('source_phase1_capture_controller_v1','3166b4e9a97e97bb596a56dd68162e73f5c357e279ca4c0f47779e47c4a40292',5)
old=raw_at('source_bound_only_native_integration_v1/stage_bound_only_native_v1.py');assert(len(old),H(old))==(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40')
new=raw_at(mfolder+'/static_source_helpers_v1.py')
funcs=lambda raw:{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
a,b=funcs(old),funcs(new);assert len(b)==17 and all(a[k]==v for k,v in b.items())
for rel,raw in cache.items():
 if rel.endswith('.py'):ast.parse(raw)
value=dict(kind='NEW_PHASE1_CAPTURE_LOCAL_SOURCE_PAYLOAD_VERIFIED_NOT_ADMISSION_V1',epoch=time.time(),materializer_content_root=ms['content_root_sha256'],source_mirror_required_files=259,source_files=len(payload),files=payload,full17_helper_AST_equal=True,actual_prepare_preflight_stage_parent_SDK_PT_raw_canonical_operations=0,gate1='UNKNOWN',capture_interface_passed=False,stage2_GO=False)
with out.open('x',encoding='utf-8')as f:json.dump(value,f,indent=2)
print(json.dumps(dict(report=str(out),files=len(payload),text_bytes=sum(x['bytes']for x in payload.values()),helpers=17,actual_preflight=False,gate1='UNKNOWN'),indent=2))
