"""NEW local source/metadata mirror, not preflight, stage, dispatch or admission.
Preserve both named R/T sibling trees; no model/raw/resource or remote operations.
"""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;WS=R.parent;D=R/'source_stage_good_expert_holdout_v3';L=R/'source_good_holdout_lifecycle_routes_v1';dest=R/'payload_good_holdout_v3_WORKSPACE';out=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3.json';assert not dest.exists()and not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();blobs={};origins={}
def add(rel,pin=None):
 pos=PurePosixPath(rel);assert not pos.is_absolute()and '..'not in pos.parts and pos.parts[0]in(R.name,'mod4v1_experts_fulldr_rm70_20261101')and pos.suffix.lower()in('.py','.json','.md','.txt','.patch');p=WS/Path(*pos.parts);b=p.read_bytes()
 if pin is not None:assert(len(b),H(b))==(pin['bytes'],pin['SHA256'])
 if pos.suffix=='.py':ast.parse(b)
 if pos.suffix=='.json':json.loads(b)
 if rel in blobs:assert blobs[rel]==b
 blobs[rel]=b;origins[rel]=dict(bytes=len(b),SHA256=H(b))
for folder,expected in [(D,(2034,'0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426')),(L,(2748,'55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c'))]:
 raw=(folder/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==expected;seal=json.loads(raw);members=seal.get('files',seal.get('members'));assert members
 for x in members:add((folder/str(x['name'])).relative_to(WS).as_posix(),x)
 add((folder/'SOURCE_SEAL.json').relative_to(WS).as_posix(),dict(bytes=len(raw),SHA256=H(raw)))
manifest=json.loads((D/'SOURCE_MIRROR_INPUTS.json').read_bytes());assert len(manifest['files'])==79
for x in manifest['files']:add(x['workspace_relative'],x)
# All bytes and paths are validated before materializing any output.
dest.mkdir()
for rel,b in blobs.items():
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
 assert H(p.read_bytes())==origins[rel]['SHA256']
v=dict(kind='GOOD_HOLDOUT_V3_LOCAL_COMPLETE_WORKSPACE_SOURCE_PAYLOAD_NOT_STAGE',epoch=time.time(),payload_root=str(dest),mirror_declared_and_current_full_files=79,unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),files=[dict(workspace_relative=k,**origins[k])for k in sorted(blobs)],actual_remote_preflight_stage_parent_SDK_model_C_or_resource_operations=0,source_layer_only=True,actual_good_holdout_quality=None,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','mirror_declared_and_current_full_files','unique_files','total_bytes','actual_remote_preflight_stage_parent_SDK_model_C_or_resource_operations')},indent=2))
