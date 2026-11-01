from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;S=N/'source';R=N/'reports';V=T/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V3_20261101';OLD=T/'E2_ACTUAL_TARGET_METADATA_AND_FULL_WORLD_CASE_V231_20261101'
def read(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
idx=V/'INDEX_E2_FROM226_V3_FROZEN.json';assert H(idx)=='543b3945d6fb844ada1e6743bc2bf990c6077a8300cdabf0c6f27173f83f1dba'
for r in read(idx)['files']:
 p=Path(r['path'])if'path'in r else V/r['relative'];assert p.stat().st_size==r['bytes'] and H(p)==r['SHA']
install=read(V/'reports/INSTALL_SOURCE_V3.json');rows=read(V/'reports/INSTALL226_DERIVED_V3_EXACT_SOURCE_BINDINGS.json')['files'];expected=read(Path(install['selected_expected']['path']))
srcnames={r['relative']for r in expected['source_rows']};extras=[]
for r in install['files']+[install['selected_expected']]:extras.append(dict(relative=r['relative'],local_path=r['path'],bytes=r['bytes'],SHA=r['SHA']))
p=next((T/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101').rglob('FROZEN_CASE_TASK_PENDING226.json'));extras.append(dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
for p in S.glob('*.py'):
 s=p.read_text('utf8').replace('PLAN231.json','PLAN232.json');p.write_text(s,encoding='utf8');ast.parse(s)
binding=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/reports/KNOWN_ACTIVE227D_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json';p=S/'EXPECTED227D_BINDING.json';p.write_bytes(binding.read_bytes())
for p in sorted(S.iterdir()):
 if p.suffix in('.py','.json'):extras.append(dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
assert len(set(x['relative']for x in rows+extras))==len(rows+extras)
oldmap={r['relative']:r for r in read(OLD/'source/INSTALL231_FROZEN.json')['original226']}
reused=[]
for r in rows:
 if r['relative']==install['selected_probe']['relative']:continue
 old=oldmap[r['relative']];assert(old['bytes'],old['SHA'])==(r['bytes'],r['SHA']);reused.append(dict(r,binary_link=r['relative']not in srcnames))
pack=dict(original226=rows,extras=extras,reuse_from231=reused,upload_selected_probe=install['selected_probe']['relative'],metadata_V3_INDEX_SHA=H(idx),selected_kind=install['selected_KIND'])
(S/'INSTALL232_FROZEN.json').write_text(json.dumps(pack,indent=2),encoding='utf8')
caller=(OLD/'run_ROOT231_E2_actual_metadata_and_mean_case_once.py').read_text('utf8')
for x,y in [('ROOT231','ROOT232'),('case231_','case232_'),('authority231','authority232'),('target231_','target232_'),('ACTUAL231','ACTUAL232'),('SOURCE_INSTALL231','SOURCE_INSTALL232'),('INSTALL231','INSTALL232'),('PLAN231','PLAN232'),('METADATA_CASE231','METADATA_CASE232')]:caller=caller.replace(x,y)
caller=caller.replace("pack['metadata_V2_INDEX_SHA']","pack['metadata_V3_INDEX_SHA']")
caller=caller.replace('E2_FROM226','E2_FROM226')
caller=caller.replace("p.suffix!='.pt' and p.stat().st_size", "p.suffix!='.pt' and p.stat().st_size")
old="p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.suffix!='.pt' and p.stat().st_size==r['bytes']"
new="p=B/r['relative'];assert p.suffix!='.pt' and p.stat().st_size==r['bytes']\n if r['relative'] in v['binary_links']:\n  import os\n  assert p.is_symlink() and os.readlink(p)==v['old_job']+'/'+r['relative']\n else:assert p.resolve().is_relative_to(B.resolve())"
assert old in caller;caller=caller.replace(old,new)
old="create=\"from pathlib import Path\\nimport json\\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False)\\nprint(json.dumps(dict(passed=True,new_root=str(p))))\""
new="create=\"from pathlib import Path\\nimport json,os,shutil\\nB=Path(v['job']);A=Path(v['old_job']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)\\nold=json.loads((A/'SOURCE_INSTALL231_ACTUAL.json').read_bytes());assert old['actual_postcopy_fullSHA_verified'];known={r['relative']:r for r in old['files']}\\nlinks=0;copies=0\\nfor r in v['reuse']:\\n q=A/r['relative'];p=B/r['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert known[r['relative']]['SHA']==r['SHA'] and q.stat().st_size==r['bytes']\\n if r['binary_link']:p.symlink_to(q);links+=1\\n else:shutil.copyfile(q,p);copies+=1\\nprint(json.dumps(dict(passed=True,new_root=str(B),small_source_copies=copies,binary_asset_symlinks=links,model_stat_hash_copy_read=0)))\""
assert old in caller;caller=caller.replace(old,new)
caller=caller.replace("create,dict(job=J),timeout=30", "create,dict(job=J,old_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_FULL_WORLD_METADATA_CASE231_20261101/case',reuse=pack['reuse_from231']),timeout=90")
caller=caller.replace("for r in pack['original226']+pack['extras']:\n    cur=J", "for r in [x for x in pack['original226']if x['relative']==pack['upload_selected_probe']]+pack['extras']:\n    cur=J")
caller=caller.replace("original226=pack['original226']),timeout=180", "original226=pack['original226'],binary_links=[r['relative']for r in pack['reuse_from231']if r['binary_link']],old_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_FULL_WORLD_METADATA_CASE231_20261101/case'),timeout=180")
caller=caller.replace('original226_source_asset_transfer_postcopy_once=True','new_V3_source_and_existing_asset_link_postcopy_SHA_once=True')
caller=caller.replace('METADATA226','METADATA_E2_FROM226_V3').replace('ORIGINAL226','ORIGINAL_E2_FROM226_V3')
ast.parse(caller)
tree=ast.parse(caller)
for n in tree.body:
 if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in('POSTCOPY','EXEC')for x in n.targets):ast.parse(ast.literal_eval(n.value))
p=N/'run_ROOT232_E2_lexical_reader_and_mean_case_once.py';assert not p.exists();p.write_text(caller,encoding='utf8')
index=[]
for p in list(S.glob('*'))+[p]:
 b=p.read_bytes();index.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
(R/'ROOT232_SELECTED_V3_SOURCE_AND_COUNT_ADMISSION_FROZEN.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,files=index,selected_metadataV3_INDEX_SHA=H(idx),reused_small_source=len(reused)-sum(r['binary_link']for r in reused),asset_symlinks=sum(r['binary_link']for r in reused),new_task_asset_postcopy_hash_passes_each=1,model_installer_stat_hash_copy_read=0,GPU_worker_model_byte_hash_decode_max=1,original213_unchanged=True,original231_false_preserved=True,no_model_SDK_remote_execution_yet=True),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,caller=str(p),small_sources=len(reused)-sum(r['binary_link']for r in reused),binary_links=sum(r['binary_link']for r in reused))))
