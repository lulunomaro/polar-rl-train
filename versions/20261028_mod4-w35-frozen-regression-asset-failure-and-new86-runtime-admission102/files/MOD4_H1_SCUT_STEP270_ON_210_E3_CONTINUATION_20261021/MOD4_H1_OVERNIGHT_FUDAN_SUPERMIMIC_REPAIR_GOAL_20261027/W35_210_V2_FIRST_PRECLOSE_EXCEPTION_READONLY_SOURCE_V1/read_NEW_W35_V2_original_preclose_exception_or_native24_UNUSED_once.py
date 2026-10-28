"""One bounded original-own first proof reader, no GPU/model/C/account operations."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
JOB='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v2/w35'
CODE=r'''
from pathlib import Path
import json,os,time
J=Path(v['job']);assert J.resolve()==J
expected=v['supervisor'];sup=json.loads((J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json').read_bytes());assert sup==expected
def state(row):
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return dict(original_out=True,expected=row,reason='known original PID absent')
 if creation!=row['creation']:return dict(original_out=True,expected=row,reason='PID reused; no new exe/argv inspected')
 return dict(original_out=a[0]=='Z',expected=row,state=a[0],creation=creation)
deadline=time.time()+110;F=J/'frozen_regression';terminal=J/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json';restore=F/'ACTUAL_ORIGINAL_N20K_W35_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json';native=F/'ACTUAL_NATIVE24_W35_40050_MEAN.json'
while True:
 errors=list(F.glob('*ORIGINAL_ERROR*.json')) if F.exists() else []
 errors+=list(J.glob('*SUPERVISOR_ORIGINAL_ERROR*.json'))
 exact=F/'FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json'
 if exact.exists():errors.append(exact)
 if restore.exists() and native.exists() or errors or terminal.exists() or time.time()>=deadline:break
 time.sleep(1)
read=lambda p:json.loads(p.read_bytes()) if p.exists() else None
worker=read(J/'OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json');rr=read(restore);nn=read(native);tt=read(terminal)
passed=bool(rr and rr['passed'] and rr['source_SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f' and rr['Adam_step']==648360 and nn and nn['passed'] and nn['controls']==24 and nn['physics_callbacks']==192 and nn['feedback_samples']==48 and not errors)
texts=[]
for p in [J/'ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',J/'FROZEN_CASE_TASK.json',J/'OWN_PRIVATE210_EX_ACQUIRED_FOR_FROZEN_EVAL.json',J/'FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',J/'FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log',restore,native,terminal]+errors:
 if p.exists() and p.is_file():
  assert p.resolve().is_relative_to(J) and not p.is_symlink();raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),UTF8=raw.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),passed_original_W35_GPU_fullrestore_and_native24=passed,source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',supervisor_state=state(sup),worker_state=state(worker) if worker else None,restore=rr,native24=nn,original_terminal_if_present=tt,original_errors=[dict(path=str(p),value=read(p)) for p in errors],complete_original_read_texts=texts,no_GPU_query_actor_model_or_account_IO=True,firstreader_not_skill_graduation=True,no_stop_or_hotpatch=True)))
'''
def put(n,v):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 R.mkdir(exist_ok=True);put('FIRST_NEW_V2_W35_DIAGNOSTIC_READ_CONSUMED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),maximum_remote_seconds=120,no_model_GPU_or_Canonical_operation=True))
 actual=json.loads((L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/reports/NEW_W35_V2_SOURCE_SDK_AND_FINITE_DIAGNOSTIC_DETACHED_RETURNED_ACTUAL.json').read_bytes());assert actual['passed_source_admission_and_detached_only'];wrapper=module('compressed_same_memory_for_W35_first_once',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_NEW_V2_W35_DIAGNOSTIC_READ',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=route.connect();value=d.code(client,route.PY,CODE,dict(job=JOB,supervisor=actual['identity']),timeout=120);put('W35_V2_FIRST_GPU_NATIVE24_OR_ORIGINAL_PRECLOSE_EXCEPTION_RETURNED_ACTUAL.json',value);print(json.dumps({k:v for k,v in value.items() if k not in ['complete_original_read_texts','restore']}))
 finally:
  stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('FIRST_NEW_V2_W35_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
