"""First-only readonly own receipts. No policy/model/GPU query/lock/account IO."""
from pathlib import Path
import hashlib,json,os,shlex,socket,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
JOB='/data/robemo/polar-rl-train/evaluation_runs/W35_ADAPTED92_N20K_PROFILE_20261029v2/w35'
CODE=r'''
from pathlib import Path
import hashlib,json,os,time
J=Path(v['job']);assert J==Path('/data/robemo/polar-rl-train/evaluation_runs/W35_ADAPTED92_N20K_PROFILE_20261029v2/w35') and J.resolve()==J
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
sup=read(J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json');assert sup==v['supervisor']
def state(row):
 if row is None:return None
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));created=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return dict(original_out=True,expected=row,reason='original PID absent')
 if created!=row.get('creation'):return dict(original_out=True,expected=row,reason='PID reused, no replacement exe/argv queried')
 if a[0]=='Z':return dict(original_out=True,expected=row,state='Z',reason='original nonexecuting zombie, actual wait still in supervisor receipt')
 actual=dict(pid=row['pid'],creation=created,exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink(p/'cwd'))
 return dict(original_out=False,expected=row,actual=actual,known_identity_exact=actual==row,state=a[0])
F=J/'frozen_regression';restore=F/'ACTUAL_ORIGINAL_N20K_W35_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json';native=F/'ACTUAL_NATIVE24_W35_40050_MEAN.json';terminal=J/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json';limit=time.monotonic()+110
while True:
 errors=list(F.glob('*ORIGINAL_ERROR*.json'))+list(F.glob('*EXCEPTION_BEFORE_APP_CLOSE*.json')) if F.exists() else []
 errors+=list(J.glob('*SUPERVISOR_ORIGINAL_ERROR*.json'))
 if (restore.exists() and native.exists()) or errors or terminal.exists() or time.monotonic()>=limit:break
 time.sleep(1)
rr=read(restore);nn=read(native);tt=read(terminal);worker=read(J/'OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json');passed=bool(rr and rr['passed'] and rr['source_SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f' and rr['Adam_step']==648360 and nn and nn['passed'] and nn['controls']==24 and nn['physics_callbacks']==192 and nn['feedback_samples']==48 and not errors)
paths=[J/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json',J/'W35_NEW86_CPU_ORIGINAL_WAIT_PROOF.json',J/'FROZEN_CASE_TASK.json',J/'FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',J/'OWN_PRIVATE86_EX_ACQUIRED_FOR_FROZEN_EVAL.json',J/'FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log',J/'FROZEN_W35_SUPERVISOR_COMPLETE_STDOUT_STDERR.log',restore,native,terminal]+errors;texts=[]
for p in dict.fromkeys(paths):
 if not p.exists():continue
 assert p.resolve().is_relative_to(J) and not p.is_symlink();before=p.stat();raw=p.read_bytes();after=p.stat();texts.append(dict(path=str(p),bytes_read=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),before_bytes=before.st_size,after_bytes=after.st_size,live_snapshot_may_grow=before.st_size!=after.st_size or before.st_mtime_ns!=after.st_mtime_ns))
print(json.dumps(dict(epoch=time.time(),passed_first_actual_W35_GPU_fullrestore_native24=passed,supervisor_state=state(sup),worker_state=state(worker),restore=rr,native24=nn,original_terminal_if_present=tt,original_errors=[dict(path=str(p),value=read(p)) for p in dict.fromkeys(errors)],complete_original_read_text_snapshots=texts,no_GPU_query_model_actor_optimizer_lock_or_C_IO=True,not1200coverage_or_skill_graduation=True,first_purpose_not_repeated_progress_watcher=True)))
'''
def put(n,x):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main():
 actual=L/'NEW86_W35_ADAPTED92_N20K_PROFILE_REGRESSION_SOURCE_V1/reports/NEW86_W35_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json';v=json.loads(actual.read_bytes());assert v['passed_source_CPU_and_detached_only'] and v['detached']['actual_detached'];expected=v['detached']['identity'];assert expected['pid']==516972 and expected['creation']==1793206302.73
 put('NEW86_W35_DISTINCT_FIRST_READ_CONSUMED_BEFORE_STDIN.json',dict(epoch=time.time(),purpose='first GPU fullrestore/native24 or original error, not terminal collection/relaunch',known_supervisor=expected,actual_startup_report_SHA=hashlib.sha256(actual.read_bytes()).hexdigest(),max_after_stdin180=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True);req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';secret=req.pop('password');t=None
 try:
  sock=socket.create_connection((req['host'],22),timeout=10);t=paramiko.Transport(sock);t.banner_timeout=10;t.auth_timeout=10;t.start_client(timeout=10);assert hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest()==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password(req['username'],secret,fallback=False);secret=None
  ch=t.open_session(timeout=10);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote("import json,sys;v=json.loads(sys.stdin.readline());exec(v['code'])"));ch.settimeout(150)
  try:
   f=ch.makefile_stdin('wb');f.write((json.dumps(dict(job=JOB,supervisor=expected,code=CODE))+chr(10)).encode());f.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(rc,err,out);value=json.loads(out);put('NEW86_W35_FIRST_ACTUAL_GPU_NATIVE24_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',value);print(json.dumps({k:x for k,x in value.items() if k not in ('complete_original_read_text_snapshots','restore')}))
  finally:ch.close()
 finally:
  secret=None
  if t:t.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW86_W35_FIRST_READ_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_retry=True));raise
