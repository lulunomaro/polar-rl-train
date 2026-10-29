from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
JOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main(mode):
 p=argparse.ArgumentParser();p.add_argument('--actual-startup-json',type=Path,required=True);p.add_argument('--actual-startup-SHA',required=True);a=p.parse_args();assert H(a.actual_startup_json)==a.actual_startup_SHA;actual=json.loads(a.actual_startup_json.read_bytes());assert actual['passed_source_CPU_and_detached_only'] and actual['job_root']==JOB and actual['detached']['actual_detached']
 sup=actual['detached']['identity'];assert sup['cwd']==JOB and str(Path(JOB)/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py') in sup['argv'];assert sup['argv'][-2:]==['--job-root',JOB]
 if mode=='terminal':assert sup['creation']+1800-time.time()<=900,'Original local supervisor remaining<=900 gate closed; once not consumed'
 index=json.loads((B/'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V1.json').read_bytes());codefile=B/'E3_source210_actual_receipts_readonly_CODE_v1.py';assert H(codefile)==index['local_source_SHAs'][codefile.name];code=next(ast.literal_eval(n.value) for n in ast.parse(codefile.read_bytes()).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));ast.parse(code)
 put('E3_SOURCE210_'+mode.upper()+'_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),known_supervisor=sup,actual_startup_SHA=a.actual_startup_SHA,purpose=mode,no_model_GPUquery_or_account=True))
 wrapper=module('E3_source210_readonly_same_compressed_memory_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d;sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route;client=None
 try:
  client=route.connect();value=d.code(client,route.PY,code,dict(job=JOB,mode=mode,supervisor=sup,manifest_SHA=index['manifest_SHA'],worker_SHA=index['local_source_SHAs']['evaluate_E3_adapted97_source210_frozen600_once_v1.py']),timeout=180 if mode=='first' else 960);put('E3_SOURCE210_'+mode.upper()+'_ORIGINAL_RETURNED_ACTUAL.json',value);print(json.dumps({k:x for k,x in value.items() if k not in ('complete_original_own_stage_UTF8','original_terminal','restore')}))
 finally:
  if client:client.close()
  transport.SESSION=previous
