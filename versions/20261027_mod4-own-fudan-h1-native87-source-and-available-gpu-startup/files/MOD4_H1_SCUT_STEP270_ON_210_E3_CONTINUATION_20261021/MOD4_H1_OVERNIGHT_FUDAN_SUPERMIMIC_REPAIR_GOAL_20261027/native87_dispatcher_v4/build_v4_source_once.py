"""Local source derivation only. No production CPU/model/process invocation."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'native87_dispatcher_v3/native87_closed_source_CPU_v1.py'
raw=OLD.read_bytes(); text=raw.decode('utf8').replace('\r\n','\n').replace('\r','')
(HERE/'ORIGINAL_V3_BYTES.txt').write_bytes(raw)
start=text.index('def wait_exact_exec_identity(')
end=text.index('\ndef validate_proof_data(',start)
replacement='''class ExecIdentityError(AssertionError):
    def __init__(self,reason,expected,lastrow,pid,creation,last_observation_error=None):
        self.details=dict(reason=reason,expected=expected,lastrow=lastrow,pid=pid,
            expected_creation=creation,last_observation_error=last_observation_error,
            mismatch={k:dict(expected=expected[k],actual=None if lastrow is None else lastrow.get(k))
                for k in ('exe','argv','root') if lastrow is None or lastrow.get(k)!=expected[k]})
        super().__init__(json.dumps(self.details,sort_keys=True))

def wait_exact_exec_identity(p,B,spec,args,timeout_s=5.):
    import psutil
    expected=expected_exec_identity(spec,args,B);until=time.monotonic()+timeout_s
    creation=None;previous=None;lastrow=None;last_observation_error=None
    while True:
        if p.poll() is not None:
            raise ExecIdentityError('child_exited_before_stable_exact_exec',expected,lastrow,p.pid,creation,last_observation_error)
        try:
            # psutil.Process.exe() caches per instance. A wrapper exec requires a
            # fresh instance on EVERY observation; retain pid/create separately.
            process=psutil.Process(p.pid)
            row=dict(pid=p.pid,creation=process.create_time(),argv=process.cmdline(),root=process.cwd(),exe=process.exe())
            lastrow=row;last_observation_error=None
            if creation is None:creation=row['creation']
            if row['creation']!=creation:
                raise ExecIdentityError('pid_creation_changed_during_exec',expected,row,p.pid,creation)
            exact=all(row[k]==expected[k] for k in ('exe','argv','root'))
            if exact and row==previous:return row
            previous=row if exact else None
        except (psutil.NoSuchProcess,psutil.AccessDenied) as exc:
            last_observation_error=dict(type=type(exc).__name__,error=str(exc));previous=None
        if time.monotonic()>=until:
            raise ExecIdentityError('exact_exec_identity_timeout',expected,lastrow,p.pid,creation,last_observation_error)
        time.sleep(.05)
'''
text=text[:start]+replacement+text[end:]
old='''    try:
        identity=wait_exact_exec_identity(p,B,spec,args)
        b.put(B/STARTED_RELATIVE,identity)
    finally:rc=p.wait()
    waited_epoch=time.time();b.put(B/WAITED_RELATIVE,dict(pid=p.pid,returncode=rc,actual_waited=True,waited_epoch=waited_epoch));assert rc==0
'''
new='''    try:
        identity=wait_exact_exec_identity(p,B,spec,args)
        b.put(B/STARTED_RELATIVE,identity)
    except BaseException as exc:
        import traceback
        error=dict(epoch=time.time(),pid=p.pid,type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc(),
            details=getattr(exc,'details',None),no_ready_or_proof_claim=True)
        with (B/'job0/native87_SOURCE_CPU_IDENTITY_ERROR_ACTUAL.json').open('x',encoding='utf8') as stream:
            json.dump(error,stream,indent=2,allow_nan=False)
        raise
    finally:
        # Persist the genuine wait result even if identity capture raised. A
        # waited EXIT0 alone never creates a ready envelope or admission proof.
        rc=p.wait();waited_epoch=time.time()
        b.put(B/WAITED_RELATIVE,dict(pid=p.pid,returncode=rc,actual_waited=True,waited_epoch=waited_epoch))
    assert rc==0
'''
assert text.count(old)==1
text=text.replace(old,new)
ast.parse(text)
newpath=HERE/'native87_closed_source_CPU_v1.py'
with newpath.open('x',encoding='utf8',newline='\n') as f:f.write(text)
def H(b):return hashlib.sha256(b).hexdigest()
origin=dict(previous_path=str(OLD),previous_SHA=H(raw),new_path=str(newpath),new_SHA=H(newpath.read_bytes()),
    changes=['fresh psutil.Process for each identity observation, fixed pid/create invariant',
    'structured timeout/exit failure with expected/lastrow/differences',
    'identity error retained; genuine child.wait receipt in finally on success or failure'],
    exact_recipe_unchanged=True,cache_and_admission_rules_unchanged=True,
    not_claiming_cache_is_proven_unique_remote_cause=True,production_execution=False)
with (HERE/'ORIGIN.json').open('x',encoding='utf8') as f:json.dump(origin,f,indent=2)
print(json.dumps(origin))
