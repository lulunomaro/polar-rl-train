"""One NEW frozen current-nine assessment. Reuse proven V8 workers/plant/curricula.
Only model-selection metadata changes; no training, new audit framework or model I/O here.
"""
from pathlib import Path,PurePosixPath
import ast,copy,datetime,hashlib,io,json,shlex,sys,time,traceback,zipfile
T=Path(__file__).resolve().parent;A=T.parent/'mod4v1_current_nine_assessment_20261104';A.mkdir(exist_ok=True);(A/'reports').mkdir(exist_ok=True);out=A/'reports/STAGE_ONCE.json';assert not out.exists();H=lambda b:hashlib.sha256(b).hexdigest();B='/home/lc01/Zonglin Li/zonglin2';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';raw=(T/'reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json').read_bytes();old=json.loads(raw);oldroot=B+'/tasks/'+old['group_id'];catalog=json.loads((T/'MOD4V1_EIGHT_POSTTRAIN_CHECKPOINT_CATALOG_V1.json').read_bytes());reg=json.loads((T/'EXPERT_NORMALIZATION_REGISTRY_v12.json').read_bytes());entries={x['role']:x for x in catalog['rows']}
def find_best(x):
 if type(x)is dict:
  if 'per_role_scoped_best_source'in x:return x['per_role_scoped_best_source']
  for v in x.values():
   q=find_best(v)
   if q is not None:return q
 elif type(x)is list:
  for v in x:
   q=find_best(v)
   if q is not None:return q
best=find_best(reg);assert set(best)==set(entries)and len(entries)==8
for role,x in entries.items():assert x['selected_source']['path']==best[role]['path']and x['selected_source']['SHA']==best[role]['SHA']
contracts=json.loads((T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json').read_bytes())
case_dirs={'CURB_PROTECTED878':'PAIR1_RETENTION_V4_CLOSED_20261102_133121','CURB_INDEPENDENT113':'PAIR2_FROZEN_RETENTION_V1_CLOSED_20261102_140549','SLOPE135':'PAIR3_FROZEN_RETENTION_V1_CLOSED_20261102_144713'}
core_provenance={}
for role,dirname in case_dirs.items():
 p=T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports'/dirname/'cases'/role/'FINAL.json';r=p.read_bytes();f=json.loads(r);cache=f['source_cache'];assert cache['source_SHA']==entries[role]['selected_source']['SHA']and cache['physical_byte_opens']==cache['SHA_calls']==cache['decodes']==1;m=cache['metadata'];assert len(set(m['Adam17']))==1
 contracts[role]['source']=copy.deepcopy(entries[role]['selected_source']);c=contracts[role]['core'];c.update(original_iteration=m['iteration'],original_17Adam_step=m['Adam17'][0],original_LR=m['LR'],original_STD6=m['STD6']);core_provenance[role]=dict(published_metadata=str(p),bytes=len(r),SHA256=H(r),selected_model_SHA=cache['source_SHA'],expected_core=dict(iteration=m['iteration'],Adam17=m['Adam17'][0],LR=m['LR'],STD6=m['STD6']))
stamp=time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());gid='MOD4V1_CURRENT_NINE_FROZEN_ASSESSMENT_'+stamp;root=B+'/tasks/'+gid;plan=copy.deepcopy(old);plan.update(group_id=gid,GPU_UUID=gpu);selection=[]
for row in plan['roles']:
 role=row['role'];row['runtime_origin']=oldroot+'/runtimes/'+role;row['runtime_root']=root+'/runtimes/'+role;row['asset_dir']=row['asset_dir'].replace(oldroot,root)
 if role in entries:
  e=entries[role];src=e['selected_source'];row.update(source_path=src['path'],source_SHA=src['SHA']);row['source_bytes']=src.get('bytes',row['source_bytes'])
  if e['conservative_scope_selection']=='CANDIDATE':
   c=e['candidate_complete_checkpoint'];row.update(source_iteration=c['actual_saved_iteration'],source_Adam17=c['actual_Adam17_unique'][0],source_LR=c['actual_saved_LR'])
 if role in contracts:
  c=contracts[role];assert(row['source_SHA'],row['source_bytes'],row['source_iteration'],row['source_Adam17'],row['source_LR'])==(c['source']['SHA'],c['source']['bytes'],c['core']['original_iteration'],c['core']['original_17Adam_step'],c['core']['original_LR'])
 selection.append(dict(role=role,source_path=row['source_path'],source_SHA=row['source_SHA'],source_bytes=row['source_bytes'],iteration=row['source_iteration'],controls=row['controls'],selection=entries[role]['conservative_scope_selection']if role in entries else'FROZEN_H1_UNCHANGED',new_optimizer_updates=0))
S=T/'NINE_N80_PARALLEL_SOURCE_V8';E=T/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR';assets=T.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets';payload={}
for row in old['worker_files']:
 rel=row['relative'];p=assets/rel.removeprefix('pinned_assets/')if rel.startswith('pinned_assets/')else(S/Path(rel).name if '/parent/'in rel or rel=='single_gpu_group_supervisor.py'else E/Path(rel).name);b=p.read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA']),str(p)
 if rel=='worker_sources/e1/ROLE_CONTRACTS.json':b=json.dumps(contracts,indent=2,allow_nan=False).encode()
 if rel.endswith('.py'):ast.parse(b)
 payload[rel]=b
plan['worker_files']=[dict(relative=n,bytes=len(b),SHA=H(b))for n,b in sorted(payload.items())]
sys.path[:0]=[str(S),str(E)];from task_contract import make_task
from e1_group_scope import validate_group_task
for row in plan['roles']:
 task=make_task(row,plan,time.time()+3600,[41,42])
 if row['role']in contracts:assert validate_group_task(task,row['role'],root,root+'/cases/'+row['role'],contracts,environment={'CUDA_VISIBLE_DEVICES':gpu},fd_check=lambda fd:None)
assert len(plan['roles'])==9 and len({x['role']for x in plan['roles']})==9
(A/'MODEL_SELECTION.json').write_text(json.dumps(dict(kind='CURRENT_REGISTRY_V12_SCOPED_BEST_NINE_FROZEN_ONLY',seed=20260928,models=selection,core_provenance=core_provenance,weights_stat_hash_decode_operations=0,not_latest_failed_SM_candidates=True),indent=2),encoding='utf8');(A/'GROUP_PLAN_SOURCE.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED)as z:
 for n,b in payload.items():z.writestr(n,b)
archive=buf.getvalue();config=dict(kind='NEW_CURRENT_NINE_ORIGINAL_SCOPE_FROZEN_ASSESSMENT_STAGE_NOT_ADMISSION',root=root,group_id=gid,GPU_UUID=gpu,epoch=time.time(),models=selection,source_original_group=oldroot,optimizer_updates=0,stage_only=True)
with out.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(root)
 except FileNotFoundError:pass
 else:raise AssertionError('Fresh assessment root already exists')
 s.mkdir(root)
 with s.open(root+'/NONPT_GROUP_SOURCE.zip','wx')as f:f.write(archive)
 with s.open(root+'/GROUP_PLAN.json','wx')as f:f.write(json.dumps(plan,indent=2,allow_nan=False).encode())
 code=r'''from pathlib import Path
import json,hashlib,zipfile,shutil
B=Path(ROOT);P=json.loads((B/'GROUP_PLAN.json').read_bytes());NO={'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.pt2','.pkl','.pickle'}
with zipfile.ZipFile(B/'NONPT_GROUP_SOURCE.zip')as z:
 for r in P['worker_files']:
  rel=Path(r['relative']);assert not rel.is_absolute()and '..'not in rel.parts and rel.suffix.lower()not in NO;raw=z.read(r['relative']);assert(len(raw),hashlib.sha256(raw).hexdigest())==(r['bytes'],r['SHA']);p=B/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
indices=[]
for role in P['roles']:
 src=Path(role['runtime_origin']);dst=Path(role['runtime_root']);assert src.is_dir()and dst.is_relative_to(B/'runtimes')and not dst.exists();dst.mkdir(parents=True);paths=[];rows=[]
 for name in('runtime','lib','new_assets','original_field','job0/runtime'):
  q=src/name
  if q.is_dir():paths.extend(p for p in q.rglob('*')if p.suffix.lower()not in NO and p.is_file())
 paths.extend(p for p in src.glob('*.py')if p.is_file())
 for name in('original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_DERIVATION_INDEX.json','E1_CANONICAL_SOURCE_METADATA.json','MOD4V1_ASSET_DIFF.json','job0/original_run_manifest.json'):
  p=src/name
  if p.exists():paths.append(p)
 for p in sorted(set(paths)):
  assert p.suffix.lower()not in NO and not p.name.upper().startswith('TRAINING_BUDGET');rel=p.relative_to(src);raw=p.read_bytes();out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);rows.append(dict(relative=rel.as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 asset=Path(role['asset_dir']);asset.mkdir(parents=True,exist_ok=True)
 for p in(B/'pinned_assets').rglob('*'):
  if p.is_file():out=asset/p.relative_to(B/'pinned_assets');out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes())
 diff=dst/'MOD4V1_ASSET_DIFF.json'
 if diff.exists():
  d=json.loads(diff.read_bytes());assert d['new_USD_SHA']==P['asset_SHA']and d['new_contract_SHA']==P['contract_SHA'];case=B/'cases'/role['role'];case.mkdir(parents=True,exist_ok=True);(case/'MOD4V1_ASSET_DIFF.json').write_bytes(diff.read_bytes())
 if role['role']in('E0','E2','E3','W35'):assert diff.exists()
 assert hashlib.sha256((asset/'robot.usd').read_bytes()).hexdigest()==P['asset_SHA']and hashlib.sha256((asset/'import_contract.json').read_bytes()).hexdigest()==P['contract_SHA'];indices.append(dict(role=role['role'],files=len(rows),origin=str(src)))
(B/'ACTUAL_NONPT_RUNTIME_STAGE_INDEX.json').write_text(json.dumps(dict(staged=True,rows=indices,models_opened=0),indent=2))
print(json.dumps(dict(staged=True,roles=len(indices),runtime_files=sum(x['files']for x in indices),models_opened=0,SDK_started=False)))
'''.replace('ROOT',repr(root));ast.parse(code)
 i,o,e=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=600);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();config.update(returncode=rc,stdout=stdout,stderr=stderr)
 with (A/'reports/STAGE_RESULT.json').open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
 print(json.dumps(dict(root=root,returncode=rc,models=selection,stage_stdout=stdout,stage_stderr=stderr),indent=2));assert rc==0,stderr
finally:s.close();c.close()
