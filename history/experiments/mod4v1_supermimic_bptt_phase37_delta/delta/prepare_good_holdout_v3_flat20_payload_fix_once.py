"""NEW packaging correction after the first real preflight failed before staging.
Keep the immutable 103-file two-tree mirror, add a distinct complete flat20 input
as required by the unchanged D3 source_mappings; no old source/caller is altered.
"""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,runpy,sys,time
R=Path(__file__).resolve().parent;WS=R.parent;out=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3_FLAT20_FIX_V1.json';dest=R/'payload_good_holdout_v3_flat20_WORKSPACE';assert not out.exists()and not dest.exists();H=lambda b:hashlib.sha256(b).hexdigest();sys.dont_write_bytecode=True
failed=json.loads((R/'reports/GOOD_HOLDOUT_V3_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert failed['returncode']==1 and "FileNotFoundError"in failed['stderr']and '/source_good_expert_holdout_subset_v1/a1_frozen_eval_runtime_v2.py'in failed['stderr'];base=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3.json').read_bytes());old=Path(base['payload_root']);blobs={}
for x in base['files']:
 rel=x['workspace_relative'];b=(old/Path(*PurePosixPath(rel).parts)).read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);blobs[rel]=b
idx_rel=R.name+'/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json';index=json.loads(blobs[idx_rel]);entries=index['overlay_entries'];assert len(entries)==20;flat_rel=R.name+'/good_holdout_complete_flat20_v1';names=set();present_old=[];missing_old=[]
for x in entries:
 path=Path(x['path']);assert path.resolve().is_relative_to(WS)and path.suffix in('.py','.json');b=path.read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);name=x['path'].replace('\\','/').rsplit('/',1)[-1];assert name not in names;names.add(name);blobs[flat_rel+'/'+name]=b
 original_source_dir=R/'source_good_expert_holdout_subset_v1';(present_old if(original_source_dir/name).is_file()else missing_old).append(name)
assert len(blobs)==123 and 'a1_frozen_eval_runtime_v2.py'in missing_old
# Validate all original source bytes before creating output directories.
for rel,b in blobs.items():
 if rel.endswith('.py'):ast.parse(b)
 elif rel.endswith('.json'):json.loads(b)
dest.mkdir()
for rel,b in blobs.items():
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
# Complete original module; only its source-mapping function executes, never main/prepare/stage.
stager=R/'source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py';sraw=stager.read_bytes();assert(len(sraw),H(sraw))==(53062,'a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11');ns=runpy.run_path(str(stager),run_name='good_flat20_source_mapping_only_v1');mapping,receipt,_=ns['source_mappings'](dest/flat_rel,dest/idx_rel);assert len(mapping)==20 and not any(n.split('.')[0]in{'torch','isaacsim','isaaclab','omni'}for n in sys.modules)
v=dict(kind='GOOD_HOLDOUT_V3_NEW_FLAT20_SOURCE_PAYLOAD_FIX_NOT_STAGE',epoch=time.time(),payload_root=str(dest),flat_source_workspace_relative=flat_rel,source_index_workspace_relative=idx_rel,files=[dict(workspace_relative=k,bytes=len(b),SHA256=H(b))for k,b in sorted(blobs.items())],unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),original_mirror_files=103,added_complete_flat20=20,whole_original_source_mappings_local_passed=True,source_mapping_count=len(mapping),first_failed_root=failed['root'],first_failure='PARENT_PACKAGING_SUPPLIED_LOGICAL_MIRROR_DIRECTORY_NOT_REQUIRED_PHYSICAL_FLAT20',first_failure_original_overlay_present=present_old,first_failure_original_overlay_missing=missing_old,old_stager_source_unchanged=True,actual_remote_stage_parent_SDK_model_C_or_resource_operations=0,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','unique_files','total_bytes','source_mapping_count','first_failure_original_overlay_missing')},indent=2))
