"""Source-only explicit R/T mirror. No source-tree pruning, native or model work."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;WS=R.parent;T=WS/'mod4v1_experts_fulldr_rm70_20261101';M=R/'source_phase1_typed_capture_materializer_v1';dest=R/'payload_phase1_typed_capture_v1_WORKSPACE';out=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_CAPTURE_WORKSPACE_SOURCE_PAYLOAD_V1.json';assert not dest.exists()and not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();blobs={}
def add(root,relative,pin):
 rel=PurePosixPath(relative);assert not rel.is_absolute()and'..'not in rel.parts and rel.suffix.lower()in('.py','.json','.md','.txt','.patch');p=root/Path(*rel.parts);assert p.resolve().is_relative_to(root.resolve());b=p.read_bytes();assert(len(b),H(b))==(pin['bytes'],pin.get('SHA256',pin.get('sha256')));name=(p.relative_to(WS)).as_posix();assert name not in blobs or blobs[name]==b;blobs[name]=b
raw=(M/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(5312,'e9edbf414c5c386236a1eccb0b35d2e525a9339a4dd93d6365e6d645b5c9ebda');seal=json.loads(raw);assert len(seal['files'])==28 and seal['content_root_SHA256']=='4348259257b4a20dcddb41ad9d0f4f022657d08d33440a9ae41a66947a064413'
for x in seal['files']:add(M,x['relative'],x)
add(M,'SOURCE_SEAL.json',dict(bytes=5312,SHA256=H(raw)));mirror=json.loads((M/'SOURCE_MIRROR_INPUTS.json').read_bytes());assert mirror['file_count']==396 and(mirror['R_file_count'],mirror['T_file_count'])==(395,1)
for x in mirror['files']:
 assert x['root']in('R','T');root=R if x['root']=='R'else T
 if x['root']=='T':assert x['relative']=='NINE_N80_PARALLEL_SOURCE_V8/n80_gpu_capacity.py'and(x['bytes'],x['SHA256'])==(653,'ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc')
 add(root,x['relative'],x)
original=json.loads((R/'source_phase1_capture_materializer_v4/SOURCE_MIRROR_INPUTS.json').read_bytes());oldrows=original['files'];newrows={x['relative']:x for x in mirror['files']if x['root']=='R'};assert len(oldrows)==332
for x in oldrows:
 y=newrows[x['relative']];assert(x['bytes'],x['SHA256'])==(y['bytes'],y['SHA256'])
for rel,b in blobs.items():
 if rel.endswith('.py'):ast.parse(b)
 elif rel.endswith('.json'):json.loads(b)
dest.mkdir()
for rel,b in sorted(blobs.items()):
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
v=dict(kind='PHASE1_TYPED_CAPTURE_COMPLETE_EXPLICIT_R_T_SOURCE_PAYLOAD_NOT_STAGE_V1',epoch=time.time(),payload_root=str(dest),files=[dict(workspace_relative=k,bytes=len(b),SHA256=H(b))for k,b in sorted(blobs.items())],unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),mirror_files=396,R_mirror_files=395,T_mirror_files=1,materializer_members_including_seal=29,old_R_332_pins_unchanged=True,entry_workspace_relative=(M/'stage_phase1_typed_capture_v1.py').relative_to(WS).as_posix(),r_source_root_relative=R.name,t_source_root_relative=T.name,active_aliases=34,overlay_aliases=32,independent_baseline_bootstrap_aliases=2,full_original_static_runtime_bank_vendor_tree='NOT_MATERIALIZED_SOURCE_PAYLOAD_IS_NOT_A_SUBSTITUTE',actual_remote_preflight_stage_or_parent_SDK_model_raw_C_or_resource_operations=0,Gate1='UNKNOWN',stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','unique_files','total_bytes','mirror_files','R_mirror_files','T_mirror_files','active_aliases','stage2_GO')},indent=2))
