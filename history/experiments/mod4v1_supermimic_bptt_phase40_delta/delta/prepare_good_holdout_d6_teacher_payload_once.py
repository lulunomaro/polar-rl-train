"""NEW D6 workspace mirror and separate active flat20; no old payload overwrite."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,runpy,sys,time
R=Path(__file__).resolve().parent;WS=R.parent;D=R/'source_stage_good_expert_holdout_v6';C=R/'source_good_holdout_teacher_schema_v2';dest=R/'payload_good_holdout_d6_teacher_WORKSPACE';out=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D6_TEACHER_SOURCE_PAYLOAD_V1.json';assert not dest.exists()and not out.exists();sys.dont_write_bytecode=True;H=lambda b:hashlib.sha256(b).hexdigest();base=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D5_ROOT_SOURCE_PAYLOAD_V1.json').read_bytes());old=Path(base['payload_root']);blobs={}
for x in base['files']:
 rel=x['workspace_relative'];b=(old/Path(*PurePosixPath(rel).parts)).read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);blobs[rel]=b
base_blobs=dict(blobs)
def add(rel,pin):
 p=PurePosixPath(rel);assert not p.is_absolute()and '..'not in p.parts and p.suffix.lower()in('.py','.json','.md','.txt','.patch')and p.parts[0]in(R.name,TNAME);b=(WS/Path(*p.parts)).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256']);assert rel not in blobs or blobs[rel]==b;blobs[rel]=b
TNAME='mod4v1_experts_fulldr_rm70_20261101';seals=[]
for root,n,sha,count,rootsha in[(D,1699,'c3d6164ee5edc8fc05dbf2741bd99b3df447b1cbe9f0abf652f82cb0111d952d',8,'976a1370e4ab6550a004c4ec621694e228a61174bf94eeac68ac797decff4bc2'),(C,1247,'4951037f9df73e05d1ffdb16f66697e6e99c6ecdcfb2be862c7f323d9eaa97c1',5,'4b3076d0cb187bd88f22699996f6b8dea9ec8650707ff75fbea204ac95ce9301')]:
 raw=(root/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(n,sha);s=json.loads(raw);assert len(s['files'])==count and s['root_SHA256']==rootsha and not any(s[x]for x in('enabled','staged','dispatched','source_native_enabled'))
 for x in s['files']:add((root/x['name']).relative_to(WS).as_posix(),x)
 add((root/'SOURCE_SEAL.json').relative_to(WS).as_posix(),dict(bytes=n,SHA256=sha));seals.append(dict(directory=root.name,SHA256=sha,root_SHA256=rootsha))
mirror=json.loads((D/'SOURCE_MIRROR_INPUTS.json').read_bytes());assert mirror['files_count']==len(mirror['files'])==145 and mirror['previous127_members_unchanged']
for x in mirror['files']:add(x['workspace_relative'],x)
idx=(C/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json').relative_to(WS).as_posix();active=json.loads(blobs[idx]);assert (len(blobs[idx]),H(blobs[idx]))==(21472,'0012cf17c566e29648418a191a89e1e925db5df8406718f9e0c39b87c83780da');old_index=json.loads(base_blobs[base['source_index_workspace_relative']]);old_rows={x['relative']:x for x in old_index['overlay_entries']};assert len(old_rows)==len(active['overlay_entries'])==20
flat=R.name+'/GOOD_HOLDOUT_ACTIVE20_D6';basenames=set();changes=[]
for row in active['overlay_entries']:
 alias=row['relative'];name=Path(row['path']).name;assert name not in basenames;basenames.add(name);p=Path(row['path']);assert p.is_relative_to(R)and p.suffix.lower()in('.py','.json');b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
 if row!=old_rows[alias]:changes.append(alias)
 rel=flat+'/'+name;assert rel not in blobs;blobs[rel]=b
assert sorted(changes)==['good_expert_holdout_runtime_v1.py','producer_teacher_guard_v1.py']and all(blobs[k]==b for k,b in base_blobs.items())
for rel,b in blobs.items():
 if rel.endswith('.py'):ast.parse(b)
 elif rel.endswith('.json'):json.loads(b)
dest.mkdir()
for rel,b in blobs.items():
 p=dest/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(b)
ns=runpy.run_path(str(D/'stage_good_expert_holdout_v6.py'),run_name='good_d6_source_mapping_only_v1');m,receipt,_=ns['source_mappings'](dest/flat,dest/idx);assert len(m)==20 and ns['INDEX_PIN']==(21472,'0012cf17c566e29648418a191a89e1e925db5df8406718f9e0c39b87c83780da')and ns['ORIGINAL_PLAN_PIN']==(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')
v=dict(kind='D6_RAW_TEACHER_COMPATIBILITY_COMPLETE_LOCAL_SOURCE_PAYLOAD_NOT_STAGE',epoch=time.time(),payload_root=str(dest),files=[dict(workspace_relative=k,bytes=len(b),SHA256=H(b))for k,b in sorted(blobs.items())],unique_files=len(blobs),total_bytes=sum(map(len,blobs.values())),mirror_files=145,flat_source_workspace_relative=flat,source_index_workspace_relative=idx,entry_workspace_relative=(D/'stage_good_expert_holdout_v6.py').relative_to(WS).as_posix(),original_complete_source_mapping_passed=20,overlay_changed_aliases=changes,all18_other_overlay_rows_unchanged=True,old169_payload_files_preserved_bytewise=True,new_active_flat20_separate_from_historical_flat20=True,seals=seals,actual_remote_prepare_preflight_stage_parent_SDK_model_C_or_resource_operations=0,stage2_GO=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps({k:v[k]for k in('kind','payload_root','unique_files','total_bytes','mirror_files','original_complete_source_mapping_passed','overlay_changed_aliases')},indent=2))
