"""Finish only the unexecuted metadata publisher; no source copy/model reread."""
from pathlib import Path
import importlib.util,ast,json,hashlib,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/prepare_unused89D_V5_source_and_original_failure_resource_binding_once.py'
sp=importlib.util.spec_from_file_location('previous_publisher_definitions_not_old_main',P);q=importlib.util.module_from_spec(sp);sp.loader.exec_module(q)
code=q.EXTEND;a=code.index('expected=previous.replace');b=code.index('assert expected==new',a)
replacement="anchor=b' def work(runner,n,log_dir):';pos=previous.index(anchor)+len(anchor);eol=bytes([13,10]) if previous[pos:pos+2]==bytes([13,10]) else bytes([10])\nexpected=previous.replace(anchor+eol,anchor+eol+b'  runner.logger.writer=None'+eol,1).replace(b'  runner.logger.writer=None;completed=0;',b'  completed=0;',1)\n"
code=code[:a]+replacement+code[b:];ast.parse(code)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('V5_MISSING_EXTENSION_ONLY_NEWLINE_SOURCE_READER_FIX_CONSUMED_ACTUAL.json',dict(epoch=time.time(),previous_source239_SyntaxError_preserved=True,only_unexecuted_source_metadata_publisher=True,no_model_copy_hash_load_SDK_or_GPU=True))
 copy=json.loads((R/'E0_89D_ACTUAL_QUALIFIED_SOURCE_COPY_AND_FAILED_RESOURCE_ADMITTED.json').read_bytes());assert copy['actual_unchanged_qualified_model_runtime_copy_fullSHA']
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('V5_missing_source_metadata_secret_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  result=d.code(c,d.PY72,code,dict(root=q.ROOT,old=q.OLD,name=q.NAME,ending_SHA='e90bda2d34777c60661880f9aa390bd6974437e21a4a9adfade71b933d096ef1',copy_receipt=copy),timeout=60)
  sf=c.open_sftp()
  try:
   with sf.open(result['path'],'rb') as f:raw=f.read()
  finally:sf.close()
  assert hashlib.sha256(raw).hexdigest()==result['SHA']
  with (R/'E0_V5_WRITER_PRESAVE_SOURCE_MIGRATION_ACTUAL.json').open('xb') as f:f.write(raw)
  final=dict(actual_finite_returned=True,actual_new89D_source_copy_and_V5_only_migration_passed=True,source_CPU_SHA=result['SHA'],source_SHA=result['value']['source_SHA'],worker_SHA=result['value']['target_worker_SHA'],root=q.ROOT,no_GPU_GO_or_model_reload=True,previous_source239_error_not_overwritten=True)
  put('E0_UNUSED89D_V5_SOURCE_EXTENSION_MISSING_ONLY_RETURNED_ACTUAL.json',final);print(json.dumps(final))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('V5_MISSING_SOURCE_PUBLISH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_Go_or_hotpatch=True));raise
