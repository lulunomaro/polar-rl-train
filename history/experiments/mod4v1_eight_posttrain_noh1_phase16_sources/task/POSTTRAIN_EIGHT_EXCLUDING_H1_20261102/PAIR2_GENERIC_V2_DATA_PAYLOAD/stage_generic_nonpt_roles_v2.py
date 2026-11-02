"""Data-driven original full20k runtime+source staging. No role-string code replacement.
Does NOT launch owner/SDK, stat/hash/read selected PT, acquirelocks or read/write C.
NEW unused group root only. Source manifests are not training Ready.
"""
from pathlib import Path
import os,sys,json,hashlib,shutil,ast,importlib.util
NO={'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.partial'}
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
ROLES={'E2','E3','W35','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'}
IMMUTABLE_JSON={'original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_DERIVATION_INDEX.json','MOD4V1_ASSET_DIFF.json','E1_CANONICAL_SOURCE_METADATA.json','VARIANT_SOURCE_METADATA.json','CPU_FOUR_LEAF_ACTUAL_COMPLETE.json','CPU_FULL_NESTED_OWNER_AUDIT.json','NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json'}

def put(p,v):
 with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 B=Path(sys.argv[1]).resolve();assert B.is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))
 assert not(B/'STAGE_COMPLETE.json').exists()and not(B/'OWNER_STARTED.json').exists()
 P=json.loads((B/'SOURCE_PLAN.json').read_bytes());assert P['H1_excluded']and len(P['entries'])==2 and len({e['role']for e in P['entries']})==2
 rows=[]
 for e in P['entries']:
  assert e['role']in ROLES and e['native0pt_evidence_file']=='evidence/NEW_ASSET_NATIVE_ACTUAL.json'
  assert e['source_family']in('e0_e2_e3','e1','w35')and e['num_envs']==20000 and e['max_additional_updates']==20
  src=Path(e['base_root']).resolve();dst=Path(e['job_root']).resolve();assert src.is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))and dst.is_relative_to(B/'roles')and not dst.exists();dst.mkdir(parents=True)
  def ignore(path,names):return[n for n in names if n=='__pycache__'or Path(n).suffix.lower()in NO or n.endswith(('.jsonl','.log'))]
  for name in('runtime','lib','original_field','new_assets','assets'):
   if(src/name).is_dir():shutil.copytree(src/name,dst/name,ignore=ignore,dirs_exist_ok=False)
  for f in src.iterdir():
   # Suffix check first: checkpoint files even at source-root are not stat/read.
   if(f.suffix=='.py'or f.name in IMMUTABLE_JSON)and f.is_file():shutil.copy2(f,dst/f.name)
  upload=B/'uploads'/e['role'];new_python=set()
  for f in upload.rglob('*'):
   assert f.suffix.lower()not in NO
   if f.is_file():
    relative=f.relative_to(upload);target=dst/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
    if f.suffix=='.py':new_python.add(relative.as_posix())
  for r in e['required_immutable_files']:
   p=dst/r['relative'];assert p.is_file(),str(p)
   if r.get('SHA'):assert sha(p)==r['SHA'],str(p)
  assert sha(dst/'runtime/assets/robot.usd')==USD and sha(dst/'runtime/assets/import_contract.json')==CONTRACT
  if e['source_family']=='w35':
   # Builder mayseal its dedicated derivation over only new worker/protocol inputs,
   # never rewrites old originalderivation or original-run metadata.
   sys.path.insert(0,str(dst));from w35_posttrain_source_builder_v2 import create_derivation_from_installed_source
   create_derivation_from_installed_source(dst)
  files=[]
  for f in sorted(dst.rglob('*')):
   assert f.suffix.lower()not in NO,str(f)
   if f.is_file():
    raw=f.read_bytes()
    if f.relative_to(dst).as_posix()in new_python:ast.parse(raw.decode('utf-8-sig'))
    assert not f.name.upper().startswith('TRAINING_BUDGET')
    files.append(dict(relative=f.relative_to(dst).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
  m=dict(kind=e.get('install_kind','MOD4V1_POSTTRAIN_ACTUAL_NONPT_INSTALL'),source_PT_copied=False,source_model_metadata=e['source_model_metadata'],asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,files=files)
  put(dst/e['manifest_file'],m);mh=sha(dst/e['manifest_file'])
  if e['source_family']=='e0_e2_e3':
   sys.path.insert(0,str(dst));from construct_source_task_go_v1 import build_task_go
   e['task_template'],e['go_template']=build_task_go(e['role'],job_root=str(dst),run_id=P['run_id'],role_key=e['role_key'],GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',worker_SHA=sha(dst/('worker_posttrain_'+e['role'].lower()+'_v1.py')),common_SHA=sha(dst/'posttrain_fullstate_common_v1.py'),descriptor_SHA=sha(dst/(e['role']+'_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json')),manifest_SHA=mh,root_admission_SHA='0'*64,owner_parent_pid=0,learning_started_epoch=0.)
  elif e['source_family']=='e1':
   t=e['task_template'];t.update(new_job_root=str(dst),asset_dir=str(dst/'runtime/assets'));assert t['source_SHA']==e['source_SHA']and t['seed']==20260928
  else:
   from w35_posttrain_source_builder_v2 import build_source_templates
   e['task_template'],e['go_template']=build_source_templates(job_root=dst,run_id=P['run_id'],role_key=e['role_key'],manifest_SHA=mh)
  # Drafts remain only inside source plan; never publish TASK/GO/Ready/admission.
  assert not(dst/'TASK.json').exists()and not(dst/'GO_PRODUCTION.json').exists()and not(dst/'ROOT_ADMISSION_ACTUAL.json').exists()
  rows.append(dict(role=e['role'],nonPTfiles=len(files),manifest_SHA=mh,base_root=str(src),job_root=str(dst),task_go_drafts_not_actual=True))
 put(B/'OWNER_PLAN.json',P);put(B/'STAGE_COMPLETE.json',dict(kind='ACTUAL_NONPT_SOFTWARE_STAGED_NOT_TRAINING_READY',rows=rows,selected_PT_stat_hash_decode=0,SDK_GPU_GO_C_or_lock_operations=0,owner_not_launched=True))
 print(json.dumps(dict(root=str(B),roles=rows,selected_PT_SDK_GO_C_operations=0,owner_not_launched=True)))
if __name__=='__main__':main()
