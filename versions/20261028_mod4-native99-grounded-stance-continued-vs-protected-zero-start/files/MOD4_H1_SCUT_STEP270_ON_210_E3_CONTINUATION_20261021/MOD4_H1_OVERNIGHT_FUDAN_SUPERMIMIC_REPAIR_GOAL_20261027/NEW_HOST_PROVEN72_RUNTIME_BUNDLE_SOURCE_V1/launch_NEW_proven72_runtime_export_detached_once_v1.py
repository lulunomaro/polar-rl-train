"""Pinned memory-only72 transport; launches only a NEW owned CPU archive export."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,shlex,socket,sys,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
SOURCE='/home/lc01/Zonglin Li/zonglin2';RUN=SOURCE+'/runtime_exports/MOD4_PROVEN72_RUNTIME_FOR86_20261028_V1'
PY=[SOURCE+'/compat/glibc240/ld-linux-x86-64.so.2','--library-path',SOURCE+'/compat/glibc240:'+SOURCE+'/envs/mod4/lib',SOURCE+'/envs/mod4/bin/python','-S','-B','-u']
PIN='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
def put(n,v):
 R.mkdir(parents=True,exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 put('PROVEN72_EXPORT_STARTUP_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),secret_in_memory_only=True,no_GPU_model_or_account=True,maximum_startup_seconds=120,maximum_background_pack_seconds=1800))
 helper=B/'pack_proven72_runtime_owned_supervisor_v1.py';raw=helper.read_bytes();ast.parse(raw);want=hashlib.sha256(raw).hexdigest()
 frozen=json.loads((B/'FROZEN_PROVEN72_RUNTIME_EXPORT_SOURCE_INDEX_V1.json').read_bytes());assert frozen['helper_SHA']==want
 wrapper=module('same_compressed_memory_for_new_runtime_export',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();secret=None;t=None;sf=None
 def run(code):
  ch=t.open_session(timeout=15);ch.exec_command(' '.join(shlex.quote(x) for x in PY+['-c',code]));ch.settimeout(45);out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(err,out);return json.loads(out)
 try:
  sec=module('same72_secret_memory_for_new_runtime_export',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();sock=socket.create_connection(('10.24.0.72',22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15);actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password('lc01',secret,fallback=False);secret=None
  print(json.dumps(dict(stage='PINNED_NEW_SOURCE72_CPU_EXPORT_STARTUP',epoch=time.time())),flush=True)
  code="from pathlib import Path\nimport json,time\nS=Path("+repr(SOURCE)+");B=Path("+repr(RUN)+")\nassert S.resolve()==S and not S.is_symlink() and B.resolve().is_relative_to(S/'runtime_exports') and not B.exists()\nB.mkdir(parents=True,mode=0o700)\nwith (B/'OWN_RUNTIME_EXPORT_MARKER.json').open('x') as f:json.dump(dict(root=str(B),source_root=str(S),purpose='USER requested existing proven runtime migration only',no_source_env_mutation=True,no_GPU_model_or_account=True),f)\nprint(json.dumps(dict(passed=True,new_owned_root=str(B),epoch=time.time())))"
  guard=run(code);put('PROVEN72_NEW_EXPORT_NAMESPACE_ACTUAL.json',guard)
  sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(30)
  with sf.open(RUN+'/'+helper.name,'wx') as f:f.write(raw)
  with sf.open(RUN+'/PACK_BUDGET.json','wx') as f:f.write(json.dumps(dict(max_seconds=1800,pigz_threads=2)).encode())
  sf.close();sf=None
  code="from pathlib import Path\nimport hashlib,importlib.util,json,subprocess,time\nB=Path("+repr(RUN)+");p=B/"+repr(helper.name)+"\nassert hashlib.sha256(p.read_bytes()).hexdigest()=="+repr(want)+"\ns=importlib.util.spec_from_file_location('owned_runtime_export',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.scope();env=m.environment()\nwith (B/'EXPORT_SUPERVISOR_FULL.log').open('xb') as f:child=subprocess.Popen(m.PY+[str(p),'--supervise'],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)\nidentity=m.ident(child.pid)\nfor _ in range(100):\n if (B/'OWN_EXPORT_LOCK_ACQUIRED_ACTUAL.json').exists() and (B/'EXPORT_WORKER_IDENTITY_ACTUAL.json').exists():break\n assert child.poll() is None,'owned export supervisor ended before startup receipts';time.sleep(.05)\nassert (B/'OWN_EXPORT_LOCK_ACQUIRED_ACTUAL.json').exists() and (B/'EXPORT_WORKER_IDENTITY_ACTUAL.json').exists()\nv=dict(passed_detached_startup_only=True,epoch=time.time(),root=str(B),supervisor=identity,worker=json.loads((B/'EXPORT_WORKER_IDENTITY_ACTUAL.json').read_bytes()),own_lock=json.loads((B/'OWN_EXPORT_LOCK_ACQUIRED_ACTUAL.json').read_bytes()),helper_SHA="+repr(want)+",budget_seconds=1800,pigz_threads=2,producer_not_yet_observed=True,no_GPU_model_GO_budget_or_source_env_write=True)\nwith (B/'EXPORT_DETACHED_STARTUP_ACTUAL.json').open('x') as f:json.dump(v,f,indent=2)\nprint(json.dumps(v))"
  value=run(code);put('PROVEN72_RUNTIME_EXPORT_DETACHED_STARTUP_RETURNED_ACTUAL.json',dict(**value,actual_startup_finite_returned=True,actual_returncode=0));print(json.dumps(value))
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('PROVEN72_EXPORT_STARTUP_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
