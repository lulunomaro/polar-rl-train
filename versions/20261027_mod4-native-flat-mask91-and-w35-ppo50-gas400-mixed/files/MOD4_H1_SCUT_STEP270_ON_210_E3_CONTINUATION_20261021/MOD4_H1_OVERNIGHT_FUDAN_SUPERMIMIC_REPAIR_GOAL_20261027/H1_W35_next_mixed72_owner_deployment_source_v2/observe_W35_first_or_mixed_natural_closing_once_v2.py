"""One read-only first-W35 observer, or natural closing, via one finite SSH handle."""
from pathlib import Path
import os,sys,json,time,shlex,importlib.util,traceback
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];R=HERE/'reports'
CODE=r"""import sys,json,traceback
from pathlib import Path
r=v['request'];sys.path.insert(0,r['owner_root'])
def emit(value):print(json.dumps(value),flush=True)
try:
 if v['mode']=='first':
  from W35_first_real_GPU_PPO_metadata_observer_v2 import watch
 else:
  from W35_shared72_natural_closing_metadata_v2 import watch
 result=watch(r,max_wait_seconds=780,emit=emit)
 emit(dict(stage='FINITE_READONLY_OBSERVER_RETURNED',result=result))
except BaseException:
 emit(dict(stage='FINITE_READONLY_OBSERVER_ORIGINAL_ERROR',error=traceback.format_exc()));raise
"""
def save(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==2 and sys.argv[1] in ('first','closing');mode=sys.argv[1];prefix='W35_FIRST_PPO' if mode=='first' else 'MIXED_NATURAL_CLOSING'
 save(prefix+'_FINITE_ENTERED_ACTUAL_V2.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),mode=mode,no_weight_GPU_or_account_mutation=True))
 request=json.loads((HERE/'ACTUAL_MIXED72_OBSERVER_REQUEST_SEALED.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_readonly_observer_v2',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  i,o,e=c.exec_command(shlex.quote(d.PY72)+' -u -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"),timeout=820)
  i.write(json.dumps(dict(code=CODE,mode=mode,request=request))+chr(10));i.flush();i.channel.shutdown_write();ch=o.channel;buf=b'';stderr=b'';last=time.time();start=time.time();final=None
  with (R/(prefix+'_EXACT_ORIGINAL_STREAM_ACTUAL_V2.jsonl')).open('x',encoding='utf8') as log:
   while not ch.exit_status_ready() or ch.recv_ready() or ch.recv_stderr_ready():
    if ch.recv_ready():
     buf+=ch.recv(65536)
     while b'\n' in buf:
      line,buf=buf.split(b'\n',1)
      if line:
       value=json.loads(line);log.write(json.dumps(value,ensure_ascii=False)+chr(10));log.flush();last=time.time()
       if value.get('stage')=='FINITE_READONLY_OBSERVER_RETURNED':final=value['result']
       if value.get('stage')=='FINITE_READONLY_OBSERVER_ORIGINAL_ERROR':print(json.dumps(value),flush=True)
       else:print(json.dumps(dict(stage=value.get('stage'),epoch=time.time(),first_positive_PPO_observed=(value.get('value') or value.get('result') or {}).get('first_positive_PPO_observed'))),flush=True)
    if ch.recv_stderr_ready():stderr+=ch.recv_stderr(65536)
    if time.time()-last>=30:print(json.dumps(dict(stage='SAME_HANDLE_READONLY_WAIT',epoch=time.time())),flush=True);last=time.time()
    assert time.time()-start<820,'finite observer original timeout, no second reader/kill/account write'
    time.sleep(.2)
  rc=ch.recv_exit_status();value=dict(actual_finite_returned=True,actual_returncode=rc,epoch=time.time(),result=final,stderr=stderr.decode(errors='replace'),remaining_stdout=buf.decode(errors='replace'),no_model_read_hash_or_account_write=True)
  save(prefix+'_FINITE_RETURNED_ACTUAL_V2.json',value);print(json.dumps(value))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  mode=sys.argv[1] if len(sys.argv)>1 else 'unknown';save('READONLY_'+mode+'_LOCAL_ORIGINAL_ERROR_ACTUAL_V2.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_other_remote=True));raise
