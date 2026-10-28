"""New unused input-only namespaces. No Torch/SDK/GPU load or account writer."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
CODE=r'''
from pathlib import Path
import hashlib,importlib.metadata as md,json,os,psutil,shutil,subprocess,time
TASKS=Path('/home/lc01/Zonglin Li/zonglin2/tasks');C=TASKS.parent/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,value):
 with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['remaining_training_seconds']==539450.9840764999 and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
old_owner=Path(v['old_owner']);final=json.loads((old_owner/'COHORT_FINAL.json').read_bytes());assert final['original_cost_settled'] is True
segments=[a for a in c['completed_segments'] if a.get('owner_parent_pid')==589937 and set(a.get('experts',{}))=={'h1','e3'} and all(a['experts'][k]['started_epoch']==final['go'][k]['learning_started_epoch'] for k in ('h1','e3'))]
assert len(segments)==1 and segments[0]['charged_expert_seconds']==19.7827205657959
versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
resource={}
for key,gpu in v['GPUS'].items():
 apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert gpu not in apps
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')]
 assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669
 resource[key]=dict(epoch=time.time(),GPU_UUID=gpu,GPU_line=line,compute_UUID_only_rows=0)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(TASKS).free>25*1024**3
values={}
for key in ('h1','e3'):
 s=v['targets'][key];old=Path(s['old_job']);new=Path(s['new_job']);assert old.resolve()==old and new.resolve().is_relative_to(TASKS) and not new.parent.exists()
 manifest_path=old/s['manifest_name'];assert H(manifest_path)==s['base_manifest_SHA'];manifest=json.loads(manifest_path.read_bytes())
 cpu=Path(s['CPU_path']);wait=Path(s['CPU_proof_path']);assert H(cpu)==s['source_CPU_SHA'] and H(wait)==s['CPU_waited_proof_SHA'];cv=json.loads(cpu.read_bytes());wv=json.loads(wait.read_bytes())
 assert cv['passed'] and cv['source_SHA']==s['source_SHA'] and cv['worker_SHA']==s['worker_SHA'] and wv['actual_waited'] is True and wv['returncode']==0 and wv['report_SHA']==s['source_CPU_SHA']
 new.mkdir(parents=True,mode=0o700);rows=[]
 # Only sealed manifest inputs. Existing outputs, GO, runtime binding and old once markers are excluded.
 for row in manifest['files']:
  rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
  assert not any(p in rel.parts for p in ('production','adaptation','clock_native50')) and rel.name not in ('GO_PRODUCTION.json','FLAT90_RUNTIME_GRANT_BINDING.json')
  src=old/rel;dest=new/rel;assert src.resolve()==src and src.is_file() and src.stat().st_size==row['bytes'];dest.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix.lower() in ('.pt','.npz','.usd','.zip') and src.stat().st_size>1024**2:
   # Exact same immutable input inode; preserve producer fullSHA without another model-byte read.
   os.link(src,dest);assert os.stat(src).st_ino==os.stat(dest).st_ino and os.stat(src).st_dev==os.stat(dest).st_dev
   kind='immutable_input_hardlink_existing_actual_producer_fullSHA_reused'
  else:
   assert H(src)==row['SHA'];shutil.copy2(src,dest);assert H(dest)==row['SHA'];kind='source_text_copy_fullSHA'
  rows.append(dict(relative=row['relative'],bytes=row['bytes'],SHA=row['SHA'],copy_kind=kind))
 if key=='h1':
  shutil.copy2(manifest_path,new/s['manifest_name']);assert H(new/s['manifest_name'])==s['base_manifest_SHA']
  extra=dict(only_namespace_and_GO_alias_projection_changed=True,source_payload_bytes_unchanged=True,payload_manifest_SHA=s['base_manifest_SHA'])
 else:
  source=old/'runtime/isaac/mod4/import_contract.json';assert H(source)=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
  dest=new/'runtime/assets/import_contract.json';assert not dest.exists();shutil.copy2(source,dest);assert H(dest)==H(source)
  text=v['new_E3_manifest_UTF8'];assert hashlib.sha256(text.encode()).hexdigest()==s['new_manifest_SHA']
  with (new/s['manifest_name']).open('x',encoding='utf8',newline='') as f:f.write(text)
  extra=dict(sole_new_relative='runtime/assets/import_contract.json',added_source_contract_SHA=H(dest),existing_adjacent_mod4_contract_SHA=H(new/'runtime/isaac/mod4/import_contract.json'),only_add_missing_actual_RM_MOD4_USD_parent_dependency=True,payload_manifest_SHA=s['new_manifest_SHA'])
  source_code=(new/'runtime/isaac/mod4/mod4_task.py').read_text()
  assert 'Path(_ENV_USD).resolve().parent' in source_code and '(MOD4_ISAAC / "import_contract.json")' in source_code
 extension=dict(passed=True,kind='MOD4_96A_SAME_SOURCE_NAMESPACE_AND_EXACT_ASSET_ROUTE_EXTENSION_V1',key=key,epoch=time.time(),old_job=str(old),new_job=str(new),source_SHA=s['source_SHA'],worker_SHA=s['worker_SHA'],base_actual_fullstate_CPU_SHA=s['source_CPU_SHA'],base_actual_fullstate_CPU_path=str(cpu),base_actual_fullstate_CPU_value=cv,base_actual_waited_proof_SHA=s['CPU_waited_proof_SHA'],base_actual_waited_proof_path=str(wait),base_actual_waited_proof_value=wv,existing_actual_installed_versions=versions,original95_failed_resource_only_not_model_source=True,original95_actual_charged_seconds=19.7827205657959,no_new_model_decode_or_Torch_SDK_GPU_import=True,no_model_bytes_rehashed_for_Git_or_model_CPU_rerun=True,source_copy_rows=rows,actual_GPU_fullrestore_native_and_new_policy_still_pending=True,**extra)
 path=new/s['extension_name'];put(path,extension);values[key]=dict(extension=extension,extension_SHA=H(path),extension_path=str(path))
assert C.read_bytes()==raw
print(json.dumps(dict(passed=True,actual_returned=True,extensions=values,resources=resource,canonical_None=True,remaining=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(raw).hexdigest(),no_GPU_model_load_GO_or_account_write=True)))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 put('TWO96A_INPUT_SOURCE_EXTENSION_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),no_GPU_GO_or_new_model_CPU=True))
 request=json.loads((B/'TWO96A_INPUT_NAMESPACE_SOURCE_REQUEST.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('two96a_same_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('two96a_same_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None;value=d.code(client,d.PY72,CODE,request,timeout=120)
  put('TWO96A_INPUT_NAMESPACE_AND_EXACT_ASSET_SOURCE_EXTENSIONS_RETURNED_ACTUAL.json',value)
  print(json.dumps(dict(passed=value['passed'],extensions={k:dict(SHA=x['extension_SHA'],path=x['extension_path']) for k,x in value['extensions'].items()},no_new_model_CPU_GPU_GO_or_account=True)),flush=True)
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO96A_SOURCE_EXTENSION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_old95_rearm=True));raise
