"""NEW D7 source mirror/flat20; preserve D6 payload and actual failed run."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,runpy,sys,time
R=Path(__file__).resolve().parent;WS=R.parent;D=R/'source_stage_good_expert_holdout_v7';C=R/'source_good_holdout_case_final_contract_v3';dest=R/'payload_good_holdout_d7_case_final_v1_WORKSPACE';out=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D7_CASE_FINAL_SOURCE_PAYLOAD_V1.json';assert not dest.exists()and not out.exists();sys.dont_write_bytecode=True;H=lambda b:hashlib.sha256(b).hexdigest();base=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D6_TEACHER_SOURCE_PAYLOAD_V2.json').read_bytes());old=Path(base['payload_root']);blobs={}
for x in base['files']:
 rel=x['workspace_relative'];b=(old/Path(*PurePosixPath(rel).parts)).read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);blobs[rel]=b
base_blobs=dict(blobs);TNAME='mod4v1_experts_fulldr_rm70_20261101'
def add(rel,pin):
 p=PurePosixPath(rel);assert not p.is_absolute()and'..'not in p.parts and p.suffix.lower()in('.py','.json','.md','.txt','.patch')and p.parts[0]in(R.name,TNAME)
 b=blobs[rel]if rel in blobs else(WS/Path(*p.parts)).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256']);blobs[rel]=b
seals=[]
for root,n,sha,count,rootsha in[(D,1699,'88da829b7f9b6d4076e8cae14c367463b79285755b3f79a91e911fdad277142e',8,'1b2624e17e69046c7c8c5d7cbb6d8ec01dbbe97021dccfccbcd5fa4553003787'),(C,1090,'3b7356b5a9ca44b0b7e86e5bd73fd424919aa8dccf3a5ce43ea1d7bd1b99a658',4,'e524d81448cf8e007ddcb79ce1cbc28a96431194882af0d62a70e549583df535')]:
 raw=(root/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(n,sha);s=json.loads(raw);assert len(s['files'])==count and s['root_SHA256']==rootsha and not any(s[x]for x in('enabled','staged','dispatched','source_native_enabled'))
 for x in s['files']:add((root/x['name']).relative_to(WS).as_posix(),x)
 add((root/'SOURCE_SEAL.json').relative_to(WS).as_posix(),dict(bytes=n,SHA256=sha));seals.append(dict(directory=root.name,SHA256=sha,root_SHA256=rootsha))
mirror=json.loads((D/'SOURCE_MIRROR_INPUTS.json').read_bytes());assert len(mirror['files'])==164 and mirror['prior_mirror_rows']==145
old_mirror=json.loads(base_blobs[(R/'source_stage_good_expert_holdout_v6/SOURCE_MIRROR_INPUTS.json').relative_to(WS).as_posix()]);new_rows={x['workspace_relative']:x for x in mirror['files']};assert all(new_rows[x['workspace_relative']]==x for x in old_mirror['files'])
for x in mirror['files']:add(x['workspace_relative'],x)
idx=(C/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json').relative_to(WS).as_posix();active=json.loads(blobs[idx]);assert(len(blobs[idx]),H(blobs[idx]))==(21907,'aa22260f2198ad37d6bb265c85d870203536a5dec19c6e554a556244cc5cddda');old_index=json.loads(base_blobs[base['source_index_workspace_relative']]);old_rows={x['relative']:x for x in old_index['overlay_entries']};assert len(old_rows)==len(active['overlay_entries'])==20
flat=R.name+'/GOOD_HOLDOUT_ACTIVE20_D7';names=set();changes=[];allowed_T={WS/TNAME/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'/n for n in('worker_curb878_n80.py','worker_slope135_n80.py','e1_endpoint_predicate.py','ROLE_CONTRACTS.json')}
for row in active['overlay_entries']:
 alias=row['relative'];p=Path(row['path']);name=p.name;assert name not in names and(p.is_relative_to(R)or p in allowed_T)and p.suffix.lower()in('.py','.json');names.add(name);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
 if row!=old_rows[alias]:changes.append(alias)
 rel=flat+'/'+name;assert rel not in blobs;blobs[rel]=b
assert changes==['good_expert_holdout_runtime_v1.py']and all(blobs[k]==b for k,b in base_blobs.items())
for rel,b in blobs.items():
 if rel.endswith('.py'):ast.parse(b)
 elif rel.endswith('.json'):json.loads(b)
dest.mkdir()
for rel,b in blobs.items():
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
ns=runpy.run_path(str(D/'stage_good_expert_holdout_v7.py'),run_name='good_d7_source_mapping_only_v1');m,receipt,_=ns['source_mappings'](dest/flat,dest/idx);assert len(m)==20 and ns['INDEX_PIN']==(21907,'aa22260f2198ad37d6bb265c85d870203536a5dec19c6e554a556244cc5cddda')and ns['ORIGINAL_PLAN_PIN']==(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')
v=dict(kind='D7_FINITE_CASE_FINAL_CONTRACT_COMPLETE_LOCAL_SOURCE_PAYLOAD_NOT_STAGE_V1',epoch=time.time(),payload_root=str(dest),files=[dict(workspace_relative=k,bytes=len(b),SHA256=H(b))for k,b in sorted(blobs.items())],unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),mirror_files=164,flat_source_workspace_relative=flat,source_index_workspace_relative=idx,entry_workspace_relative=(D/'stage_good_expert_holdout_v7.py').relative_to(WS).as_posix(),original_complete_source_mapping_passed=20,overlay_changed_aliases=changes,all19_other_overlay_rows_unchanged=True,old207_payload_files_preserved_bytewise=True,new_active_flat20_separate_from_historical_flat20=True,seals=seals,actual_remote_prepare_preflight_stage_parent_SDK_model_C_or_resource_operations=0,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','unique_files','total_bytes','mirror_files','original_complete_source_mapping_passed','overlay_changed_aliases')},indent=2))
