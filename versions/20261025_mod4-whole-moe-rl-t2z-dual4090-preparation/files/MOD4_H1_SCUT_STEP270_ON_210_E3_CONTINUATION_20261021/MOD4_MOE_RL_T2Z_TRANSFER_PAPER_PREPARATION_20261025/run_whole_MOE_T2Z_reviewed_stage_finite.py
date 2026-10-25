"""One exact isolated preparation action per invocation, serial root transport."""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports'
ROOT='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
choices=['stage-method','cpu-imports','method-tests']+['download'+str(i).zfill(2) for i in range(1,21)]+['verify-final']
p=argparse.ArgumentParser();p.add_argument('stage',choices=choices);args=p.parse_args();stage=args.stage
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
try:
 for phase in ('torch','requirements','check'):
  value=json.loads((R/('HOST72_'+phase.upper()+'_FINITE_PHASE_RETURNED_ACTUAL.json')).read_bytes());assert value['phase_passed'] and value['actual_returncode']==0
 put('HOST72_REVIEWED_'+stage+'_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,root=ROOT,no_training=True))
 helper=Z/'root_preparation_sources/weights_and_method_stage_v1'
 request=dict(root=ROOT,action=stage,phase_id={'stage-method':'METHOD_STAGE_EXACT71_V1','cpu-imports':'CPU_IMPORT_REGISTRY_V1','method-tests':'METHOD_CPU_TESTS_AND_BIND_V1','verify-final':'WEIGHTS_FINAL_FULL_SHA_V1'}.get(stage,'WEIGHTS_BATCH_'+stage.removeprefix('download')))
 timeout=660
 if stage=='stage-method':
  raw=(helper/'cpu_method_runner.py').read_bytes()
  request.update(method_payload=json.loads((helper/'METHOD_TRANSFER_PAYLOAD.json').read_bytes()),cpu_runner=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
 elif stage=='method-tests':request['method_stage_binding']=ROOT+'/receipts/METHOD_STAGE_EXACT71_V1_METHOD_SOURCE_BINDING.json'
 elif stage.startswith('download'):
  request.update(action='download-batch',max_seconds=300,max_files=13,max_new_bytes=8*1024**3);timeout=480
 elif stage=='verify-final':request['action']='verify-weights';timeout=1980
 remote="""from pathlib import Path
import base64,hashlib,json,time
ns={'__name__':'reviewed_stage_helper'};exec(v['helper_source'],ns)
result=ns['run_request'](v['request']);result['text_files']=[]
for p in sorted((Path(v['request']['root'])/'receipts').rglob('*')):
 if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.json','.jsonl','.py','.txt','.md','.log','.csv','.yaml','.yml','.sh'):
  raw=p.read_bytes();result['text_files'].append(dict(relative=p.relative_to(Path(v['request']['root'])/'receipts').as_posix(),path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(result))
"""
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(spec);spec.loader.exec_module(memory);secret=memory.recover();c=d.connect72(secret);secret=None
 try:result=d.code(c,d.PY72,remote,dict(helper_source=(helper/'remote_stage_helper.py').read_text('utf8'),request=request),timeout=timeout)
 finally:c.close()
 dest=Z/'actual_host72_preparation_texts'/('reviewed_'+stage);dest.mkdir()
 for row in result['text_files']:
  rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
  raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
  target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write(raw)
  row['local_path']=str(target)
 put('HOST72_REVIEWED_'+stage+'_RETURNED_ACTUAL.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='text_files'}))
except BaseException:
 put('HOST72_REVIEWED_'+stage+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_budget_change=True));raise
