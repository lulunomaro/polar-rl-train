"""Finish only two absent small files; preserve exact original raw manifest SHA."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parents[1];T=L.parent;W=T.parent;R=B/'reports'
CODE=r'''
from pathlib import Path
import base64,hashlib,importlib.metadata as md,json,os,time
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,value):
 with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');craw=C.read_bytes();c=json.loads(craw)
assert c['active_segment'] is None and c['remaining_training_seconds']==539450.9840764999 and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
values={};versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
for key in ('h1','e3'):
 s=v['targets'][key];old=Path(s['old_job']);new=Path(s['new_job']);assert new.is_dir() and not new.is_symlink()
 assert not (new/'GO_PRODUCTION.json').exists() and not (new/'job0/GO_PRODUCTION.json').exists() and not (new/'adaptation').exists() and not (new/'job0/production').exists()
 cpu=Path(s['CPU_path']);wait=Path(s['CPU_proof_path']);assert H(cpu)==s['source_CPU_SHA'] and H(wait)==s['CPU_waited_proof_SHA'];cv=json.loads(cpu.read_bytes());wv=json.loads(wait.read_bytes())
 assert cv['passed'] and cv['source_SHA']==s['source_SHA'] and cv['worker_SHA']==s['worker_SHA'] and wv['actual_waited'] and wv['returncode']==0 and wv['report_SHA']==s['source_CPU_SHA']
 if key=='h1':
  path=new/s['extension_name'];ext=json.loads(path.read_bytes());assert ext['passed'] and ext['key']==key and ext['new_job']==str(new) and ext['base_actual_fullstate_CPU_SHA']==s['source_CPU_SHA'] and ext['base_actual_waited_proof_SHA']==s['CPU_waited_proof_SHA']
  assert H(new/s['manifest_name'])==s['base_manifest_SHA'] and ext['payload_manifest_SHA']==s['base_manifest_SHA']
  values[key]=dict(extension=ext,extension_SHA=H(path),extension_path=str(path),already_complete_reused_without_write=True);continue
 manifest=old/s['manifest_name'];assert H(manifest)==s['base_manifest_SHA'];rows=[]
 for row in json.loads(manifest.read_bytes())['files']:
  rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;src=old/rel;dest=new/rel
  assert src.resolve()==src and dest.resolve()==dest and dest.is_file() and src.stat().st_size==dest.stat().st_size==row['bytes']
  if src.suffix.lower() in ('.pt','.npz','.usd','.zip') and row['bytes']>1024**2:
   assert os.stat(src).st_ino==os.stat(dest).st_ino and os.stat(src).st_dev==os.stat(dest).st_dev;kind='immutable_input_hardlink_existing_actual_producer_fullSHA_reused'
  else:assert H(src)==H(dest)==row['SHA'];kind='source_text_copy_fullSHA'
  rows.append(dict(relative=row['relative'],bytes=row['bytes'],SHA=row['SHA'],copy_kind=kind))
 added=new/'runtime/assets/import_contract.json';assert H(added)==H(new/'runtime/isaac/mod4/import_contract.json')=='517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
 raw=base64.b64decode(v['new_E3_manifest_base64']);assert hashlib.sha256(raw).hexdigest()==s['new_manifest_SHA'];target=new/s['manifest_name'];assert not target.exists()
 with target.open('xb') as f:f.write(raw)
 assert H(target)==s['new_manifest_SHA'];path=new/s['extension_name'];assert not path.exists()
 ext=dict(passed=True,kind='MOD4_96A_SAME_SOURCE_NAMESPACE_AND_EXACT_ASSET_ROUTE_EXTENSION_V1',key=key,epoch=time.time(),old_job=str(old),new_job=str(new),source_SHA=s['source_SHA'],worker_SHA=s['worker_SHA'],base_actual_fullstate_CPU_SHA=s['source_CPU_SHA'],base_actual_fullstate_CPU_path=str(cpu),base_actual_fullstate_CPU_value=cv,base_actual_waited_proof_SHA=s['CPU_waited_proof_SHA'],base_actual_waited_proof_path=str(wait),base_actual_waited_proof_value=wv,existing_actual_installed_versions=versions,original95_failed_resource_only_not_model_source=True,original95_actual_charged_seconds=19.7827205657959,no_new_model_decode_or_Torch_SDK_GPU_import=True,no_model_bytes_rehashed_for_Git_or_model_CPU_rerun=True,source_copy_rows=rows,actual_GPU_fullrestore_native_and_new_policy_still_pending=True,sole_new_relative='runtime/assets/import_contract.json',added_source_contract_SHA=H(added),existing_adjacent_mod4_contract_SHA=H(new/'runtime/isaac/mod4/import_contract.json'),only_add_missing_actual_RM_MOD4_USD_parent_dependency=True,payload_manifest_SHA=s['new_manifest_SHA'],raw_original_manifest_bytes_preserved=True,missing_only_after_original_CRLF_text_transport_error=True)
 put(path,ext);values[key]=dict(extension=ext,extension_SHA=H(path),extension_path=str(path))
assert C.read_bytes()==craw
print(json.dumps(dict(passed=True,actual_returned=True,extensions=values,canonical_None=True,remaining=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(craw).hexdigest(),only_missing_E3_manifest_and_extension_written=True,no_new_model_CPU_GPU_GO_or_account_write=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 put('MISSING_ONLY_V2_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),no_old_once_rerun=True))
 request=json.loads((B/'EXACT_RAW_MISSING_ONLY_REQUEST.json').read_bytes());sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same96a_missing_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('same96a_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install();secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None;value=d.code(client,d.PY72,CODE,request,timeout=90);put('TWO96A_MISSING_ONLY_EXACT_RAW_EXTENSIONS_RETURNED_ACTUAL_V2.json',value)
  print(json.dumps(dict(passed=value['passed'],extensions={k:dict(SHA=x['extension_SHA'],path=x['extension_path']) for k,x in value['extensions'].items()})))
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('MISSING_ONLY_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry=True));raise
