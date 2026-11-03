"""NEW D4 source mirror, with strict actual-wire proof and real flat20.
Read-only old payloads/sources. No remote, native, model or resource operation.
"""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,runpy,sys,time
R=Path(__file__).resolve().parent;WS=R.parent;D=R/'source_stage_good_expert_holdout_v4';dest=R/'payload_good_holdout_d4_wire_WORKSPACE';out=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D4_WIRE_SOURCE_PAYLOAD_V1.json';assert not dest.exists()and not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();sys.dont_write_bytecode=True;base=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3_FLAT20_FIX_V1.json').read_bytes());old=Path(base['payload_root']);blobs={}
for x in base['files']:
 rel=x['workspace_relative'];b=(old/Path(*PurePosixPath(rel).parts)).read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);blobs[rel]=b
sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert(len(sealraw),H(sealraw))==(2033,'a90f11f25b17d8a84caf5681d5ad8a5179f38b781e71118e161a0e5b1a0261a9');seal=json.loads(sealraw);assert not any(seal[x]for x in('enabled','staged','dispatched','source_native_enabled'))
def add(rel,pin):
 p=PurePosixPath(rel);assert not p.is_absolute()and '..'not in p.parts and p.suffix.lower()in('.py','.json','.md','.txt','.patch')and p.parts[0]in(R.name,'mod4v1_experts_fulldr_rm70_20261101');b=(WS/Path(*p.parts)).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256'])
 if rel in blobs:assert blobs[rel]==b
 blobs[rel]=b
for x in seal['files']:add((D/x['name']).relative_to(WS).as_posix(),x)
add((D/'SOURCE_SEAL.json').relative_to(WS).as_posix(),dict(bytes=len(sealraw),SHA256=H(sealraw)));mirror=json.loads((D/'SOURCE_MIRROR_INPUTS.json').read_bytes());assert len(mirror['files'])==92
for x in mirror['files']:add(x['workspace_relative'],x)
for rel,b in blobs.items():
 if rel.endswith('.py'):ast.parse(b)
 elif rel.endswith('.json'):json.loads(b)
dest.mkdir()
for rel,b in blobs.items():
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
stager=D/'stage_good_expert_holdout_v4.py';ns=runpy.run_path(str(stager),run_name='good_d4_source_mapping_only_v1');flat=base['flat_source_workspace_relative'];idx=base['source_index_workspace_relative'];m,receipt,_=ns['source_mappings'](dest/flat,dest/idx);assert len(m)==20 and ns['ORIGINAL_PLAN_PIN']==(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')and ns['PUBLISHED_ORIGINAL_PLAN_PIN']==(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
v=dict(kind='D4_STRICT_WIRE_AND_FLAT20_COMPLETE_LOCAL_SOURCE_PAYLOAD_NOT_STAGE',epoch=time.time(),payload_root=str(dest),files=[dict(workspace_relative=k,bytes=len(b),SHA256=H(b))for k,b in sorted(blobs.items())],unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),mirror_files=92,flat_source_workspace_relative=flat,source_index_workspace_relative=idx,original_complete_source_mapping_passed=20,entry_workspace_relative=(D/'stage_good_expert_holdout_v4.py').relative_to(WS).as_posix(),D4_seal_SHA256=H(sealraw),actual_remote_stage_parent_SDK_model_C_or_resource_operations=0,old_payloads_and_failures_unchanged=True,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','unique_files','total_bytes','mirror_files','original_complete_source_mapping_passed')},indent=2))
